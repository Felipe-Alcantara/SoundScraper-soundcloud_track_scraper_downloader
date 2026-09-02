#!/usr/bin/env python3
"""Entrada principal do SoundScraper.

Sem argumentos, o launcher oferece um menu curto para instalar, configurar,
iniciar e verificar o projeto. Os argumentos históricos continuam disponíveis
para automação e para scripts existentes.
"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000
DEV_PORT = 5173
OPEN_BROWSER = True

REQUIREMENTS = ROOT / "deps" / "requirements.txt"
VENV_DIR = ROOT / ".venv"
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"
PACKAGE_JSON = FRONTEND_DIR / "package.json"
ENV_FILE = ROOT / ".env"

NPM = "npm.cmd" if os.name == "nt" else "npm"
_DEFAULT_HOST = HOST
_DEFAULT_PORT = PORT
_DEFAULT_DEV_PORT = DEV_PORT


def _color(text: str, code: str) -> str:
    """Aplica cor ANSI no terminal, respeitando ``NO_COLOR`` e pipes."""
    if os.getenv("NO_COLOR") or not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def python_executable() -> str:
    """Retorna o interpretador do ambiente virtual do projeto, quando existe."""
    executable = VENV_DIR / ("Scripts" if os.name == "nt" else "bin") / (
        "python.exe" if os.name == "nt" else "python"
    )
    return str(executable) if executable.exists() else sys.executable


def log(msg: str) -> None:
    """Mostra uma mensagem do launcher imediatamente."""
    print(f"[start_app] {msg}", flush=True)


def port_in_use(host: str, port: int) -> bool:
    """Indica se há um processo aceitando conexões na porta informada."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def kill_port(port: int) -> None:
    """Tenta liberar a porta, usando a ferramenta nativa de cada plataforma."""
    log(f"Liberando a porta {port}...")
    try:
        if os.name == "nt":
            output = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True, check=False
            ).stdout
            pids = {
                line.split()[-1]
                for line in output.splitlines()
                if f":{port}" in line and "LISTENING" in line
            }
            for pid in pids:
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True, check=False)
            return

        output = subprocess.run(
            ["lsof", "-ti", f"tcp:{port}"], capture_output=True, text=True, check=False
        ).stdout
        for pid in output.split():
            subprocess.run(["kill", "-9", pid], capture_output=True, check=False)
    except FileNotFoundError:
        log("Não consegui liberar a porta automaticamente; feche o processo manualmente.")


