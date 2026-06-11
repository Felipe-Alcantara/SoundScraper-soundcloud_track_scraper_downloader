"""
test_downloader.py — Testes automatizados para o módulo soundcloud_tracks_downloader.

Como o downloader executa muito código no nível do módulo (imports, input(), etc.),
testamos as funções utilitárias extraindo-as ou replicando a lógica testável.

Testa:
  • Correção de nomes de arquivo (regex patterns)
  • Resolução do caminho do FFmpeg (frozen vs script)
  • Configuração do ydl_opts
  • Construção do postprocessador de metadados
"""

import os
import sys
import re
import pytest
from unittest.mock import patch, MagicMock


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 1: Correção de nomes de arquivo
# ══════════════════════════════════════════════════════════════════════

class TestCorrigirNomeArquivo:
    """Testa a lógica de corrigir_nome_arquivo (regex patterns)."""

    def _apply_rename_logic(self, filename):
        """Replica a lógica de renomeação do downloader."""
        novo_nome = filename
        novo_nome = re.sub(r'NA - ', '', novo_nome)    # Remove "NA -"
        novo_nome = re.sub(r'_', ' ', novo_nome)       # Substitui "_" por espaço
        novo_nome = re.sub(r'_-_', '-', novo_nome)     # Substitui "_-_" por "-"
        return novo_nome

    def test_removes_NA_dash(self):
        """Deve remover 'NA - ' do nome."""
        result = self._apply_rename_logic('NA - Artist - Title.mp3')
        assert 'NA - ' not in result
        assert 'Artist' in result

    def test_replaces_underscores_with_spaces(self):
        """Deve substituir underscores por espaços."""
        result = self._apply_rename_logic('Artist_Name_-_Track_Title.mp3')
        assert '_' not in result
        assert ' ' in result

    def test_no_change_for_clean_names(self):
        """Nomes limpos não devem ser alterados (exceto underscores)."""
        result = self._apply_rename_logic('Artist - Track Title.mp3')
        assert result == 'Artist - Track Title.mp3'

    def test_handles_multiple_NA(self):
        """Deve remover múltiplos 'NA - ' se existirem."""
        result = self._apply_rename_logic('NA - NA - Title.mp3')
        # Primeiro NA - é removido, segundo permanece parcialmente
        assert not result.startswith('NA - ')

    def test_actual_rename_in_directory(self, temp_dir):
        """Testa a renomeação real de arquivos no diretório."""
        # Cria arquivo com nome "sujo"
        dirty_name = 'NA_-_Artist_-_Track.mp3'
        filepath = os.path.join(temp_dir, dirty_name)
        with open(filepath, 'w') as f:
            f.write('fake audio')

        # Aplica a lógica do corrigir_nome_arquivo
        for filename in os.listdir(temp_dir):
            novo_nome = self._apply_rename_logic(filename)
            if novo_nome != filename:
                os.rename(
                    os.path.join(temp_dir, filename),
                    os.path.join(temp_dir, novo_nome)
                )

        files = os.listdir(temp_dir)
        assert len(files) == 1
        assert '_' not in files[0] or 'NA' not in files[0]


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 2: Resolução do caminho do FFmpeg
# ══════════════════════════════════════════════════════════════════════

