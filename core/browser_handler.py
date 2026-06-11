"""
browser_handler.py — Módulo responsável por toda a lógica de navegador e scraping HTTP.

Gerencia:
  • Localização do Chrome e ChromeDriver (portátil e sistema)
  • Inicialização do WebDriver com múltiplas estratégias de fallback
  • Correção de paths para funcionar dentro de EXEs (PyInstaller)
  • Fallback completo via HTTP/API v2 do SoundCloud (sem navegador)
"""

import os
import sys
import re
import json
import time
import shutil


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 1: Localização de binários (Chrome / ChromeDriver)
# ══════════════════════════════════════════════════════════════════════

def _get_base_path():
    """Retorna o diretório base dependendo se está rodando como EXE ou script."""
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.getcwd())
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(script_dir)


def _find_chrome_binary():
    """
    Procura o binário do Chrome em múltiplos locais.
    Retorna (caminho, origem) ou (None, None).
    """
    base_path = _get_base_path()

    print("")
    print("─" * 70)
    print("🔍  PROCURANDO GOOGLE CHROME")
    print("─" * 70)
    print("")

    # Chrome portátil no projeto/bundle
    print("📦 Verificando Chrome portátil (bundle/projeto)...")
    portable_chrome_paths = [
        os.path.join(base_path, 'deps', 'Navegador', 'chrome-win64', 'chrome.exe'),
        os.path.join(base_path, 'Navegador', 'chrome-win64', 'chrome.exe'),
        os.path.join(base_path, 'Chrome-bin', 'chrome.exe'),
    ]

    for chrome_path in portable_chrome_paths:
        print(f"   📂 Verificando: {chrome_path}")
        if os.path.exists(chrome_path):
            print(f"   ✅ ENCONTRADO! Chrome portátil em: {chrome_path}")
            print("")
            return chrome_path, "portátil"
    print("   ❌ Chrome portátil não encontrado.")
    print("")

    # Chrome instalado no sistema
    print("💻 Verificando Chrome instalado no sistema...")
    system_chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
    ]

    for chrome_path in system_chrome_paths:
        print(f"   📂 Verificando: {chrome_path}")
        if os.path.exists(chrome_path):
            print(f"   ✅ ENCONTRADO! Chrome do sistema em: {chrome_path}")
            print("")
            return chrome_path, "sistema"
    print("   ❌ Chrome do sistema não encontrado (locais do Windows).")
    print("")

    # Linux / macOS — procura no PATH e em locais comuns de instalação
    print("🐧🍎 Verificando Chrome/Chromium no PATH e em locais Linux/macOS...")
    for binary in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome'):
        found = shutil.which(binary)
        if found:
            print(f"   ✅ ENCONTRADO! Chrome no PATH: {found}")
            print("")
            return found, "sistema"

    unix_chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for chrome_path in unix_chrome_paths:
        if os.path.exists(chrome_path):
            print(f"   ✅ ENCONTRADO! Chrome em: {chrome_path}")
            print("")
            return chrome_path, "sistema"
    print("   ❌ Chrome/Chromium não encontrado em Linux/macOS.")
    print("")

    print("⚠️  Nenhuma instalação do Chrome foi localizada.")
    print("")
    return None, None


