"""
Serviço de Scraping — Encapsula a lógica do soundcloud_track_scraper
para uso via WebSocket, sem depender de input()/print() do console.
"""

import asyncio
import re
import sys
import os
import time
from pathlib import Path

# Adiciona o diretório Arquivos/ ao path
_arquivos_dir = str(Path(__file__).parent.parent.parent / "Arquivos")
if _arquivos_dir not in sys.path:
    sys.path.insert(0, _arquivos_dir)


async def run_scraper(url: str, choice: str, send_event):
    """
    Executa a coleta de faixas do SoundCloud.
    
    Args:
        url: URL do perfil/playlist (ex: "soundcloud.com/artista" ou URL completa)
        choice: Opção escolhida ('1'-'7')
        send_event: Coroutine async para enviar eventos ao frontend.
                    Recebe dict com {"type": ..., ...}
    
    Returns:
        Lista de URLs coletadas.
    """
    await send_event({"type": "log", "message": "Iniciando coleta de faixas..."})

    # ── Normalizar URL ──
    clean_url = url.strip().replace('http://', '').replace('https://', '').rstrip('/')
    if not clean_url.startswith('soundcloud.com'):
        # Assume que é só o username
        clean_url = f"soundcloud.com/{clean_url}"

    parts = clean_url.split('/')
    if len(parts) < 2 or not parts[1]:
        await send_event({"type": "error", "message": "URL inválida. Precisa conter o nome do artista."})
        return []

    artist_base_url = f"https://{parts[0]}/{parts[1]}"
    await send_event({"type": "log", "message": f"Artista: {artist_base_url}"})

    # ── Montar URL final baseado na opção ──
    soundcloud_link = artist_base_url
    choice_names = {
        '1': 'Todas as Faixas', '2': 'Faixas Populares', '3': 'Faixas',
        '4': 'Álbuns', '5': 'Playlists', '6': 'Republicações', '7': 'Curtidas'
    }

    if choice == '2':
        soundcloud_link += '/popular-tracks'
    elif choice == '3':
        soundcloud_link += '/tracks'
    elif choice == '6':
        soundcloud_link += '/reposts'
    elif choice == '7':
        soundcloud_link += '/likes'
    # choice '4' e '5': URL já deve ser o link do álbum/playlist (vem no campo url)

    await send_event({"type": "log", "message": f"Modo: {choice_names.get(choice, 'Desconhecido')}"})
    await send_event({"type": "log", "message": f"URL: {soundcloud_link}"})

    selenium_urls = set()
    http_urls = set()

    # ── ETAPA 1: Selenium ──
    await send_event({"type": "stage", "stage": "selenium", "message": "Iniciando coleta via Selenium..."})

    selenium_ok = False
    driver = None

    try:
        from browser_handler import get_webdriver, get_selenium_version
        from selenium.webdriver.common.by import By

        get_selenium_version()
        driver = await asyncio.to_thread(get_webdriver)
        selenium_ok = True
        await send_event({"type": "log", "message": "✅ Navegador iniciado com sucesso"})
    except Exception as e:
        await send_event({"type": "log", "message": f"⚠️ Selenium não disponível: {e}"})

    if selenium_ok and driver:
        try:
            await send_event({"type": "log", "message": f"Acessando {soundcloud_link}..."})
            await asyncio.to_thread(driver.get, soundcloud_link)
            await send_event({"type": "log", "message": "✅ Página carregada"})

            css_selector = (
                "li.trackList__item a.trackItem__trackTitle"
                if choice in ['4', '5']
                else "a.soundTitle__title"
            )

            # Scroll e coleta
            await send_event({"type": "log", "message": "Rolando página para carregar faixas..."})
            tracks = await asyncio.to_thread(
                _scroll_and_collect, driver, css_selector, send_event_sync=None
            )

            for track in tracks:
                href = track.get_attribute("href")
                if href:
                    selenium_urls.add(href)

            await send_event({
                "type": "log",
                "message": f"📊 Selenium coletou: {len(selenium_urls)} link(s)"
            })
            await asyncio.to_thread(driver.quit)
        except Exception as e:
            await send_event({"type": "log", "message": f"⚠️ Erro no Selenium: {e}"})
            try:
                await asyncio.to_thread(driver.quit)
            except Exception:
                pass

    # ── ETAPA 2: HTTP API ──
    await send_event({"type": "stage", "stage": "http_api", "message": "Verificando cobertura via API..."})

    try:
        from browser_handler import http_fallback_scraper
        result = await asyncio.to_thread(http_fallback_scraper, soundcloud_link, choice)
        if result:
            http_urls = set(result)
            await send_event({
                "type": "log",
                "message": f"📡 HTTP API coletou: {len(http_urls)} link(s)"
            })
    except Exception as e:
        await send_event({"type": "log", "message": f"⚠️ Erro na API HTTP: {e}"})

    # ── ETAPA 3: Mesclar ──
    all_urls = selenium_urls | http_urls

    if not all_urls:
        await send_event({"type": "error", "message": "Não foi possível coletar links por nenhum método."})
        return []

    # Estatísticas
    apenas_selenium = selenium_urls - http_urls
    apenas_http = http_urls - selenium_urls
    em_comum = selenium_urls & http_urls

    stats = []
    if selenium_urls:
        stats.append(f"Selenium: {len(selenium_urls)}")
    if http_urls:
        stats.append(f"HTTP API: {len(http_urls)}")
    if selenium_urls and http_urls:
        stats.append(f"Em comum: {len(em_comum)}")
        if apenas_http:
            stats.append(f"Extras (API): {len(apenas_http)}")
        if apenas_selenium:
            stats.append(f"Extras (Selenium): {len(apenas_selenium)}")

    await send_event({
        "type": "log",
        "message": f"📊 Estatísticas: {' | '.join(stats)}"
    })

    sorted_urls = sorted(all_urls)

    # Envia cada track individualmente
    for i, url in enumerate(sorted_urls, 1):
        await send_event({
            "type": "track",
            "url": url,
            "index": i,
            "total": len(sorted_urls)
        })

    await send_event({
        "type": "done",
        "tracks": sorted_urls,
        "total": len(sorted_urls),
        "message": f"Coleta concluída! {len(sorted_urls)} faixa(s) encontrada(s)."
    })

    return sorted_urls


def _scroll_and_collect(driver, css_selector, send_event_sync=None):
    """
    Rola a página e coleta tracks via Selenium.
    Versão síncrona para rodar em thread.
    """
    from selenium.webdriver.common.by import By

    scroll_pause = 4
    max_attempts = 5
    num_tracks = 0
    attempts = 0

    while attempts < max_attempts:
        # Tenta clicar "Show more"
        try:
            show_more_selectors = [
                "a.showMore", "button.showMore",
                "a[class*='ShowMore']", "button[class*='ShowMore']",
                "a.compactTrackList__moreLink",
            ]
            for sel in show_more_selectors:
                buttons = driver.find_elements(By.CSS_SELECTOR, sel)
                for btn in buttons:
                    if btn.is_displayed():
                        try:
                            btn.click()
                            time.sleep(scroll_pause)
                        except Exception:
                            pass
        except Exception:
            pass

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        tracks = driver.find_elements(By.CSS_SELECTOR, css_selector)
        new_num_tracks = len(tracks)

        if new_num_tracks == num_tracks:
            attempts += 1
        else:
            num_tracks = new_num_tracks
            attempts = 0

    return tracks
