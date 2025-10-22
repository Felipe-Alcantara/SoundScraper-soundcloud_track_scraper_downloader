import os
import sys
import subprocess
import re

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
    print("🔍 Verificando dependências...")
    print("")
    
    # Verifica cada pacote
    for package in required_packages:
        # Remove especificações de versão para checagem
        package_name = package.split('==')[0].split('>=')[0].split('<=')[0].strip()
        
        try:
            __import__(package_name.replace('-', '_'))
            print(f"✅ {package_name} - instalado")
        except ImportError:
            print(f"❌ {package_name} - NÃO instalado")
            missing_packages.append(package)
    
    print("")
    
    # Se houver pacotes faltando, oferece instalação
    if missing_packages:
        print(f"⚠️  {len(missing_packages)} dependência(s) faltando!")
        print("")
        print("Pacotes faltando:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("")
        
        resposta = input("Deseja instalar as dependências faltantes agora? (S/N): ").strip().upper()
        print("")
        
        if resposta == 'S':
            print("📦 Instalando dependências...")
            print("")
            
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
                print("")
                print("✅ Todas as dependências foram instaladas com sucesso!")
                print("")
                return True
            except subprocess.CalledProcessError as e:
                print("")
                print(f"❌ Erro ao instalar dependências: {e}")
                print("")
                return False
        else:
            print("⚠️  O programa pode não funcionar corretamente sem as dependências.")
            print("")
            continuar = input("Deseja continuar mesmo assim? (S/N): ").strip().upper()
            print("")
            return continuar == 'S'
    else:
        print("✅ Todas as dependências estão instaladas!")
        print("")
        return True

# Verifica as dependências antes de continuar
if not check_and_install_requirements():
    print("❌ Programa encerrado.")
    sys.exit(1)

# Importa as dependências após verificação
import yt_dlp
from soundcloud_track_scraper import soundcloud_track_scraper

# Classe personalizada para adicionar metadados ao info_dict
class AddCustomMetadataPP(yt_dlp.postprocessor.PostProcessor):
    def run(self, info):
        print(" ")
        print("Adicionando metadados personalizados ao info_dict")
        print(" ")
        # Modifica o info_dict com os metadados desejados
        info['title'] = info.get('title', '')
        info['artist'] = info.get('artist', '') or info.get('uploader', '')  # Usa artist se disponível, senão usa uploader
        info['album'] = info.get('album', '')  # Se disponível
        info['genre'] = info.get('genre', '')  # Se disponível
        info['date'] = info.get('upload_date', '')  # Formato YYYYMMDD
        info['comment'] = 'Baixado com SOUNDSCRAPER'

        # Se quiser formatar a data para outro formato (ex: DD/MM/YYYY)
        if info['date']:
            from datetime import datetime
            info['date'] = datetime.strptime(info['date'], '%Y%m%d').strftime('%d/%m/%Y')

        return [], info

filename = soundcloud_track_scraper()

# Caminho da pasta onde os arquivos serão salvos
print(" ")
output_folder = input("Digite o nome da pasta onde os arquivos serão salvos: ")
print(" ")

# Criar a pasta se ela não existir
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(" ")
    print(f"Pasta criada: {output_folder}")
    print(" ")

# Função para solicitar o formato
def solicitar_formato():
    # Solicitar ao usuário o formato desejado
    print(" ")
    print("Escolha o formato de áudio:")
    print(" ")
    print("1 - FLAC (Sem perdas mas com menor compatibilidade)")
    print(" ")
    print("2 - MP3 (Melhor compatibilidade e menor tamanho de arquivo)")
    print(" ")
    formato_escolhido = input("Digite 1 para FLAC ou 2 para MP3: ")
    print(" ")

    if formato_escolhido == '1':
        audio_format = 'flac'
    elif formato_escolhido == '2':
        audio_format = 'mp3'
    else:
        print("")
        print("Opção inválida. Usando MP3 como padrão...")
        print("")
        audio_format = 'mp3'

    print("")
    print(f"Formato escolhido: {audio_format}")
    print("")
    return audio_format

# Chamar a função e obter o formato escolhido
audio_format = solicitar_formato()

# Ler os URLs do arquivo
with open(filename, 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]
    print(" ")
    print(f"Total de URLs carregados: {len(urls)}")
    print(" ")

# Definir o postprocessador FFmpegExtractAudio com base no formato escolhido
ffmpeg_extract_audio = {
    'key': 'FFmpegExtractAudio',
    'preferredcodec': audio_format,
}

# Se o formato for MP3, adicionar 'preferredquality'
if audio_format == 'mp3':
    ffmpeg_extract_audio['preferredquality'] = '320'

# Verifica se o script está rodando em um ambiente "congelado" (após ser convertido para exe)
if getattr(sys, 'frozen', False):
    # Obtém o diretório temporário do executável
    bundle_dir = sys._MEIPASS

    # Define o caminho para o executável do FFmpeg dentro do diretório do bundle
    ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg', 'bin', 'ffmpeg.exe')
else:
    # Usa o ffmpeg da pasta do repositório (Dependencias/ffmpeg/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    ffmpeg_path = os.path.join(project_root, 'Dependencias', 'ffmpeg', 'ffmpeg-8.0-essentials_build', 'bin', 'ffmpeg.exe')

# Opções de download
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(output_folder, '%(uploader)s - %(artist)s - %(title)s.%(ext)s'),
    'restrictfilenames': True,
    'postprocessors': [
        ffmpeg_extract_audio,
        {
            # Incorpora metadados usando FFmpeg
            'key': 'FFmpegMetadata',
            'add_metadata': True,
        },
        {
            # Embute a imagem da capa no arquivo de áudio
            'key': 'EmbedThumbnail',
        },
    ],
    'writethumbnail': True,  # Baixa a miniatura para embutir
    'prefer_ffmpeg': True,
    'ffmpeg_location': ffmpeg_path,  # Caminho completo para o ffmpeg.exe
}