def _find_bundled_chromedriver():
    """
    Procura um chromedriver bundled junto com o EXE ou no projeto.
    Retorna o caminho ou None.
    """
    base_path = _get_base_path()

    print("─" * 70)
    print("🔍  PROCURANDO CHROMEDRIVER")
    print("─" * 70)
    print("")

    print("📦 Verificando ChromeDriver bundled (bundle/projeto)...")
    chromedriver_paths = [
        os.path.join(base_path, 'Navegador', 'chrome-win64', 'chromedriver.exe'),
        os.path.join(base_path, 'Navegador', 'chromedriver.exe'),
        os.path.join(base_path, 'deps', 'Navegador', 'chrome-win64', 'chromedriver.exe'),
        os.path.join(base_path, 'deps', 'Navegador', 'chromedriver.exe'),
        os.path.join(base_path, 'chromedriver.exe'),
    ]

    for path in chromedriver_paths:
        print(f"   📂 Verificando: {path}")
        if os.path.exists(path):
            print(f"   ✅ ENCONTRADO! ChromeDriver em: {path}")
            print("")
            return path
    print("   ❌ ChromeDriver bundled não encontrado.")
    print("")

    # Também procura no PATH do sistema
    print("💻 Verificando ChromeDriver no PATH do sistema...")
    chromedriver_in_path = shutil.which('chromedriver')
    if chromedriver_in_path:
        print(f"   ✅ ENCONTRADO! ChromeDriver no PATH: {chromedriver_in_path}")
        print("")
        return chromedriver_in_path
    print("   ❌ ChromeDriver não encontrado no PATH.")
    print("")

    print("ℹ️  Nenhum ChromeDriver local encontrado. Será gerenciado automaticamente.")
    print("")
    return None


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 2: Inicialização do WebDriver (Selenium)
# ══════════════════════════════════════════════════════════════════════

def get_selenium_version():
    """Exibe a versão do Selenium instalada."""
    try:
        import selenium
        print("")
        print(f"Versão do Selenium: {selenium.__version__}")
        print("")
    except ImportError:
        print("")
        print("O Selenium não está instalado.")
        print("")


def _setup_selenium_manager_for_exe():
    """
    Configura o path do Selenium Manager para funcionar dentro de EXEs do PyInstaller.
    O selenium-manager.exe precisa ser encontrado pelo Selenium no bundle.
    """
    if not getattr(sys, 'frozen', False):
        return

    bundle_dir = getattr(sys, '_MEIPASS', os.getcwd())
    sm_path = os.path.join(bundle_dir, 'selenium', 'webdriver', 'common', 'windows', 'selenium-manager.exe')

    if os.path.exists(sm_path):
        os.environ['SE_MANAGER_PATH'] = sm_path
        print(f"✅ Selenium Manager encontrado no bundle: {sm_path}")
        print("")
    else:
        print(f"⚠️  Selenium Manager não encontrado em: {sm_path}")
        print("   Tentando caminhos alternativos...")
        print("")


