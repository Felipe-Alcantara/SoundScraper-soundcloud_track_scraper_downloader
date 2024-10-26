import yt_dlp
import os
from soundcloud_track_scraper import soundcloud_track_scraper

filename = soundcloud_track_scraper()

# Caminho da pasta onde os arquivos serão salvos
output_folder = input("Digite o nome da pasta onde os arquivos serão salvos: ")

# Criar a pasta se ela não existir
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Função para solicitar o formato
def solicitar_formato():
    # Solicitar ao usuário o formato desejado
    print("Escolha o formato de áudio:")
    print("1 - WAV (melhor qualidade)")
    print("2 - MP3 (melhor compatibilidade e menor tamanho de arquivo)")
    formato_escolhido = input("Digite 1 para WAV ou 2 para MP3: ")

    if formato_escolhido == '1':
        audio_format = 'wav'
    elif formato_escolhido == '2':
        audio_format = 'mp3'
    else:
        print("Opção inválida. Usando MP3 como padrão.")
        audio_format = 'mp3'

    return audio_format

# Chamar a função e obter o formato escolhido
audio_format = solicitar_formato()

# Ler os URLs do arquivo
with open(filename, 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

# Opções de download
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(output_folder, '%(uploader)s - %(artist)s - %(title)s.%(ext)s'),
    'restrictfilenames': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': audio_format,
    }],
    'prefer_ffmpeg': True,
    'ffmpeg_location': r'C:\ffmpeg\ffmpeg-7.1\bin\ffmpeg.exe',  # Caminho completo para o ffmpeg.exe
}

# Função para corrigir o nome dos arquivos, removendo "NA" e corrigindo formatação
def corrigir_nome_arquivo(output_folder):
    for filename in os.listdir(output_folder):
        # Cria uma nova variável para armazenar o nome atualizado
        novo_nome = filename
        
        # Verifica se o arquivo contém "NA" no nome e substitui por uma string vazia
        if "NA -" in novo_nome:
            novo_nome = novo_nome.replace("NA - ", "")
        
        # Substitui "_" por espaço
        if "_" in novo_nome:
            novo_nome = novo_nome.replace("_", " ")
        
        # Substitui "_-_" por "-"
        if "_-_" in novo_nome:
            novo_nome = novo_nome.replace("_-_", "-")
        
        # Se o nome foi alterado, renomeia o arquivo
        if novo_nome != filename:
            try:
                os.rename(os.path.join(output_folder, filename), os.path.join(output_folder, novo_nome))
                print(f"Nome atualizado: {novo_nome}")
            except FileNotFoundError as e:
                print(f"Erro ao renomear {filename}: {e}")

# Função para baixar um único URL
def download_url(url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Processar cada URL
for url in urls:
    try:
        print(f"Baixando: {url}")
        download_url(url)
        # Corrigir os nomes dos arquivos baixados
        corrigir_nome_arquivo(output_folder)

    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")