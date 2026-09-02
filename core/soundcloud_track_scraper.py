"""CLI compatível para coleta de links do SoundCloud.

As decisões de coleta ficam no pipeline de ``core/scraping``. Este entry point
preserva as funções públicas históricas e cuida apenas da experiência de
terminal e da persistência do arquivo temporário de links.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from dependency_manager import check_and_install_requirements as _check_dependencies
from scraping import cli, pipeline
from scraping.adapters import selenium_browser
from scraping.config import ScraperConfig
from scraping.registry import get_choice


SCROLL_PAUSE_TIME = 4
MAX_ATTEMPTS = 5
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_FILE = PROJECT_ROOT / "deps" / "requirements.txt"


def check_and_install_requirements() -> bool:
    """Mantém o helper legado para quem executa este módulo diretamente."""
    return _check_dependencies(REQUIREMENTS_FILE)


def get_soundcloud_link() -> str:
    """Pede e valida a URL base do artista."""
    return cli.prompt_profile_url()


def get_user_choice(artist_url: str) -> tuple[str, str]:
    """Pede a coleção e retorna o alvo e a escolha histórica 1–7."""
    return cli.prompt_collection_target(artist_url)


def scroll_and_collect_tracks(
    driver: Any,
    scroll_pause_time: float,
    max_attempts: int,
    css_selector: str,
) -> list[Any]:
    """Fachada compatível para o scroll do adapter Selenium."""
    config = ScraperConfig(
        scroll_pause_s=scroll_pause_time,
        scroll_rounds=max_attempts,
    )
    return selenium_browser.scroll_and_collect(driver, css_selector, config)


def _track_url(track: Any) -> str | None:
    """Obtém o href de um WebElement sem repetir uma chamada remota."""
    try:
        href = track.get_attribute("href")
    except Exception:
        return None
    return href if isinstance(href, str) and href else None


def save_track_urls(filename: str | Path, urls: Iterable[str]) -> None:
    """Salva URLs deduplicadas em ordem estável."""
    unique_urls = list(dict.fromkeys(url for url in urls if url))
    path = Path(filename)
    path.write_text("".join(f"{url}\n" for url in unique_urls), encoding="utf-8")
    print(f"📄 {len(unique_urls)} link(s) salvo(s) em: {path}")


def save_track_links(filename: str | Path, tracks: Iterable[Any]) -> None:
    """Mantém a API histórica que recebe WebElements do Selenium."""
    save_track_urls(filename, (_track_url(track) for track in tracks))


def soundcloud_track_scraper() -> str:
    """Executa uma coleta via pipeline HTTP → Selenium e grava os links."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + "  🎵  SOUNDSCRAPER - Link Collector  🔗".center(68) + "║")
    print("╚" + "═" * 68 + "╝\n")

    artist_url = get_soundcloud_link()
    target_url, choice = get_user_choice(artist_url)
    spec = get_choice(choice)
    pipeline_url = target_url if spec.is_set else artist_url
    filename = cli.output_filename(target_url)

    print(f"📄 Arquivo temporário de links: {filename}\n")
    result = pipeline.collect(
        pipeline_url,
        choice,
        ScraperConfig.from_env(),
        print,
    )
    if not result.urls:
        print("\n❌ Não foi possível coletar links por nenhum método.")
        raise SystemExit(1)

    save_track_urls(filename, result.urls)
    print(f"✅ Coleta concluída: {len(result.urls)} faixa(s).\n")
    return filename


if __name__ == "__main__":
    if not check_and_install_requirements():
        raise SystemExit(1)
    soundcloud_track_scraper()
