import subprocess
import time
import os
import sys
import re


# Função para verificar e instalar dependências
def check_and_install_requirements():
    """
    Verifica se todas as dependências do requirements.txt estão instaladas.
    Se alguma estiver faltando, oferece a opção de instalá-las automaticamente.
    """
    # Vai para a pasta pai (raiz do projeto) e depois para deps
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    requirements_file = os.path.join(project_root, 'deps', 'requirements.txt')
    
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
        # Remove versão (==, >=, <=) e extras ([standard]) para obter o nome do módulo.
        package_name = package.split('==')[0].split('>=')[0].split('<=')[0]
        package_name = package_name.split('[')[0].strip()

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

# Verifica as dependências apenas se executado diretamente (não quando importado pelo downloader)
if __name__ == '__main__':
    if not check_and_install_requirements():
        print("")
        print("═" * 70)
        print("❌  Programa encerrado devido a dependências faltantes.")
        print("═" * 70)
        print("")
        sys.exit(1)

# Importa as dependências após verificação
from selenium.webdriver.common.by import By

# Importa o módulo de navegador (toda lógica de Chrome/HTTP fica lá)
from browser_handler import get_webdriver, get_selenium_version, http_fallback_scraper

# Configurações iniciais para a rolagem
SCROLL_PAUSE_TIME = 4  # Tempo de espera após cada scroll (ajuste se necessário)
MAX_ATTEMPTS = 5  # Número máximo de tentativas sem novas faixas serem carregadas


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
    Também tenta clicar em botões 'Show more' / 'Ver mais' para carregar tudo.
    """
    tracks = []
    num_tracks = 0  # Inicializa a contagem de faixas encontradas
    attempts = 0  # Inicializa o contador de tentativas

    while attempts < max_attempts:
        # Tenta clicar em botões "Show more" / "Ver mais" se existirem
        try:
            show_more_selectors = [
                "a.showMore",
                "button.showMore",
                "a[class*='ShowMore']",
                "button[class*='ShowMore']",
                "a.compactTrackList__moreLink",
            ]
            for sel in show_more_selectors:
                buttons = driver.find_elements(By.CSS_SELECTOR, sel)
                for btn in buttons:
                    if btn.is_displayed():
                        try:
                            btn.click()
                            print("")
                            print("🔘 Botão 'Ver mais' encontrado e clicado!")
                            time.sleep(scroll_pause_time)
                        except Exception:
                            pass
        except Exception:
            pass

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
    Usa Selenium + HTTP API combinados para máxima cobertura.
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
    artist_base_url = get_soundcloud_link()  # Ex: https://soundcloud.com/glurckyy
    soundcloud_link, choice = get_user_choice(artist_base_url)
    
    # Gera nome do arquivo automaticamente baseado no link
    # Ex: soundcloud.com/artista/tracks → artista_tracks.txt
    clean_url = soundcloud_link.replace('https://', '').replace('http://', '')
    clean_url = clean_url.replace('soundcloud.com/', '')
    # Sanitiza: substitui barras e caracteres inválidos por underscore
    filename = re.sub(r'[^\w\-]', '_', clean_url).strip('_')
    if not filename:
        filename = 'soundcloud_links'
    filename += '.txt'
    print("")
    print(f"📄 Arquivo temporário de links: {filename}")
    print("")

    # ══════════════════════════════════════════════════════════════
    #  Coleta via Selenium + HTTP API (cobertura dupla)
    # ══════════════════════════════════════════════════════════════
    
    selenium_urls = set()
    http_urls = set()
    
    # ── ETAPA 1: Selenium ──
    selenium_ok = False
    driver = None
    
    try:
        get_selenium_version()
        driver = get_webdriver()  # Inicializa o WebDriver
        selenium_ok = True
    except SystemExit:
        selenium_ok = False
        print("")
        print("═" * 70)
        print("⚠️  Selenium não disponível — usando apenas HTTP/API")
        print("═" * 70)
        print("")
    except Exception as e:
        selenium_ok = False
        print("")
        print(f"⚠️  Erro ao inicializar Selenium: {e}")
        print("")
        print("═" * 70)
        print("⚠️  Selenium não disponível — usando apenas HTTP/API")
        print("═" * 70)
        print("")

    if selenium_ok and driver:
        try:
            print("═" * 70)
            print("🌐  ACESSANDO SOUNDCLOUD (via Selenium)")
            print("═" * 70)
            print("")
            print(f"🔗 URL: {soundcloud_link}")
            print("⏳ Aguarde enquanto a página carrega...")
            print("")
            driver.get(soundcloud_link)
            print("✅ Página carregada com sucesso!")
            print("")

            opcoes_nomes = {
                '1': 'Todas as Faixas',
                '2': 'Faixas Populares',
                '3': 'Faixas',
                '4': 'Álbuns',
                '5': 'Playlists',
                '6': 'Republicações',
                '7': 'Curtidas'
            }
            
            print("─" * 70)
            print(f"📊 Modo selecionado: {opcoes_nomes.get(choice, 'Desconhecido')}")
            print("─" * 70)
            print("")

            css_selector = "li.trackList__item a.trackItem__trackTitle" if choice in ['4', '5'] else "a.soundTitle__title"
            tracks = scroll_and_collect_tracks(driver, SCROLL_PAUSE_TIME, MAX_ATTEMPTS, css_selector)
            
            # Extrai URLs dos WebElements
            for track in tracks:
                href = track.get_attribute("href")
                if href:
                    selenium_urls.add(href)
            
            print(f"\n📊 Selenium coletou: {len(selenium_urls)} link(s)")
            driver.quit()
        except Exception as e:
            print(f"⚠️  Erro durante scraping com Selenium: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    # ── ETAPA 2: HTTP API (verificação e complemento) ──
    print("")
    print("═" * 70)
    print("🔍  VERIFICANDO COBERTURA VIA API")
    print("═" * 70)
    print("")
    
    try:
        result = http_fallback_scraper(soundcloud_link, choice)
        if result:
            http_urls = set(result)
    except Exception as e:
        print(f"⚠️  Erro no HTTP fallback: {e}")

    # ── ETAPA 3: Mesclar resultados ──
    all_urls = selenium_urls | http_urls
    
    if not all_urls:
        print("")
        print("❌ Não foi possível coletar links por nenhum método!")
        print("")
        print("💡 Soluções possíveis:")
        print("   1. Instale o Google Chrome para usar o modo Selenium")
        print("   2. Verifique sua conexão com a internet")
        print("   3. Tente novamente mais tarde")
        print("")
        input("Pressione ENTER para encerrar...")
        sys.exit(1)

    # ── ETAPA 4: Estatísticas ──
    apenas_selenium = selenium_urls - http_urls
    apenas_http = http_urls - selenium_urls
    em_comum = selenium_urls & http_urls
    
    print("")
    print("═" * 70)
    print("📊  RESULTADO DA COLETA")
    print("═" * 70)
    if selenium_urls:
        print(f"   🌐 Selenium:  {len(selenium_urls)} link(s)")
    if http_urls:
        print(f"   📡 HTTP API:   {len(http_urls)} link(s)")
    if selenium_urls and http_urls:
        print(f"   🔗 Em comum:   {len(em_comum)}")
        if apenas_http:
            print(f"   ➕ Extras (só API): {len(apenas_http)} faixa(s) recuperada(s)!")
        if apenas_selenium:
            print(f"   ➕ Extras (só Selenium): {len(apenas_selenium)}")
    print(f"   ✅ Total final: {len(all_urls)} faixa(s) únicas")
    print("═" * 70)
    print("")

    # ── ETAPA 5: Salvar resultados ──
    with open(filename, 'w', encoding='utf-8') as f:
        for url in sorted(all_urls):
            f.write(url + '\n')
            print(f"   🔗 {url}")
    
    print("")
    print("═" * 70)
    print("✅  COLETA CONCLUÍDA COM SUCESSO!")
    print("═" * 70)
    print("")
    print(f"📁 Links salvos em: {filename}")
    print("")
    print("═" * 70)
    print("")
    
    return filename  # Retorna o nome do arquivo criado
