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


# ── Paginação por cursor (loop seguindo next_href) ──────────────────

from scraping.adapters import http_api


def _page(urls, next_href):
    """Monta o corpo JSON de uma página de coleção com next_href explícito."""
    import json as _json
    return _json.dumps({
        "collection": [{"permalink_url": u} for u in urls],
        "next_href": next_href,
    })


class TestCursorPagination:
    """Cobre o item 'Paginação por cursor' da matriz de testes do guia."""

    def test_follows_next_href_until_end(self, monkeypatch):
        """Segue next_href por várias páginas e para quando ele vira null."""
        # 3 páginas encadeadas; a última traz next_href=null (fim).
        responses = {
            "page-1": _page(["https://sc.com/t1", "https://sc.com/t2"], "page-2"),
            "page-2": _page(["https://sc.com/t3", "https://sc.com/t4"], "page-3"),
            "page-3": _page(["https://sc.com/t5"], None),
        }

        def fake_get(url, headers=None, timeout=30.0):
            # resolve do perfil → usuário com id
            if "/resolve" in url:
                return SAMPLE_USER_RESOLVE_RESPONSE
            # primeira página da coleção (offset=0) ou as páginas encadeadas
            if "offset=0" in url:
                return responses["page-1"]
            for key in ("page-2", "page-3"):
                if key in url:
                    return responses[key]
            return None

        monkeypatch.setattr(http_api, "fetch_client_id", lambda timeout=30.0: "x" * 32)
        monkeypatch.setattr(http_api, "http_get", fake_get)

        adapter = http_api.HttpApiAdapter()
        tracks = adapter.collect(
            "https://soundcloud.com/artist", registry.get_choice("3"), ScraperConfig()
        )
        assert [t.url for t in tracks] == [
            "https://sc.com/t1", "https://sc.com/t2",
            "https://sc.com/t3", "https://sc.com/t4",
            "https://sc.com/t5",
        ]

    def test_respects_max_pages_ceiling(self, monkeypatch):
        """Mesmo com next_href infinito, para no teto de páginas."""
        def fake_get(url, headers=None, timeout=30.0):
            if "/resolve" in url:
                return SAMPLE_USER_RESOLVE_RESPONSE
            return _page(["https://sc.com/loop"], "next-forever")  # nunca acaba

        monkeypatch.setattr(http_api, "fetch_client_id", lambda timeout=30.0: "x" * 32)
        monkeypatch.setattr(http_api, "http_get", fake_get)
        monkeypatch.setattr(http_api.time, "sleep", lambda *_: None)  # sem espera real

        config = ScraperConfig(max_pages=3, max_tracks=1000)
        adapter = http_api.HttpApiAdapter()
        tracks = adapter.collect(
            "https://soundcloud.com/artist", registry.get_choice("3"), config
        )
        assert len(tracks) == 3  # 1 faixa por página × 3 páginas (teto)

    def test_respects_max_tracks_ceiling(self, monkeypatch):
        """Para no teto de faixas, truncando a página que ultrapassa."""
        def fake_get(url, headers=None, timeout=30.0):
            if "/resolve" in url:
                return SAMPLE_USER_RESOLVE_RESPONSE
            urls = [f"https://sc.com/t{i}" for i in range(10)]
            return _page(urls, "next-forever")

        monkeypatch.setattr(http_api, "fetch_client_id", lambda timeout=30.0: "x" * 32)
        monkeypatch.setattr(http_api, "http_get", fake_get)
        monkeypatch.setattr(http_api.time, "sleep", lambda *_: None)

        config = ScraperConfig(max_pages=100, max_tracks=5)
        adapter = http_api.HttpApiAdapter()
        tracks = adapter.collect(
            "https://soundcloud.com/artist", registry.get_choice("3"), config
        )
        assert len(tracks) == 5  # truncado em max_tracks


# ── Rate-limit / backoff no http_get ────────────────────────────────

class _FakeHTTPError(Exception):
    """Imita urllib.error.HTTPError o suficiente para _retry_wait."""
    def __init__(self, code, retry_after=None):
        self.code = code
        self.headers = {"Retry-After": str(retry_after)} if retry_after is not None else {}


class TestRetryWait:
    """Cobre o item 'Backoff / rate-limit' da matriz de testes do guia."""

    def test_429_respects_retry_after(self):
        assert http_api._retry_wait(_FakeHTTPError(429, retry_after=7), attempt=0) == 7.0

    def test_429_without_header_uses_backoff(self):
        # attempt=2 → 2.0 ** 2 = 4.0
        assert http_api._retry_wait(_FakeHTTPError(429), attempt=2) == 4.0

    def test_5xx_uses_backoff(self):
        assert http_api._retry_wait(_FakeHTTPError(503), attempt=1) == 2.0

    def test_4xx_is_not_retried(self):
        assert http_api._retry_wait(_FakeHTTPError(404), attempt=0) is None
        assert http_api._retry_wait(_FakeHTTPError(403), attempt=0) is None
