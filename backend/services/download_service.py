"""
Serviço de Download — Encapsula a lógica do soundcloud_tracks_downloader
para uso via WebSocket, sem depender de input()/print() do console.
"""

import asyncio
import os
import sys
import time
from queue import Empty, Queue
from pathlib import Path

from backend.core.validation import validate_track_url

# Adiciona o diretório core/ ao path
_core_dir = str(Path(__file__).parent.parent.parent / "core")
if _core_dir not in sys.path:
    sys.path.insert(0, _core_dir)

YTDLP_SOCKET_TIMEOUT = int(os.getenv("SOUNDSCRAPER_SOCKET_TIMEOUT", "30"))
YTDLP_RETRIES = int(os.getenv("SOUNDSCRAPER_RETRIES", "3"))
DOWNLOAD_HEARTBEAT_SECONDS = int(os.getenv("SOUNDSCRAPER_DOWNLOAD_HEARTBEAT_SECONDS", "10"))


def _get_ffmpeg_path():
    """
    Retorna o caminho do FFmpeg de forma portável (bundle EXE → projeto → PATH do
    sistema), ou None se não encontrar. Cross-platform (Windows, Linux, macOS).
    """
    from platform_utils import find_ffmpeg
    return find_ffmpeg()


def _get_ydl_opts(output_dir: str, audio_format: str, ffmpeg_path: str | None) -> dict:
    """Fachada compatível para as opções compartilhadas do yt-dlp."""
    from downloading.options import build_ydl_options

    options = build_ydl_options(
        output_dir,
        audio_format,
        ffmpeg_path,
        socket_timeout=YTDLP_SOCKET_TIMEOUT,
        retries=YTDLP_RETRIES,
    )
    options.update({"quiet": True, "no_warnings": True})
    return options


def _corrigir_nomes(output_dir: str) -> list:
    """Fachada compatível para normalização de nomes."""
    from downloading.options import rename_downloaded_files

    return rename_downloaded_files(output_dir)


def _download_single(url: str, ydl_opts: dict, progress_queue: Queue | None = None) -> dict:
    """
    Baixa uma única faixa. Retorna dict com infos e status.
    Versão síncrona para rodar em thread.
    """
    import yt_dlp
    from downloading.metadata import AddCustomMetadataPP

    captured_meta = {}

    try:
        local_opts = dict(ydl_opts)

        if progress_queue is not None:
            def _progress_hook(data):
                try:
                    progress_queue.put_nowait({
                        "status": data.get("status"),
                        "downloaded_bytes": data.get("downloaded_bytes"),
                        "total_bytes": data.get("total_bytes") or data.get("total_bytes_estimate"),
                        "eta": data.get("eta"),
                        "speed": data.get("speed"),
                    })
                except Exception:
                    pass

            local_opts["progress_hooks"] = [_progress_hook]

        with yt_dlp.YoutubeDL(local_opts) as ydl:
            ydl.add_post_processor(AddCustomMetadataPP(captured_meta), when="pre_process")
            ydl.download([url])

        return {
            "success": True,
            "url": url,
            "metadata": captured_meta,
        }
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": str(e),
        }


async def run_downloader(tracks: list, output_dir: str, audio_format: str, send_event):
    """
    Executa o download de uma lista de faixas.

    Args:
        tracks: Lista de URLs para baixar
        output_dir: Pasta de destino
        audio_format: 'flac' ou 'mp3'
        send_event: Coroutine async para enviar eventos ao frontend.
    """
    from downloading.options import normalize_audio_format

    if not tracks:
        raise ValueError("A lista de faixas não pode estar vazia.")
    normalized_tracks = [validate_track_url(track) for track in tracks]
    output_dir = output_dir.strip()
    if not output_dir or "\x00" in output_dir:
        raise ValueError("A pasta de destino é inválida.")
    audio_format = normalize_audio_format(audio_format)
    total = len(normalized_tracks)

    await send_event({
        "type": "log",
        "message": f"Iniciando download de {total} faixa(s) em {audio_format.upper()}..."
    })

    # Criar pasta se não existir
    os.makedirs(output_dir, exist_ok=True)

    ffmpeg_path = _get_ffmpeg_path()
    ydl_opts = _get_ydl_opts(output_dir, audio_format, ffmpeg_path)

    if ffmpeg_path:
        await send_event({"type": "log", "message": f"FFmpeg detectado: {ffmpeg_path}"})
    else:
        await send_event({
            "type": "log",
            "message": "⚠️ FFmpeg não localizado no projeto nem no PATH. O yt-dlp tentará o FFmpeg do sistema."
        })

    sucessos = 0
    erros = 0

    for i, url in enumerate(normalized_tracks, 1):
        track_started = time.monotonic()
        await send_event({
            "type": "start",
            "index": i,
            "total": total,
            "url": url,
            "message": f"Baixando [{i}/{total}]..."
        })

        # Roda download em thread para não bloquear o event loop.
        # Em paralelo, emite heartbeat/progresso para não parecer travado.
        progress_queue: Queue = Queue()
        task = asyncio.create_task(asyncio.to_thread(_download_single, url, ydl_opts, progress_queue))
        next_heartbeat_at = track_started + DOWNLOAD_HEARTBEAT_SECONDS
        last_percent_reported = -1

        while not task.done():
            await asyncio.sleep(1)
            while True:
                try:
                    item = progress_queue.get_nowait()
                except Empty:
                    break

                status = item.get("status")
                if status == "downloading":
                    downloaded = item.get("downloaded_bytes") or 0
                    total_bytes = item.get("total_bytes") or 0
                    if total_bytes:
                        percent = int((float(downloaded) / float(total_bytes)) * 100)
                        if percent >= last_percent_reported + 10:
                            last_percent_reported = percent
                            await send_event({
                                "type": "log",
                                "message": f"⬇️ [{i}/{total}] {percent}% concluído"
                            })
                elif status == "finished":
                    await send_event({
                        "type": "log",
                        "message": f"🔄 [{i}/{total}] Download concluído, convertendo áudio..."
                    })

            now = time.monotonic()
            if now >= next_heartbeat_at:
                elapsed = int(now - track_started)
                await send_event({
                    "type": "log",
                    "message": f"⏳ [{i}/{total}] Processando há {elapsed}s..."
                })
                next_heartbeat_at = now + DOWNLOAD_HEARTBEAT_SECONDS

        result = await task

        if result["success"]:
            sucessos += 1
            meta = result.get("metadata", {})

            # Corrigir nomes
            await asyncio.to_thread(_corrigir_nomes, output_dir)

            await send_event({
                "type": "complete",
                "index": i,
                "total": total,
                "url": url,
                "title": meta.get("title", ""),
                "artist": meta.get("artist", ""),
                "message": (
                    f"✅ [{i}/{total}] {meta.get('artist', '')} - {meta.get('title', '')} "
                    f"({int(time.monotonic() - track_started)}s)"
                )
            })
        else:
            erros += 1
            await send_event({
                "type": "track_error",
                "index": i,
                "total": total,
                "url": url,
                "message": (
                    f"❌ [{i}/{total}] Erro após {int(time.monotonic() - track_started)}s: "
                    f"{result.get('error', 'desconhecido')}"
                )
            })

    await send_event({
        "type": "done",
        "downloaded": sucessos,
        "failed": erros,
        "output_dir": output_dir,
        "message": f"Download concluído! {sucessos} sucesso(s), {erros} erro(s)."
    })

    return {"downloaded": sucessos, "failed": erros}
