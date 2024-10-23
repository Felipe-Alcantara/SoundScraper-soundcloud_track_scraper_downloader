from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time

# Configurações iniciais para a rolagem
SCROLL_PAUSE_TIME = 4  # Tempo de espera após cada scroll (ajuste se necessário)
MAX_ATTEMPTS = 5  # Número máximo de tentativas sem novas faixas serem carregadas

def get_webdriver():
    """
    Inicializa o WebDriver do Chrome usando o webdriver-manager.
    """
    print("Iniciando o WebDriver do Chrome usando webdriver-manager...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Executa o Chrome em modo headless para não abrir a janela do navegador
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def get_soundcloud_link():
    """
    Obtém o link do perfil do SoundCloud e valida a escolha do usuário.
    """
    user_input = input("Insira o link do perfil do SoundCloud: ").strip()
    user_input = user_input.replace('http://', '').replace('https://', '').rstrip('/')

    if not user_input.startswith("soundcloud.com"):
        raise ValueError("O link inserido não parece ser do SoundCloud.")

    base_url = user_input.split("?")[0]
    path_parts = base_url.split("/")

    if len(path_parts) < 2 or not path_parts[1]:
        raise ValueError("O link deve conter o nome do artista.")

    artist_url = f"https://{path_parts[0]}/{path_parts[1]}"

    print("O que você deseja puxar deste perfil?")
    print("1: Todas")
    print("2: Faixas populares")
    print("3: Faixas")
    print("4: Álbuns")  # Não funcional atualmente
    print("5: Playlists")  # Não funcional atualmente
    print("6: Republicações")

    choice = input("Escolha uma opção (1-6): ").strip()

    if choice == '3':
        return artist_url + "/tracks", choice
    elif choice == '2':
        return artist_url + "/popular-tracks", choice
    elif choice == '1':
        return artist_url, choice
    elif choice == '6':
        return artist_url + "/reposts", choice
    elif choice in ['4', '5']:
        set_list = input("Insira o link do Álbum/Playlist: ").strip()
        return set_list, choice
    else:
        raise ValueError("Opção inválida.")


def scroll_and_collect_tracks(driver, scroll_pause_time, max_attempts, css_selector):
    """
    Função para rolar a página e coletar links das faixas encontradas.
    """
    num_tracks = 0
    attempts = 0

    while attempts < max_attempts:
        # Rola até o final da página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)  # Pausa para permitir o carregamento das novas faixas

        tracks = driver.find_elements(By.CSS_SELECTOR, css_selector)
        new_num_tracks = len(tracks)
        print(f"Número de faixas carregadas: {new_num_tracks}")

        # Verifica se novas faixas foram carregadas
        if new_num_tracks == num_tracks:
            attempts += 1
            print(f"Nenhuma nova faixa carregada, tentando novamente... ({attempts}/{max_attempts})")
        else:
            num_tracks = new_num_tracks
            attempts = 0  # Reinicia o contador de tentativas se novas faixas forem encontradas
            print("Novas faixas foram carregadas, reiniciando contagem de tentativas...")

    return tracks


def save_track_links(filename, tracks):
    """
    Salva os links das faixas coletadas em um arquivo.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        track_urls = {track.get_attribute("href") for track in tracks if track.get_attribute("href")}

        for url in track_urls:
            file.write(url + '\n')
            print(f"Link salvo: {url}")
        print(f"Total de faixas coletadas: {len(track_urls)}")


def executar_todas_funcoes():
    """
    Executa o fluxo completo de coleta de links de faixas do SoundCloud.
    """
    soundcloud_link, choice = get_soundcloud_link()
    
    filename = input("Digite o nome do arquivo que deseja salvar os links das tracks: ") + ".txt"
    driver = get_webdriver()
    driver.get(soundcloud_link)

    print(f"Você escolheu a opção {choice}")

    # Seleciona o CSS Selector de acordo com a escolha do usuário
    css_selector = "li.trackList__item a.trackItem__trackTitle" if choice in ['4', '5'] else "a.soundTitle__title"
    
    # Coleta as faixas disponíveis na página
    tracks = scroll_and_collect_tracks(driver, SCROLL_PAUSE_TIME, MAX_ATTEMPTS, css_selector)
    
    # Salva os links das faixas em um arquivo
    save_track_links(filename, tracks)

    driver.quit()
    return filename