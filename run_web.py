"""
SoundScraper — Launcher
Inicia o servidor FastAPI e abre o navegador na interface.
Pode ser usado tanto em dev quanto empacotado via PyInstaller.
"""

import os
import sys
import time
import webbrowser
import threading

def main():
    # Adiciona o diretório raiz ao path para imports funcionarem
    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    host = "127.0.0.1"
    port = 8000

    def open_browser():
        """Abre o navegador após um breve delay para o servidor subir."""
        time.sleep(1.5)
        webbrowser.open(f"http://{host}:{port}")

    print("╔" + "═" * 58 + "╗")
    print("║" + "  🎵  SoundScraper v3.0 — Interface Web".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print("")
    print(f"🌐 Servidor: http://{host}:{port}")
    print("🛑 Para encerrar: Ctrl+C")
    print("")

    # Abre o navegador em background
    threading.Thread(target=open_browser, daemon=True).start()

    # Inicia o uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            log_level="info",
            reload=False,
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor encerrado.")


if __name__ == "__main__":
    main()
