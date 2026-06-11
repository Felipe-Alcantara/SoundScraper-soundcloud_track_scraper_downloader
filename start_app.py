#!/usr/bin/env python3
"""
start_app.py — Script padrão de inicialização do SoundScraper (Felixo System Design).

Instala dependências, builda o frontend, sobe o servidor e abre o navegador — com
um único comando. Cross-platform (Windows, Linux, macOS), só usa a stdlib.

Uso:
    python start_app.py                # instala (se preciso) + builda + sobe + abre o navegador
    python start_app.py restart        # mata a instância na porta e sobe de novo
    python start_app.py --no-browser   # sobe sem abrir o navegador (servidor/automação)
    python start_app.py --no-install   # pula a instalação de dependências
    python start_app.py --dev          # modo desenvolvimento: uvicorn --reload + Vite (:5173)

Modos:
  • Produção (padrão): builda o frontend para frontend/dist/ e o backend serve tudo
    em http://127.0.0.1:8000 (um único processo, uma única porta).
  • Desenvolvimento (--dev): sobe o backend com reload em :8000 e o Vite dev server em
    :5173 (hot reload do frontend); o navegador abre no Vite.
"""

import argparse
import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000          # backend (FastAPI/uvicorn)
DEV_PORT = 5173      # frontend (Vite dev server)

REQUIREMENTS = ROOT / "deps" / "requirements.txt"
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"
PACKAGE_JSON = FRONTEND_DIR / "package.json"

NPM = "npm.cmd" if os.name == "nt" else "npm"
# ---------------------------------------------------------------------------


def log(msg: str) -> None:
    print(f"[start_app] {msg}", flush=True)


def port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def kill_port(port: int) -> None:
    """Mata o processo que ocupa a porta (cross-platform)."""
    log(f"Liberando a porta {port}...")
    try:
        if os.name == "nt":
            out = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True
            ).stdout
            pids = {
                line.split()[-1]
                for line in out.splitlines()
                if f":{port}" in line and "LISTENING" in line
            }
            for pid in pids:
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
        else:
            out = subprocess.run(
                ["lsof", "-ti", f"tcp:{port}"], capture_output=True, text=True
            ).stdout
            for pid in out.split():
                subprocess.run(["kill", "-9", pid], capture_output=True)
    except FileNotFoundError:
        log("Não consegui liberar a porta automaticamente. Feche o processo manualmente.")


