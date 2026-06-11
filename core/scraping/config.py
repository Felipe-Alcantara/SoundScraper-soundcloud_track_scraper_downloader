"""
config.py — Limites operacionais do pipeline de coleta.

Centraliza os números mágicos (antes espalhados pelo código) num único ponto,
configurável por variável de ambiente. Tudo tem padrão seguro.
"""

import os
from dataclasses import dataclass


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class ScraperConfig:
    """Limites de coleta. Imutável; criado a partir do ambiente via from_env()."""
    max_tracks: int = 1000           # teto de faixas coletadas por execução
    max_pages: int = 100             # teto de páginas da API paginada
    page_size: int = 50              # itens por página na API v2
    timeout_ms: int = 30000          # timeout de cada requisição/navegação
    scroll_rounds: int = 5           # tentativas de scroll sem novidade antes de parar (Selenium)
    scroll_pause_s: float = 4.0      # pausa entre scrolls (Selenium)

    @classmethod
    def from_env(cls) -> "ScraperConfig":
        return cls(
            max_tracks=_env_int("SOUNDSCRAPER_MAX_TRACKS", 1000),
            max_pages=_env_int("SOUNDSCRAPER_MAX_PAGES", 100),
            page_size=_env_int("SOUNDSCRAPER_PAGE_SIZE", 50),
            timeout_ms=_env_int("SOUNDSCRAPER_TIMEOUT_MS", 30000),
            scroll_rounds=_env_int("SOUNDSCRAPER_SCROLL_ROUNDS", 5),
            scroll_pause_s=float(_env_int("SOUNDSCRAPER_SCROLL_PAUSE_MS", 4000)) / 1000.0,
        )
