import yt_dlp

# URL do arquivo que você deseja baixar
url = ""

# Configurações do yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',  # Seleciona a melhor faixa de áudio disponível
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',  # Postprocessador para extrair o áudio
        'preferredcodec': 'wav',      # Converte para WAV (formato sem compressão)
        # Se preferir FLAC (lossless com compressão sem perdas), use:
        # 'preferredcodec': 'flac',
    }],
    'outtmpl': '%(title)s.%(ext)s',  # Nome do arquivo de saída baseado no título do vídeo
}

# Execução do download
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])