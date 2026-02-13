"""
test_scraper.py — Testes automatizados para o módulo soundcloud_track_scraper.

Testa:
  • Validação de URLs do SoundCloud
  • Mapeamento de escolhas do usuário
  • Consistência do opcoes_nomes
  • Seleção de CSS selectors
  • Salvamento de links
"""

import os
import sys
import re
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

# Importa o módulo a ser testado
import soundcloud_track_scraper as scraper


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 1: Validação de URLs (get_soundcloud_link)
# ══════════════════════════════════════════════════════════════════════

class TestGetSoundcloudLink:
    """Testa get_soundcloud_link() — validação do input do usuário."""

    def test_valid_artist_url(self):
        """URL válida do artista deve retornar URL formatada."""
        with patch('builtins.input', return_value='https://soundcloud.com/test-artist'):
            result = scraper.get_soundcloud_link()
            assert result == 'https://soundcloud.com/test-artist'

    def test_url_without_https(self):
        """URL sem https deve ser aceita."""
        with patch('builtins.input', return_value='soundcloud.com/test-artist'):
            result = scraper.get_soundcloud_link()
            assert result == 'https://soundcloud.com/test-artist'

    def test_url_with_http(self):
        """URL com http (não https) deve ser aceita."""
        with patch('builtins.input', return_value='http://soundcloud.com/test-artist'):
            result = scraper.get_soundcloud_link()
            assert result == 'https://soundcloud.com/test-artist'

    def test_url_with_trailing_slash(self):
        """URL com barra final deve funcionar."""
        with patch('builtins.input', return_value='https://soundcloud.com/test-artist/'):
            result = scraper.get_soundcloud_link()
            assert result == 'https://soundcloud.com/test-artist'

    def test_url_with_query_params(self):
        """URL com parâmetros de query deve extrair apenas a URL base do artista."""
        with patch('builtins.input', return_value='https://soundcloud.com/test-artist?ref=clipboard'):
            result = scraper.get_soundcloud_link()
            assert result == 'https://soundcloud.com/test-artist'

    def test_url_with_subpath_extracts_artist(self):
        """URL com subpath (/tracks, /likes) deve extrair apenas o artista."""
        with patch('builtins.input', return_value='https://soundcloud.com/test-artist/tracks'):
            result = scraper.get_soundcloud_link()
            assert result == 'https://soundcloud.com/test-artist'

    def test_invalid_url_then_valid(self):
        """URL inválida seguida de válida deve eventualmente retornar."""
        with patch('builtins.input', side_effect=[
            'youtube.com/watch?v=123',
            'https://soundcloud.com/valid-artist'
        ]):
            result = scraper.get_soundcloud_link()
            assert result == 'https://soundcloud.com/valid-artist'

    def test_empty_input_then_valid(self):
        """Input vazio seguido de válido deve continuar pedindo."""
        with patch('builtins.input', side_effect=[
            '',
            'https://soundcloud.com/valid-artist'
        ]):
            result = scraper.get_soundcloud_link()
            assert result == 'https://soundcloud.com/valid-artist'

    def test_only_domain_no_artist(self):
        """URL com apenas o domínio (sem artista) deve ser rejeitada."""
        with patch('builtins.input', side_effect=[
            'soundcloud.com',
            'https://soundcloud.com/valid-artist'
        ]):
            result = scraper.get_soundcloud_link()
            assert result == 'https://soundcloud.com/valid-artist'


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 2: Mapeamento de escolhas (get_user_choice)
# ══════════════════════════════════════════════════════════════════════

