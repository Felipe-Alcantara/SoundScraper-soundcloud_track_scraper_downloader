"""Compatibilidade para navegador e APIs antigas do SoundScraper.

O pipeline atual vive em ``core/scraping``. Este módulo mantém os nomes
históricos usados pelo CLI, pelo executável PyInstaller e por integrações
externas, mas separa a localização do navegador da implementação HTTP legada.
"""

from __future__ import annotations

import os
import shutil
import sys
import time

from scraping import legacy_http


def _get_base_path() -> str:
    """Retorna a raiz do bundle ou a raiz do projeto em modo script."""
    if getattr(sys, "frozen", False):
        return str(getattr(sys, "_MEIPASS", os.getcwd()))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_chrome_binary() -> tuple[str | None, str | None]:
    """Procura Chrome portátil, instalado e disponível no PATH."""
    base_path = _get_base_path()
    print("\n" + "─" * 70)
    print("🔍  PROCURANDO GOOGLE CHROME")
    print("─" * 70 + "\n")

    portable_paths = [
        os.path.join(base_path, "deps", "Navegador", "chrome-win64", "chrome.exe"),
        os.path.join(base_path, "Navegador", "chrome-win64", "chrome.exe"),
        os.path.join(base_path, "Chrome-bin", "chrome.exe"),
    ]
    print("📦 Verificando Chrome portátil (bundle/projeto)...")
    for chrome_path in portable_paths:
        print(f"   📂 Verificando: {chrome_path}")
        if os.path.exists(chrome_path):
            print(f"   ✅ ENCONTRADO! Chrome portátil em: {chrome_path}\n")
            return chrome_path, "portátil"
    print("   ❌ Chrome portátil não encontrado.\n")

    system_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
    ]
    print("💻 Verificando Chrome instalado no sistema...")
    for chrome_path in system_paths:
        print(f"   📂 Verificando: {chrome_path}")
        if os.path.exists(chrome_path):
            print(f"   ✅ ENCONTRADO! Chrome do sistema em: {chrome_path}\n")
            return chrome_path, "sistema"
    print("   ❌ Chrome do sistema não encontrado (locais do Windows).\n")

    print("🐧🍎 Verificando Chrome/Chromium no PATH e em locais Linux/macOS...")
    for binary in (
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "chrome",
    ):
        found = shutil.which(binary)
        if found:
            print(f"   ✅ ENCONTRADO! Chrome no PATH: {found}\n")
            return found, "sistema"

    unix_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for chrome_path in unix_paths:
        if os.path.exists(chrome_path):
            print(f"   ✅ ENCONTRADO! Chrome em: {chrome_path}\n")
            return chrome_path, "sistema"

    print("   ❌ Chrome/Chromium não encontrado em Linux/macOS.\n")
    print("⚠️  Nenhuma instalação do Chrome foi localizada.\n")
    return None, None


def _find_bundled_chromedriver() -> str | None:
    """Procura ChromeDriver no bundle, no projeto e no PATH."""
    base_path = _get_base_path()
    print("─" * 70)
    print("🔍  PROCURANDO CHROMEDRIVER")
    print("─" * 70 + "\n")

    candidates = [
        os.path.join(base_path, "Navegador", "chrome-win64", "chromedriver.exe"),
        os.path.join(base_path, "Navegador", "chromedriver.exe"),
        os.path.join(base_path, "deps", "Navegador", "chrome-win64", "chromedriver.exe"),
        os.path.join(base_path, "deps", "Navegador", "chromedriver.exe"),
        os.path.join(base_path, "chromedriver.exe"),
    ]
    print("📦 Verificando ChromeDriver bundled (bundle/projeto)...")
    for path in candidates:
        print(f"   📂 Verificando: {path}")
        if os.path.exists(path):
            print(f"   ✅ ENCONTRADO! ChromeDriver em: {path}\n")
            return path
    print("   ❌ ChromeDriver bundled não encontrado.\n")

    found = shutil.which("chromedriver")
    if found:
        print(f"   ✅ ENCONTRADO! ChromeDriver no PATH: {found}\n")
        return found
    print("   ❌ ChromeDriver não encontrado no PATH.\n")
    print("ℹ️  Nenhum ChromeDriver local encontrado. Será gerenciado automaticamente.\n")
    return None


def get_selenium_version() -> None:
    """Exibe a versão do Selenium sem tornar a dependência obrigatória ao HTTP."""
    try:
        import selenium
    except ImportError:
        print("\nO Selenium não está instalado.\n")
        return
    print(f"\nVersão do Selenium: {selenium.__version__}\n")


