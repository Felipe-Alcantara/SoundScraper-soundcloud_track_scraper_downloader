"""
parsers.py — Parsers PUROS da API v2 do SoundCloud.

Recebem texto/JSON já baixado e devolvem dados estruturados. Não tocam a rede,
o que os torna totalmente testáveis offline com fixtures sanitizadas (ver tests/).
Esta é a única fonte de verdade do parsing; browser_handler.py delega para cá.
"""

import json
import re


# Regex do client_id embutido nos scripts JS do SoundCloud.
_CLIENT_ID_RE = re.compile(r'client_id\s*[:=]\s*["\']([a-zA-Z0-9]{32})["\']')
# URLs dos scripts JS da home do SoundCloud.
_SCRIPT_URL_RE = re.compile(r'src="(https://a-v2\.sndcdn\.com/assets/[^"]+\.js)"')


def find_script_urls(html_content: str) -> list[str]:
    """Extrai as URLs dos scripts JS da página (onde mora o client_id)."""
    if not html_content:
        return []
    return _SCRIPT_URL_RE.findall(html_content)


def extract_client_id_from_js(js_content: str) -> str | None:
    """Extrai o client_id de um conteúdo JS, ou None se não houver."""
    if not js_content:
        return None
    match = _CLIENT_ID_RE.search(js_content)
    return match.group(1) if match else None


def parse_collection_page(payload: str, collection_type: str = "") -> tuple[list[str], str | None]:
    """
    Faz o parsing de uma página de coleção da API v2.

    Args:
        payload: corpo JSON da resposta (string).
        collection_type: tipo da coleção ('reposts' tem o track aninhado em 'track').

    Returns:
        (urls_desta_pagina, next_href) — next_href é None na última página/erro.
        Em payload inválido devolve ([], None) — fail-safe, nunca dado parcial enganoso.
    """
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return [], None

    urls: list[str] = []
    for item in data.get("collection", []) or []:
        # 'reposts' aninha a faixa real em item['track'].
        track = item.get("track", item) if collection_type == "reposts" else item
        if not isinstance(track, dict):
            continue
        permalink = track.get("permalink_url")
        if permalink:
            urls.append(permalink)

    return urls, data.get("next_href")


def parse_set(payload: str) -> tuple[list[str], list[int], str]:
    """
    Faz o parsing de um álbum/playlist resolvido pela API v2.

    Returns:
        (urls_diretas, ids_para_resolver, set_title)
        urls_diretas: faixas que já trazem permalink_url.
        ids_para_resolver: ids de faixas sem permalink (precisam de uma chamada extra).
        set_title: título do conjunto (ou "" se ausente/ inválido).
    """
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return [], [], ""

    urls: list[str] = []
    pending_ids: list[int] = []
    for track in data.get("tracks", []) or []:
        if not isinstance(track, dict):
            continue
        permalink = track.get("permalink_url")
        if permalink:
            urls.append(permalink)
        elif track.get("id"):
            pending_ids.append(track["id"])

    return urls, pending_ids, data.get("title", "")


def parse_resolved_user(payload: str) -> dict | None:
    """Faz o parsing da resposta de /resolve. Devolve o dict ou None se inválido."""
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return None
    return data if isinstance(data, dict) else None


def parse_track_permalink(payload: str) -> str | None:
    """Extrai o permalink_url de uma faixa resolvida por id, ou None."""
    data = parse_resolved_user(payload)
    if not data:
        return None
    return data.get("permalink_url")
