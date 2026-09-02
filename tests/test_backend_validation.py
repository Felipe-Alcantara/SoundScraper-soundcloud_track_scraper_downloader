"""Testes offline dos contratos de entrada da API."""

import pytest
from pydantic import ValidationError

from backend.api.routes.download import DownloadRequest
from backend.api.routes.scraper import ScrapeRequest
from backend.core.validation import normalize_soundcloud_url, validate_track_url


def test_normalize_soundcloud_url_rejects_domain_prefix_attack():
    assert normalize_soundcloud_url("https://soundcloud.com.evil.example/artist") is None


def test_normalize_soundcloud_url_accepts_username_and_removes_query():
    assert normalize_soundcloud_url("artist_01") == "https://soundcloud.com/artist_01"
    assert normalize_soundcloud_url("https://soundcloud.com/artist?ref=clipboard") == (
        "https://soundcloud.com/artist"
    )


def test_validate_track_url_requires_soundcloud_host():
    assert validate_track_url("soundcloud.com/artist/track") == (
        "https://soundcloud.com/artist/track"
    )
    with pytest.raises(ValueError):
        validate_track_url("https://example.com/track")


def test_scrape_request_validates_choice_and_control_characters():
    request = ScrapeRequest(url=" soundcloud.com/artist ", choice="3")
    assert request.url == "soundcloud.com/artist"
    with pytest.raises(ValidationError):
        ScrapeRequest(url="soundcloud.com/artist\n", choice="9")


def test_download_request_normalizes_tracks_and_output_dir():
    request = DownloadRequest(
        tracks=["soundcloud.com/artist/track"],
        output_dir=" /tmp/downloads ",
        format="mp3",
    )
    assert request.tracks == ["https://soundcloud.com/artist/track"]
    assert request.output_dir == "/tmp/downloads"
