from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import time
from selenium.webdriver.chrome.options import Options
import os
import sys

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
    print("Iniciando o WebDriver com webdriver-manager...")
    print("")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--enable-unsafe-swiftshader')
    
    # Corrigir o caminho do Chrome-bin para quando estiver dentro de um .exe
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # Quando compilado, os arquivos são extraídos para essa pasta temporária
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    options.binary_location = os.path.join(base_path, 'Chrome-bin', 'chrome.exe')

    service = Service(chromedriver_path = r"C:\Users\Felipe\.wdm\drivers\chromedriver\win64\130.0.6723.91\chromedriver-win32\chromedriver.exe") # Isso no meu PC né, atualize para o caminho no seu pc caso você vá usar pelo código fonte

    print("Configurações do WebDriver definidas com sucesso.")
    return webdriver.Chrome(service=service, options=options)


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
                raise ValueError("Nenhum link foi inserido.")

            print("")
            print(f"Link fornecido: {user_input}")
            print("")

            # Valida se o link parece ser do SoundCloud
            if not user_input.startswith("soundcloud.com"):
                print("")
                raise ValueError("O link inserido não parece ser do SoundCloud.")

            # Extrai a URL base e verifica se o link contém o nome do artista
            base_url = user_input.split("?")[0]
            path_parts = base_url.split("/")

            print("")
            print(f"URL base: {base_url}, partes do caminho: {path_parts}")
            print("")

            if len(path_parts) < 2 or not path_parts[1]:
                print("")
                raise ValueError("O link deve conter o nome do artista.")

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
            
        else:print("Opção inválida. Por favor, escolha uma opção válida (1-7).")    

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
        set_list = input("Insira o link do Álbum/Playlist: ").strip()
        print(f"Link do álbum/playlist fornecido: {set_list}\n")
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
        print("")
        print(f"Total de faixas coletadas: {len(track_urls)}")
        print("")


def soundcloud_track_scraper():
    """
    Executa o fluxo completo de coleta de links de faixas do SoundCloud.
    """
    # Obtém o link do perfil do SoundCloud e a opção escolhida pelo usuário
    soundcloud_link = get_soundcloud_link()
    soundcloud_link, choice = get_user_choice(soundcloud_link)
    
    # Solicita o nome do arquivo para salvar os links
    print("")
    filename = input("Digite o nome do arquivo em que deseja salvar os links das tracks: ") + ".txt"
    print("")
    print(f"Nome do arquivo fornecido: {filename}")
    print("")

    get_selenium_version()

    driver = get_webdriver()  # Inicializa o WebDriver
    print("")
    print(f"Navegando até o link do perfil do SoundCloud: {soundcloud_link}")
    print("")
    driver.get(soundcloud_link)  # Navega até o link do perfil do SoundCloud

    print("")
    print(f"Você escolheu a opção {choice}")
    print("")

    # Seleciona o CSS Selector de acordo com a escolha do usuário
    css_selector = "li.trackList__item a.trackItem__trackTitle" if choice in ['4', '5'] else "a.soundTitle__title"
    
    # Coleta as faixas disponíveis na página
    tracks = scroll_and_collect_tracks(driver, SCROLL_PAUSE_TIME, MAX_ATTEMPTS, css_selector)
    
    # Salva os links das faixas em um arquivo
    save_track_links(filename, tracks)

    driver.quit()  # Fecha o navegador
    print("")
    print(f"Processo concluído, faixas salvas em: {filename}")
    print("")
    return filename  # Retorna o nome do arquivo criado