def _setup_selenium_manager_for_exe() -> None:
    """Configura o Selenium Manager quando o processo está congelado."""
    if not getattr(sys, "frozen", False):
        return

    bundle_dir = getattr(sys, "_MEIPASS", os.getcwd())
    platform_dir = "windows" if os.name == "nt" else "macos" if sys.platform == "darwin" else "linux"
    filename = "selenium-manager.exe" if os.name == "nt" else "selenium-manager"
    manager_path = os.path.join(
        bundle_dir,
        "selenium",
        "webdriver",
        "common",
        platform_dir,
        filename,
    )
    if os.path.exists(manager_path):
        os.environ["SE_MANAGER_PATH"] = manager_path
        print(f"✅ Selenium Manager encontrado no bundle: {manager_path}\n")
    else:
        print(f"⚠️  Selenium Manager não encontrado em: {manager_path}")
        print("   Tentando caminhos alternativos...\n")


def get_webdriver():
    """Inicializa o Chrome com estratégias de fallback portáveis."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    print("\n" + "═" * 70)
    print("🌐  INICIALIZANDO NAVEGADOR")
    print("═" * 70 + "\n")
    is_frozen = getattr(sys, "frozen", False)
    _setup_selenium_manager_for_exe()

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    if is_frozen:
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--log-level=3")

    chrome_path, chrome_source = _find_chrome_binary()
    if chrome_path:
        options.binary_location = chrome_path
        print(f"✅ Chrome {chrome_source} encontrado: {chrome_path}\n")
    else:
        print("⚠️  Chrome não encontrado em locais conhecidos.")
        print("   O Selenium tentará detectar automaticamente...\n")

    errors: list[str] = []
    bundled_driver = _find_bundled_chromedriver()
    if bundled_driver:
        try:
            print(f"🔧 [Tentativa 1/3] Usando ChromeDriver bundled: {bundled_driver}")
            driver = webdriver.Chrome(
                service=Service(executable_path=bundled_driver),
                options=options,
            )
            print("✅ Navegador iniciado com sucesso! (ChromeDriver bundled)\n")
            return driver
        except Exception as exc:
            errors.append(f"ChromeDriver bundled: {exc}")
            print(f"   ⚠️  Falhou: {exc}\n")

    try:
        tentativa = "2/3" if bundled_driver else "1/3"
        print(f"🔧 [Tentativa {tentativa}] Usando Selenium Manager nativo...")
        driver = webdriver.Chrome(options=options)
        print("✅ Navegador iniciado com sucesso! (Selenium Manager)\n")
        return driver
    except Exception as exc:
        errors.append(f"Selenium Manager: {exc}")
        print(f"   ⚠️  Falhou: {exc}\n")

    if not is_frozen:
        try:
            print("🔧 [Tentativa 3/3] Usando webdriver_manager (pip)...")
            from webdriver_manager.chrome import ChromeDriverManager

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✅ Navegador iniciado com sucesso! (webdriver_manager)\n")
            return driver
        except ImportError:
            errors.append("webdriver_manager: pacote não instalado")
            print("   ⚠️  webdriver_manager não está instalado.\n")
        except Exception as exc:
            errors.append(f"webdriver_manager: {exc}")
            print(f"   ⚠️  Falhou: {exc}\n")
    else:
        print("ℹ️  [Tentativa 3/3] webdriver_manager ignorado (ambiente EXE)\n")

    print("\n" + "═" * 70)
    print("❌ ERRO CRÍTICO: Não foi possível inicializar o navegador!")
    print("═" * 70 + "\n")
    for index, error in enumerate(errors, 1):
        print(f"   {index}. {error}")
    print("\n💡 Instale o Google Chrome ou use a coleta HTTP automática.\n")
    raise RuntimeError("Não foi possível inicializar o navegador Chrome. Tentando fallback HTTP...")


def _http_get(url: str, headers: dict[str, str] | None = None) -> str | None:
    """Fachada compatível para o cliente HTTP legado."""
    return legacy_http.http_get(url, headers)


def _extract_client_id(html_content: str) -> str | None:
    """Fachada compatível para extração de client_id."""
    return legacy_http.extract_client_id(html_content, _http_get)


def _resolve_soundcloud_url(url: str, client_id: str) -> dict | None:
    """Fachada compatível para resolução da API."""
    return legacy_http.resolve_url(url, client_id, _http_get)


def _get_collection_tracks(user_id: int, collection_type: str, client_id: str, limit: int = 200) -> list[str]:
    """Fachada compatível para coleta paginada."""
    return legacy_http.get_collection_tracks(
        user_id,
        collection_type,
        client_id,
        _http_get,
        time.sleep,
        limit,
    )


def _get_set_tracks(set_url: str, client_id: str) -> list[str]:
    """Fachada compatível para coleta de playlists/álbuns."""
    return legacy_http.get_set_tracks(set_url, client_id, _resolve_soundcloud_url, _http_get)


def http_fallback_scraper(soundcloud_link: str, choice: str) -> list[str]:
    """Executa o fallback HTTP preservando a API pública histórica."""
    return legacy_http.fallback_scraper(
        soundcloud_link,
        choice,
        _http_get,
        _extract_client_id,
        _resolve_soundcloud_url,
        _get_collection_tracks,
        _get_set_tracks,
    )