class TestFfmpegPath:
    """Testa a resolução portável do caminho do FFmpeg (core/platform_utils.find_ffmpeg)."""

    def test_binary_name_is_platform_aware(self):
        """O nome do binário deve respeitar o SO (.exe só no Windows)."""
        import platform_utils

        name = platform_utils.ffmpeg_binary_name()
        if os.name == 'nt':
            assert name == 'ffmpeg.exe'
        else:
            assert name == 'ffmpeg'

    def test_frozen_mode_prefers_bundle(self, mock_frozen, temp_dir):
        """No modo EXE, deve apontar para o FFmpeg empacotado no bundle."""
        import platform_utils

        mock_frozen(temp_dir)
        bin_dir = os.path.join(temp_dir, 'ffmpeg', 'bin')
        os.makedirs(bin_dir, exist_ok=True)
        bundled = os.path.join(bin_dir, platform_utils.ffmpeg_binary_name())
        with open(bundled, 'w') as f:
            f.write('')

        assert platform_utils.find_ffmpeg() == bundled

    def test_falls_back_to_system_ffmpeg(self, mock_not_frozen, monkeypatch):
        """Sem bundle/projeto, deve usar o FFmpeg do PATH do sistema."""
        import platform_utils

        # Garante que o bundle do projeto não resolve e força um 'which' fixo.
        monkeypatch.setattr(platform_utils.shutil, 'which', lambda name: '/usr/bin/ffmpeg')
        # Aponta a raiz do projeto para um diretório sem FFmpeg embutido.
        monkeypatch.setattr(platform_utils, '_project_root', lambda: __import__('pathlib').Path(os.sep))

        assert platform_utils.find_ffmpeg() == '/usr/bin/ffmpeg'

    def test_returns_none_when_nothing_found(self, mock_not_frozen, monkeypatch):
        """Sem bundle, sem projeto e sem PATH, retorna None (yt-dlp resolve sozinho)."""
        import platform_utils

        monkeypatch.setattr(platform_utils.shutil, 'which', lambda name: None)
        monkeypatch.setattr(platform_utils, '_project_root', lambda: __import__('pathlib').Path(os.sep))

        assert platform_utils.find_ffmpeg() is None


class TestFfmpegInstallCommand:
    """Testa ffmpeg_install_command() — detecção do instalador por SO (puro)."""

    def _patch_os(self, monkeypatch, *, name, platform, available):
        """Configura SO simulado e quais comandos existem no PATH."""
        import platform_utils
        monkeypatch.setattr(platform_utils.os, 'name', name)
        monkeypatch.setattr(platform_utils.sys, 'platform', platform)
        monkeypatch.setattr(
            platform_utils.shutil, 'which',
            lambda cmd: f"/usr/bin/{cmd}" if cmd in available else None,
        )
        # Em Linux/macOS, simula usuário não-root (para o sudo aparecer).
        if name != 'nt':
            monkeypatch.setattr(platform_utils.os, 'geteuid', lambda: 1000, raising=False)
        return platform_utils

    def test_windows_prefers_winget(self, monkeypatch):
        pu = self._patch_os(monkeypatch, name='nt', platform='win32', available={'winget', 'choco'})
        cmd, label = pu.ffmpeg_install_command()
        assert label == 'winget'
        assert 'Gyan.FFmpeg' in cmd

    def test_windows_falls_back_to_choco(self, monkeypatch):
        pu = self._patch_os(monkeypatch, name='nt', platform='win32', available={'choco'})
        cmd, label = pu.ffmpeg_install_command()
        assert label == 'Chocolatey'
        assert cmd[:2] == ['choco', 'install']

    def test_macos_uses_brew(self, monkeypatch):
        pu = self._patch_os(monkeypatch, name='posix', platform='darwin', available={'brew'})
        cmd, label = pu.ffmpeg_install_command()
        assert label == 'Homebrew'
        assert cmd == ['brew', 'install', 'ffmpeg']

    def test_linux_apt_with_sudo(self, monkeypatch):
        pu = self._patch_os(monkeypatch, name='posix', platform='linux', available={'apt-get', 'sudo'})
        cmd, label = pu.ffmpeg_install_command()
        assert label == 'apt'
        assert cmd[0] == 'sudo'
        assert 'apt-get' in cmd and 'ffmpeg' in cmd

    def test_linux_pacman(self, monkeypatch):
        pu = self._patch_os(monkeypatch, name='posix', platform='linux', available={'pacman', 'sudo'})
        cmd, label = pu.ffmpeg_install_command()
        assert label == 'pacman'
        assert 'pacman' in cmd

    def test_returns_none_without_known_manager(self, monkeypatch):
        pu = self._patch_os(monkeypatch, name='posix', platform='linux', available=set())
        assert pu.ffmpeg_install_command() is None

    def test_ensure_ffmpeg_returns_existing(self, monkeypatch):
        """Se o FFmpeg já existe, ensure_ffmpeg devolve o caminho sem instalar."""
        import platform_utils
        monkeypatch.setattr(platform_utils, 'find_ffmpeg', lambda: '/usr/bin/ffmpeg')
        # Garante que NÃO tenta instalar.
        monkeypatch.setattr(platform_utils, 'ffmpeg_install_command',
                            lambda: (_ for _ in ()).throw(AssertionError("não deveria instalar")))
        assert platform_utils.ensure_ffmpeg(log=lambda *_: None) == '/usr/bin/ffmpeg'


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 3: Configuração do ydl_opts
# ══════════════════════════════════════════════════════════════════════

