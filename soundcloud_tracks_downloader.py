import yt_dlp
import os

# Caminho da pasta onde os arquivos serão salvos
output_folder = 'musicas'

# Criar a pasta se ela não existir
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Ler os URLs do arquivo
with open('links_musicas.txt', 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

# Opções de download
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(output_folder, '%(title)s.mp3'),  # Salvar na pasta desejada
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',  # Formato de áudio desejado
        'preferredquality': '192',  # Qualidade do áudio
    }],
    'postprocessor_args': [
        '-ar', '44100'  # Opcional: definir taxa de amostragem
    ],
    'prefer_ffmpeg': True,  # Certificar-se de usar o FFmpeg
    # 'ffmpeg_location': 'C:/ffmpeg/bin/ffmpeg.exe',  # Atualize o caminho se necessário
}

# Função para baixar um único URL
def download_url(url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Processar cada URL
for url in urls:
    try:
        print(f"Baixando: {url}")
        download_url(url)
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")