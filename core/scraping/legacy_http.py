"""Compatibilidade do scraper HTTP legado.

O pipeline novo usa :mod:`http_api`, mas ``browser_handler`` ainda expõe
funções internas que consumidores antigos importam. Este módulo concentra o
I/O e a orquestração compatível para que o handler fique responsável somente
por navegador e por uma fachada estável.
"""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request

from . import parsers


HttpGet = Callable[[str, dict[str, str] | None], str | None]
ResolveUrl = Callable[[str, str], dict[str, Any] | None]
ExtractClientId = Callable[[str], str | None]

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def http_get(url: str, headers: dict[str, str] | None = None) -> str | None:
    """Faz um GET simples usando apenas a biblioteca padrão."""
    from urllib.request import urlopen

    request = Request(url, headers=headers or DEFAULT_HEADERS)
    try:
        with urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")
    except (URLError, HTTPError) as exc:
        print(f"   ⚠️  Erro HTTP: {exc}")
        return None


def extract_client_id(
    html_content: str,
    http_get_fn: HttpGet = http_get,
) -> str | None:
    """Baixa os scripts da home e extrai o ``client_id`` do SoundCloud."""
    print("🔑 Procurando client_id nos scripts do SoundCloud...")
    script_urls = parsers.find_script_urls(html_content)
    total_scripts = len(script_urls)
    print(f"   📜 {total_scripts} scripts encontrados na página.")
    print(f"   🔍 Analisando os últimos {min(3, total_scripts)} scripts...")
    print("")

    for index, script_url in enumerate(script_urls[-3:], 1):
        print(f"   ⏳ [{index}/3] Analisando script: ...{script_url[-40:]}")
        js_content = http_get_fn(script_url, None)
        client_id = parsers.extract_client_id_from_js(js_content or "")
        if client_id:
            print(f"   ✅ client_id encontrado no script {index}!")
            print("")
            return client_id
        if js_content:
            print("   ❌ client_id não encontrado neste script.")
        else:
            print("   ⚠️  Não foi possível baixar este script.")

    print("")
    print("❌ Não foi possível encontrar o client_id em nenhum script.")
    print("")
    return None


def resolve_url(
    url: str,
    client_id: str,
    http_get_fn: HttpGet = http_get,
) -> dict[str, Any] | None:
    """Resolve uma URL do SoundCloud usando a API v2."""
    print(f"   ⤴️  Resolvendo URL: {url}")
    api_url = f"https://api-v2.soundcloud.com/resolve?url={url}&client_id={client_id}"
    response = http_get_fn(
        api_url,
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        },
    )
    if response:
        data = parsers.parse_resolved_user(response)
        if data is not None:
            print(f"   ✅ Resposta recebida! Tipo: {data.get('kind', 'desconhecido')}")
            return data
        print("   ⚠️  Resposta da API não é um JSON válido.")
        return None
    print("   ❌ Sem resposta da API.")
    return None


def get_collection_tracks(
    user_id: int,
    collection_type: str,
    client_id: str,
    http_get_fn: HttpGet = http_get,
    sleep_fn: Callable[[float], None] = time.sleep,
    limit: int = 200,
) -> list[str]:
    """Coleta faixas de uma coleção paginada da API v2."""
    tracks: list[str] = []
    page = 1
    next_href = (
        f"https://api-v2.soundcloud.com/users/{user_id}/{collection_type}"
        f"?client_id={client_id}&limit=50&offset=0"
        "&linked_partitioning=1&app_locale=en"
    )
    api_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Origin": "https://soundcloud.com",
        "Referer": "https://soundcloud.com/",
    }

    print("─" * 70)
    print(f"⏳ Carregando faixas da API (tipo: {collection_type})...")
    print("─" * 70)
    print("")

    while next_href and len(tracks) < limit * 5:
        print(f"   📄 Carregando página {page}...")
        response = http_get_fn(next_href, api_headers)
        if not response:
            print("   ⚠️  Falha ao carregar página. Encerrando coleta.")
            break

        page_urls, next_href = parsers.parse_collection_page(response, collection_type)
        if not page_urls:
            print("   ℹ️  Nenhuma faixa adicional encontrada nesta página.")
            break

        tracks.extend(page_urls)
        for permalink_url in page_urls:
            print(f"      🔗 {permalink_url}")

        print(f"   ✅ {len(page_urls)} faixa(s) encontrada(s) na página {page}")
        print(f"   📊 Total acumulado: {len(tracks)} faixa(s)")
        print("")

        if next_href and "client_id" not in next_href:
            next_href += f"&client_id={client_id}"
        if next_href:
            print("   ⏳ Carregando próxima página...")
        else:
            print("   ℹ️  Última página alcançada.")

        page += 1
        sleep_fn(0.5)

    print("")
    print("─" * 70)
    print(f"✅ Coleta via API finalizada! Total: {len(tracks)} faixa(s)")
    print("─" * 70)
    print("")
    return tracks


