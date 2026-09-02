"""
test_downloader.py — Testes automatizados para o módulo soundcloud_tracks_downloader.

O downloader mantém o fluxo interativo, mas suas regras reutilizáveis ficam em
``core/downloading`` e são exercitadas diretamente aqui.

Testa:
  • Correção de nomes de arquivo (regex patterns)
  • Resolução do caminho do FFmpeg (frozen vs script)
  • Configuração do ydl_opts
  • Construção do postprocessador de metadados
"""

import os

from downloading.metadata import enrich_metadata
from downloading.options import build_ydl_options, rename_downloaded_files


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 1: Correção de nomes de arquivo
# ══════════════════════════════════════════════════════════════════════

class TestCorrigirNomeArquivo:
    """Testa a renomeação real compartilhada pelo CLI e pelo backend."""

    def test_removes_NA_dash(self, tmp_path):
        """Deve remover 'NA - ' do nome."""
        (tmp_path / 'NA - Artist - Title.mp3').write_text('audio')
        renamed = rename_downloaded_files(tmp_path)
        assert renamed == ['Artist - Title.mp3']

    def test_replaces_underscores_with_spaces(self, tmp_path):
        """Deve substituir underscores por espaços."""
        (tmp_path / 'Artist_Name_-_Track_Title.mp3').write_text('audio')
        renamed = rename_downloaded_files(tmp_path)
        assert renamed == ['Artist Name - Track Title.mp3']

    def test_no_change_for_clean_names(self, tmp_path):
        """Nomes limpos não devem ser alterados (exceto underscores)."""
        (tmp_path / 'Artist - Track Title.mp3').write_text('audio')
        assert rename_downloaded_files(tmp_path) == []

    def test_handles_multiple_NA(self, tmp_path):
        """Deve remover múltiplos 'NA - ' se existirem."""
        (tmp_path / 'NA - NA - Title.mp3').write_text('audio')
        assert rename_downloaded_files(tmp_path) == ['Title.mp3']

    def test_actual_rename_in_directory(self, temp_dir):
        """Testa a renomeação real de arquivos no diretório."""
        dirty_name = 'NA - Artist_Name.mp3'
        filepath = os.path.join(temp_dir, dirty_name)
        with open(filepath, 'w') as f:
            f.write('fake audio')

        renamed = rename_downloaded_files(temp_dir)
        assert renamed == ['Artist Name.mp3']
        assert os.listdir(temp_dir) == ['Artist Name.mp3']


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
        config = build_ydl_options('/tmp/downloads', 'mp3')['postprocessors'][0]
        assert config['preferredcodec'] == 'mp3'
        assert config['preferredquality'] == '320'

    def test_flac_format_config(self):
        """Configuração para FLAC não deve ter preferredquality."""
        config = build_ydl_options('/tmp/downloads', 'flac')['postprocessors'][0]
        assert config['preferredcodec'] == 'flac'
        assert 'preferredquality' not in config

    def test_output_template_format(self):
        """Template de output deve conter uploader, artist e title."""
        template = build_ydl_options('/tmp/downloads', 'mp3')['outtmpl']
        assert '%(uploader)s' in template
        assert '%(artist)s' in template
        assert '%(title)s' in template
        assert '%(ext)s' in template

    def test_postprocessors_include_metadata(self):
        """Postprocessors devem incluir FFmpegMetadata e EmbedThumbnail."""
        postprocessors = build_ydl_options('/tmp/downloads', 'mp3')['postprocessors']
        keys = [pp['key'] for pp in postprocessors]
        assert 'FFmpegMetadata' in keys
        assert 'EmbedThumbnail' in keys
        assert 'FFmpegExtractAudio' in keys


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 4: Metadados personalizados
# ══════════════════════════════════════════════════════════════════════

class TestAddCustomMetadata:
    """Testa a normalização real de metadados do postprocessor."""

    def test_artist_fallback_to_uploader(self):
        """Se artist estiver vazio, deve usar uploader."""
        info = {'artist': '', 'uploader': 'Test Artist', 'title': 'Song'}
        result = enrich_metadata(info)
        assert result['artist'] == 'Test Artist'

    def test_artist_uses_artist_if_present(self):
        """Se artist existir, deve usar artist (não uploader)."""
        info = {'artist': 'Real Artist', 'uploader': 'Uploader Name', 'title': 'Song'}
        result = enrich_metadata(info)
        assert result['artist'] == 'Real Artist'

    def test_album_from_playlist_title(self):
        """Se album não existir, deve tentar playlist_title."""
        info = {'title': 'Song', 'playlist_title': 'My Playlist'}
        result = enrich_metadata(info)
        assert result.get('album') == 'My Playlist'

    def test_upload_date_parsing(self):
        """Deve parsear upload_date no formato YYYYMMDD."""
        info = {'title': 'Song', 'upload_date': '20231115'}
        result = enrich_metadata(info)
        assert result['date'] == '2023'

    def test_comment_contains_soundscraper(self):
        """Comentário deve conter referência ao SoundScraper."""
        info = {'title': 'Song', 'webpage_url': 'https://soundcloud.com/test/song'}
        result = enrich_metadata(info)
        assert 'SoundScraper' in result['comment']
        assert 'soundcloud.com/test/song' in result['comment']

    def test_encoder_set_correctly(self):
        """encoder deve identificar a versão atual do SoundScraper."""
        info = {'title': 'Song'}
        result = enrich_metadata(info)
        assert result['encoder'] == 'SoundScraper v3.0'

    def test_empty_info_dict(self):
        """Não deve crashar com info dict vazio."""
        info = {}
        result = enrich_metadata(info)
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
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        assert len(packages) > 0, "requirements.txt está vazio"
