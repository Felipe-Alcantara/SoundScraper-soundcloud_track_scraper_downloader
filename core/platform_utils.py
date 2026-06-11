"""
platform_utils.py — Helpers cross-platform compartilhados pelo CLI e pelo backend.

Centraliza tudo que depende do sistema operacional (nome do binário do FFmpeg,
localização do FFmpeg, abertura da pasta de destino) para que SoundScraper funcione
de forma idêntica em Windows, Linux e macOS — sem código preso a um SO só.

Apenas stdlib: sem dependências externas.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def is_windows() -> bool:
    """True quando rodando no Windows."""
    return os.name == "nt"


def ffmpeg_binary_name() -> str:
    """Nome do executável do FFmpeg para o SO atual."""
    return "ffmpeg.exe" if is_windows() else "ffmpeg"


def _project_root() -> Path:
    """Raiz do projeto (pasta que contém core/, deps/, etc.)."""
    return Path(__file__).resolve().parent.parent


def find_ffmpeg() -> str | None:
    """
    Localiza o FFmpeg de forma portável, na ordem:
      1. Bundle do PyInstaller (sys._MEIPASS/ffmpeg/bin/<bin>)  — modo EXE
      2. FFmpeg embutido no projeto (deps/ffmpeg/.../bin/<bin>) — modo script
      3. FFmpeg do sistema no PATH (shutil.which)

    Retorna o caminho do executável, ou None se nada for encontrado
    (nesse caso o yt-dlp tenta o FFmpeg do PATH por conta própria).
    """
    binary = ffmpeg_binary_name()

    # 1. Bundle PyInstaller
    if getattr(sys, "frozen", False):
        bundle_dir = getattr(sys, "_MEIPASS", os.getcwd())
        bundled = Path(bundle_dir) / "ffmpeg" / "bin" / binary
        if bundled.exists():
            return str(bundled)

    # 2. FFmpeg embutido no projeto
    project_bundled = (
        _project_root()
        / "deps" / "ffmpeg" / "ffmpeg-8.0-essentials_build" / "bin" / binary
    )
    if project_bundled.exists():
        return str(project_bundled)

    # 3. FFmpeg do sistema
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    return None


def open_folder(path: str) -> bool:
    """
    Abre uma pasta no gerenciador de arquivos do SO, cross-platform.

    Windows: os.startfile  •  macOS: open  •  Linux: xdg-open

    Retorna True se conseguiu disparar a abertura, False caso contrário
    (nunca levanta exceção — abrir a pasta é uma conveniência, não crítico).
    """
    abs_path = os.path.abspath(path)
    try:
        if is_windows():
            os.startfile(abs_path)  # type: ignore[attr-defined]  # só existe no Windows
        elif sys.platform == "darwin":
            subprocess.run(["open", abs_path], check=False)
        else:
            subprocess.run(["xdg-open", abs_path], check=False)
        return True
    except Exception:
        return False
