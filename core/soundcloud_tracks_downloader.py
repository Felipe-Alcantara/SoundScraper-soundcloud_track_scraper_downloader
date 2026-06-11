import os
import sys
import subprocess
import re
from typing import Any, cast

# Inicializa o sistema de logging ANTES de tudo
# Isso garante que qualquer crash será capturado e salvo em arquivo
from crash_logger import inicializar_logger
from platform_utils import ensure_ffmpeg, find_ffmpeg, open_folder
session_log = inicializar_logger()

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
        # Remove especificações de versão para checagem
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
        resposta = input("\n💡 Deseja instalar automaticamente agora? (S/N, padrão=S): ").strip().upper()
        
        # Se o usuário não digitou nada, usar 'S' como padrão
        if not resposta:
            resposta = 'S'
            print("")
            print("ℹ️  Usando opção padrão: SIM")
        
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
            continuar = input("💭 Deseja tentar continuar mesmo assim? (S/N, padrão=N): ").strip().upper()
            
            # Se o usuário não digitou nada, usar 'N' como padrão (não continuar)
            if not continuar:
                continuar = 'N'
                print("")
                print("ℹ️  Usando opção padrão: NÃO")
            
            print("")
            return continuar == 'S'
    else:
        print("")
        print("✅  Perfeito! Todas as dependências estão prontas!")
        print("")
        return True

# Banner de boas-vindas
print("")
print("╔" + "═" * 68 + "╗")
print("║" + " " * 68 + "║")
print("║" + "  🎵  SOUNDSCRAPER - SoundCloud Downloader  🎶".center(68) + "║")
print("║" + " " * 68 + "║")
print("╚" + "═" * 68 + "╝")
print("")

# Verifica as dependências antes de continuar
if not check_and_install_requirements():
    print("")
    print("═" * 70)
    print("❌  Programa encerrado devido a dependências faltantes.")
    print("═" * 70)
    print("")
    sys.exit(1)

# Importa as dependências após verificação
import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor
from soundcloud_track_scraper import soundcloud_track_scraper

# Classe personalizada para adicionar metadados ao info_dict
class AddCustomMetadataPP(PostProcessor):
    def run(self, information):
        info = cast(dict[str, Any], information)
        print("")
        print("📝 Adicionando metadados personalizados...")
        
        # ===== METADADOS PRINCIPAIS =====
        info['title'] = info.get('title', '')
        info['artist'] = info.get('artist', '') or info.get('uploader', '')
        
        # ===== METADADOS DO SOUNDCLOUD =====
        # Álbum / Playlist (tenta múltiplas fontes)
        album_name = None
        if info.get('album'):
            album_name = info['album']
        elif info.get('playlist'):
            album_name = info['playlist']
        elif info.get('playlist_title'):
            album_name = info['playlist_title']
        
        if album_name:
            info['album'] = album_name
        
        # Gênero
        if info.get('genre'):
            info['genre'] = info['genre']
        
        # Data de upload e Ano
        if info.get('upload_date'):
            from datetime import datetime
            try:
                # upload_date vem no formato YYYYMMDD (ex: 20181103)
                date_obj = datetime.strptime(info['upload_date'], '%Y%m%d')
                
                # Define o ano separadamente
                info['date'] = str(date_obj.year)  # Ano para o campo 'date' (usado por players)
                
                # Adiciona também timestamp completo se desejar
                info['timestamp'] = date_obj.strftime('%Y-%m-%d')
                
            except Exception as e:
                # Se falhar, tenta usar direto
                info['date'] = info['upload_date'][:4] if len(info['upload_date']) >= 4 else info['upload_date']
        
        # Tenta extrair ano de outras fontes se não tiver upload_date
        if not info.get('date'):
            if info.get('release_date'):
                info['date'] = info['release_date'][:4] if len(str(info['release_date'])) >= 4 else info['release_date']
            elif info.get('release_year'):
                info['date'] = str(info['release_year'])
        
        # Descrição (pode conter letra, BPM, feat, etc)
        if info.get('description'):
            info['description'] = info['description']
            # Também adiciona na seção de comentários se for curta
            if len(info['description']) < 500:
                info['lyrics'] = info['description']
        
        # Tags do SoundCloud
        if info.get('tags'):
            tags = info['tags']
            if isinstance(tags, list):
                info['keywords'] = ', '.join(tags)
            else:
                info['keywords'] = str(tags)
        
        # BPM (se disponível nos metadados do SoundCloud)
        if info.get('bpm'):
            info['bpm'] = str(info['bpm'])
        
        # Licença
        if info.get('license'):
            info['copyright'] = info['license']
        
        # Label/Publisher
        if info.get('publisher'):
            info['publisher'] = info['publisher']
        elif info.get('label'):
            info['publisher'] = info['label']
        
        # Track number / Position na playlist
        if info.get('track_number'):
            info['track'] = str(info['track_number'])
        elif info.get('playlist_index'):
            info['track'] = str(info['playlist_index'])
        
        # Duration
        if info.get('duration'):
            info['length'] = str(int(info['duration'] * 1000))  # em milliseconds
        
        # Composer (se houver informação de featured artists)
        if info.get('composer'):
            info['composer'] = info['composer']
        
        # ===== METADADOS DO SOUNDSCRAPER =====
        # Comentário personalizado com URL original
        comment_parts = [
            "Downloaded by SoundScraper",
            f"Source: {info.get('webpage_url', 'SoundCloud')}",
            "",
            "GitHub: https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader"
        ]
        info['comment'] = '\n'.join(comment_parts)
        
        # Website e Encoder
        info['website'] = 'https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader'
        info['encoder'] = 'SoundScraper v1.0'
        
        # ===== DEBUG: Mostra metadados disponíveis =====
        print("\n" + "="*70)
        print("🔍 DEBUG - METADADOS CAPTURADOS DO SOUNDCLOUD:")
        print("="*70)
        
        # Metadados mais importantes para debug
        debug_keys = [
            'title', 'artist', 'uploader', 'album', 'playlist', 'playlist_title',
            'genre', 'upload_date', 'release_date', 'release_year', 'date', 'timestamp',
            'description', 'tags', 'bpm', 'license', 'track_number', 'playlist_index',
            'duration', 'webpage_url'
        ]
        
        for key in debug_keys:
            if info.get(key):
                value = info[key]
                # Trunca descrições longas
                if key == 'description' and len(str(value)) > 100:
                    value = str(value)[:100] + "..."
                print(f"  📌 {key}: {value}")
        
        print("="*70 + "\n")

        return [], information


