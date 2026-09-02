"""CLI de download do SoundScraper.

O módulo mantém o fluxo interativo histórico, mas delega opções, metadados e
renomeação para ``core/downloading``. Assim o backend e o executável usam as
mesmas regras sem duplicar o caso de uso.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from dependency_manager import check_and_install_requirements as _check_dependencies
from downloading.metadata import AddCustomMetadataPP
from downloading.options import build_ydl_options, rename_downloaded_files
from platform_utils import ensure_ffmpeg, open_folder


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_FILE = PROJECT_ROOT / "deps" / "requirements.txt"
session_log: str | None = None


def check_and_install_requirements() -> bool:
    """Mantém o helper legado para execução direta do módulo."""
    if getattr(sys, "frozen", False):
        return True
    return _check_dependencies(REQUIREMENTS_FILE)


def _selecionar_pasta() -> str:
    """Abre o seletor nativo e oferece entrada textual como fallback."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Selecione a pasta para salvar as músicas")
        root.destroy()
        if folder:
            return folder
        print("⚠️  Nenhuma pasta selecionada no diálogo.\n")
    except Exception as exc:
        print(f"⚠️  Não foi possível abrir o seletor de pastas: {exc}\n")

    print("💡 Digite o caminho da pasta ou deixe em branco para 'SoundCloud_Downloads'")
    try:
        folder = input("📂 Caminho da pasta: ").strip()
    except EOFError:
        folder = ""
    return folder


def _solicitar_formato() -> str:
    """Solicita FLAC ou MP3, usando MP3 como padrão compatível."""
    print("═" * 70)
    print("🎵  ESCOLHA O FORMATO DE ÁUDIO")
    print("═" * 70)
    print("\n  [1] 🎼  FLAC — qualidade máxima (sem perdas)")
    print("  [2] 🎧  MP3 — alta qualidade (320kbps)\n")
    try:
        selected = input("💿 Digite sua escolha (1 ou 2, padrão=2): ").strip()
    except EOFError:
        selected = ""
    if selected == "1":
        print("\n✅ Formato selecionado: FLAC (Lossless)\n")
        return "flac"
    print("\n✅ Formato selecionado: MP3 (320kbps)\n")
    return "mp3"


def _corrigir_nome_arquivo(output_folder: str | Path) -> list[str]:
    """Normaliza nomes após o download e informa colisões de arquivo."""
    return rename_downloaded_files(output_folder, log=print)


def _download_url(url: str, index: int, total: int, ydl_opts: dict[str, Any]) -> bool:
    """Baixa uma URL e retorna sucesso, deixando o loop contar falhas."""
    import yt_dlp

    print("\n" + "─" * 70)
    print(f"⬇️  BAIXANDO [{index}/{total}]")
    print("─" * 70)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.add_post_processor(AddCustomMetadataPP(), when="pre_process")
            ydl.download([url])
    except Exception as exc:
        print(f"\n❌  ERRO ao baixar música {index}/{total}")
        print(f"    URL: {url}")
        print(f"    Motivo: {exc}\n")
        return False
    print(f"\n✅  CONCLUÍDO [{index}/{total}]\n")
    return True


def main() -> int:
    """Executa o fluxo completo de coleta e download."""
    global session_log
    from crash_logger import inicializar_logger
    from soundcloud_track_scraper import soundcloud_track_scraper

    session_log = inicializar_logger()
    while True:
        filename = soundcloud_track_scraper()
        print("═" * 70)
        print("📁  CONFIGURAÇÃO DA PASTA DE DESTINO")
        print("═" * 70)
        output_folder = _selecionar_pasta() or "SoundCloud_Downloads"
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"📂 Pasta de destino: {output_path}")

        audio_format = _solicitar_formato()
        urls = [
            line.strip()
            for line in Path(filename).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        Path(filename).unlink(missing_ok=True)
        print(f"📊 Total de URLs carregados: {len(urls)}")

        ffmpeg_path = ensure_ffmpeg()
        if ffmpeg_path:
            print(f"🎥  FFmpeg: {ffmpeg_path}")
        else:
            print("⚠️  FFmpeg indisponível; o download pode falhar.")

        ydl_opts = build_ydl_options(output_path, audio_format, ffmpeg_path)
        print("\n🎵  INICIANDO DOWNLOAD DAS MÚSICAS")
        print(f"📂  Pasta: {output_path}")
        print(f"🎼  Formato: {audio_format.upper()}\n")

        successes = 0
        failures = 0
        for index, url in enumerate(urls, start=1):
            if _download_url(url, index, len(urls), ydl_opts):
                _corrigir_nome_arquivo(output_path)
                successes += 1
            else:
                failures += 1

        print("\n" + "═" * 70)
        print("🎉  PROCESSO CONCLUÍDO!")
        print("═" * 70)
        print(f"✅  Sucessos: {successes} música(s)")
        if failures:
            print(f"❌  Erros: {failures} música(s)")
        print(f"📂  Pasta: {output_path}\n")
        if open_folder(str(output_path.resolve())):
            print(f"📂 Pasta aberta: {output_path.resolve()}\n")

        try:
            repeat = input("🔄 Deseja baixar mais músicas? (S/N, padrão=N): ").strip().upper()
        except EOFError:
            repeat = "N"
        if repeat != "S":
            print("\nObrigado por usar o SoundScraper! 🎵\n")
            return 0


if __name__ == "__main__":
    if not check_and_install_requirements():
        raise SystemExit(1)
    raise SystemExit(main())