def get_webdriver():
    """
    Inicializa o WebDriver do Chrome usando múltiplas estratégias de fallback.
    Funciona tanto em ambiente Python quanto compilado como EXE (PyInstaller).

    Estratégia de inicialização (em ordem):
      1. ChromeDriver bundled (se existir junto ao projeto/EXE)
      2. Selenium Manager nativo (Selenium 4.6+)
      3. webdriver_manager via pip (apenas fora do EXE)

    Raises:
        RuntimeError: Se todas as estratégias falharem.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    print("")
    print("═" * 70)
    print("🌐  INICIALIZANDO NAVEGADOR")
    print("═" * 70)
    print("")
    print("⚙️  Configurando Chrome em modo invisível (headless)...")
    print("")

    is_frozen = getattr(sys, 'frozen', False)

    # Corrigir path do Selenium Manager para EXE
    _setup_selenium_manager_for_exe()

    # Configurar opções do Chrome
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)

    # Flags extras para estabilidade no ambiente EXE
    if is_frozen:
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--log-level=3")

    # ── Encontrar binário do Chrome ──
    chrome_path, chrome_source = _find_chrome_binary()

    if chrome_path:
        options.binary_location = chrome_path
        print(f"✅ Chrome {chrome_source} encontrado: {chrome_path}")
        print("")
    else:
        print("⚠️  Chrome não encontrado em locais conhecidos.")
        print("   O Selenium tentará detectar automaticamente...")
        print("")

    # ── Inicializar o driver com múltiplas estratégias ──
    errors = []

    # === ESTRATÉGIA 1: ChromeDriver bundled ===
    bundled_driver = _find_bundled_chromedriver()
    if bundled_driver:
        try:
            print(f"🔧 [Tentativa 1/3] Usando ChromeDriver bundled: {bundled_driver}")
            service = Service(executable_path=bundled_driver)
            driver = webdriver.Chrome(service=service, options=options)
            print("✅ Navegador iniciado com sucesso! (ChromeDriver bundled)")
            print("")
            print("─" * 70)
            print("")
            return driver
        except Exception as e:
            errors.append(f"ChromeDriver bundled: {e}")
            print(f"   ⚠️  Falhou: {e}")
            print("")

    # === ESTRATÉGIA 2: Selenium Manager nativo (Selenium 4.6+) ===
    try:
        tentativa = "2/3" if bundled_driver else "1/3"
        print(f"🔧 [Tentativa {tentativa}] Usando Selenium Manager nativo...")
        driver = webdriver.Chrome(options=options)
        print("✅ Navegador iniciado com sucesso! (Selenium Manager)")
        print("")
        print("─" * 70)
        print("")
        return driver
    except Exception as e:
        errors.append(f"Selenium Manager: {e}")
        print(f"   ⚠️  Falhou: {e}")
        print("")

    # === ESTRATÉGIA 3: webdriver_manager (apenas fora do EXE) ===
    if not is_frozen:
        try:
            print("🔧 [Tentativa 3/3] Usando webdriver_manager (pip)...")
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✅ Navegador iniciado com sucesso! (webdriver_manager)")
            print("")
            print("─" * 70)
            print("")
            return driver
        except ImportError:
            errors.append("webdriver_manager: pacote não instalado (pip install webdriver_manager)")
            print("   ⚠️  webdriver_manager não está instalado.")
            print("")
        except Exception as e:
            errors.append(f"webdriver_manager: {e}")
            print(f"   ⚠️  Falhou: {e}")
            print("")
    else:
        print("ℹ️  [Tentativa 3/3] webdriver_manager ignorado (ambiente EXE)")
        print("")

    # ── Se todas as estratégias falharam ──
    print("")
    print("═" * 70)
    print("❌ ERRO CRÍTICO: Não foi possível inicializar o navegador!")
    print("═" * 70)
    print("")
    print("📋 Detalhes das tentativas:")
    for i, err in enumerate(errors, 1):
        print(f"   {i}. {err}")
    print("")
    print("💡 Soluções possíveis:")
    print("   1. Instale o Google Chrome: https://www.google.com/chrome/")
    print("   2. Baixe o ChromeDriver compatível com seu Chrome:")
    print("      → https://googlechromelabs.github.io/chrome-for-testing/")
    print("      → Coloque o chromedriver.exe na pasta deps/Navegador/")
    print("   3. Verifique se o Chrome e o ChromeDriver são da mesma versão")
    print("   4. Execute como administrador")
    print("")
    print("═" * 70)
    print("")

    raise RuntimeError("Não foi possível inicializar o navegador Chrome. Tentando fallback HTTP...")


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 3: Fallback — Scraping via HTTP / API v2 do SoundCloud
# ══════════════════════════════════════════════════════════════════════

def _http_get(url, headers=None):
    """Faz GET request simples usando urllib (sem dependências extras)."""
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError

    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8', errors='replace')
    except (URLError, HTTPError) as e:
        print(f"   ⚠️  Erro HTTP: {e}")
        return None


def _extract_client_id(html_content):
    """Extrai o client_id do SoundCloud a partir dos scripts da página."""
    print("🔑 Procurando client_id nos scripts do SoundCloud...")
    script_urls = re.findall(r'src="(https://a-v2\.sndcdn\.com/assets/[^"]+\.js)"', html_content)
    total_scripts = len(script_urls)
    print(f"   📜 {total_scripts} scripts encontrados na página.")
    print(f"   🔍 Analisando os últimos {min(3, total_scripts)} scripts...")
    print("")

    for i, script_url in enumerate(script_urls[-3:], 1):
        print(f"   ⏳ [{i}/3] Analisando script: ...{script_url[-40:]}")
        js_content = _http_get(script_url)
        if js_content:
            match = re.search(r'client_id\s*[:=]\s*["\']([a-zA-Z0-9]{32})["\']', js_content)
            if match:
                print(f"   ✅ client_id encontrado no script {i}!")
                print("")
                return match.group(1)
            else:
                print(f"   ❌ client_id não encontrado neste script.")
        else:
            print(f"   ⚠️  Não foi possível baixar este script.")
    
    print("")
    print("❌ Não foi possível encontrar o client_id em nenhum script.")
    print("")
    return None


def _resolve_soundcloud_url(url, client_id):
    """Resolve uma URL do SoundCloud usando a API v2."""
    print(f"   ⤴️  Resolvendo URL: {url}")
    api_url = f"https://api-v2.soundcloud.com/resolve?url={url}&client_id={client_id}"
    response = _http_get(api_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    })
    if response:
        try:
            data = json.loads(response)
            kind = data.get('kind', 'desconhecido')
            print(f"   ✅ Resposta recebida! Tipo: {kind}")
            return data
        except json.JSONDecodeError:
            print("   ⚠️  Resposta da API não é um JSON válido.")
            return None
    print("   ❌ Sem resposta da API.")
    return None


def _get_collection_tracks(user_id, collection_type, client_id, limit=200):
    """Coleta tracks de uma coleção do usuário via API."""
    tracks = []
    page = 1
    next_href = (f"https://api-v2.soundcloud.com/users/{user_id}/{collection_type}"
                 f"?client_id={client_id}&limit=50&offset=0"
                 f"&linked_partitioning=1&app_locale=en")

    api_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Origin': 'https://soundcloud.com',
        'Referer': 'https://soundcloud.com/',
    }

    print("─" * 70)
    print(f"⏳ Carregando faixas da API (tipo: {collection_type})...")
    print("─" * 70)
    print("")

    while next_href and len(tracks) < limit * 5:
        print(f"   📄 Carregando página {page}...")
        response = _http_get(next_href, headers=api_headers)

        if not response:
            print("   ⚠️  Falha ao carregar página. Encerrando coleta.")
            break

        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            print("   ⚠️  Resposta inválida da API. Encerrando coleta.")
            break

        collection = data.get('collection', [])
        if not collection:
            print("   ℹ️  Nenhuma faixa adicional encontrada nesta página.")
            break

        tracks_nesta_pagina = 0
        for item in collection:
            track = item.get('track', item) if collection_type == 'reposts' else item
            permalink_url = track.get('permalink_url')
            if permalink_url:
                tracks.append(permalink_url)
                tracks_nesta_pagina += 1
                print(f"      🔗 {permalink_url}")

        print(f"   ✅ {tracks_nesta_pagina} faixa(s) encontrada(s) na página {page}")
        print(f"   📊 Total acumulado: {len(tracks)} faixa(s)")
        print("")

        next_href = data.get('next_href')
        if next_href and 'client_id' not in next_href:
            next_href += f"&client_id={client_id}"

        if next_href:
            print("   ⏳ Carregando próxima página...")
        else:
            print("   ℹ️  Última página alcançada.")

        page += 1
        time.sleep(0.5)

    print("")
    print("─" * 70)
    print(f"✅ Coleta via API finalizada! Total: {len(tracks)} faixa(s)")
    print("─" * 70)
    print("")
    return tracks


def _get_set_tracks(set_url, client_id):
    """Coleta tracks de um álbum/playlist via API."""
    print("─" * 70)
    print("📀 Resolvendo álbum/playlist via API...")
    print("─" * 70)
    print("")

    data = _resolve_soundcloud_url(set_url, client_id)
    if not data:
        print("❌ Não foi possível resolver o álbum/playlist!")
        print("")
        return []

    set_title = data.get('title', 'Sem título')
    total_na_playlist = len(data.get('tracks', []))
    print(f"✅ Álbum/Playlist encontrado: {set_title}")
    print(f"🎵 Total de faixas na playlist: {total_na_playlist}")
    print("")

    tracks = []
    for i, track in enumerate(data.get('tracks', []), 1):
        permalink_url = track.get('permalink_url')
        if permalink_url:
            tracks.append(permalink_url)
            print(f"   ✅ [{i}/{total_na_playlist}] {permalink_url}")
        elif track.get('id'):
            print(f"   ⏳ [{i}/{total_na_playlist}] Faixa com ID {track['id']} — resolvendo URL...")
            track_url = f"https://api-v2.soundcloud.com/tracks/{track['id']}?client_id={client_id}"
            track_response = _http_get(track_url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
            })
            if track_response:
                try:
                    track_data = json.loads(track_response)
                    purl = track_data.get('permalink_url')
                    if purl:
                        tracks.append(purl)
                        print(f"   ✅ [{i}/{total_na_playlist}] {purl}")
                    else:
                        print(f"   ⚠️  [{i}/{total_na_playlist}] URL não encontrada para ID {track['id']}")
                except json.JSONDecodeError:
                    print(f"   ⚠️  [{i}/{total_na_playlist}] Resposta inválida para ID {track['id']}")
            else:
                print(f"   ❌ [{i}/{total_na_playlist}] Falha ao resolver ID {track['id']}")

    print("")
    print("─" * 70)
    print(f"✅ Coleta do álbum/playlist finalizada! Total: {len(tracks)} faixa(s)")
    print("─" * 70)
    print("")
    return tracks


def http_fallback_scraper(soundcloud_link, choice):
    """
    Fallback: coleta links de tracks usando HTTP direto (sem Selenium).
    Usa a API v2 do SoundCloud.

    Args:
        soundcloud_link: URL completa do SoundCloud (perfil, playlist, etc.)
        choice: Opção escolhida pelo usuário ('1'-'7')

    Returns:
        Lista de URLs de tracks coletadas.
    """
    print("")
    print("═" * 70)
    print("🔄  MODO ALTERNATIVO: Scraping via HTTP (sem navegador)")
    print("═" * 70)
    print("")
    print("⏳ Obtendo client_id do SoundCloud...")
    print("")

    html = _http_get("https://soundcloud.com")
    if not html:
        print("❌ Não foi possível acessar o SoundCloud!")
        return []

    client_id = _extract_client_id(html)
    if not client_id:
        print("❌ Não foi possível obter o client_id do SoundCloud!")
        print("   Isso pode acontecer se o SoundCloud mudou a estrutura do site.")
        return []

    print(f"✅ client_id obtido: {client_id[:8]}...")
    print("")

    print("🔍 Resolvendo URL do artista...")
    print("")

    # Álbum/Playlist — pega direto
    if choice in ['4', '5']:
        print("📀 Coletando tracks do álbum/playlist...")
        print("")
        return _get_set_tracks(soundcloud_link, client_id)

    # Perfil de artista — resolve o user_id
    base_url = re.sub(r'/(tracks|popular-tracks|reposts|likes)$', '', soundcloud_link)
    user_data = _resolve_soundcloud_url(base_url, client_id)

    if not user_data or 'id' not in user_data:
        print("❌ Não foi possível resolver o perfil do artista!")
        return []

    user_id = user_data['id']
    username = user_data.get('username', 'Desconhecido')
    track_count = user_data.get('track_count', '?')
    print(f"✅ Artista encontrado: {username} (ID: {user_id})")
    print(f"📊 Faixas no perfil (informado pela API): {track_count}")
    print("")

    collection_map = {
        '1': 'tracks',
        '2': 'toptracks',
        '3': 'tracks',
        '6': 'reposts',
        '7': 'likes',
    }
    collection_type = collection_map.get(choice, 'tracks')

    opcoes_nomes = {
        '1': 'Todas as Faixas',
        '2': 'Faixas Populares',
        '3': 'Faixas',
        '6': 'Republicações',
        '7': 'Curtidas',
    }
    print(f"📊 Coletando: {opcoes_nomes.get(choice, collection_type)}")
    print("")

    return _get_collection_tracks(user_id, collection_type, client_id)