def has_npm() -> bool:
    """True se o npm estiver disponível no PATH."""
    try:
        subprocess.run(
            [NPM, "--version"], capture_output=True, check=True
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def install_python_deps() -> None:
    if not REQUIREMENTS.exists():
        log(f"requirements.txt não encontrado em {REQUIREMENTS} — pulando deps Python.")
        return
    log("Instalando dependências Python (pip install -r deps/requirements.txt)...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        check=True,
    )


def ensure_ffmpeg_present() -> None:
    """
    Garante o FFmpeg (necessário para o download). Reaproveita o ensure_ffmpeg()
    do core/, que detecta o gerenciador do SO, oferece instalar e, se não der,
    mostra o comando manual. Nunca interrompe o start do servidor.
    """
    core = str(ROOT / "core")
    if core not in sys.path:
        sys.path.insert(0, core)
    try:
        from platform_utils import ensure_ffmpeg
        ensure_ffmpeg(log=lambda m: log(m) if m else None)
    except Exception as exc:
        log(f"Não foi possível verificar o FFmpeg automaticamente: {exc}")


def install_node_deps() -> None:
    if not PACKAGE_JSON.exists():
        return
    if not has_npm():
        log("⚠️  npm não encontrado no PATH. Instale o Node.js (https://nodejs.org) "
            "para usar o frontend. Pulando a parte web.")
        return
    log("Instalando dependências do frontend (npm install)...")
    subprocess.run([NPM, "install"], cwd=str(FRONTEND_DIR), check=True)


def build_frontend() -> bool:
    """Builda o frontend para frontend/dist/. Retorna True se houver build disponível."""
    if not PACKAGE_JSON.exists():
        return False
    if not has_npm():
        log("⚠️  npm não encontrado: não é possível buildar o frontend. "
            "O servidor sobe mesmo assim, mas a interface web pode não estar disponível.")
        return FRONTEND_DIST.is_dir()
    log("Buildando o frontend (npm run build)...")
    subprocess.run([NPM, "run", "build"], cwd=str(FRONTEND_DIR), check=True)
    return FRONTEND_DIST.is_dir()


def open_browser_when_ready(url: str, host: str, port: int) -> None:
    log("Aguardando o servidor responder...")
    for _ in range(120):  # até ~60s
        if port_in_use(host, port):
            log(f"Servidor de pé. Abrindo {url}")
            webbrowser.open(url)
            return
        time.sleep(0.5)
    log(f"Servidor demorou para subir. Abra manualmente: {url}")


def run_production(open_browser: bool) -> int:
    """Sobe o uvicorn servindo a API + o frontend buildado em uma única porta."""
    url = f"http://{HOST}:{PORT}"
    if open_browser:
        threading.Thread(
            target=open_browser_when_ready, args=(url, HOST, PORT), daemon=True
        ).start()

    log(f"Iniciando o SoundScraper em {url} ... (Ctrl+C para parar)")
    cmd = [
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", HOST, "--port", str(PORT),
    ]
    try:
        return subprocess.run(cmd, cwd=str(ROOT)).returncode
    except KeyboardInterrupt:
        log("Encerrado pelo usuário.")
        return 0
    except FileNotFoundError:
        log("uvicorn não encontrado. Rode 'python start_app.py' sem --no-install "
            "ou instale com 'pip install -r deps/requirements.txt'.")
        return 1


def run_dev(open_browser: bool) -> int:
    """Sobe backend com reload (:8000) + Vite dev server (:5173)."""
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", HOST, "--port", str(PORT), "--reload",
    ]
    log(f"[dev] Subindo backend (reload) em http://{HOST}:{PORT} ...")
    backend = subprocess.Popen(backend_cmd, cwd=str(ROOT))

    frontend = None
    dev_url = f"http://{HOST}:{DEV_PORT}"
    if PACKAGE_JSON.exists() and has_npm():
        log(f"[dev] Subindo Vite dev server em {dev_url} ...")
        frontend = subprocess.Popen(
            [NPM, "run", "dev", "--", "--port", str(DEV_PORT)],
            cwd=str(FRONTEND_DIR),
        )
        target_url, target_port = dev_url, DEV_PORT
    else:
        log("[dev] npm/frontend indisponível — abrindo direto o backend.")
        target_url, target_port = f"http://{HOST}:{PORT}", PORT

    if open_browser:
        threading.Thread(
            target=open_browser_when_ready,
            args=(target_url, HOST, target_port),
            daemon=True,
        ).start()

    log("[dev] Rodando. Ctrl+C para parar os dois processos.")
    try:
        backend.wait()
    except KeyboardInterrupt:
        log("[dev] Encerrando...")
    finally:
        for proc in (frontend, backend):
            if proc and proc.poll() is None:
                proc.terminate()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inicia o SoundScraper (Felixo System Design)."
    )
    parser.add_argument(
        "command", nargs="?", default="start", choices=["start", "restart"],
        help="start (padrão) ou restart",
    )
    parser.add_argument("--no-browser", action="store_true", help="não abre o navegador")
    parser.add_argument("--no-install", action="store_true", help="pula a instalação de dependências")
    parser.add_argument("--dev", action="store_true", help="modo desenvolvimento (reload + Vite)")
    args = parser.parse_args()

    os.chdir(ROOT)
    open_browser = not args.no_browser

    # Porta já em uso?
    if port_in_use(HOST, PORT):
        if args.command == "restart":
            kill_port(PORT)
            time.sleep(1)
        else:
            log(f"A porta {PORT} já está em uso. Use 'python start_app.py restart' para reiniciar.")
            if open_browser:
                webbrowser.open(f"http://{HOST}:{PORT}")
            return 0

    # Instalação
    if not args.no_install:
        try:
            install_python_deps()
            install_node_deps()
            ensure_ffmpeg_present()
        except subprocess.CalledProcessError as e:
            log(f"Falha ao instalar dependências: {e}. Resolva e rode de novo.")
            return 1

    # Build do frontend (apenas em produção)
    if not args.dev and not args.no_install:
        try:
            if not build_frontend():
                log("ℹ️  Frontend não buildado (sem npm). A API REST/WebSocket continua disponível.")
        except subprocess.CalledProcessError as e:
            log(f"Falha ao buildar o frontend: {e}.")
            return 1

    return run_dev(open_browser) if args.dev else run_production(open_browser)


if __name__ == "__main__":
    raise SystemExit(main())
