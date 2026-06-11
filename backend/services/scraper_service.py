"""
Serviço de Scraping — adapta o pipeline de coleta (core.scraping) ao WebSocket,
sem depender de input()/print() do console.

Toda a lógica de coleta (Selenium, HTTP API v2, paginação, dedupe) vive em
core/scraping/. Aqui só fazemos a ponte: normalizar a URL/opção e traduzir os
logs/contadores do pipeline para os eventos do WebSocket que o frontend espera.
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório core/ ao path para importar o pacote scraping.
_core_dir = str(Path(__file__).parent.parent.parent / "core")
if _core_dir not in sys.path:
    sys.path.insert(0, _core_dir)


def _normalize_profile_url(url: str) -> str | None:
    """
    Normaliza a entrada do usuário para 'https://soundcloud.com/<artista>'.
    Aceita URL completa, 'soundcloud.com/x' ou só o username. None se inválida.
    """
    clean = url.strip().replace("http://", "").replace("https://", "").rstrip("/")
    if not clean.startswith("soundcloud.com"):
        clean = f"soundcloud.com/{clean}"
    parts = clean.split("/")
    if len(parts) < 2 or not parts[1]:
        return None
    # Mantém o caminho completo (perfil, ou link de set para álbum/playlist).
    return f"https://{clean}"


async def run_scraper(url: str, choice: str, send_event):
    """
    Executa a coleta de faixas e emite eventos no contrato do WebSocket:
        {"type": "log",   "message": ...}
        {"type": "stage", "stage": ..., "message": ...}
        {"type": "track", "url": ..., "index": ..., "total": ...}
        {"type": "done",  "tracks": [...], "total": ...}
        {"type": "error", "message": ...}
    Retorna a lista de URLs coletadas.
    """
    from scraping import ScraperConfig, get_choice
    from scraping import pipeline

    await send_event({"type": "log", "message": "Iniciando coleta de faixas..."})

    profile_url = _normalize_profile_url(url)
    if not profile_url:
        await send_event({"type": "error", "message": "URL inválida. Precisa conter o nome do artista."})
        return []

    try:
        spec = get_choice(choice)
    except ValueError as exc:
        await send_event({"type": "error", "message": str(exc)})
        return []

    await send_event({"type": "log", "message": f"Artista/alvo: {profile_url}"})
    await send_event({"type": "log", "message": f"Modo: {spec.name}"})

    # Fila para repassar os logs síncronos do pipeline (que roda em thread) ao WebSocket.
    log_queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def on_log(message: str):
        # Marca transições de método como "stage" (espelha o comportamento antigo).
        if message.startswith("── Tentando"):
            event = {"type": "stage", "stage": "method", "message": message}
        else:
            event = {"type": "log", "message": message}
        loop.call_soon_threadsafe(log_queue.put_nowait, event)

    config = ScraperConfig.from_env()

    async def drain_logs():
        while True:
            event = await log_queue.get()
            if event is None:
                break
            await send_event(event)

    drainer = asyncio.create_task(drain_logs())
    try:
        result = await asyncio.to_thread(
            pipeline.collect, profile_url, choice, config, on_log, None
        )
    finally:
        log_queue.put_nowait(None)
        await drainer

    urls = result.urls
    if not urls:
        await send_event({"type": "error", "message": "Não foi possível coletar links por nenhum método."})
        return []

    for i, track_url in enumerate(urls, 1):
        await send_event({"type": "track", "url": track_url, "index": i, "total": len(urls)})

    await send_event({
        "type": "done",
        "tracks": urls,
        "total": len(urls),
        "message": f"Coleta concluída! {len(urls)} faixa(s) encontrada(s).",
    })
    return urls
