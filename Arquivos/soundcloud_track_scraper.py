import subprocess
import time
import os
import sys

# Função para verificar e instalar dependências
def check_and_install_requirements():
    """
    Verifica se todas as dependências do requirements.txt estão instaladas.
    Se alguma estiver faltando, oferece a opção de instalá-las automaticamente.
    """
    # Vai para a pasta pai (raiz do projeto) e depois para Dependencias
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    requirements_file = os.path.join(project_root, 'Dependencias', 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        print("⚠️  Arquivo requirements.txt não encontrado!")
        print("")
        return True
    
    # Ler as dependências do arquivo
    with open(requirements_file, 'r', encoding='utf-8') as f:
        required_packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    missing_packages = []
    
    print("")
    print("═" * 70)
    print("🔍  VERIFICANDO DEPENDÊNCIAS DO PYTHON")
    print("═" * 70)
    print("")
    
    # Verifica cada pacote
    for package in required_packages:
        # Remove especificações de versão para checagem
        package_name = package.split('==')[0].split('>=')[0].split('<=')[0].strip()
        
        try:
            __import__(package_name.replace('-', '_'))
            print(f"  ✅  {package_name:<20} → Instalado")
        except ImportError:
            print(f"  ❌  {package_name:<20} → NÃO instalado")
            missing_packages.append(package)
    
    print("")
    print("─" * 70)
    
    # Se houver pacotes faltando, oferece instalação
    if missing_packages:
        print("")
        print(f"⚠️  ATENÇÃO: {len(missing_packages)} pacote(s) Python faltando!")
        print("")
        print("📋 Pacotes necessários:")
        for pkg in missing_packages:
            print(f"     • {pkg}")
        print("")
        print("─" * 70)
        resposta = input("\n💡 Deseja instalar automaticamente agora? (S/N): ").strip().upper()
        
        if resposta == 'S':
            print("")
            print("═" * 70)
            print("📦  INSTALANDO DEPENDÊNCIAS...")
            print("═" * 70)
            print("")
            
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
                print("")
                print("═" * 70)
                print("✅  SUCESSO! Todas as dependências foram instaladas!")
                print("═" * 70)
                print("")
                return True
            except subprocess.CalledProcessError as e:
                print("")
                print("═" * 70)
                print(f"❌  ERRO ao instalar dependências:")
                print(f"    {e}")
                print("═" * 70)
                print("")
                return False
        else:
            print("")
            print("⚠️  AVISO: O programa pode não funcionar sem as dependências!")
            print("")
            continuar = input("💭 Deseja tentar continuar mesmo assim? (S/N): ").strip().upper()
            print("")
            return continuar == 'S'
    else:
        print("")
        print("✅  Perfeito! Todas as dependências estão prontas!")
        print("")
        return True

# Verifica as dependências antes de continuar
if not check_and_install_requirements():
    print("")
    print("═" * 70)
    print("❌  Programa encerrado devido a dependências faltantes.")
    print("═" * 70)
    print("")
    sys.exit(1)

# Importa as dependências após verificação
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Configurações iniciais para a rolagem
SCROLL_PAUSE_TIME = 4  # Tempo de espera após cada scroll (ajuste se necessário)
MAX_ATTEMPTS = 5  # Número máximo de tentativas sem novas faixas serem carregadas

def get_selenium_version():
    try:
        import selenium
        print("")
        print(f"Versão do Selenium: {selenium.__version__}")
        print("")
    except ImportError:
        print("")
        print("O Selenium não está instalado.")
        print("")

def get_webdriver():
    """
    Inicializa o WebDriver do Chromium portátil usando o webdriver-manager.
    """
    print("")
    print("═" * 70)
    print("🌐  INICIALIZANDO NAVEGADOR")
    print("═" * 70)
    print("")
    print("⚙️  Configurando Chrome em modo invisível (headless)...")
    print("")

    options = Options()
    # Modo headless - navegador não abre janela visível
    options.add_argument("--headless=new")  # Usa o novo modo headless do Chrome
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Desabilita GPU para modo headless
    options.add_argument("--window-size=1920,1080")  # Define tamanho da janela virtual
    options.add_argument("--disable-blink-features=AutomationControlled")  # Evita detecção de automação
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Remove logs desnecessários
    options.add_experimental_option('useAutomationExtension', False)  # Desabilita extensão de automação
    
    # Configurar o caminho do Chrome se disponível
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # Quando compilado, os arquivos são extraídos para essa pasta temporária
    else:
        # Vai para a pasta pai (raiz do projeto)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(script_dir)

    # Lista de possíveis locais do Chrome no projeto (agora em Dependencias/Navegador/)
    portable_chrome_paths = [
        os.path.join(base_path, 'Dependencias', 'Navegador', 'chrome-win64', 'chrome.exe'),
        os.path.join(base_path, 'Navegador', 'chrome-win64', 'chrome.exe'),
        os.path.join(base_path, 'Chrome-bin', 'chrome.exe'),
    ]
    
    # Tenta encontrar o Chrome
    chrome_found = False
    
    # Primeiro, procura Chrome portátil no projeto
    for chrome_path in portable_chrome_paths:
        if os.path.exists(chrome_path):
            options.binary_location = chrome_path
            chrome_found = True
            print(f"✅ Chrome portátil encontrado: {chrome_path}")
            print("")
            break
    
    # Se não encontrou no projeto, procura Chrome instalado no sistema
    if not chrome_found:
        system_chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
        ]
        
        for chrome_path in system_chrome_paths:
            if os.path.exists(chrome_path):
                options.binary_location = chrome_path
                chrome_found = True
                print(f"✅ Chrome do sistema encontrado: {chrome_path}")
                print("")
                break
        
        if not chrome_found:
            print("❌ ERRO: Google Chrome não foi encontrado!")
            print("")
            print("Locais verificados no projeto:")
            for path in portable_chrome_paths:
                print(f"  - {path}")
            print("")
            print("📋 Soluções possíveis:")
            print("")
            print("OPÇÃO 1 (Recomendada) - Instalar Chrome no Sistema:")
            print("  → https://www.google.com/chrome/")
            print("")
            print("OPÇÃO 2 - Baixar Chrome Portátil:")
            print("  1. Baixe: https://storage.googleapis.com/chrome-for-testing-public/114.0.5708.0/win64/chrome-win64.zip")
            print("  2. Extraia para: Dependencias/Navegador/")
            print("  3. Certifique-se que existe: Dependencias/Navegador/chrome-win64/chrome.exe")
            print("")
            print("📖 Leia mais em: Dependencias/README.md")
            print("")
            
            continuar = input("Deseja tentar continuar mesmo assim? (S/N): ").strip().upper()
            if continuar != 'S':
                print("")
                print("Programa encerrado.")
                sys.exit(1)
            print("")

    # Usa o ChromeDriverManager para baixar e gerenciar automaticamente o chromedriver
    try:
        print("🔧 Baixando/atualizando ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        print("✅ ChromeDriver configurado com sucesso!")
        print("")
    except Exception as e:
        print("")
        print("═" * 70)
        print(f"❌ ERRO ao configurar ChromeDriver:")
        print(f"   {e}")
        print("═" * 70)
        print("")
        raise

    try:
        print("🚀 Iniciando navegador...")
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Navegador iniciado com sucesso!")
        print("")
        print("─" * 70)
        print("")
        return driver
    except Exception as e:
        print("")
        print("═" * 70)
        print("❌ ERRO CRÍTICO ao inicializar o navegador!")
        print("═" * 70)
        print(f"   Detalhes: {e}")
        print("")
        print("💡 Possíveis soluções:")
        print("   • Verifique se o Google Chrome está instalado")
        print("   • Tente reinstalar o Google Chrome")
        print("   • Execute o script como administrador")
        print("   • Verifique sua conexão com a internet")
        print("")
        print("═" * 70)
        print("")
        raise


def get_soundcloud_link():
    """
    Obtém o link do perfil do SoundCloud e valida a escolha do usuário.
    """

    while True:
        try:

            # Solicita o link do perfil do usuário e remove partes desnecessárias do URL
            user_input = input("Insira o link do perfil do SoundCloud: ").strip()
            user_input = user_input.replace('http://', '').replace('https://', '').rstrip('/')

            if not user_input:
                raise ValueError("Nenhum link foi inserido. Por favor, insira o link do perfil do SoundCloud.")

            print("")
            print(f"Link fornecido: {user_input}")
            print("")

            # Verifica se o link começa com "soundcloud.com"
            if not user_input.startswith("soundcloud.com"):
                raise ValueError(
                    "O link inserido não parece ser do SoundCloud. "
                    "Certifique-se de que o link seja do tipo 'https://soundcloud.com/...' "
                    "e tente novamente."
                )

            # Extrai a URL base e verifica se o link contém o nome do artista
            base_url = user_input.split("?")[0]
            path_parts = base_url.split("/")

            print("")
            print(f"URL base: {base_url}, partes do caminho: {path_parts}")
            print("")

            # Verifica se a URL contém o suficiente para determinar um perfil de artista
            if len(path_parts) < 2 or not path_parts[1]:
                print("")
                raise ValueError(
                    "O link fornecido deve conter o nome do artista. "
                    "Exemplo de link válido: 'https://soundcloud.com/nome-do-artista'."
                )

            # Monta a URL do artista
            artist_url = f"https://{path_parts[0]}/{path_parts[1]}"
            print("")
            print(f"URL do artista montada: {artist_url}")
            print("")
            
            # Se todas as validações passarem, retorna o link do artista
            return artist_url
        
        except ValueError as e:
            print(f"Erro: {e}")
            print("Por favor, tente novamente.\n")

def get_user_choice(artist_url):

    """
    Apresenta opções ao usuário e retorna a URL correspondente baseada na escolha.
    """

    # Apresenta opções ao usuário sobre o que ele deseja puxar do perfil
    print("O que você deseja puxar deste perfil?")
    print("1: Todas")
    print("2: Faixas populares")
    print("3: Faixas")
    print("4: Álbuns")  # Funcional
    print("5: Playlists")  # Funcional
    print("6: Republicações")
    print("7: Curtidas")
    print("")

    valid_choices = ["1", "2", "3", "4", "5", "6", "7"]
    
    # Loop para garantir que o usuário insira uma opção válida
    while True:

        # Solicita a escolha do usuário
        print("")
        choice = input("Escolha uma opção (1-7): ").strip()
        print("")


        if choice in valid_choices:
            print("")
            print(f"Opção escolhida: {choice}")
            print("")
            print("Validando opção...")
            print("")
            print("Opção válida!")
            print("")
            break  # Sai do loop se a opção for válida
            
        else:print(f"A opção '{choice}' não é válida. Por favor, escolha uma das seguintes opções: {', '.join(valid_choices)}.") 

    print("")
    print(f"Opção escolhida: {choice}")
    print("")

    # Define a URL de acordo com a escolha do usuário
    if choice == '1':
        return artist_url, choice
    elif choice == '2':
        return artist_url + "/popular-tracks", choice
    elif choice == '3':
        return artist_url + "/tracks", choice
    elif choice == '4' or choice == '5':
        # Solicita link de álbum ou playlist caso o usuário escolha álbuns ou playlists
        while True:
            set_list = input("Insira o link do Álbum/Playlist: ").strip()
            
            # Validação 1: não permite link vazio
            if not set_list:
                print("")
                print("❌ ERRO: Você precisa fornecer um link válido do álbum/playlist!")
                print("   Exemplo: https://soundcloud.com/artista/sets/playlist-name")
                print("")
                print("Por favor, tente novamente.")
                print("")
                continue
            
            # Validação 2: remove http/https e verifica se é do SoundCloud
            clean_link = set_list.replace('http://', '').replace('https://', '').rstrip('/')
            
            if not clean_link.startswith("soundcloud.com"):
                print("")
                print("❌ ERRO: O link inserido não parece ser do SoundCloud.")
                print("   Certifique-se de que o link seja do tipo:")
                print("   'https://soundcloud.com/artista/sets/playlist-name'")
                print("")
                print("Por favor, tente novamente.")
                print("")
                continue
            
            # Validação 3: verifica se contém '/sets/' para álbuns/playlists
            if '/sets/' not in clean_link:
                print("")
                print("⚠️  AVISO: O link não contém '/sets/', que geralmente indica um álbum/playlist.")
                print("   Você digitou: " + set_list)
                print("")
                confirmar = input("Deseja continuar mesmo assim? (S/N, padrão=N): ").strip().upper()
                if not confirmar:
                    confirmar = 'N'
                if confirmar != 'S':
                    print("")
                    print("Por favor, tente novamente.")
                    print("")
                    continue
            
            # Todas as validações passaram, sai do loop
            break
        
        print("")
        print(f"Link do álbum/playlist fornecido: {set_list}")
        print("")
        return set_list, choice
    elif choice == '6':
        return artist_url + "/reposts", choice
    elif choice == '7':
        return artist_url + "/likes", choice
    else:
        raise ValueError("Opção inválida.")

def scroll_and_collect_tracks(driver, scroll_pause_time, max_attempts, css_selector):
    """
    Função para rolar a página e coletar links das faixas encontradas.
    """
    num_tracks = 0  # Inicializa a contagem de faixas encontradas
    attempts = 0  # Inicializa o contador de tentativas

    while attempts < max_attempts:
        # Rola até o final da página para carregar mais conteúdo
        print("")
        print("Rolando a página para carregar mais faixas...")
        print("")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)  # Pausa para permitir o carregamento das novas faixas

        # Coleta as faixas que foram carregadas na página
        tracks = driver.find_elements(By.CSS_SELECTOR, css_selector)
        new_num_tracks = len(tracks)
        print("")
        print(f"Número de faixas carregadas: {new_num_tracks}")
        print("")

        # Verifica se novas faixas foram carregadas em comparação com a última contagem
        if new_num_tracks == num_tracks:
            attempts += 1
            print("")
            print(f"Nenhuma nova faixa carregada, tentando novamente... ({attempts}/{max_attempts})")
            print("")
        else:
            num_tracks = new_num_tracks  # Atualiza o número de faixas encontradas
            attempts = 0  # Reinicia o contador de tentativas se novas faixas forem encontradas
            print("")
            print("Novas faixas foram carregadas, reiniciando contagem de tentativas...")
            print("")

    print("")
    print(f"Total de faixas coletadas: {len(tracks)}")
    print("")
    return tracks  # Retorna a lista de faixas coletadas


