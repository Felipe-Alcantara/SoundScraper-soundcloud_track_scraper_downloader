import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configurações iniciais para a rolagem
scroll_pause_time = 4  # Tempo de espera após cada scroll (ajuste se necessário)
max_attempts = 5  # Número máximo de tentativas sem novas faixas serem carregadas

def get_webdriver():
    chrome_path = shutil.which("google-chrome") or shutil.which("chrome")
    firefox_path = shutil.which("firefox")
    edge_path = shutil.which("msedge")
    safari_path = shutil.which("safari")

    if chrome_path:
        print("Google Chrome encontrado!")
        return webdriver.Chrome()
    elif firefox_path:
        print("Mozilla firefox encontrado!")
        return webdriver.Firefox()
    elif edge_path:
        print("Microsoft EDGE encontrado!")
        return webdriver.Edge()
    elif safari_path:
        print("Safari encontrado!")
        return webdriver.Safari()

    else:
        raise Exception("Nenhum navegador suportado foi encontrado.")

def get_soundcloud_link():
    while True:
        try: # Loop até o input ser válido
            usuario_link = input("Insira o link do perfil do SoundCloud: ").strip()
            
            # Remove "http://" ou "https://" do início, se existir
            usuario_link = usuario_link.replace('http://', '').replace('https://', '')

            # Verifica se o link é do SoundCloud
            if not usuario_link.startswith("soundcloud.com"):
                raise ValueError("O link inserido não parece ser do SoundCloud.")
            
            # Remove parâmetros de URL, se existirem
            base_url = usuario_link.split("?")[0]
            path_parts = base_url.split("/")  # Divide o link por "/"

            # Mantém apenas a parte até o nome do artista (segunda posição)
            if len(path_parts) < 2 or not path_parts[1]:  # Verifica se o formato é correto
                raise ValueError("O link deve conter o nome do artista.")
            
            # Retorna o link formatado no estilo https://soundcloud.com/artista
            return f"{path_parts[0]}/{path_parts[1]}"
    
        except ValueError as ve:  # Captura a exceção e imprime a mensagem correta
            print(f"Erro: {ve}. Por favor, insira um link válido.")

def scroll_and_collect_tracks(driver, scroll_pause_time, max_attempts):
    num_tracks = 0 # Número de tracks
    attempts = 0 # Tentativas

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
    with open(filename, 'w', encoding='utf-8') as file: #O método "W", se o arquivo não existir, ele cria um novo arquivo.
        track_urls = set()
        for track in tracks:
            url = track.get_attribute("href")
            if url:  # Apenas verifica se o link não é None ou vazio
                track_urls.add(url)

        # Remover duplicatas e salvar
        for url in track_urls:
            file.write(url + '\n')
            print(url)

def executar_todas_funcoes(soundcloud_link, filename):
    driver = get_webdriver()
    formatted_link = get_soundcloud_link(soundcloud_link)
    driver.get(formatted_link)

    tracks = scroll_and_collect_tracks(driver, scroll_pause_time, max_attempts)
    save_track_links(filename, tracks)

    driver.quit()

executar_todas_funcoes("https://soundcloud.com/pzzs/tracks", "links de teste")