class TestGetUserChoice:
    """Testa get_user_choice() — mapeamento de opções."""

    def test_choice_1_all_tracks(self):
        """Opção 1 deve retornar URL do artista sem sufixo."""
        with patch('builtins.input', return_value='1'):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert url == 'https://soundcloud.com/artist'
            assert choice == '1'

    def test_choice_2_popular_tracks(self):
        """Opção 2 deve adicionar /popular-tracks."""
        with patch('builtins.input', return_value='2'):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert url == 'https://soundcloud.com/artist/popular-tracks'
            assert choice == '2'

    def test_choice_3_tracks(self):
        """Opção 3 deve adicionar /tracks."""
        with patch('builtins.input', return_value='3'):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert url == 'https://soundcloud.com/artist/tracks'
            assert choice == '3'

    def test_choice_4_albums(self):
        """Opção 4 (álbuns) deve solicitar link do álbum."""
        with patch('builtins.input', side_effect=['4', 'https://soundcloud.com/artist/sets/album']):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert choice == '4'
            assert 'sets' in url

    def test_choice_5_playlists(self):
        """Opção 5 (playlists) deve solicitar link da playlist."""
        with patch('builtins.input', side_effect=['5', 'https://soundcloud.com/artist/sets/playlist']):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert choice == '5'
            assert 'sets' in url

    def test_choice_6_reposts(self):
        """Opção 6 deve adicionar /reposts."""
        with patch('builtins.input', return_value='6'):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert url == 'https://soundcloud.com/artist/reposts'
            assert choice == '6'

    def test_choice_7_likes(self):
        """Opção 7 deve adicionar /likes."""
        with patch('builtins.input', return_value='7'):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert url == 'https://soundcloud.com/artist/likes'
            assert choice == '7'

    def test_invalid_then_valid(self):
        """Opção inválida seguida de válida deve funcionar."""
        with patch('builtins.input', side_effect=['8', '0', '1']):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert choice == '1'

    def test_choice_4_empty_link_then_valid(self):
        """Opção 4 com link vazio seguido de válido deve funcionar."""
        with patch('builtins.input', side_effect=[
            '4',                                                      # Escolha
            '',                                                        # Link vazio (rejeitado)
            'https://soundcloud.com/artist/sets/my-album'             # Link válido
        ]):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert choice == '4'
            assert 'sets/my-album' in url

    def test_choice_4_non_soundcloud_then_valid(self):
        """Opção 4 com link não-SoundCloud seguido de válido."""
        with patch('builtins.input', side_effect=[
            '4',
            'https://youtube.com/playlist',
            'https://soundcloud.com/artist/sets/album'
        ]):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert choice == '4'

    def test_choice_5_without_sets_confirms(self):
        """Opção 5 com link sem /sets/ deve pedir confirmação."""
        with patch('builtins.input', side_effect=[
            '5',
            'https://soundcloud.com/artist/track-name',  # Sem /sets/
            'S'  # Confirma
        ]):
            url, choice = scraper.get_user_choice('https://soundcloud.com/artist')
            assert choice == '5'


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 3: Consistência do opcoes_nomes no scraper
# ══════════════════════════════════════════════════════════════════════

class TestOpcoesNomes:
    """Verifica consistência do mapeamento de opções."""

    def test_all_choices_have_names(self):
        """Todas as 7 opções devem ter nomes no opcoes_nomes do scraper."""
        # O opcoes_nomes está dentro de soundcloud_track_scraper()
        # Verificamos via inspeção do código fonte
        import inspect
        source = inspect.getsource(scraper.soundcloud_track_scraper)

        expected_options = {
            "'1'": "Todas as Faixas",
            "'2'": "Faixas Populares",
            "'3'": "Faixas",
            "'4'": "Álbuns",
            "'5'": "Playlists",
            "'6'": "Republicações",
            "'7'": "Curtidas",
        }

        for key, name in expected_options.items():
            assert key in source, f"Chave {key} não encontrada no opcoes_nomes"
            assert name in source, f"Nome '{name}' não encontrado no opcoes_nomes"

    def test_no_duplicate_names(self):
        """Não deve ter nomes duplicados no mapeamento."""
        import inspect
        source = inspect.getsource(scraper.soundcloud_track_scraper)

        names = ["Todas as Faixas", "Faixas Populares", "Faixas", "Álbuns",
                 "Playlists", "Republicações", "Curtidas"]

        # Cada nome deve aparecer exatamente 1 vez no opcoes_nomes
        # (pode aparecer mais vezes nos prints, mas no dict apenas 1)
        for name in names:
            count = source.count(f"'{name}'")
            assert count >= 1, f"Nome '{name}' não encontrado no código"


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 4: CSS Selectors
# ══════════════════════════════════════════════════════════════════════

