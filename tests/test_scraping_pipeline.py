"""
test_scraping_pipeline.py — Testes offline do pacote core.scraping.

Validam, sem rede, os parsers puros (com as fixtures sanitizadas do conftest),
o registry das 7 opções e o fail-safe do pipeline. Cobrem o critério de pronto
do guia de scraping (parser offline, fixture, fail-safe, limites).
"""

import pytest

# conftest.py já adiciona core/ ao sys.path, tornando o pacote scraping importável.
from scraping import parsers
from scraping import registry
from scraping import pipeline
from scraping.config import ScraperConfig
from scraping.models import TrackLink, SOURCE_HTTP_API

# Fixtures sanitizadas (espelham as do conftest.py; reproduzidas aqui para
# importação direta, já que conftest não é um módulo importável por nome).
SAMPLE_SOUNDCLOUD_HTML = '''
<html>
<head><title>SoundCloud</title></head>
<body>
<script src="https://a-v2.sndcdn.com/assets/app-12345abcde.js"></script>
</body>
</html>
'''
# client_id com exatamente 32 caracteres alfanuméricos (como o do site real).
_VALID_CLIENT_ID = "abcdefghijklmnopqrstuvwxyz012345"
SAMPLE_JS_WITH_CLIENT_ID = f'var config = {{client_id:"{_VALID_CLIENT_ID}"}};'
SAMPLE_JS_WITHOUT_CLIENT_ID = 'var config = {someOtherKey: "value"};'
SAMPLE_USER_RESOLVE_RESPONSE = (
    '{"kind":"user","id":123456,"username":"test-artist",'
    '"permalink_url":"https://soundcloud.com/test-artist"}'
)
SAMPLE_TRACKS_RESPONSE = (
    '{"collection":['
    '{"permalink_url":"https://soundcloud.com/test-artist/track-1"},'
    '{"permalink_url":"https://soundcloud.com/test-artist/track-2"},'
    '{"permalink_url":"https://soundcloud.com/test-artist/track-3"}'
    '],"next_href":null}'
)
SAMPLE_SET_RESPONSE = (
    '{"kind":"playlist","title":"Test Playlist","tracks":['
    '{"permalink_url":"https://soundcloud.com/test-artist/track-a"},'
    '{"permalink_url":"https://soundcloud.com/test-artist/track-b"},'
    '{"id":999,"permalink_url":null}'
    ']}'
)
SAMPLE_TRACK_BY_ID_RESPONSE = '{"permalink_url":"https://soundcloud.com/test-artist/track-c"}'


# ── Parsers puros ───────────────────────────────────────────────────

class TestParsers:
    def test_find_script_urls(self):
        urls = parsers.find_script_urls(SAMPLE_SOUNDCLOUD_HTML)
        assert urls == ["https://a-v2.sndcdn.com/assets/app-12345abcde.js"]

    def test_find_script_urls_empty(self):
        assert parsers.find_script_urls("") == []
        assert parsers.find_script_urls("<html>sem scripts</html>") == []

    def test_extract_client_id(self):
        cid = parsers.extract_client_id_from_js(SAMPLE_JS_WITH_CLIENT_ID)
        assert cid == _VALID_CLIENT_ID

    def test_extract_client_id_absent(self):
        assert parsers.extract_client_id_from_js(SAMPLE_JS_WITHOUT_CLIENT_ID) is None
        assert parsers.extract_client_id_from_js("") is None

    def test_parse_collection_page(self):
        urls, next_href = parsers.parse_collection_page(SAMPLE_TRACKS_RESPONSE, "tracks")
        assert urls == [
            "https://soundcloud.com/test-artist/track-1",
            "https://soundcloud.com/test-artist/track-2",
            "https://soundcloud.com/test-artist/track-3",
        ]
        assert next_href is None

    def test_parse_collection_page_invalid_json_is_failsafe(self):
        urls, next_href = parsers.parse_collection_page("not json", "tracks")
        assert urls == []
        assert next_href is None

    def test_parse_collection_reposts_nesting(self):
        payload = '{"collection":[{"track":{"permalink_url":"https://soundcloud.com/a/r1"}}],"next_href":null}'
        urls, _ = parsers.parse_collection_page(payload, "reposts")
        assert urls == ["https://soundcloud.com/a/r1"]

    def test_parse_set(self):
        urls, pending_ids, title = parsers.parse_set(SAMPLE_SET_RESPONSE)
        assert urls == [
            "https://soundcloud.com/test-artist/track-a",
            "https://soundcloud.com/test-artist/track-b",
        ]
        assert pending_ids == [999]   # faixa sem permalink, só id
        assert title == "Test Playlist"

    def test_parse_resolved_user(self):
        data = parsers.parse_resolved_user(SAMPLE_USER_RESOLVE_RESPONSE)
        assert data is not None
        assert data["id"] == 123456
        assert data["username"] == "test-artist"

    def test_parse_resolved_user_invalid(self):
        assert parsers.parse_resolved_user("not json") is None

    def test_parse_track_permalink(self):
        assert parsers.parse_track_permalink(SAMPLE_TRACK_BY_ID_RESPONSE) == (
            "https://soundcloud.com/test-artist/track-c"
        )


