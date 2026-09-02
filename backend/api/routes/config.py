"""
Rota de Configuração — file dialog, info do sistema, etc.
"""

import logging
import platform

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Schemas ────────────────────────────────────────────────────────
class FolderResponse(BaseModel):
    """Resposta da seleção de pasta."""
    success: bool
    path: str = ""
    message: str = ""


class SystemInfo(BaseModel):
    """Informações do sistema."""
    version: str
    python: str
    platform: str
    os: str


# ── Endpoints ──────────────────────────────────────────────────────
@router.get("/info", response_model=SystemInfo)
async def get_system_info():
    """Retorna informações do sistema e versão do SoundScraper."""
    return SystemInfo(
        version="3.0.0",
        python=platform.python_version(),
        platform=platform.platform(),
        os=platform.system(),
    )


@router.post("/select-folder", response_model=FolderResponse)
async def select_folder():
    """
    Abre o file dialog nativo do sistema para o usuário escolher
    a pasta de destino dos downloads.
    Roda tkinter no backend (acesso nativo ao OS).
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        folder = filedialog.askdirectory(
            title="Selecione a pasta de destino das músicas"
        )
        root.destroy()

        if folder:
            return FolderResponse(success=True, path=folder)
        return FolderResponse(success=False, message="Nenhuma pasta selecionada.")

    except Exception:
        logger.exception("Falha ao abrir seletor de pasta")
        return FolderResponse(success=False, message="Não foi possível abrir o seletor de pastas.")