def save_track_links(filename, tracks):
    """
    Salva os links das faixas coletadas em um arquivo.
    """
    print("")
    print(f"Salvando links das faixas no arquivo: {filename}")
    print("")
    # Abre o arquivo especificado para escrita
    with open(filename, 'w', encoding='utf-8') as file:
        # Extrai os URLs das faixas coletadas, garantindo que sejam únicos
        track_urls = {track.get_attribute("href") for track in tracks if track.get_attribute("href")}

        # Escreve cada link coletado no arquivo e imprime para o usuário
        for url in track_urls:
            file.write(url + '\n')
            print("")
            print(f"Link salvo: {url}")
            print("")

        # Como já sabemos que haverá faixas, podemos apenas mostrar a quantidade coletada
        print("")
        print(f"Total de faixas coletadas e salvas: {len(track_urls)}")
        print("")


def soundcloud_track_scraper():
    """
    Executa o fluxo completo de coleta de links de faixas do SoundCloud.
    """
    # Banner inicial
    print("")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🎵  SOUNDSCRAPER - Link Collector  🔗".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print("")
    
    # Obtém o link do perfil do SoundCloud e a opção escolhida pelo usuário
    soundcloud_link = get_soundcloud_link()
    soundcloud_link, choice = get_user_choice(soundcloud_link)
    
    # Solicita o nome do arquivo para salvar os links
    print("")
    print("═" * 70)
    print("📄  CONFIGURAÇÃO DO ARQUIVO DE SAÍDA")
    print("═" * 70)
    print("")
    print("💡 Dica: Escolha um nome descritivo, como 'links_artista' ou 'playlist_favoritas'")
    print("")
    filename = input("📝 Digite o nome do arquivo (sem extensão): ").strip()
    if not filename:
        filename = "soundcloud_links"
        print(f"⚠️  Nome vazio! Usando padrão: {filename}")
    filename += ".txt"
    print("")
    print(f"✅ Arquivo será salvo como: {filename}")
    print("")

    get_selenium_version()

    driver = get_webdriver()  # Inicializa o WebDriver
    
    print("═" * 70)
    print("🌐  ACESSANDO SOUNDCLOUD")
    print("═" * 70)
    print("")
    print(f"🔗 URL: {soundcloud_link}")
    print("⏳ Aguarde enquanto a página carrega...")
    print("")
    driver.get(soundcloud_link)  # Navega até o link do perfil do SoundCloud
    print("✅ Página carregada com sucesso!")
    print("")

    # Mapeamento de opções para nomes amigáveis
    opcoes_nomes = {
        '1': 'Todas as Faixas',
        '2': 'Álbuns',
        '3': 'Playlists',
        '4': 'Curtidas',
        '5': 'Faixas Populares',
        '6': 'Reposts'
    }
    
    print("─" * 70)
    print(f"📊 Modo selecionado: {opcoes_nomes.get(choice, 'Desconhecido')}")
    print("─" * 70)
    print("")

    # Seleciona o CSS Selector de acordo com a escolha do usuário
    css_selector = "li.trackList__item a.trackItem__trackTitle" if choice in ['4', '5'] else "a.soundTitle__title"
    
    # Coleta as faixas disponíveis na página
    tracks = scroll_and_collect_tracks(driver, SCROLL_PAUSE_TIME, MAX_ATTEMPTS, css_selector)
    
    # Salva os links das faixas em um arquivo
    save_track_links(filename, tracks)

    driver.quit()  # Fecha o navegador
    
    print("")
    print("═" * 70)
    print("✅  COLETA CONCLUÍDA COM SUCESSO!")
    print("═" * 70)
    print("")
    print(f"📁 Links salvos em: {filename}")
    print(f"📊 Total de faixas encontradas: {len(tracks)}")
    print("")
    print("═" * 70)
    print("")
    
    return filename  # Retorna o nome do arquivo criado