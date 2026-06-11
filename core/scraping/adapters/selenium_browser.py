"""
selenium_browser.py — Adapter de coleta via navegador (Selenium).

Método de FALLBACK: usado quando a API v2 não cobre o caso. Encapsula a
inicialização do WebDriver e o scroll/coleta — antes duplicados entre o CLI e o
backend. Selenium é importado preguiçosamente para não ser obrigatório quando só
se usa o HTTP API.
"""

import time

from ..base import LogFn, SourceAdapter, _noop
from ..config import ScraperConfig
from ..models import SOURCE_SELENIUM, TrackLink
from ..registry import ChoiceSpec, css_selector_for

_SHOW_MORE_SELECTORS = [
    "a.showMore", "button.showMore",
    "a[class*='ShowMore']", "button[class*='ShowMore']",
    "a.compactTrackList__moreLink",
]


def scroll_and_collect(driver, css_selector: str, config: ScraperConfig):
    """
    Rola a página clicando em "Show more" e coleta os elementos do seletor.
    Retorna a lista de WebElements encontrados. Síncrono (rodar em thread no async).
    """
    from selenium.webdriver.common.by import By

    num_tracks = 0
    attempts = 0
    elements = []

    while attempts < config.scroll_rounds:
        try:
            for sel in _SHOW_MORE_SELECTORS:
                for btn in driver.find_elements(By.CSS_SELECTOR, sel):
                    if btn.is_displayed():
                        try:
                            btn.click()
                            time.sleep(config.scroll_pause_s)
                        except Exception:
                            pass
        except Exception:
            pass

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(config.scroll_pause_s)

        elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
        if len(elements) == num_tracks:
            attempts += 1
        else:
            num_tracks = len(elements)
            attempts = 0

    return elements


class SeleniumAdapter(SourceAdapter):
    slug = SOURCE_SELENIUM
    display_name = "Navegador (Selenium)"

    def collect(
        self,
        profile_url: str,
        spec: ChoiceSpec,
        config: ScraperConfig,
        log: LogFn = _noop,
    ) -> list[TrackLink]:
        try:
            from browser_handler import get_webdriver
        except Exception as exc:  # selenium ausente, etc.
            log(f"⚠️ Selenium indisponível: {exc}")
            return []

        driver = None
        try:
            driver = get_webdriver()
        except Exception as exc:
            log(f"⚠️ Não foi possível iniciar o navegador: {exc}")
            return []

        if not driver:
            return []

        try:
            log(f"Acessando {profile_url} ...")
            driver.get(profile_url)
            selector = css_selector_for(spec)
            elements = scroll_and_collect(driver, selector, config)

            tracks: list[TrackLink] = []
            for el in elements:
                href = el.get_attribute("href")
                if href:
                    tracks.append(TrackLink(url=href, source=self.slug))
                if len(tracks) >= config.max_tracks:
                    break
            log(f"📊 Selenium coletou {len(tracks)} link(s).")
            return tracks
        except Exception as exc:
            log(f"⚠️ Erro no Selenium: {exc}")
            return []
        finally:
            try:
                driver.quit()
            except Exception:
                pass
