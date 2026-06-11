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


def ffmpeg_install_command() -> tuple[list[str], str] | None:
    """
    Decide o melhor comando de instalação do FFmpeg para o SO atual, detectando
    o gerenciador de pacotes disponível (via shutil.which).

    Retorna (comando, rótulo-humano) ou None se nenhum gerenciador conhecido for
    encontrado. PURO/sem efeitos colaterais (apenas consulta o PATH), para ser
    testável. No Linux, comandos com apt/dnf/pacman incluem 'sudo' quando o
    usuário não é root.
    """
    def _sudo() -> list[str]:
        # Em Linux/macOS, usa sudo se não for root e o sudo existir.
        if not is_windows() and os.geteuid() != 0 and shutil.which("sudo"):  # type: ignore[attr-defined]
            return ["sudo"]
        return []

    if is_windows():
        if shutil.which("winget"):
            return (["winget", "install", "--silent", "--accept-package-agreements",
                     "--accept-source-agreements", "-e", "--id", "Gyan.FFmpeg"], "winget")
        if shutil.which("choco"):
            return (["choco", "install", "-y", "ffmpeg"], "Chocolatey")
        return None

    if sys.platform == "darwin":
        if shutil.which("brew"):
            return (["brew", "install", "ffmpeg"], "Homebrew")
        return None

    # Linux — escolhe o gerenciador da distro.
    if shutil.which("apt-get"):
        return (_sudo() + ["apt-get", "install", "-y", "ffmpeg"], "apt")
    if shutil.which("apt"):
        return (_sudo() + ["apt", "install", "-y", "ffmpeg"], "apt")
    if shutil.which("dnf"):
        return (_sudo() + ["dnf", "install", "-y", "ffmpeg"], "dnf")
    if shutil.which("pacman"):
        return (_sudo() + ["pacman", "-S", "--noconfirm", "ffmpeg"], "pacman")
    if shutil.which("zypper"):
        return (_sudo() + ["zypper", "install", "-y", "ffmpeg"], "zypper")
    return None


def ensure_ffmpeg(assume_yes: bool = False, log=print) -> str | None:
    """
    Garante o FFmpeg disponível. Se já existir, retorna o caminho. Se faltar:
      1. detecta o gerenciador de pacotes do SO;
      2. pede confirmação (a menos que assume_yes=True);
      3. tenta instalar;
      4. em qualquer falha, mostra o comando exato para o usuário rodar.

    Retorna o caminho do FFmpeg (se ficou disponível) ou None.
    """
    found = find_ffmpeg()
    if found:
        return found

    log("")
    log("⚠️  FFmpeg não encontrado — ele é necessário para converter o áudio.")

    install = ffmpeg_install_command()
    if not install:
        log("   Não foi possível detectar um gerenciador de pacotes para instalar automaticamente.")
        log("   Instale o FFmpeg manualmente:")
        if is_windows():
            log("     • winget install Gyan.FFmpeg   (ou baixe em https://ffmpeg.org)")
        elif sys.platform == "darwin":
            log("     • brew install ffmpeg          (instale o Homebrew em https://brew.sh)")
        else:
            log("     • sudo apt install ffmpeg      (ou o gerenciador da sua distro)")
        return None

    cmd, label = install
    cmd_str = " ".join(cmd)

    if not assume_yes:
        try:
            resp = input(f"💡 Deseja instalar o FFmpeg agora via {label}? [{cmd_str}] (S/N): ").strip().upper()
        except EOFError:
            resp = "N"
        if resp != "S":
            log(f"   Ok. Para instalar depois, rode: {cmd_str}")
            return None

    log(f"📦 Instalando o FFmpeg via {label}...")
    try:
        result = subprocess.run(cmd)
    except FileNotFoundError:
        log(f"   Falha: comando não encontrado. Rode manualmente: {cmd_str}")
        return None
    except Exception as exc:
        log(f"   Falha ao instalar: {exc}. Rode manualmente: {cmd_str}")
        return None

    if result.returncode != 0:
        log(f"   A instalação retornou erro (código {result.returncode}). Rode manualmente: {cmd_str}")
        return None

    found = find_ffmpeg()
    if found:
        log(f"✅ FFmpeg instalado: {found}")
    else:
        log("   Instalação concluída, mas o FFmpeg ainda não foi localizado no PATH. "
            "Talvez seja preciso reabrir o terminal.")
    return found


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
