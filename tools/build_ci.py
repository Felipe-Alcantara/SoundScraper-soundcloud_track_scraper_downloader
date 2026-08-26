"""
build_ci.py — Build cross-platform do executável CLI do SoundScraper para CI.

Diferente de build_exe.py (Windows local), este script é reproduzível em qualquer
runner GitHub Actions (ubuntu-latest, windows-latest) sem paths absolutos locais.

Pré-requisitos esperados no ambiente de CI:
  - FFmpeg instalado e disponível no PATH (apt / choco no workflow)
  - Dependências Python instaladas (deps/requirements-dev.txt)
  - PyInstaller instalado

Uso:
    python tools/build_ci.py
"""

import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _localizar_selenium_manager() -> tuple[Path, str]:
    """
    Encontra o binário selenium-manager empacotado com o selenium instalado.
    Retorna (caminho_absoluto, destino_no_bundle).
    """
    try:
        selenium_pkg = importlib.import_module("selenium")
    except ImportError:
        print("ERRO: selenium não está instalado.")
        sys.exit(1)

    selenium_dir = Path(selenium_pkg.__file__).resolve().parent

    if os.name == "nt":
        rel = Path("webdriver") / "common" / "windows" / "selenium-manager.exe"
        destino = "selenium/webdriver/common/windows"
    else:
        rel = Path("webdriver") / "common" / "linux" / "selenium-manager"
        destino = "selenium/webdriver/common/linux"

    sm_path = selenium_dir / rel
    if not sm_path.exists():
        print(f"ERRO: selenium-manager não encontrado em {sm_path}")
        sys.exit(1)

    return sm_path, destino


def _par(src: Path | str, dst: str) -> str:
    """Formata um par src{sep}dst para --add-data / --add-binary."""
    return f"{src}{os.pathsep}{dst}"


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    core_dir = project_root / "core"
    entry_point = core_dir / "soundcloud_tracks_downloader.py"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    script_dir = Path(__file__).resolve().parent

    exe_nome = "soundcloud-downloader"

    print("")
    print("╔" + "═" * 68 + "╗")
    print("║" + "  SOUNDSCRAPER — Build CI (cross-platform)".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print("")

    # ── Validações ──────────────────────────────────────────────────────────
    erros: list[str] = []

    if not entry_point.exists():
        erros.append(f"Entry point não encontrado: {entry_point}")

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        erros.append("ffmpeg não encontrado no PATH (instale via apt/choco no CI)")
    else:
        print(f"  FFmpeg: {ffmpeg_path}")

    sm_path, sm_destino = _localizar_selenium_manager()
    print(f"  Selenium Manager: {sm_path}")

    try:
        import PyInstaller  # noqa: F401
        print(f"  PyInstaller: {PyInstaller.__version__}")  # type: ignore[attr-defined]
    except ImportError:
        erros.append("PyInstaller não está instalado")

    if erros:
        print("\nERROS encontrados:")
        for e in erros:
            print(f"  • {e}")
        sys.exit(1)

    # ── Limpar builds anteriores ─────────────────────────────────────────────
    for pasta in [dist_dir, build_dir]:
        if pasta.exists():
            shutil.rmtree(pasta)
            print(f"  Removido: {pasta}")

    # ── Montar comando PyInstaller ───────────────────────────────────────────
    ffmpeg_bin_dir = Path(ffmpeg_path).parent  # type: ignore[arg-type]
    scraping_pkg = core_dir / "scraping"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--name", exe_nome,
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--specpath", str(script_dir),
        "--paths", str(core_dir),

        # Binários externos
        "--add-binary", _par(sm_path, sm_destino),
        "--add-binary", _par(ffmpeg_path, "ffmpeg/bin"),

        # Módulos do core
        "--add-data", _par(core_dir / "soundcloud_track_scraper.py", "."),
        "--add-data", _par(core_dir / "browser_handler.py", "."),
        "--add-data", _par(core_dir / "crash_logger.py", "."),
        "--add-data", _par(core_dir / "platform_utils.py", "."),
        "--add-data", _par(scraping_pkg, "scraping"),

        # Hidden imports
        "--hidden-import", "soundcloud_track_scraper",
        "--hidden-import", "browser_handler",
        "--hidden-import", "crash_logger",
        "--hidden-import", "platform_utils",
        "--collect-submodules", "scraping",
        "--hidden-import", "selenium",
        "--hidden-import", "selenium.webdriver.common.selenium_manager",
        "--hidden-import", "yt_dlp",
        "--hidden-import", "mutagen",
        "--clean",

        str(entry_point),
    ]

    print("\nIniciando PyInstaller...")
    resultado = subprocess.run(cmd, cwd=str(project_root))

    # ── Resultado ────────────────────────────────────────────────────────────
    sufixo = ".exe" if os.name == "nt" else ""
    exe_path = dist_dir / f"{exe_nome}{sufixo}"

    if resultado.returncode != 0 or not exe_path.exists():
        print("\nERRO: Build falhou.")
        sys.exit(1)

    tamanho_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"\nBuild concluído: {exe_path} ({tamanho_mb:.1f} MB)")

    # Limpa pasta de trabalho intermediária
    if build_dir.exists():
        shutil.rmtree(build_dir)


if __name__ == "__main__":
    main()
