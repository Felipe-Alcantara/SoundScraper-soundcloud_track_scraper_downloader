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
    options.add_argument("--no-sandbox")  # Necessário para ambientes de conteinerização
    options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória compartilhada
    print("Configurações do WebDriver definidas com sucesso.")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def get_soundcloud_link():
    """
    Obtém o link do perfil do SoundCloud e valida a escolha do usuário.
    """
    # Solicita o link do perfil do usuário e remove partes desnecessárias do URL
    user_input = input("Insira o link do perfil do SoundCloud: ").strip()
    user_input = user_input.replace('http://', '').replace('https://', '').rstrip('/')
    print(f"Link fornecido: {user_input}")

    # Valida se o link parece ser do SoundCloud
    if not user_input.startswith("soundcloud.com"):
        raise ValueError("O link inserido não parece ser do SoundCloud.")

    # Extrai a URL base e verifica se o link contém o nome do artista
    base_url = user_input.split("?")[0]
    path_parts = base_url.split("/")
    print(f"URL base: {base_url}, partes do caminho: {path_parts}")

    if len(path_parts) < 2 or not path_parts[1]:
        raise ValueError("O link deve conter o nome do artista.")

    # Monta a URL do artista
    artist_url = f"https://{path_parts[0]}/{path_parts[1]}"
    print(f"URL do artista montada: {artist_url}")

    # Apresenta opções ao usuário sobre o que ele deseja puxar do perfil
    print("O que você deseja puxar deste perfil?")
    print("1: Todas")
    print("2: Faixas populares")
    print("3: Faixas")
    print("4: Álbuns")  # Funcional
    print("5: Playlists")  # Funcional
    print("6: Republicações")

    # Solicita a escolha do usuário
    choice = input("Escolha uma opção (1-6): ").strip()
    print(f"Opção escolhida: {choice}")

    # Define a URL de acordo com a escolha do usuário
    if choice == '3':
        return artist_url + "/tracks", choice
    elif choice == '2':
        return artist_url + "/popular-tracks", choice
    elif choice == '1':
        return artist_url, choice
    elif choice == '6':
        return artist_url + "/reposts", choice
    elif choice in ['4', '5']:
        # Solicita link de álbum ou playlist caso o usuário escolha álbuns ou playlists
        set_list = input("Insira o link do Álbum/Playlist: ").strip()
        print(f"Link do álbum/playlist fornecido: {set_list}")
        return set_list, choice
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
        print("Rolando a página para carregar mais faixas...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)  # Pausa para permitir o carregamento das novas faixas

        # Coleta as faixas que foram carregadas na página
        tracks = driver.find_elements(By.CSS_SELECTOR, css_selector)
        new_num_tracks = len(tracks)
        print(f"Número de faixas carregadas: {new_num_tracks}")

        # Verifica se novas faixas foram carregadas em comparação com a última contagem
        if new_num_tracks == num_tracks:
            attempts += 1
            print(f"Nenhuma nova faixa carregada, tentando novamente... ({attempts}/{max_attempts})")
        else:
            num_tracks = new_num_tracks  # Atualiza o número de faixas encontradas
            attempts = 0  # Reinicia o contador de tentativas se novas faixas forem encontradas
            print("Novas faixas foram carregadas, reiniciando contagem de tentativas...")

    print(f"Total de faixas coletadas: {len(tracks)}")
    return tracks  # Retorna a lista de faixas coletadas


def save_track_links(filename, tracks):
    """
    Salva os links das faixas coletadas em um arquivo.
    """
    print(f"Salvando links das faixas no arquivo: {filename}")
    # Abre o arquivo especificado para escrita
    with open(filename, 'w', encoding='utf-8') as file:
        # Extrai os URLs das faixas coletadas, garantindo que sejam únicos
        track_urls = {track.get_attribute("href") for track in tracks if track.get_attribute("href")}

        # Escreve cada link coletado no arquivo e imprime para o usuário
        for url in track_urls:
            file.write(url + '\n')
            print(f"Link salvo: {url}")
        print(f"Total de faixas coletadas: {len(track_urls)}")


def executar_todas_funcoes():
    """
    Executa o fluxo completo de coleta de links de faixas do SoundCloud.
    """
    # Obtém o link do perfil do SoundCloud e a opção escolhida pelo usuário
    soundcloud_link, choice = get_soundcloud_link()
    
    # Solicita o nome do arquivo para salvar os links
    filename = input("Digite o nome do arquivo que deseja salvar os links das tracks: ") + ".txt"
    print(f"Nome do arquivo fornecido: {filename}")
    driver = get_webdriver()  # Inicializa o WebDriver
    print(f"Navegando até o link do perfil do SoundCloud: {soundcloud_link}")
    driver.get(soundcloud_link)  # Navega até o link do perfil do SoundCloud

    print(f"Você escolheu a opção {choice}")

    # Seleciona o CSS Selector de acordo com a escolha do usuário
    css_selector = "li.trackList__item a.trackItem__trackTitle" if choice in ['4', '5'] else "a.soundTitle__title"
    
    # Coleta as faixas disponíveis na página
    tracks = scroll_and_collect_tracks(driver, SCROLL_PAUSE_TIME, MAX_ATTEMPTS, css_selector)
    
    # Salva os links das faixas em um arquivo
    save_track_links(filename, tracks)

    driver.quit()  # Fecha o navegador
    print(f"Processo concluído, faixas salvas em: {filename}")
    return filename  # Retorna o nome do arquivo criado