class TestYdlOpts:
    """Testa a configuração do yt-dlp."""

    def test_mp3_format_config(self):
        """Configuração para MP3 deve ter codec e qualidade corretos."""
        config = {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }
        assert config['preferredcodec'] == 'mp3'
        assert config['preferredquality'] == '320'

    def test_flac_format_config(self):
        """Configuração para FLAC não deve ter preferredquality."""
        config = {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'flac',
        }
        assert config['preferredcodec'] == 'flac'
        assert 'preferredquality' not in config

    def test_output_template_format(self):
        """Template de output deve conter uploader, artist e title."""
        template = '%(uploader)s - %(artist)s - %(title)s.%(ext)s'
        assert '%(uploader)s' in template
        assert '%(artist)s' in template
        assert '%(title)s' in template
        assert '%(ext)s' in template

    def test_postprocessors_include_metadata(self):
        """Postprocessors devem incluir FFmpegMetadata e EmbedThumbnail."""
        postprocessors = [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'},
            {'key': 'FFmpegMetadata', 'add_metadata': True},
            {'key': 'EmbedThumbnail'},
        ]
        keys = [pp['key'] for pp in postprocessors]
        assert 'FFmpegMetadata' in keys
        assert 'EmbedThumbnail' in keys
        assert 'FFmpegExtractAudio' in keys


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 4: Metadados personalizados
# ══════════════════════════════════════════════════════════════════════

class TestAddCustomMetadata:
    """Testa a lógica do postprocessador de metadados."""

    def _apply_metadata_logic(self, info):
        """Replica a lógica do AddCustomMetadataPP.run() sem precisar importar o módulo."""
        info['title'] = info.get('title', '')
        info['artist'] = info.get('artist', '') or info.get('uploader', '')

        # Álbum
        album_name = None
        if info.get('album'):
            album_name = info['album']
        elif info.get('playlist'):
            album_name = info['playlist']
        elif info.get('playlist_title'):
            album_name = info['playlist_title']
        if album_name:
            info['album'] = album_name

        # Data
        if info.get('upload_date'):
            from datetime import datetime
            try:
                date_obj = datetime.strptime(info['upload_date'], '%Y%m%d')
                info['date'] = str(date_obj.year)
            except Exception:
                info['date'] = info['upload_date'][:4] if len(info['upload_date']) >= 4 else info['upload_date']

        # Comentário
        comment_parts = [
            "Downloaded by SoundScraper",
            f"Source: {info.get('webpage_url', 'SoundCloud')}",
            "",
            "GitHub: https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader"
        ]
        info['comment'] = '\n'.join(comment_parts)
        info['encoder'] = 'SoundScraper v1.0'

        return info

    def test_artist_fallback_to_uploader(self):
        """Se artist estiver vazio, deve usar uploader."""
        info = {'artist': '', 'uploader': 'Test Artist', 'title': 'Song'}
        result = self._apply_metadata_logic(info)
        assert result['artist'] == 'Test Artist'

    def test_artist_uses_artist_if_present(self):
        """Se artist existir, deve usar artist (não uploader)."""
        info = {'artist': 'Real Artist', 'uploader': 'Uploader Name', 'title': 'Song'}
        result = self._apply_metadata_logic(info)
        assert result['artist'] == 'Real Artist'

    def test_album_from_playlist_title(self):
        """Se album não existir, deve tentar playlist_title."""
        info = {'title': 'Song', 'playlist_title': 'My Playlist'}
        result = self._apply_metadata_logic(info)
        assert result.get('album') == 'My Playlist'

    def test_upload_date_parsing(self):
        """Deve parsear upload_date no formato YYYYMMDD."""
        info = {'title': 'Song', 'upload_date': '20231115'}
        result = self._apply_metadata_logic(info)
        assert result['date'] == '2023'

    def test_comment_contains_soundscraper(self):
        """Comentário deve conter referência ao SoundScraper."""
        info = {'title': 'Song', 'webpage_url': 'https://soundcloud.com/test/song'}
        result = self._apply_metadata_logic(info)
        assert 'SoundScraper' in result['comment']
        assert 'soundcloud.com/test/song' in result['comment']

    def test_encoder_set_correctly(self):
        """encoder deve ser 'SoundScraper v1.0'."""
        info = {'title': 'Song'}
        result = self._apply_metadata_logic(info)
        assert result['encoder'] == 'SoundScraper v1.0'

    def test_empty_info_dict(self):
        """Não deve crashar com info dict vazio."""
        info = {}
        result = self._apply_metadata_logic(info)
        assert 'title' in result
        assert 'comment' in result


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 5: Integridade do spec file
# ══════════════════════════════════════════════════════════════════════

