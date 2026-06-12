"""
http_api.py — Adapter de coleta via API v2 do SoundCloud (sem navegador).

É o método PREFERIDO: não depende de Chrome/Selenium, é estável e funciona em
qualquer SO. Faz apenas o I/O HTTP (urllib, sem dependências extras) e delega
todo o parsing para core/scraping/parsers.py (testável offline).
"""

import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..base import LogFn, SourceAdapter, _noop
from ..config import ScraperConfig
from ..models import SOURCE_HTTP_API, TrackLink
from ..registry import ChoiceSpec
from .. import parsers

_DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
_API_HEADERS = {
    "User-Agent": _DEFAULT_UA,
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "https://soundcloud.com",
    "Referer": "https://soundcloud.com/",
}
_API_BASE = "https://api-v2.soundcloud.com"

# Rate-limit / erros transitórios: respeita Retry-After (429) e faz backoff
# exponencial em 5xx. 4xx definitivo não é repetido (não adianta).
_BACKOFF_BASE = 2.0
_MAX_RETRIES = 3
_MAX_BACKOFF_S = 30.0


def http_get(url: str, headers: dict | None = None, timeout: float = 30.0) -> str | None:
    """
    GET via urllib. Retorna o corpo como texto, ou None em erro.

    Respeita rate-limit (429 com Retry-After) e tenta novamente em erros
    transitórios (5xx) com backoff exponencial. 4xx definitivo (exceto 429)
    não é repetido. Fail-safe: esgotadas as tentativas, devolve None.
    """
    req = Request(url, headers=headers or {"User-Agent": _DEFAULT_UA})
    for attempt in range(_MAX_RETRIES):
        try:
            with urlopen(req, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            wait = _retry_wait(exc, attempt)
            if wait is None or attempt == _MAX_RETRIES - 1:
                return None  # 4xx definitivo, ou tentativas esgotadas
            time.sleep(wait)
        except (URLError, TimeoutError):
            return None
    return None


def _retry_wait(exc: HTTPError, attempt: int) -> float | None:
    """
    Segundos a esperar antes de repetir, ou None se o erro não é repetível.

    429 → respeita Retry-After (senão, backoff). 5xx → backoff exponencial.
    Demais 4xx → None (não repete).
    """
    if exc.code == 429:
        retry_after = 0
        try:
            retry_after = int(exc.headers.get("Retry-After", 0) or 0)
        except (TypeError, ValueError):
            retry_after = 0
        return float(retry_after) or min(_BACKOFF_BASE ** attempt, _MAX_BACKOFF_S)
    if exc.code >= 500:
        return min(_BACKOFF_BASE ** attempt, _MAX_BACKOFF_S)
    return None


def fetch_client_id(timeout: float = 30.0) -> str | None:
    """Baixa a home do SoundCloud e extrai o client_id dos últimos scripts JS."""
    html = http_get("https://soundcloud.com", timeout=timeout)
    if not html:
        return None
    script_urls = parsers.find_script_urls(html)
    for script_url in script_urls[-3:]:
        js = http_get(script_url, timeout=timeout)
        client_id = parsers.extract_client_id_from_js(js or "")
        if client_id:
            return client_id
    return None


def resolve_url(url: str, client_id: str, timeout: float = 30.0) -> dict | None:
    """Resolve uma URL via API v2 (/resolve) e devolve o dict, ou None."""
    api_url = f"{_API_BASE}/resolve?url={url}&client_id={client_id}"
    body = http_get(api_url, headers={"User-Agent": _DEFAULT_UA, "Accept": "application/json"}, timeout=timeout)
    return parsers.parse_resolved_user(body or "")


class HttpApiAdapter(SourceAdapter):
    slug = SOURCE_HTTP_API
    display_name = "API v2 (HTTP)"

    def collect(
        self,
        profile_url: str,
        spec: ChoiceSpec,
        config: ScraperConfig,
        log: LogFn = _noop,
    ) -> list[TrackLink]:
        timeout = config.timeout_ms / 1000.0
        log("Obtendo client_id do SoundCloud...")
        client_id = fetch_client_id(timeout=timeout)
        if not client_id:
            log("❌ Não foi possível obter o client_id (o site pode ter mudado).")
            return []
        log(f"✅ client_id obtido: {client_id[:8]}...")

        if spec.is_set:
            return self._collect_set(profile_url, client_id, config, log)
        return self._collect_collection(profile_url, spec, client_id, config, log)

    def _collect_set(self, set_url, client_id, config, log) -> list[TrackLink]:
        timeout = config.timeout_ms / 1000.0
        data = resolve_url(set_url, client_id, timeout=timeout)
        if not data:
            log("❌ Não foi possível resolver o álbum/playlist.")
            return []
        urls, pending_ids, set_title = parsers.parse_set_dict(data)
        log(f"📀 {set_title or 'Álbum/Playlist'}: {len(urls)} faixa(s) diretas, "
            f"{len(pending_ids)} a resolver.")

        tracks = [TrackLink(url=u, source=self.slug, set_title=set_title) for u in urls]
        for track_id in pending_ids:
            if len(tracks) >= config.max_tracks:
                break
            body = http_get(
                f"{_API_BASE}/tracks/{track_id}?client_id={client_id}",
                headers={"User-Agent": _DEFAULT_UA, "Accept": "application/json"},
                timeout=timeout,
            )
            permalink = parsers.parse_track_permalink(body or "")
            if permalink:
                tracks.append(TrackLink(url=permalink, source=self.slug, set_title=set_title))
        return tracks[: config.max_tracks]

    def _collect_collection(self, profile_url, spec, client_id, config, log) -> list[TrackLink]:
        timeout = config.timeout_ms / 1000.0
        user_data = resolve_url(profile_url, client_id, timeout=timeout)
        if not user_data or "id" not in user_data:
            log("❌ Não foi possível resolver o perfil do artista.")
            return []

        user_id = user_data["id"]
        username = user_data.get("username", "Desconhecido")
        log(f"✅ Artista: {username} (ID: {user_id}) — coletando {spec.name}...")

        tracks: list[TrackLink] = []
        next_href = (
            f"{_API_BASE}/users/{user_id}/{spec.collection_type}"
            f"?client_id={client_id}&limit={config.page_size}&offset=0"
            f"&linked_partitioning=1&app_locale=en"
        )
        page = 0
        while next_href and page < config.max_pages and len(tracks) < config.max_tracks:
            body = http_get(next_href, headers=_API_HEADERS, timeout=timeout)
            if not body:
                log("⚠️ Falha ao carregar página da API. Encerrando coleta.")
                break

            urls, next_href = parsers.parse_collection_page(body, spec.collection_type)
            for url in urls:
                tracks.append(TrackLink(url=url, source=self.slug))
            page += 1
            log(f"📄 Página {page}: +{len(urls)} faixa(s) (total {len(tracks)}).")

            if next_href and "client_id" not in next_href:
                next_href += f"&client_id={client_id}"
            if next_href:
                time.sleep(0.5)

        return tracks[: config.max_tracks]
