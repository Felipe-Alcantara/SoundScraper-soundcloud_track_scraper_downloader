"""
pipeline.py — Orquestração da coleta com fallback entre métodos.

Estratégia (decisão do projeto): tentar o método MAIS FÁCIL e robusto primeiro
(API v2 HTTP, sem navegador) e só cair para o navegador (Selenium) se necessário.
A ordem fica em get_pipeline(), então somar um método novo é só registrar o adapter.

Falha de forma segura: se nenhum método coletar nada, devolve lista vazia
(nunca dado parcial enganoso) com um resumo auditável.
"""

from .base import LogFn, SourceAdapter, _noop
from .config import ScraperConfig
from .adapters.http_api import HttpApiAdapter
from .adapters.selenium_browser import SeleniumAdapter
from .models import CollectResult, TrackLink
from .registry import ChoiceSpec, get_choice


def get_pipeline() -> list[SourceAdapter]:
    """Métodos de coleta na ordem de tentativa: o mais fácil/robusto primeiro."""
    return [HttpApiAdapter(), SeleniumAdapter()]


def build_target_url(profile_url: str, spec: ChoiceSpec) -> str:
    """
    Monta a URL final. Para perfis, anexa o sufixo da opção (/tracks, /likes, ...).
    Para sets (álbum/playlist), a URL recebida já é o link do conjunto.
    """
    if spec.is_set:
        return profile_url
    return f"{profile_url.rstrip('/')}{spec.url_suffix}"


def _dedupe(tracks: list[TrackLink]) -> list[str]:
    """Deduplica por URL preservando ordem estável (sorted no fim)."""
    seen = set()
    for t in tracks:
        if t.url:
            seen.add(t.url)
    return sorted(seen)


def collect(
    profile_url: str,
    choice: str,
    config: ScraperConfig | None = None,
    log: LogFn = _noop,
    on_track=None,
) -> CollectResult:
    """
    Coleta os links para uma opção, tentando cada método na ordem do pipeline
    até obter resultado. Retorna um CollectResult com a lista deduplicada.

    Args:
        profile_url: URL do perfil (ou do set, para álbum/playlist).
        choice: opção '1'..'7'.
        config: limites operacionais (default: ScraperConfig.from_env()).
        log: callback de log (print no CLI, WebSocket no backend).
        on_track: callback opcional chamado por URL coletada (índice, total).
    """
    config = config or ScraperConfig.from_env()
    spec = get_choice(choice)  # opção inválida → ValueError claro
    target = build_target_url(profile_url, spec)
    log(f"Modo: {spec.name} — {target}")

    result = CollectResult()
    for adapter in get_pipeline():
        log(f"── Tentando {adapter.display_name}...")
        try:
            tracks = adapter.collect(target, spec, config, log)
        except Exception as exc:
            log(f"⚠️ {adapter.display_name} falhou: {exc}")
            tracks = []

        if tracks:
            result.by_source[adapter.slug] = len(tracks)
            urls = _dedupe(tracks)
            result.urls = urls
            result.used_source = adapter.slug
            log(f"✅ {adapter.display_name}: {len(urls)} faixa(s) (após dedupe).")
            break  # método mais fácil já resolveu; não precisa do fallback
        log(f"… {adapter.display_name} não trouxe resultados; tentando o próximo método.")

    if not result.urls:
        log("❌ Nenhum método coletou links.")
        return result

    if on_track:
        total = len(result.urls)
        for i, url in enumerate(result.urls, 1):
            on_track(url, i, total)

    return result
