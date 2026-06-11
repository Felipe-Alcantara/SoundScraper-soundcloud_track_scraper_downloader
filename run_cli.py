#!/usr/bin/env python3
"""
run_cli.py — SoundScraper no terminal (modo CLI), em um único comando.

Ponto de entrada do uso por terminal, de qualquer pasta do projeto (resolve o
sys.path de core/, então não é preciso 'cd core').

Uso:
    python run_cli.py            # fluxo completo: coleta + download (com loop "baixar mais?")
    python run_cli.py scrape     # só coleta os links (gera o .txt) e encerra

O fluxo completo é o próprio programa de download (core/soundcloud_tracks_downloader.py),
que já coleta e baixa em sequência. O subcomando 'scrape' roda apenas a coleta.
Cross-platform (Windows, Linux, macOS).
"""

import sys
from pathlib import Path

# Garante que os módulos de core/ sejam importáveis a partir de qualquer diretório.
ROOT = Path(__file__).resolve().parent
CORE = ROOT / "core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))


def main() -> int:
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    if command in ("all", "download"):
        # main() do downloader já faz coleta + download + loop "baixar mais?".
        from soundcloud_tracks_downloader import main as downloader_main
        downloader_main()
        return 0

    if command == "scrape":
        from soundcloud_track_scraper import soundcloud_track_scraper
        filename = soundcloud_track_scraper()
        print(f"\n📁 Links salvos em: {filename}")
        print("➡️  Para baixar essas faixas: python run_cli.py")
        return 0

    print(f"Comando desconhecido: {command!r}. Use: (sem argumento) | scrape")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