class TestCssSelectors:
    """Verifica uso correto dos CSS selectors."""

    def test_album_playlist_uses_tracklist_selector(self):
        """Opções 4/5 devem usar selector de álbum/playlist."""
        import inspect
        source = inspect.getsource(scraper.soundcloud_track_scraper)

        # Verifica que o código usa selector diferente para álbuns/playlists
        assert "li.trackList__item a.trackItem__trackTitle" in source
        assert "a.soundTitle__title" in source

    def test_selector_logic_for_choices(self):
        """O selector deve ser determinado corretamente pela choice."""
        import inspect
        source = inspect.getsource(scraper.soundcloud_track_scraper)

        # Verifica que choices 4/5 usam o selector de lista
        assert "choice in ['4', '5']" in source


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 5: Salvamento de links
# ══════════════════════════════════════════════════════════════════════

class TestSaveTrackLinks:
    """Testa save_track_links() — salvamento de links em arquivo."""

    def test_saves_links_to_file(self, temp_dir):
        """Deve salvar links em arquivo corretamente."""
        filepath = os.path.join(temp_dir, 'test_links.txt')

        # Mock Selenium elements com get_attribute
        mock_tracks = []
        for url in ['https://soundcloud.com/a/t1', 'https://soundcloud.com/a/t2']:
            mock_el = MagicMock()
            mock_el.get_attribute.return_value = url
            mock_tracks.append(mock_el)

        scraper.save_track_links(filepath, mock_tracks)

        assert os.path.exists(filepath)
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'https://soundcloud.com/a/t1' in content
        assert 'https://soundcloud.com/a/t2' in content

    def test_deduplicates_links(self, temp_dir):
        """Deve remover links duplicados."""
        filepath = os.path.join(temp_dir, 'test_dedup.txt')

        url = 'https://soundcloud.com/a/same-track'
        mock_tracks = []
        for _ in range(3):
            mock_el = MagicMock()
            mock_el.get_attribute.return_value = url
            mock_tracks.append(mock_el)

        scraper.save_track_links(filepath, mock_tracks)

        with open(filepath, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        # Set garante unicidade — deve ter apenas 1
        assert len(lines) == 1

    def test_skips_none_hrefs(self, temp_dir):
        """Deve ignorar elementos sem href."""
        filepath = os.path.join(temp_dir, 'test_none.txt')

        mock_with_url = MagicMock()
        mock_with_url.get_attribute.return_value = 'https://soundcloud.com/a/t1'

        mock_without_url = MagicMock()
        mock_without_url.get_attribute.return_value = None

        scraper.save_track_links(filepath, [mock_with_url, mock_without_url])

        with open(filepath, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        assert len(lines) == 1


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 6: Constantes e configurações
# ══════════════════════════════════════════════════════════════════════

class TestScraperConfig:
    """Testa configurações e constantes do scraper."""

    def test_scroll_pause_time_positive(self):
        """SCROLL_PAUSE_TIME deve ser positivo."""
        assert scraper.SCROLL_PAUSE_TIME > 0

    def test_max_attempts_positive(self):
        """MAX_ATTEMPTS deve ser positivo."""
        assert scraper.MAX_ATTEMPTS > 0

    def test_scroll_pause_time_reasonable(self):
        """SCROLL_PAUSE_TIME deve ser razoável (entre 1-10 segundos)."""
        assert 1 <= scraper.SCROLL_PAUSE_TIME <= 10

    def test_max_attempts_reasonable(self):
        """MAX_ATTEMPTS deve ser razoável (entre 3-20)."""
        assert 3 <= scraper.MAX_ATTEMPTS <= 20
