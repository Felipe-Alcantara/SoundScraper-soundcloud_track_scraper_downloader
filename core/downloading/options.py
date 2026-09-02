"""Opções e operações de arquivo compartilhadas pelo CLI e pelo backend."""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any


SUPPORTED_AUDIO_FORMATS = frozenset({"flac", "mp3"})
DEFAULT_SOCKET_TIMEOUT = 30
DEFAULT_RETRIES = 3


def normalize_audio_format(audio_format: str) -> str:
    """Valida e normaliza o formato aceito pelo downloader."""
    normalized = audio_format.strip().lower()
    if normalized not in SUPPORTED_AUDIO_FORMATS:
        accepted = ", ".join(sorted(SUPPORTED_AUDIO_FORMATS))
        raise ValueError(f"Formato de áudio inválido: {audio_format!r}. Use: {accepted}.")
    return normalized


def build_ydl_options(
    output_dir: str | Path,
    audio_format: str,
    ffmpeg_path: str | None = None,
    *,
    socket_timeout: int = DEFAULT_SOCKET_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> dict[str, Any]:
    """Monta as opções comuns do yt-dlp para uma execução."""
    normalized_format = normalize_audio_format(audio_format)
    extract_audio: dict[str, Any] = {
        "key": "FFmpegExtractAudio",
        "preferredcodec": normalized_format,
    }
    if normalized_format == "mp3":
        extract_audio["preferredquality"] = "320"

    options: dict[str, Any] = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(
            os.fspath(output_dir),
            "%(uploader)s - %(artist)s - %(title)s.%(ext)s",
        ),
        "restrictfilenames": True,
        "postprocessors": [
            extract_audio,
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail"},
        ],
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "socket_timeout": socket_timeout,
        "retries": retries,
        "fragment_retries": retries,
        "extractor_retries": retries,
        "file_access_retries": retries,
    }
    if ffmpeg_path:
        options["ffmpeg_location"] = ffmpeg_path
    return options


def rename_downloaded_files(
    output_dir: str | Path,
    log: Callable[[str], None] | None = None,
) -> list[str]:
    """Normaliza nomes gerados pelo yt-dlp e relata falhas de rename."""
    renamed: list[str] = []
    directory = Path(output_dir)
    for path in directory.iterdir():
        if not path.is_file():
            continue
        new_name = re.sub(r"NA - ", "", path.name)
        new_name = re.sub(r"_", " ", new_name)
        new_name = re.sub(r"_-_", "-", new_name)
        if new_name == path.name:
            continue
        try:
            path.rename(directory / new_name)
        except OSError as exc:
            if log:
                log(f"⚠️  Não foi possível renomear {path.name}: {exc}")
            continue
        renamed.append(new_name)
    return renamed