# Função para corrigir o nome dos arquivos, removendo "NA" e corrigindo formatação
def corrigir_nome_arquivo(output_folder):
    for filename in os.listdir(output_folder):
        # Cria uma nova variável para armazenar o nome atualizado
        novo_nome = filename

        # Substituir múltiplos padrões usando expressões regulares
        novo_nome = re.sub(r'NA - ', '', novo_nome)  # Remove "NA -"
        novo_nome = re.sub(r'_', ' ', novo_nome)     # Substitui "_" por espaço
        novo_nome = re.sub(r'_-_', '-', novo_nome)   # Substitui "_-_" por "-"

        # Se o nome foi alterado, renomeia o arquivo
        if novo_nome != filename:
            try:
                os.rename(os.path.join(output_folder, filename), os.path.join(output_folder, novo_nome))
                print(" ")
                print(f"Nome atualizado: {novo_nome}")
                print(" ")
            except FileNotFoundError as e:
                print(" ")
                print(f"Erro ao renomear {filename}: {e}")
                print(" ")

# Função para baixar um único URL
def download_url(url, index, total):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Adiciona o postprocessor personalizado para modificar os metadados
        ydl.add_post_processor(AddCustomMetadataPP(), when='pre_process')

        # Baixa e processa o vídeo
        try:
            print(" ")
            print(f"Baixando link {index}/{total}")
            print(" ")
            ydl.download([url])
            print(" ")
            print(f"Baixado link {index}/{total}")
            print(" ")
        except Exception as e:
            print(" ")
            print(f"Erro ao baixar {url}: {e}")
            print(" ")

# Processar cada URL
total_urls = len(urls)
for index, url in enumerate(urls, start=1):
    try:
        download_url(url, index, total_urls)
        # Corrigir os nomes dos arquivos baixados
        corrigir_nome_arquivo(output_folder)
    except Exception as e:
        print(" ")
        print(f"Erro ao processar {url}: {e}")
        print(" ")

print(" ")
print("Processo concluído!")
print(" ")