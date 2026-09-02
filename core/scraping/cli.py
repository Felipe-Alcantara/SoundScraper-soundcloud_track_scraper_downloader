"""Entrada interativa do scraper legado.

As funções deste módulo cuidam apenas de validar entradas e transformar a
escolha humana em um alvo do pipeline. Elas não importam Selenium nem fazem
requisições, por isso podem ser testadas offline e reutilizadas pelo CLI.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from urllib.parse import urlsplit

from .registry import CHOICES, get_choice


InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]


def normalize_profile_url(value: str) -> str:
    """Retorna a URL do perfil ou levanta ``ValueError`` com motivo claro."""
    raw = value.strip()
    if not raw:
        raise ValueError("Nenhum link foi inserido. Informe um perfil do SoundCloud.")

    candidate = raw if "://" in raw else f"https://{raw}"
    parsed = urlsplit(candidate)
    hostname = (parsed.hostname or "").lower()
    if hostname not in {"soundcloud.com", "www.soundcloud.com"}:
        raise ValueError(
            "O link precisa apontar para soundcloud.com, por exemplo "
            "https://soundcloud.com/artista."
        )
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        raise ValueError("O link precisa conter o nome do artista.")
    return f"https://soundcloud.com/{parts[0]}"


def prompt_profile_url(
    input_fn: InputFn | None = None,
    output_fn: OutputFn = print,
) -> str:
    """Pede um perfil até receber uma URL válida."""
    reader = input_fn or input
    while True:
        try:
            raw = reader("Insira o link do perfil do SoundCloud: ")
            normalized = normalize_profile_url(raw)
        except EOFError:
            output_fn("Entrada encerrada; o scraper não será iniciado.")
            raise SystemExit(0)
        except ValueError as exc:
            output_fn(f"Erro: {exc}")
            output_fn("Por favor, tente novamente.\n")
            continue
        output_fn(f"URL do artista montada: {normalized}\n")
        return normalized


def _prompt_set_url(reader: InputFn, output_fn: OutputFn) -> str:
    """Valida a URL de álbum/playlist escolhida pelo usuário."""
    while True:
        try:
            raw = reader("Insira o link do Álbum/Playlist: ").strip()
        except EOFError:
            output_fn("Entrada encerrada; o scraper não será iniciado.")
            raise SystemExit(0)
        if not raw:
            output_fn("❌ ERRO: você precisa fornecer um link válido.\n")
            continue

        candidate = raw if "://" in raw else f"https://{raw}"
        parsed = urlsplit(candidate)
        hostname = (parsed.hostname or "").lower()
        clean_path = parsed.path.rstrip("/")
        if hostname not in {"soundcloud.com", "www.soundcloud.com"}:
            output_fn("❌ O link precisa apontar para soundcloud.com.\n")
            continue
        if "/sets/" not in f"{hostname}{clean_path}":
            output_fn("⚠️  O link não contém '/sets/'.")
            try:
                confirm = reader("Deseja continuar mesmo assim? (S/N, padrão=N): ").strip().upper()
            except EOFError:
                confirm = "N"
            if confirm != "S":
                output_fn("Por favor, tente novamente.\n")
                continue
        return raw.rstrip("/")


def prompt_collection_target(
    artist_url: str,
    input_fn: InputFn | None = None,
    output_fn: OutputFn = print,
) -> tuple[str, str]:
    """Transforma a escolha 1–7 em ``(alvo, escolha)``."""
    reader = input_fn or input
    output_fn("O que você deseja puxar deste perfil?")
    for key in sorted(CHOICES):
        output_fn(f"{key}: {CHOICES[key].name}")

    while True:
        try:
            choice = reader("Escolha uma opção (1-7): ").strip()
        except EOFError:
            output_fn("Entrada encerrada; o scraper não será iniciado.")
            raise SystemExit(0)
        try:
            spec = get_choice(choice)
        except ValueError:
            output_fn(f"A opção '{choice}' não é válida. Escolha 1 a 7.\n")
            continue
        break

    if spec.is_set:
        target = _prompt_set_url(reader, output_fn)
    else:
        target = f"{artist_url.rstrip('/')}{spec.url_suffix}"
    output_fn(f"Opção escolhida: {choice}\n")
    return target, choice


def output_filename(url: str) -> str:
    """Gera um nome seguro e estável para o arquivo temporário de links."""
    clean_url = re.sub(r"^https?://", "", url, flags=re.IGNORECASE)
    clean_url = re.sub(r"^www\.", "", clean_url, flags=re.IGNORECASE)
    filename = re.sub(r"[^\w-]", "_", clean_url).strip("_") or "soundcloud_links"
    return f"{filename}.txt"
