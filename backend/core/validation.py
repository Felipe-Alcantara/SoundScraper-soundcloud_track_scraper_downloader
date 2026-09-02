"""Validações de entrada compartilhadas pelas rotas e services."""

from __future__ import annotations

import re
from urllib.parse import urlsplit


SOUNDCLOUD_HOSTS = frozenset({"soundcloud.com", "www.soundcloud.com"})
USERNAME_PATTERN = re.compile(r"^[a-z0-9_-]+$", re.IGNORECASE)


def normalize_soundcloud_url(value: str, *, allow_username: bool = True) -> str | None:
    """Normaliza perfis/sets do SoundCloud sem aceitar domínios parecidos."""
    raw = value.strip()
    if not raw:
        return None

    if allow_username and "/" not in raw and "://" not in raw and USERNAME_PATTERN.fullmatch(raw):
        return f"https://soundcloud.com/{raw}"

    candidate = raw if "://" in raw else f"https://{raw}"
    parsed = urlsplit(candidate)
    if (parsed.hostname or "").lower() not in SOUNDCLOUD_HOSTS:
        return None
    path = "/".join(part for part in parsed.path.split("/") if part)
    if not path:
        return None
    return f"https://soundcloud.com/{path}"


def validate_track_url(value: str) -> str:
    """Valida um permalink individual e devolve sua forma normalizada."""
    normalized = normalize_soundcloud_url(value, allow_username=False)
    if not normalized or normalized.rstrip("/") == "https://soundcloud.com":
        raise ValueError("Cada faixa precisa ser uma URL válida do SoundCloud.")
    return normalized
