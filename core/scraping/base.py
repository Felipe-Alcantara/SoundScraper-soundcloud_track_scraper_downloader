"""
base.py — Interface Strategy comum a todos os métodos de coleta.

Cada método (HTTP API, Selenium, ...) implementa um SourceAdapter. O pipeline
não precisa conhecer detalhes de cada um — só a interface. Adicionar um método
novo é criar um adapter e registrá-lo na ordem do pipeline.
"""

from abc import ABC, abstractmethod
from typing import Callable

from .config import ScraperConfig
from .models import TrackLink
from .registry import ChoiceSpec

# Callback de log: recebe uma mensagem e a repassa (print no CLI, WebSocket no backend).
LogFn = Callable[[str], None]


def _noop(_msg: str) -> None:
    pass


class SourceAdapter(ABC):
    """Interface única de um método de coleta de links."""

    slug: str = ""
    display_name: str = ""

    @abstractmethod
    def collect(
        self,
        profile_url: str,
        spec: ChoiceSpec,
        config: ScraperConfig,
        log: LogFn = _noop,
    ) -> list[TrackLink]:
        """
        Coleta as faixas para a opção `spec` a partir de `profile_url`.

        Deve falhar de forma segura: em erro ou ausência de dados, retorna [] —
        nunca dado parcial enganoso. Toda saída humana vai pelo callback `log`.
        """
        raise NotImplementedError