def _selecionar_pasta():
    """Abre diálogo nativo de seleção de pasta. Fallback para input de texto."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal
        root.attributes('-topmost', True)  # Garante que o diálogo fique por cima
        pasta = filedialog.askdirectory(title="Selecione a pasta para salvar as músicas")
        root.destroy()
        if pasta:
            return pasta
        # Se o usuário cancelou o diálogo, cai para o input manual
        print("⚠️  Nenhuma pasta selecionada no diálogo.")
        print("")
    except Exception:
        print("⚠️  Não foi possível abrir o seletor de pastas.")
        print("")

    # Fallback: input manual
    print("💡 Digite o caminho da pasta ou deixe em branco para 'SoundCloud_Downloads'")
    output_folder = input("📂 Caminho da pasta: ").strip()
    return output_folder if output_folder else ""


def main():
    """Loop principal do programa."""
    while True:
        filename = soundcloud_track_scraper()

        # Caminho da pasta onde os arquivos serão salvos
        print("═" * 70)
        print("📁  CONFIGURAÇÃO DA PASTA DE DESTINO")
        print("═" * 70)
        print("")
        print("📂 Selecione a pasta onde as músicas serão salvas...")
        print("")
        output_folder = _selecionar_pasta()

        # Se o usuário não selecionou nada, usar valor padrão
        if not output_folder:
            output_folder = "SoundCloud_Downloads"
            print(f"ℹ️  Usando pasta padrão: {output_folder}")
            print("")

        # Criar a pasta se ela não existir
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"✅ Pasta criada com sucesso: {output_folder}")
            print("")
        else:
            print(f"📂 Usando pasta existente: {output_folder}")
            print("")

        # Solicitar formato de áudio
        audio_format = _solicitar_formato()

        # Ler os URLs do arquivo
        with open(filename, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
            print(" ")
            print(f"Total de URLs carregados: {len(urls)}")
            print(" ")

        # Apaga o arquivo TXT temporário de links
        try:
            os.remove(filename)
            print(f"🗑️  Arquivo temporário removido: {filename}")
            print("")
        except Exception:
            pass

        # Definir o postprocessador FFmpegExtractAudio com base no formato escolhido
        ffmpeg_extract_audio = {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
        }

        # Se o formato for MP3, adicionar 'preferredquality'
        if audio_format == 'mp3':
            ffmpeg_extract_audio['preferredquality'] = '320'

        # Garante o FFmpeg (bundle EXE → projeto → PATH; se faltar, oferece instalar).
        # Funciona em Windows, Linux e macOS.
        ffmpeg_path = ensure_ffmpeg()
        if ffmpeg_path:
            print(f"🎥  FFmpeg: {ffmpeg_path}")
        else:
            print("⚠️  FFmpeg indisponível; o yt-dlp tentará o do sistema (o download pode falhar).")
        print("")

        # Opções de download
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_folder, '%(uploader)s - %(artist)s - %(title)s.%(ext)s'),
            'restrictfilenames': True,
            'postprocessors': [
                ffmpeg_extract_audio,
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                },
                {
                    'key': 'EmbedThumbnail',
                },
            ],
            'writethumbnail': True,
            'prefer_ffmpeg': True,
        }
        # Só fixa o ffmpeg_location quando temos um caminho; senão deixa o yt-dlp resolver pelo PATH.
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path

        # Banner de início do download
        print("═" * 70)
        print("🎵  INICIANDO DOWNLOAD DAS MÚSICAS")
        print("═" * 70)
        print("")
        print(f"📊  Total de músicas na fila: {len(urls)}")
        print(f"📂  Pasta de destino: {output_folder}")
        print(f"🎼  Formato: {audio_format.upper()}")
        print("")
        print("─" * 70)
        print("")

        # Processar cada URL
        total_urls = len(urls)
        sucessos = 0
        erros = 0

        for index, url in enumerate(urls, start=1):
            try:
                _download_url(url, index, total_urls, ydl_opts)
                _corrigir_nome_arquivo(output_folder)
                sucessos += 1
            except Exception as e:
                print("")
                print(f"❌  ERRO CRÍTICO ao processar música {index}/{total_urls}")
                print(f"    {e}")
                print("")
                erros += 1

        # Relatório final
        print("")
        print("═" * 70)
        print("🎉  PROCESSO CONCLUÍDO!")
        print("═" * 70)
        print("")
        print(f"✅  Sucessos: {sucessos} música(s)")
        if erros > 0:
            print(f"❌  Erros: {erros} música(s)")
        print(f"📂  Pasta: {output_folder}")
        print("")
        print("═" * 70)
        print("")

        # Abre a pasta de destino no gerenciador de arquivos (cross-platform)
        abs_folder = os.path.abspath(output_folder)
        if open_folder(abs_folder):
            print(f"📂 Pasta aberta: {abs_folder}")
            print("")

        # Perguntar se quer baixar mais
        print("─" * 70)
        repetir = input("🔄 Deseja baixar mais músicas? (S/N, padrão=N): ").strip().upper()
        if not repetir:
            repetir = 'N'
        if repetir != 'S':
            print("")
            print("Obrigado por usar o SoundScraper! 🎵")
            print("")
            break
        print("")
        print("═" * 70)
        print("🔁  REINICIANDO...")
        print("═" * 70)
        print("")


def _solicitar_formato():
    """Solicita ao usuário o formato de áudio desejado."""
    print("═" * 70)
    print("🎵  ESCOLHA O FORMATO DE ÁUDIO")
    print("═" * 70)
    print("")
    print("  [1] 🎼  FLAC")
    print("      • Qualidade máxima (sem perdas)")
    print("      • Arquivos maiores (~30-40 MB por música)")
    print("      • Ideal para audiófilos e arquivamento")
    print("")
    print("  [2] 🎧  MP3")
    print("      • Alta qualidade (320kbps)")
    print("      • Arquivos menores (~8-12 MB por música)")
    print("      • Compatível com qualquer dispositivo")
    print("")
    print("─" * 70)
    formato_escolhido = input("\n💿 Digite sua escolha (1 ou 2, padrão=2): ").strip()

    if not formato_escolhido:
        formato_escolhido = '2'
        print("")
        print("ℹ️  Usando formato padrão: MP3 (320kbps)")

    if formato_escolhido == '1':
        audio_format = 'flac'
        print("")
        print("✅ Formato selecionado: FLAC (Lossless)")
    elif formato_escolhido == '2':
        audio_format = 'mp3'
        print("")
        print("✅ Formato selecionado: MP3 (320kbps)")
    else:
        print("")
        print("⚠️  Opção inválida! Usando MP3 como padrão...")
        audio_format = 'mp3'

    print("")
    return audio_format


def _corrigir_nome_arquivo(output_folder):
    """Corrige nomes de arquivos, removendo 'NA' e substituindo underscores."""
    for fname in os.listdir(output_folder):
        novo_nome = fname
        novo_nome = re.sub(r'NA - ', '', novo_nome)
        novo_nome = re.sub(r'_', ' ', novo_nome)
        novo_nome = re.sub(r'_-_', '-', novo_nome)

        if novo_nome != fname:
            try:
                os.rename(os.path.join(output_folder, fname), os.path.join(output_folder, novo_nome))
                print(f"   ✏️  Arquivo renomeado: {novo_nome}")
            except FileNotFoundError as e:
                print(f"   ⚠️  Erro ao renomear: {e}")


def _download_url(url, index, total, ydl_opts):
    """Baixa um único URL usando yt-dlp."""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.add_post_processor(AddCustomMetadataPP(), when='pre_process')
        try:
            print("")
            print("─" * 70)
            print(f"⬇️  BAIXANDO [{index}/{total}]")
            print("─" * 70)
            ydl.download([url])
            print("")
            print(f"✅  CONCLUÍDO [{index}/{total}]")
            print("")
        except Exception as e:
            print("")
            print(f"❌  ERRO ao baixar música {index}/{total}")
            print(f"    URL: {url}")
            print(f"    Motivo: {e}")
            print("")


# ══════════════════════════════════════════════════════════════
#  Ponto de entrada
# ══════════════════════════════════════════════════════════════
# Guarda __main__: roda main() quando executado direto (terminal) ou empacotado
# pelo PyInstaller (que roda o script como __main__), mas permite importar o
# módulo (run_cli.py, testes) sem disparar o fluxo interativo.
if __name__ == '__main__':
    main()