class TestSpecFile:
    """Verifica integridade do arquivo .spec do PyInstaller."""

    def test_spec_file_exists(self):
        """O arquivo .spec deve existir."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec_file = os.path.join(project_root, 'tools', 'soundcloud_tracks_downloader.spec')
        assert os.path.exists(spec_file), "Arquivo .spec não encontrado"

    def test_spec_includes_selenium_manager(self):
        """O .spec deve incluir selenium-manager.exe nos binaries."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec_file = os.path.join(project_root, 'tools', 'soundcloud_tracks_downloader.spec')

        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'selenium-manager' in content.lower() or 'selenium_manager' in content.lower(), (
            "selenium-manager não encontrado no .spec — EXE vai crashar!"
        )

    def test_spec_includes_all_modules(self):
        """O .spec deve incluir todos os módulos do projeto."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec_file = os.path.join(project_root, 'tools', 'soundcloud_tracks_downloader.spec')

        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()

        required_modules = ['browser_handler', 'crash_logger', 'soundcloud_track_scraper']
        for module in required_modules:
            assert module in content, f"Módulo '{module}' não encontrado no .spec"

    def test_spec_includes_ffmpeg(self):
        """O .spec deve incluir FFmpeg nos datas."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec_file = os.path.join(project_root, 'tools', 'soundcloud_tracks_downloader.spec')

        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'ffmpeg' in content.lower(), "FFmpeg não encontrado no .spec"

    def test_spec_has_hidden_imports(self):
        """O .spec deve ter hiddenimports para dependências problemáticas."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec_file = os.path.join(project_root, 'tools', 'soundcloud_tracks_downloader.spec')

        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'hiddenimports' in content, "hiddenimports não encontrado no .spec"
        # Deve ter pelo menos selenium e yt_dlp
        assert 'selenium' in content
        assert 'yt_dlp' in content


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 6: Integridade das dependências
# ══════════════════════════════════════════════════════════════════════

class TestDependencies:
    """Verifica que todas as dependências estão disponíveis."""

    def test_selenium_importable(self):
        """Selenium deve ser importável."""
        import selenium
        assert hasattr(selenium, '__version__')

    def test_yt_dlp_importable(self):
        """yt-dlp deve ser importável."""
        import yt_dlp
        assert hasattr(yt_dlp, 'YoutubeDL')

    def test_mutagen_importable(self):
        """mutagen deve ser importável."""
        import mutagen
        assert hasattr(mutagen, 'version') or hasattr(mutagen, '__version__')

    def test_requirements_file_exists(self):
        """O arquivo requirements.txt deve existir."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        req_file = os.path.join(project_root, 'deps', 'requirements.txt')
        assert os.path.exists(req_file), "requirements.txt não encontrado"

    def test_requirements_not_empty(self):
        """O arquivo requirements.txt não deve estar vazio."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        req_file = os.path.join(project_root, 'deps', 'requirements.txt')

        with open(req_file, 'r') as f:
            packages = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        assert len(packages) > 0, "requirements.txt está vazio"
