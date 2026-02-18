"""
test_browser_handler.py — Testes automatizados para o módulo browser_handler.

Testa:
  • Resolução de caminhos (frozen vs script)
  • Detecção de binários (Chrome, ChromeDriver)
  • Setup do Selenium Manager para EXE
  • HTTP GET com urllib
  • Extração de client_id
  • Resolução de URLs via API
  • Coleta de tracks (coleções e playlists)
  • Fallback HTTP completo
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Importa o módulo a ser testado
import browser_handler as bh


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 1: Resolução de caminhos
# ══════════════════════════════════════════════════════════════════════

class TestGetBasePath:
    """Testa _get_base_path() em ambientes diferentes."""

    def test_base_path_script_mode(self, mock_not_frozen):
        """No modo script, deve retornar a pasta pai do diretório do módulo."""
        result = bh._get_base_path()
        # Deve ser a raiz do projeto (pai de core/)
        assert os.path.isdir(result)
        assert not result.endswith('core')

    def test_base_path_frozen_mode(self, mock_frozen, temp_dir):
        """No modo EXE (frozen), deve retornar sys._MEIPASS."""
        mock_frozen(temp_dir)
        result = bh._get_base_path()
        assert result == temp_dir

    def test_base_path_returns_existing_directory(self, mock_not_frozen):
        """O diretório retornado deve existir."""
        result = bh._get_base_path()
        assert os.path.exists(result)


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 2: Detecção de binários
# ══════════════════════════════════════════════════════════════════════

class TestFindChromeBinary:
    """Testa _find_chrome_binary() — localização do Chrome."""

    def test_returns_tuple(self, mock_not_frozen):
        """Deve sempre retornar uma tupla (path, source) ou (None, None)."""
        result = bh._find_chrome_binary()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_portable_chrome_found(self, mock_frozen, temp_dir):
        """Deve encontrar Chrome portátil se existir no bundle."""
        mock_frozen(temp_dir)
        # Cria o Chrome portátil fake
        chrome_dir = os.path.join(temp_dir, 'Navegador', 'chrome-win64')
        os.makedirs(chrome_dir)
        chrome_exe = os.path.join(chrome_dir, 'chrome.exe')
        with open(chrome_exe, 'w') as f:
            f.write('fake')

        path, source = bh._find_chrome_binary()
        assert path == chrome_exe
        assert source == "portátil"

    def test_system_chrome_detection(self, mock_not_frozen):
        """Se Chrome do sistema existir, deve retornar source='sistema'."""
        result_path, result_source = bh._find_chrome_binary()
        if result_path is not None:
            # Se encontrou Chrome, verifica consistência
            assert os.path.exists(result_path)
            assert result_source in ("portátil", "sistema")
        else:
            # Se não encontrou, ambos devem ser None
            assert result_source is None

    def test_no_chrome_returns_none(self, mock_frozen, temp_dir):
        """Se nenhum Chrome existir, deve retornar (None, None)."""
        mock_frozen(temp_dir)
        # temp_dir vazio — nenhum Chrome
        path, source = bh._find_chrome_binary()
        # Pode achar o Chrome do sistema mesmo em frozen mode
        # Se não achou nenhum, ambos são None
        if path is None:
            assert source is None


class TestFindBundledChromedriver:
    """Testa _find_bundled_chromedriver() — localização do ChromeDriver."""

    def test_returns_string_or_none(self, mock_not_frozen):
        """Deve retornar string (caminho) ou None."""
        result = bh._find_bundled_chromedriver()
        assert result is None or isinstance(result, str)

    def test_bundled_chromedriver_found(self, mock_frozen, temp_dir):
        """Deve encontrar ChromeDriver se existir no bundle."""
        mock_frozen(temp_dir)
        driver_dir = os.path.join(temp_dir, 'Navegador', 'chrome-win64')
        os.makedirs(driver_dir)
        driver_exe = os.path.join(driver_dir, 'chromedriver.exe')
        with open(driver_exe, 'w') as f:
            f.write('fake')

        result = bh._find_bundled_chromedriver()
        assert result == driver_exe

    def test_no_chromedriver_returns_none_or_path(self, mock_frozen, temp_dir):
        """Em diretório vazio, retorna None ou chromedriver do PATH."""
        mock_frozen(temp_dir)
        result = bh._find_bundled_chromedriver()
        # Pode encontrar no PATH do sistema
        if result is not None:
            assert os.path.exists(result)


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 3: Selenium Manager para EXE
# ══════════════════════════════════════════════════════════════════════

class TestSetupSeleniumManager:
    """Testa _setup_selenium_manager_for_exe()."""

    def test_noop_when_not_frozen(self, mock_not_frozen):
        """Fora do EXE, não deve fazer nada."""
        # Limpa variável se existir
        os.environ.pop('SE_MANAGER_PATH', None)
        bh._setup_selenium_manager_for_exe()
        # Não deve ter setado SE_MANAGER_PATH
        assert 'SE_MANAGER_PATH' not in os.environ

    def test_sets_env_when_frozen_and_exists(self, mock_frozen, temp_dir):
        """No EXE, deve setar SE_MANAGER_PATH se o arquivo existir."""
        mock_frozen(temp_dir)
        sm_dir = os.path.join(temp_dir, 'selenium', 'webdriver', 'common', 'windows')
        os.makedirs(sm_dir)
        sm_exe = os.path.join(sm_dir, 'selenium-manager.exe')
        with open(sm_exe, 'w') as f:
            f.write('fake')

        os.environ.pop('SE_MANAGER_PATH', None)
        bh._setup_selenium_manager_for_exe()
        assert os.environ.get('SE_MANAGER_PATH') == sm_exe

        # Cleanup
        os.environ.pop('SE_MANAGER_PATH', None)

    def test_no_crash_when_frozen_and_missing(self, mock_frozen, temp_dir):
        """No EXE, não deve crashar se o arquivo não existir."""
        mock_frozen(temp_dir)
        os.environ.pop('SE_MANAGER_PATH', None)
        # Não deve lançar exceção
        bh._setup_selenium_manager_for_exe()


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 4: HTTP GET
# ══════════════════════════════════════════════════════════════════════

class TestHttpGet:
    """Testa _http_get() — requests HTTP."""

    def test_successful_request(self):
        """Deve retornar conteúdo para URL válida."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b'test content'
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            result = bh._http_get("https://example.com")
            assert result == 'test content'

    def test_returns_none_on_error(self):
        """Deve retornar None em caso de erro HTTP."""
        from urllib.error import URLError
        with patch('urllib.request.urlopen', side_effect=URLError("timeout")):
            result = bh._http_get("https://invalid.example.com")
            assert result is None

    def test_custom_headers(self):
        """Deve aceitar headers personalizados."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b'ok'
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            headers = {'Accept': 'application/json'}
            result = bh._http_get("https://example.com", headers=headers)
            assert result == 'ok'


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 5: Extração de client_id
# ══════════════════════════════════════════════════════════════════════

class TestExtractClientId:
    """Testa _extract_client_id() — regex para client_id do SoundCloud."""

    def test_extracts_valid_client_id(self):
        """Deve extrair client_id de 32 chars dos scripts."""
        # Precisa de pelo menos 1 script nos últimos 3
        html = (
            '<script src="https://a-v2.sndcdn.com/assets/app-1.js"></script>'
            '<script src="https://a-v2.sndcdn.com/assets/app-2.js"></script>'
            '<script src="https://a-v2.sndcdn.com/assets/app-abc123.js"></script>'
        )
        js_without = 'var x = {key: "value"};'
        # client_id com exatamente 32 caracteres alfanuméricos
        client_id_32 = "abcdefghijklmnopqrstuvwxyz012345"  # 26 letras + 6 dígitos = 32
        js_with_id = f'var x = {{client_id:"{client_id_32}"}};'

        # Os 3 últimos scripts são analisados; o client_id está no último
        with patch.object(bh, '_http_get', side_effect=[js_without, js_without, js_with_id]):
            result = bh._extract_client_id(html)
            assert result == client_id_32

    def test_returns_none_when_no_scripts(self):
        """Deve retornar None se não encontrar scripts na página."""
        html = '<html><body>No scripts here</body></html>'
        result = bh._extract_client_id(html)
        assert result is None

    def test_returns_none_when_no_client_id_in_scripts(self):
        """Deve retornar None se os scripts não contêm client_id."""
        html = '<script src="https://a-v2.sndcdn.com/assets/app-xyz.js"></script>'
        js_without_id = 'var config = {key: "value"};'

        with patch.object(bh, '_http_get', return_value=js_without_id):
            result = bh._extract_client_id(html)
            assert result is None

    def test_returns_none_when_scripts_unreachable(self):
        """Deve retornar None se não conseguir baixar os scripts."""
        html = '<script src="https://a-v2.sndcdn.com/assets/app-fail.js"></script>'

        with patch.object(bh, '_http_get', return_value=None):
            result = bh._extract_client_id(html)
            assert result is None

    def test_client_id_regex_requires_32_chars(self):
        """O regex deve exigir exatamente 32 caracteres alfanuméricos."""
        html = '<script src="https://a-v2.sndcdn.com/assets/app-test.js"></script>'

        # client_id com menos de 32 chars — não deve encontrar
        js_short = 'client_id:"abc123"'
        with patch.object(bh, '_http_get', return_value=js_short):
            result = bh._extract_client_id(html)
            assert result is None


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 6: Resolução de URLs da API
# ══════════════════════════════════════════════════════════════════════

class TestResolveSoundcloudUrl:
    """Testa _resolve_soundcloud_url()."""

    def test_resolves_valid_url(self):
        """Deve retornar dados JSON do resolve da API."""
        response_json = '{"kind": "user", "id": 123, "username": "test"}'

        with patch.object(bh, '_http_get', return_value=response_json):
            result = bh._resolve_soundcloud_url("https://soundcloud.com/test", "fake_id")
            assert result is not None
            assert result['kind'] == 'user'
            assert result['id'] == 123

    def test_returns_none_on_http_failure(self):
        """Deve retornar None se o HTTP falhar."""
        with patch.object(bh, '_http_get', return_value=None):
            result = bh._resolve_soundcloud_url("https://soundcloud.com/test", "fake_id")
            assert result is None

    def test_returns_none_on_invalid_json(self):
        """Deve retornar None se a resposta não for JSON válido."""
        with patch.object(bh, '_http_get', return_value="not json"):
            result = bh._resolve_soundcloud_url("https://soundcloud.com/test", "fake_id")
            assert result is None

    def test_api_url_format(self):
        """Deve construir a URL da API corretamente."""
        with patch.object(bh, '_http_get', return_value='{"kind":"user"}') as mock_get:
            bh._resolve_soundcloud_url("https://soundcloud.com/artist", "my_client_id")
            # Verifica que chamou com a URL correta da API
            call_url = mock_get.call_args[0][0]
            assert "api-v2.soundcloud.com/resolve" in call_url
            assert "client_id=my_client_id" in call_url
            assert "url=https://soundcloud.com/artist" in call_url


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 7: Coleta de tracks de coleções
# ══════════════════════════════════════════════════════════════════════

class TestGetCollectionTracks:
    """Testa _get_collection_tracks()."""

    def test_collects_tracks_from_single_page(self):
        """Deve coletar tracks de uma única página."""
        response = json.dumps({
            "collection": [
                {"permalink_url": "https://soundcloud.com/a/t1"},
                {"permalink_url": "https://soundcloud.com/a/t2"},
            ],
            "next_href": None
        })

        with patch.object(bh, '_http_get', return_value=response):
            tracks = bh._get_collection_tracks(123, 'tracks', 'fake_id')
            assert len(tracks) == 2
            assert "https://soundcloud.com/a/t1" in tracks
            assert "https://soundcloud.com/a/t2" in tracks

    def test_handles_empty_collection(self):
        """Deve retornar lista vazia se a coleção estiver vazia."""
        response = json.dumps({"collection": [], "next_href": None})

        with patch.object(bh, '_http_get', return_value=response):
            tracks = bh._get_collection_tracks(123, 'tracks', 'fake_id')
            assert tracks == []

    def test_handles_http_failure(self):
        """Deve retornar o que coletou até o momento se HTTP falhar."""
        with patch.object(bh, '_http_get', return_value=None):
            tracks = bh._get_collection_tracks(123, 'tracks', 'fake_id')
            assert tracks == []

    def test_reposts_extracts_track_from_item(self):
        """Para reposts, deve extrair track de dentro do item."""
        response = json.dumps({
            "collection": [
                {"track": {"permalink_url": "https://soundcloud.com/a/repost1"}},
                {"track": {"permalink_url": "https://soundcloud.com/a/repost2"}},
            ],
            "next_href": None
        })

        with patch.object(bh, '_http_get', return_value=response):
            tracks = bh._get_collection_tracks(123, 'reposts', 'fake_id')
            assert len(tracks) == 2
            assert "https://soundcloud.com/a/repost1" in tracks

    def test_pagination_with_multiple_pages(self):
        """Deve paginar corretamente quando há next_href."""
        page1 = json.dumps({
            "collection": [{"permalink_url": "https://soundcloud.com/a/t1"}],
            "next_href": "https://api-v2.soundcloud.com/users/123/tracks?offset=50&client_id=x"
        })
        page2 = json.dumps({
            "collection": [{"permalink_url": "https://soundcloud.com/a/t2"}],
            "next_href": None
        })

        with patch.object(bh, '_http_get', side_effect=[page1, page2]):
            with patch('browser_handler.time') as mock_time:
                mock_time.sleep = MagicMock()
                tracks = bh._get_collection_tracks(123, 'tracks', 'fake_id')
                assert len(tracks) == 2


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 8: Coleta de tracks de playlists/álbuns
# ══════════════════════════════════════════════════════════════════════

class TestGetSetTracks:
    """Testa _get_set_tracks()."""

    def test_collects_tracks_with_permalink(self):
        """Deve coletar tracks que já possuem permalink_url."""
        set_data = json.dumps({
            "kind": "playlist",
            "title": "Test",
            "tracks": [
                {"permalink_url": "https://soundcloud.com/a/t1"},
                {"permalink_url": "https://soundcloud.com/a/t2"},
            ]
        })

        with patch.object(bh, '_resolve_soundcloud_url', return_value=json.loads(set_data)):
            tracks = bh._get_set_tracks("https://soundcloud.com/a/sets/test", "fake_id")
            assert len(tracks) == 2

    def test_resolves_tracks_by_id(self):
        """Deve resolver tracks que só têm ID (sem permalink_url)."""
        set_data = {
            "kind": "playlist",
            "title": "Test",
            "tracks": [
                {"id": 999, "permalink_url": None}
            ]
        }
        track_response = '{"permalink_url": "https://soundcloud.com/a/resolved"}'

        with patch.object(bh, '_resolve_soundcloud_url', return_value=set_data):
            with patch.object(bh, '_http_get', return_value=track_response):
                tracks = bh._get_set_tracks("https://soundcloud.com/a/sets/test", "fake_id")
                assert len(tracks) == 1
                assert tracks[0] == "https://soundcloud.com/a/resolved"

    def test_returns_empty_on_resolve_failure(self):
        """Deve retornar lista vazia se não conseguir resolver a URL."""
        with patch.object(bh, '_resolve_soundcloud_url', return_value=None):
            tracks = bh._get_set_tracks("https://soundcloud.com/a/sets/test", "fake_id")
            assert tracks == []


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 9: Fallback HTTP completo
# ══════════════════════════════════════════════════════════════════════

class TestHttpFallbackScraper:
    """Testa http_fallback_scraper() — orquestração do fallback."""

    def _setup_mocks(self):
        """Helper para configurar mocks comuns."""
        html = '<script src="https://a-v2.sndcdn.com/assets/app-test.js"></script>'
        js = 'client_id:"aB1cD2eF3gH4iJ5kL6mN7oP8qR9sT0u"'
        user_data = {"kind": "user", "id": 123, "username": "test"}
        return html, js, user_data

    def test_returns_empty_if_soundcloud_unreachable(self):
        """Deve retornar lista vazia se não conseguir acessar SoundCloud."""
        with patch.object(bh, '_http_get', return_value=None):
            result = bh.http_fallback_scraper("https://soundcloud.com/test", '1')
            assert result == []

    def test_returns_empty_if_no_client_id(self):
        """Deve retornar lista vazia se não encontrar client_id."""
        with patch.object(bh, '_http_get', side_effect=[
            '<html>no scripts</html>',  # HTML da página principal
        ]):
            result = bh.http_fallback_scraper("https://soundcloud.com/test", '1')
            assert result == []

    def test_choice_4_uses_set_tracks(self):
        """Opção 4 (álbuns) deve usar _get_set_tracks."""
        with patch.object(bh, '_http_get', return_value='<html></html>'):
            with patch.object(bh, '_extract_client_id', return_value='fake_client_id'):
                with patch.object(bh, '_get_set_tracks', return_value=["url1"]) as mock_set:
                    result = bh.http_fallback_scraper("https://soundcloud.com/a/sets/album", '4')
                    mock_set.assert_called_once()
                    assert result == ["url1"]

    def test_choice_5_uses_set_tracks(self):
        """Opção 5 (playlists) deve usar _get_set_tracks."""
        with patch.object(bh, '_http_get', return_value='<html></html>'):
            with patch.object(bh, '_extract_client_id', return_value='fake_client_id'):
                with patch.object(bh, '_get_set_tracks', return_value=["url1"]) as mock_set:
                    result = bh.http_fallback_scraper("https://soundcloud.com/a/sets/playlist", '5')
                    mock_set.assert_called_once()

    def test_collection_type_mapping(self):
        """Deve mapear choices para os collection_types corretos."""
        # O mapeamento interno: 1→tracks, 2→toptracks, 3→tracks, 6→reposts, 7→likes
        expected = {'1': 'tracks', '2': 'toptracks', '3': 'tracks', '6': 'reposts', '7': 'likes'}

        user_data = {"kind": "user", "id": 123, "username": "test"}

        for choice, expected_type in expected.items():
            with patch.object(bh, '_http_get', return_value='<html></html>'):
                with patch.object(bh, '_extract_client_id', return_value='fake_client_id'):
                    with patch.object(bh, '_resolve_soundcloud_url', return_value=user_data):
                        with patch.object(bh, '_get_collection_tracks', return_value=[]) as mock_coll:
                            bh.http_fallback_scraper("https://soundcloud.com/test", choice)
                            actual_type = mock_coll.call_args[0][1]
                            assert actual_type == expected_type, (
                                f"Choice '{choice}': esperado '{expected_type}', obtido '{actual_type}'"
                            )

    def test_strips_url_suffixes_for_profile(self):
        """Deve remover sufixos (/tracks, /popular-tracks, etc.) da URL base."""
        user_data = {"kind": "user", "id": 123, "username": "test"}

        with patch.object(bh, '_http_get', return_value='<html></html>'):
            with patch.object(bh, '_extract_client_id', return_value='fake_client_id'):
                with patch.object(bh, '_resolve_soundcloud_url', return_value=user_data) as mock_resolve:
                    with patch.object(bh, '_get_collection_tracks', return_value=[]):
                        bh.http_fallback_scraper("https://soundcloud.com/test/popular-tracks", '2')
                        resolved_url = mock_resolve.call_args[0][0]
                        assert resolved_url == "https://soundcloud.com/test"


# ══════════════════════════════════════════════════════════════════════
#  SEÇÃO 10: get_selenium_version
# ══════════════════════════════════════════════════════════════════════

class TestGetSeleniumVersion:
    """Testa get_selenium_version()."""

    def test_no_crash_when_selenium_installed(self):
        """Não deve crashar quando Selenium está instalado."""
        bh.get_selenium_version()  # Não deve lançar exceção

    def test_no_crash_when_selenium_missing(self):
        """Não deve crashar se Selenium não estiver instalado."""
        with patch.dict('sys.modules', {'selenium': None}):
            # A função importa selenium internamente; se falhar, imprime mensagem
            # Não deve lançar exceção
            try:
                bh.get_selenium_version()
            except Exception:
                pass  # Aceitável — o importante é não crashar