def has_npm() -> bool:
    """Indica se o npm está disponível no PATH."""
    try:
        subprocess.run([NPM, "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    return True


def _valid_port(value: str, fallback: int) -> int:
    try:
        port = int(value)
    except (TypeError, ValueError):
        return fallback
    return port if 1 <= port <= 65535 else fallback


def _read_env_settings() -> dict[str, str]:
    """Lê somente as configurações públicas conhecidas do ``.env``."""
    if not ENV_FILE.exists():
        return {}
    settings: dict[str, str] = {}
    try:
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        log(f"Não foi possível ler {ENV_FILE}: {exc}")
        return settings
    for line in lines:
        key, separator, value = line.partition("=")
        if separator and key.strip() in {"SOUNDSCRAPER_HOST", "SOUNDSCRAPER_PORT", "SOUNDSCRAPER_DEV_PORT", "SOUNDSCRAPER_OPEN_BROWSER"}:
            settings[key.strip()] = value.strip().strip('"').strip("'")
    return settings


def load_config() -> None:
    """Aplica configurações não secretas do ``.env`` aos defaults do launcher."""
    global HOST, PORT, DEV_PORT, OPEN_BROWSER
    settings = _read_env_settings()
    HOST = settings.get("SOUNDSCRAPER_HOST", _DEFAULT_HOST) or _DEFAULT_HOST
    PORT = _valid_port(settings.get("SOUNDSCRAPER_PORT", ""), _DEFAULT_PORT)
    DEV_PORT = _valid_port(settings.get("SOUNDSCRAPER_DEV_PORT", ""), _DEFAULT_DEV_PORT)
    OPEN_BROWSER = settings.get("SOUNDSCRAPER_OPEN_BROWSER", "true").lower() not in {
        "0",
        "false",
        "não",
        "nao",
        "n",
    }


def _env_lines() -> list[str]:
    if ENV_FILE.exists():
        try:
            return ENV_FILE.read_text(encoding="utf-8").splitlines()
        except OSError:
            return []
    return []


def save_config(*, host: str, port: int, dev_port: int, open_browser: bool) -> None:
    """Atualiza chaves do launcher sem remover variáveis desconhecidas."""
    values = {
        "SOUNDSCRAPER_HOST": host,
        "SOUNDSCRAPER_PORT": str(port),
        "SOUNDSCRAPER_DEV_PORT": str(dev_port),
        "SOUNDSCRAPER_OPEN_BROWSER": "true" if open_browser else "false",
    }
    lines = _env_lines()
    seen: set[str] = set()
    result: list[str] = []
    for line in lines:
        key, separator, _value = line.partition("=")
        key = key.strip()
        if separator and key in values:
            result.append(f"{key}={values[key]}")
            seen.add(key)
        else:
            result.append(line)
    if result and result[-1].strip():
        result.append("")
    result.extend(f"{key}={value}" for key, value in values.items() if key not in seen)
    ENV_FILE.write_text("\n".join(result) + "\n", encoding="utf-8")
    load_config()


def install_python_deps() -> None:
    """Cria o venv, quando necessário, e instala os pins de runtime."""
    if not REQUIREMENTS.exists():
        log(f"requirements.txt não encontrado em {REQUIREMENTS}; pulando deps Python.")
        return
    interpreter = python_executable()
    if interpreter == sys.executable:
        log(f"Criando ambiente virtual Python em {VENV_DIR}...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], cwd=str(ROOT), check=True)
        interpreter = python_executable()
    log("Instalando dependências Python fixadas...")
    subprocess.run(
        [interpreter, "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        cwd=str(ROOT),
        check=True,
    )


def ensure_ffmpeg_present(*, assume_yes: bool = False) -> str | None:
    """Verifica/instala FFmpeg pelo helper portável do projeto."""
    core = str(ROOT / "core")
    if core not in sys.path:
        sys.path.insert(0, core)
    try:
        from platform_utils import ensure_ffmpeg

        return ensure_ffmpeg(assume_yes=assume_yes, log=lambda msg: log(msg) if msg else None)
    except Exception as exc:
        log(f"Não foi possível verificar o FFmpeg automaticamente: {exc}")
        return None


def install_node_deps() -> None:
    """Instala o frontend com o lockfile, de forma reprodutível."""
    if not PACKAGE_JSON.exists():
        log("package.json não encontrado; pulando dependências do frontend.")
        return
    if not has_npm():
        log("npm não encontrado no PATH; instale Node.js para usar a interface web.")
        return
    log("Instalando dependências do frontend (npm ci)...")
    subprocess.run([NPM, "ci"], cwd=str(FRONTEND_DIR), check=True)


def build_frontend() -> bool:
    """Gera o frontend e retorna se a pasta de artefatos existe."""
    if not PACKAGE_JSON.exists():
        return False
    if not has_npm():
        log("npm não encontrado; não é possível buildar o frontend.")
        return FRONTEND_DIST.is_dir()
    log("Buildando o frontend (npm run build)...")
    subprocess.run([NPM, "run", "build"], cwd=str(FRONTEND_DIR), check=True)
    return FRONTEND_DIST.is_dir()


def open_browser_when_ready(url: str, host: str, port: int) -> None:
    """Aguarda a porta abrir e chama o navegador padrão."""
    log("Aguardando o servidor responder...")
    for _ in range(120):
        if port_in_use(host, port):
            log(f"Servidor de pé. Abrindo {url}")
            webbrowser.open(url)
            return
        time.sleep(0.5)
    log(f"Servidor demorou para subir. Abra manualmente: {url}")


def run_production(open_browser: bool) -> int:
    """Sobe API e frontend buildado em uma única porta."""
    url = f"http://{HOST}:{PORT}"
    if open_browser:
        threading.Thread(
            target=open_browser_when_ready, args=(url, HOST, PORT), daemon=True
        ).start()
    log(f"Iniciando o SoundScraper em {url} ... (Ctrl+C para parar)")
    command = [
        python_executable(),
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        HOST,
        "--port",
        str(PORT),
    ]
    try:
        return subprocess.run(command, cwd=str(ROOT), check=False).returncode
    except KeyboardInterrupt:
        log("Encerrado pelo usuário.")
        return 0
    except FileNotFoundError:
        log("uvicorn não encontrado; instale as dependências Python e tente novamente.")
        return 1


def run_dev(open_browser: bool) -> int:
    """Sobe backend com reload e Vite em processos coordenados."""
    backend_command = [
        python_executable(),
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        HOST,
        "--port",
        str(PORT),
        "--reload",
    ]
    log(f"[dev] Subindo backend em http://{HOST}:{PORT} ...")
    backend = subprocess.Popen(backend_command, cwd=str(ROOT))
    frontend = None
    dev_url = f"http://{HOST}:{DEV_PORT}"
    if PACKAGE_JSON.exists() and has_npm():
        log(f"[dev] Subindo Vite em {dev_url} ...")
        frontend = subprocess.Popen(
            [NPM, "run", "dev", "--", "--port", str(DEV_PORT)],
            cwd=str(FRONTEND_DIR),
        )
        target_url, target_port = dev_url, DEV_PORT
    else:
        log("[dev] npm/frontend indisponível; abrindo o backend diretamente.")
        target_url, target_port = f"http://{HOST}:{PORT}", PORT
    if open_browser:
        threading.Thread(
            target=open_browser_when_ready,
            args=(target_url, HOST, target_port),
            daemon=True,
        ).start()
    log("[dev] Rodando. Ctrl+C para parar os processos.")
    try:
        backend.wait()
    except KeyboardInterrupt:
        log("[dev] Encerrando...")
    finally:
        for process in (frontend, backend):
            if process and process.poll() is None:
                process.terminate()
    return 0


def _run_checked(label: str, action) -> bool:
    try:
        action()
    except (OSError, subprocess.CalledProcessError) as exc:
        log(f"{label}: falhou ({exc}).")
        return False
    log(f"{label}: concluído.")
    return True


def install_all() -> bool:
    """Instala Python, frontend e tenta preparar FFmpeg."""
    python_ok = _run_checked("Dependências Python", install_python_deps)
    node_ok = _run_checked("Dependências do frontend", install_node_deps)
    ensure_ffmpeg_present()
    return python_ok and node_ok


def _status_row(label: str, value: str, ok: bool | None = None) -> None:
    marker = "OK" if ok is True else "--" if ok is None else "ERRO"
    marker_text = _color(marker, "92" if ok is True else "91" if ok is False else "90")
    print(f"  [{marker_text:>4}] {label}: {value}")


def show_status() -> None:
    """Exibe verificações reais do ambiente local e das portas configuradas."""
    load_config()
    print("\nSoundScraper — Status\n")
    interpreter = python_executable()
    _status_row("Python do projeto", interpreter, Path(interpreter).exists())
    _status_row("requirements.txt", str(REQUIREMENTS), REQUIREMENTS.exists())
    _status_row("npm", shutil.which(NPM) or "não encontrado", has_npm())
    _status_row("frontend/dist", str(FRONTEND_DIST), FRONTEND_DIST.is_dir())
    ffmpeg = _find_ffmpeg()
    _status_row("FFmpeg", ffmpeg or "não encontrado", bool(ffmpeg))
    _status_row("Backend", f"{HOST}:{PORT}", port_in_use(HOST, PORT))
    _status_row("Vite", f"{HOST}:{DEV_PORT}", port_in_use(HOST, DEV_PORT))
    print()


def _find_ffmpeg() -> str | None:
    core = str(ROOT / "core")
    if core not in sys.path:
        sys.path.insert(0, core)
    try:
        from platform_utils import find_ffmpeg

        return find_ffmpeg()
    except Exception:
        return None


def _ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        answer = ""
    return answer or default


def configure() -> None:
    """Configura host, portas e abertura do navegador sem tocar em segredos."""
    load_config()
    print("\nConfigurar SoundScraper\n")
    print("Estas opções são locais e não são segredos; outras linhas do .env serão preservadas.")
    host = _ask("Host", HOST)
    port = _valid_port(_ask("Porta do backend", str(PORT)), PORT)
    dev_port = _valid_port(_ask("Porta do Vite", str(DEV_PORT)), DEV_PORT)
    browser = _ask("Abrir navegador automaticamente? (S/N)", "S" if OPEN_BROWSER else "N")
    save_config(host=host, port=port, dev_port=dev_port, open_browser=browser.lower() not in {"n", "nao", "não", "0", "false"})
    log(f"Configuração salva em {ENV_FILE}.")


def _install_and_build(*, build: bool = True) -> bool:
    if not install_all():
        return False
    return not build or _run_checked("Build do frontend", build_frontend)


def run_cli() -> int:
    """Abre o entry point CLI mantendo a seleção fora do launcher Web."""
    command = _ask("Comando CLI (vazio = fluxo completo, 'scrape' = só links)", "")
    args = [python_executable(), str(ROOT / "run_cli.py")]
    if command:
        args.append(command)
    try:
        return subprocess.run(args, cwd=str(ROOT), check=False).returncode
    except (FileNotFoundError, OSError) as exc:
        log(f"CLI indisponível: {exc}")
        return 1


def _start_menu() -> int:
    print("\nIniciar SoundScraper\n")
    print("  [1] Produção — API + frontend em uma porta")
    print("  [2] Desenvolvimento — reload + Vite")
    print("  [3] CLI — coleta/download no terminal")
    print("  [0] Voltar")
    choice = _ask("Escolha", "1")
    if choice == "3":
        return run_cli()
    if choice not in {"1", "2"}:
        return 0
    load_config()
    if port_in_use(HOST, PORT):
        answer = _ask(f"A porta {PORT} está ocupada. Reiniciar? (S/N)", "N")
        if answer.lower() in {"s", "sim", "y", "yes"}:
            kill_port(PORT)
            time.sleep(1)
        else:
            log(f"Acesse o serviço existente em http://{HOST}:{PORT}.")
            return 0
    if not _install_and_build(build=choice == "1"):
        return 1
    return run_dev(OPEN_BROWSER) if choice == "2" else run_production(OPEN_BROWSER)


def interactive_menu() -> int:
    """Loop principal sem dependências externas ou edição manual de arquivos."""
    while True:
        print("\n" + "=" * 54)
        print(_color(" SoundScraper — Felixo System Design", "95"))
        print("=" * 54)
        print(_color("  [1] Iniciar", "96"))
        print(_color("  [2] Instalar", "96"))
        print(_color("  [3] Configurar", "96"))
        print(_color("  [4] Status", "96"))
        print(_color("  [0] Sair", "96"))
        choice = _ask("Escolha", "1")
        if choice == "1":
            return _start_menu()
        if choice == "2":
            install_all()
            continue
        if choice == "3":
            configure()
            continue
        if choice == "4":
            show_status()
            continue
        if choice == "0":
            print("Até logo.")
            return 0
        print("Opção inválida; escolha 1, 2, 3, 4 ou 0.")


def _legacy_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inicia o SoundScraper.")
    parser.add_argument(
        "command", nargs="?", default="start", choices=["start", "restart"],
        help="start (padrão) ou restart",
    )
    parser.add_argument("--no-browser", action="store_true", help="não abre o navegador")
    parser.add_argument("--no-install", action="store_true", help="pula a instalação")
    parser.add_argument("--dev", action="store_true", help="modo desenvolvimento")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Usa o menu sem argumentos; com argumentos preserva o modo automatizável."""
    if argv is None and len(sys.argv) == 1:
        return interactive_menu()
    args = _legacy_parser().parse_args(argv)
    os.chdir(ROOT)
    load_config()
    open_browser = OPEN_BROWSER and not args.no_browser
    if port_in_use(HOST, PORT):
        if args.command == "restart":
            kill_port(PORT)
            time.sleep(1)
        else:
            log(f"A porta {PORT} já está em uso. Use 'python start_app.py restart'.")
            if open_browser:
                webbrowser.open(f"http://{HOST}:{PORT}")
            return 0
    if not args.no_install:
        if not install_all():
            return 1
    if not args.dev and not args.no_install:
        if not _run_checked("Build do frontend", build_frontend):
            log("O frontend não foi buildado; a API ainda pode ser executada.")
    return run_dev(open_browser) if args.dev else run_production(open_browser)


if __name__ == "__main__":
    raise SystemExit(main())
