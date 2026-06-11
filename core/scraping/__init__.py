"""
core.scraping — Pipeline de coleta de links do SoundCloud.

Arquitetura (padrão GUIA-SCRAPING-MULTIFORMATO, no recorte pertinente):
  models    → DTOs puros (TrackLink, CollectResult)
  config    → limites operacionais (ScraperConfig)
  parsers   → parsing puro da API v2, testável offline
  registry  → mapa único das 7 opções de coleta
  base      → interface Strategy (SourceAdapter)
  adapters  → http_api (preferido) e selenium_browser (fallback)
  pipeline  → orquestração com fallback e fail-safe

Usado tanto pelo CLI (core/soundcloud_track_scraper.py) quanto pelo backend
(backend/services/scraper_service.py), eliminando duplicação.
"""

from .config import ScraperConfig
from .models import CollectResult, TrackLink
from .pipeline import build_target_url, collect, get_pipeline
from .registry import CHOICES, ChoiceSpec, get_choice

__all__ = [
    "ScraperConfig",
    "CollectResult",
    "TrackLink",
    "build_target_url",
    "collect",
    "get_pipeline",
    "CHOICES",
    "ChoiceSpec",
    "get_choice",
]