# ── Registry ────────────────────────────────────────────────────────

class TestRegistry:
    def test_all_seven_choices_present(self):
        assert sorted(registry.CHOICES) == ["1", "2", "3", "4", "5", "6", "7"]

    def test_get_choice_returns_spec(self):
        spec = registry.get_choice("3")
        assert spec.name == "Faixas"
        assert spec.url_suffix == "/tracks"
        assert spec.collection_type == "tracks"
        assert spec.is_set is False

    def test_set_choices_flagged(self):
        assert registry.get_choice("4").is_set is True
        assert registry.get_choice("5").is_set is True

    def test_unknown_choice_raises_clear_error(self):
        with pytest.raises(ValueError) as exc:
            registry.get_choice("99")
        assert "desconhecida" in str(exc.value).lower()

    def test_selector_depends_on_set(self):
        assert registry.css_selector_for(registry.get_choice("4")) == registry.CSS_SELECTOR_SET
        assert registry.css_selector_for(registry.get_choice("3")) == registry.CSS_SELECTOR_PROFILE


# ── Pipeline (orquestração / fail-safe) ─────────────────────────────

class _EmptyAdapter:
    slug = "empty"
    display_name = "Vazio"

    def collect(self, profile_url, spec, config, log):
        return []


class _FakeAdapter:
    slug = SOURCE_HTTP_API
    display_name = "Fake HTTP"

    def __init__(self, urls):
        self._urls = urls

    def collect(self, profile_url, spec, config, log):
        return [TrackLink(url=u, source=self.slug) for u in self._urls]


class TestPipeline:
    def test_build_target_url_profile(self):
        spec = registry.get_choice("3")
        assert pipeline.build_target_url("https://soundcloud.com/artist", spec) == (
            "https://soundcloud.com/artist/tracks"
        )

    def test_build_target_url_set_is_unchanged(self):
        spec = registry.get_choice("4")
        url = "https://soundcloud.com/artist/sets/album"
        assert pipeline.build_target_url(url, spec) == url

    def test_failsafe_returns_empty(self, monkeypatch):
        """Todos os adapters vazios → CollectResult vazio, sem exceção."""
        monkeypatch.setattr(pipeline, "get_pipeline", lambda: [_EmptyAdapter(), _EmptyAdapter()])
        result = pipeline.collect("https://soundcloud.com/x", "3", ScraperConfig())
        assert result.urls == []
        assert result.used_source == ""

    def test_first_method_wins_and_dedupes(self, monkeypatch):
        """O primeiro método com resultado vence; URLs são deduplicadas e ordenadas."""
        fake = _FakeAdapter(["https://b.com/2", "https://a.com/1", "https://b.com/2"])
        monkeypatch.setattr(pipeline, "get_pipeline", lambda: [fake, _EmptyAdapter()])
        result = pipeline.collect("https://soundcloud.com/x", "1", ScraperConfig())
        assert result.urls == ["https://a.com/1", "https://b.com/2"]
        assert result.used_source == SOURCE_HTTP_API

    def test_falls_back_to_next_method(self, monkeypatch):
        """Se o primeiro método não traz nada, usa o próximo."""
        fake = _FakeAdapter(["https://a.com/1"])
        monkeypatch.setattr(pipeline, "get_pipeline", lambda: [_EmptyAdapter(), fake])
        result = pipeline.collect("https://soundcloud.com/x", "1", ScraperConfig())
        assert result.urls == ["https://a.com/1"]

    def test_unknown_choice_propagates(self):
        with pytest.raises(ValueError):
            pipeline.collect("https://soundcloud.com/x", "99", ScraperConfig())
