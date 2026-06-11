#!/usr/bin/env python3
"""
run_cli.py — SoundScraper no terminal (modo CLI), em um único comando.

Roda o fluxo completo no terminal, sem navegador nem interface web:
  1. Coleta os links das faixas (pergunta a URL e o que coletar) → gera um .txt
  2. Baixa o áudio das faixas coletadas (escolha de pasta e formato FLAC/MP3)

Uso (de qualquer lugar do projeto):
    python run_cli.py            # coleta + download (fluxo completo)
    python run_cli.py scrape     # só coleta os links (gera o .txt)
    python run_cli.py download   # só baixa (lê o .txt já existente)

Cross-platform (Windows, Linux, macOS). Resolve os imports do core/ sozinho,
então não é preciso 'cd core'.
"""

import os
import sys
from pathlib import Path

# Garante que os módulos de core/ sejam importáveis a partir de qualquer diretório.
ROOT = Path(__file__).resolve().parent
CORE = ROOT / "core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))


def main() -> int:
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    if command not in ("all", "scrape", "download"):
        print(f"Comando desconhecido: {command!r}. Use: all | scrape | download")
        return 2

    # Importados aqui (não no topo) para os scripts cuidarem da checagem de dependências.
    if command in ("all", "scrape"):
        from soundcloud_track_scraper import soundcloud_track_scraper
        filename = soundcloud_track_scraper()
        if command == "scrape":
            print(f"\n📁 Links salvos em: {filename}")
            print("➡️  Para baixar: python run_cli.py download")
            return 0

    if command in ("all", "download"):
        from soundcloud_tracks_downloader import main as download_main
        download_main()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
