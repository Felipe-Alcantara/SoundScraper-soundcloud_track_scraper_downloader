"""
conftest.py — Fixtures e configurações compartilhadas para os testes do SoundScraper.
"""

import sys
import os
import pytest
import tempfile
import shutil

# Adiciona a pasta core ao sys.path para importar os módulos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(PROJECT_ROOT, 'core')

if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def temp_dir():
    """Cria um diretório temporário que é limpo após o teste."""
    d = tempfile.mkdtemp(prefix='soundscraper_test_')
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def temp_file(temp_dir):
    """Cria um arquivo temporário dentro do diretório temporário."""
    def _create(name, content=""):
        path = os.path.join(temp_dir, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    return _create


@pytest.fixture
def mock_frozen(monkeypatch):
    """Simula ambiente PyInstaller (sys.frozen = True)."""
    def _freeze(meipass_dir):
        monkeypatch.setattr(sys, 'frozen', True, raising=False)
        monkeypatch.setattr(sys, '_MEIPASS', meipass_dir, raising=False)
    return _freeze


@pytest.fixture
def mock_not_frozen(monkeypatch):
    """Garante que NÃO estamos em ambiente frozen."""
    if hasattr(sys, 'frozen'):
        monkeypatch.delattr(sys, 'frozen', raising=False)
    if hasattr(sys, '_MEIPASS'):
        monkeypatch.delattr(sys, '_MEIPASS', raising=False)


# ── Dados de exemplo para testes ──

SAMPLE_SOUNDCLOUD_HTML = '''
<html>
<head><title>SoundCloud</title></head>
<body>
<script src="https://a-v2.sndcdn.com/assets/app-12345abcde.js"></script>
</body>
</html>
'''

SAMPLE_JS_WITH_CLIENT_ID = '''
var config = {client_id:"aB1cD2eF3gH4iJ5kL6mN7oP8qR9sT0u"};
'''

SAMPLE_JS_WITHOUT_CLIENT_ID = '''
var config = {someOtherKey: "value"};
'''

SAMPLE_USER_RESOLVE_RESPONSE = '''{
    "kind": "user",
    "id": 123456,
    "username": "test-artist",
    "permalink_url": "https://soundcloud.com/test-artist"
}'''

SAMPLE_TRACKS_RESPONSE = '''{
    "collection": [
        {"permalink_url": "https://soundcloud.com/test-artist/track-1"},
        {"permalink_url": "https://soundcloud.com/test-artist/track-2"},
        {"permalink_url": "https://soundcloud.com/test-artist/track-3"}
    ],
    "next_href": null
}'''

SAMPLE_SET_RESPONSE = '''{
    "kind": "playlist",
    "title": "Test Playlist",
    "tracks": [
        {"permalink_url": "https://soundcloud.com/test-artist/track-a"},
        {"permalink_url": "https://soundcloud.com/test-artist/track-b"},
        {"id": 999, "permalink_url": null}
    ]
}'''

SAMPLE_TRACK_BY_ID_RESPONSE = '''{
    "permalink_url": "https://soundcloud.com/test-artist/track-c"
}'''
