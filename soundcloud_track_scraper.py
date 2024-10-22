from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configurações iniciais para a rolagem
scroll_pause_time = 4  # Tempo de espera após cada scroll (ajuste se necessário)
max_attempts = 5  # Número máximo de tentativas sem novas faixas serem carregadas

def get_webdriver():
    print("Iniciando o WebDriver do Chrome usando webdriver-manager...")
    options = webdriver.ChromeOptions()
    # Especifique o caminho para o executável do Chrome, se necessário
    # options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_soundcloud_link():
    user_input = input("Insira o link do perfil do SoundCloud: ").strip()
    
    # Remove "http://" ou "https://" do início, se existir
    user_input = user_input.replace('http://', '').replace('https://', '').rstrip('/')
    
    # Verifica se o link é do SoundCloud
    if not user_input.startswith("soundcloud.com"):
        raise ValueError("O link inserido não parece ser do SoundCloud.")
    
    # Remove parâmetros de URL, se existirem
    base_url = user_input.split("?")[0]
    path_parts = base_url.split("/")  # Divide o link por "/"

    # Verifica se o link contém pelo menos o domínio e o nome do artista
    if len(path_parts) < 2 or not path_parts[1]:
        raise ValueError("O link deve conter o nome do artista.")

    # Constrói o link base até o nome do artista
    artist_url = f"https://{path_parts[0]}/{path_parts[1]}"

    print("O que você deseja puxar deste perfil?")
    print("1: Faixas")
    print("2: Republicações")
    print("3: Playlists")
    print("4: Todas as atividades (pode incluir republicações e faixas de outros artistas)")

    choice = input("Escolha uma opção (1-4): ").strip()

    # Formata o link de acordo com a escolha do usuário
    if choice == '1':
        return artist_url + "/tracks"
    elif choice == '2':
        return artist_url + "/reposts"
    elif choice == '3':
        return artist_url + "/sets"
    elif choice == '4':
        return artist_url  # Retorna o link da página de atividades
    else:
        raise ValueError("Opção inválida.")

def scroll_and_collect_tracks(driver, scroll_pause_time, max_attempts):
    num_tracks = 0  # Número de tracks
    attempts = 0  # Tentativas

    while True:
        # Rolar até o final da página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Esperar o carregamento das novas faixas
        time.sleep(scroll_pause_time)

        # Contar o número de faixas carregadas
        tracks = driver.find_elements(By.CSS_SELECTOR, "a.soundTitle__title")
        new_num_tracks = len(tracks)
        print(f"Número de faixas carregadas: {new_num_tracks}")

        # Verificar se novas faixas foram carregadas
        if new_num_tracks == num_tracks:
            attempts += 1
            if attempts >= max_attempts:
                # Se não houver novas faixas após várias tentativas, sair do loop
                break
        else:
            num_tracks = new_num_tracks
            attempts = 0  # Resetar o contador de tentativas

    # Retorna as faixas encontradas
    return tracks

def save_track_links(filename, tracks):
    # Abrir um arquivo para salvar os links
    with open(filename, 'w', encoding='utf-8') as file:
        track_urls = set()
        for track in tracks:
            url = track.get_attribute("href")
            if url:
                track_urls.add(url)

        # Remover duplicatas e salvar
        for url in track_urls:
            file.write(url + '\n')
            print(url)

def executar_todas_funcoes():

    soundcloud_link = get_soundcloud_link()

    nome_arquivo = input("Digite o nome do arquivo que deseja salvar os links das tracks: ")
    filename = nome_arquivo + ".txt"
    
    driver = get_webdriver()
    driver.get(soundcloud_link)

    tracks = scroll_and_collect_tracks(driver, scroll_pause_time, max_attempts)
    save_track_links(filename, tracks)

    driver.quit()