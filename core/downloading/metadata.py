"""Metadados SoundCloud aplicados pelo postprocessor do yt-dlp."""

from __future__ import annotations

from datetime import datetime
from typing import Any, cast

from yt_dlp.postprocessor.common import PostProcessor


GITHUB_URL = "https://github.com/Felipe-Alcantara/SoundScraper-soundcloud_track_scraper_downloader"


def enrich_metadata(information: dict[str, Any]) -> dict[str, Any]:
    """Enriquece e normaliza o ``info_dict`` sem depender de arquivo ou rede."""
    info = cast(dict[str, Any], information)
    info["title"] = info.get("title", "")
    info["artist"] = info.get("artist", "") or info.get("uploader", "")

    if not info.get("album"):
        for candidate in ("playlist", "playlist_title"):
            if info.get(candidate):
                info["album"] = info[candidate]
                break

    upload_date = info.get("upload_date")
    if upload_date:
        upload_date_text = str(upload_date)
        try:
            date_value = datetime.strptime(upload_date_text, "%Y%m%d")
        except ValueError:
            info["date"] = upload_date_text[:4]
        else:
            info["date"] = str(date_value.year)
            info["timestamp"] = date_value.strftime("%Y-%m-%d")

    if not info.get("date"):
        release_date = info.get("release_date")
        release_year = info.get("release_year")
        if release_date:
            info["date"] = str(release_date)[:4]
        elif release_year:
            info["date"] = str(release_year)

    description = info.get("description")
    if description and len(str(description)) < 500:
        info["lyrics"] = str(description)

    tags = info.get("tags")
    if tags:
        info["keywords"] = ", ".join(tags) if isinstance(tags, list) else str(tags)

    if info.get("bpm"):
        info["bpm"] = str(info["bpm"])
    if info.get("license"):
        info["copyright"] = info["license"]
    if not info.get("publisher") and info.get("label"):
        info["publisher"] = info["label"]
    if info.get("track_number"):
        info["track"] = str(info["track_number"])
    elif info.get("playlist_index"):
        info["track"] = str(info["playlist_index"])
    if info.get("duration"):
        info["length"] = str(int(float(info["duration"]) * 1000))

    info["comment"] = "\n".join(
        [
            "Downloaded by SoundScraper",
            f"Source: {info.get('webpage_url', 'SoundCloud')}",
            "",
            f"GitHub: {GITHUB_URL}",
        ]
    )
    info["website"] = GITHUB_URL
    info["encoder"] = "SoundScraper v3.0"
    return info


class AddCustomMetadataPP(PostProcessor):
    """Postprocessor yt-dlp que aplica os campos próprios do SoundScraper."""

    def __init__(self, captured_meta: dict[str, Any] | None = None) -> None:
        super().__init__(None)
        self.captured_meta = captured_meta

    def run(self, information: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
        info = enrich_metadata(information)
        if self.captured_meta is not None:
            self.captured_meta.update(
                {
                    "title": info.get("title", ""),
                    "artist": info.get("artist", ""),
                    "genre": info.get("genre", ""),
                    "duration": info.get("duration", 0),
                    "webpage_url": info.get("webpage_url", ""),
                }
            )
        print("📝 Metadados personalizados adicionados.")
        return [], info
