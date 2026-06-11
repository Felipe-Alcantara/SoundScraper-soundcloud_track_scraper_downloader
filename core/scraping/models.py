"""
models.py — DTOs puros do pipeline de coleta.

Contrato entre coleta (adapters), orquestração (pipeline) e consumidores (CLI / backend).
Mantém-se PURO: não importa Selenium, urllib, FastAPI nem nenhuma camada de I/O ou framework.
"""

from dataclasses import dataclass, field


# Identificadores estáveis dos métodos de coleta (origem do link).
SOURCE_HTTP_API = "http_api"
SOURCE_SELENIUM = "selenium"


@dataclass(frozen=True)
class TrackLink:
    """
    Uma faixa coletada.

    Atributos:
        url:        permalink público da faixa (ex.: https://soundcloud.com/artista/faixa).
        source:     método que coletou o link (SOURCE_HTTP_API | SOURCE_SELENIUM).
        title:      título da faixa, quando disponível (opcional).
        set_title:  título do álbum/playlist de origem, quando aplicável (opcional).
    """
    url: str
    source: str = ""
    title: str = ""
    set_title: str = ""


@dataclass
class CollectResult:
    """
    Resultado auditável de uma coleta.

    urls:        lista ordenada e deduplicada de permalinks (contrato de saída).
    by_source:   contagem por método de coleta, para o resumo/log.
    used_source: método que efetivamente trouxe os links (ou "" se nada foi coletado).
    """
    urls: list[str] = field(default_factory=list)
    by_source: dict[str, int] = field(default_factory=dict)
    used_source: str = ""