def get_set_tracks(
    set_url: str,
    client_id: str,
    resolve_url_fn: ResolveUrl,
    http_get_fn: HttpGet = http_get,
) -> list[str]:
    """Coleta faixas de um álbum/playlist, resolvendo IDs sem permalink."""
    print("─" * 70)
    print("📀 Resolvendo álbum/playlist via API...")
    print("─" * 70)
    print("")

    data = resolve_url_fn(set_url, client_id)
    if not data:
        print("❌ Não foi possível resolver o álbum/playlist!")
        print("")
        return []

    set_title = data.get("title", "Sem título")
    set_tracks = data.get("tracks", [])
    total = len(set_tracks)
    print(f"✅ Álbum/Playlist encontrado: {set_title}")
    print(f"🎵 Total de faixas na playlist: {total}")
    print("")

    tracks: list[str] = []
    for index, track in enumerate(set_tracks, 1):
        if not isinstance(track, dict):
            continue
        permalink_url = track.get("permalink_url")
        if permalink_url:
            tracks.append(permalink_url)
            print(f"   ✅ [{index}/{total}] {permalink_url}")
            continue

        track_id = track.get("id")
        if not track_id:
            continue
        print(f"   ⏳ [{index}/{total}] Faixa com ID {track_id} — resolvendo URL...")
        track_url = f"https://api-v2.soundcloud.com/tracks/{track_id}?client_id={client_id}"
        track_response = http_get_fn(
            track_url,
            {"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
        )
        if not track_response:
            print(f"   ❌ [{index}/{total}] Falha ao resolver ID {track_id}")
            continue
        try:
            track_data = json.loads(track_response)
        except (json.JSONDecodeError, TypeError):
            print(f"   ⚠️  [{index}/{total}] Resposta inválida para ID {track_id}")
            continue
        permalink = track_data.get("permalink_url")
        if permalink:
            tracks.append(permalink)
            print(f"   ✅ [{index}/{total}] {permalink}")
        else:
            print(f"   ⚠️  [{index}/{total}] URL não encontrada para ID {track_id}")

    print("")
    print("─" * 70)
    print(f"✅ Coleta do álbum/playlist finalizada! Total: {len(tracks)} faixa(s)")
    print("─" * 70)
    print("")
    return tracks


def fallback_scraper(
    soundcloud_link: str,
    choice: str,
    http_get_fn: HttpGet,
    extract_client_id_fn: ExtractClientId,
    resolve_url_fn: ResolveUrl,
    get_collection_tracks_fn: Callable[[int, str, str], list[str]],
    get_set_tracks_fn: Callable[[str, str], list[str]],
) -> list[str]:
    """Mantém o fluxo de fallback legado usando callbacks testáveis."""
    print("")
    print("═" * 70)
    print("🔄  MODO ALTERNATIVO: Scraping via HTTP (sem navegador)")
    print("═" * 70)
    print("")
    print("⏳ Obtendo client_id do SoundCloud...")
    print("")

    html = http_get_fn("https://soundcloud.com", None)
    if not html:
        print("❌ Não foi possível acessar o SoundCloud!")
        return []

    client_id = extract_client_id_fn(html)
    if not client_id:
        print("❌ Não foi possível obter o client_id do SoundCloud!")
        print("   Isso pode acontecer se o SoundCloud mudou a estrutura do site.")
        return []

    print(f"✅ client_id obtido: {client_id[:8]}...")
    print("")
    print("🔍 Resolvendo URL do artista...")
    print("")

    if choice in {"4", "5"}:
        print("📀 Coletando tracks do álbum/playlist...")
        print("")
        return get_set_tracks_fn(soundcloud_link, client_id)

    base_url = re.sub(r"/(tracks|popular-tracks|reposts|likes)$", "", soundcloud_link)
    user_data = resolve_url_fn(base_url, client_id)
    if not user_data or "id" not in user_data:
        print("❌ Não foi possível resolver o perfil do artista!")
        return []

    user_id = user_data["id"]
    username = user_data.get("username", "Desconhecido")
    track_count = user_data.get("track_count", "?")
    print(f"✅ Artista encontrado: {username} (ID: {user_id})")
    print(f"📊 Faixas no perfil (informado pela API): {track_count}")
    print("")

    collection_map = {
        "1": "tracks",
        "2": "toptracks",
        "3": "tracks",
        "6": "reposts",
        "7": "likes",
    }
    collection_type = collection_map.get(choice, "tracks")
    choice_names = {
        "1": "Todas as Faixas",
        "2": "Faixas Populares",
        "3": "Faixas",
        "6": "Republicações",
        "7": "Curtidas",
    }
    print(f"📊 Coletando: {choice_names.get(choice, collection_type)}")
    print("")
    return get_collection_tracks_fn(user_id, collection_type, client_id)
