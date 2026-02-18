"""
Rota de Download — gerencia o download e conversão de faixas.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from backend.services.download_service import run_downloader

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────
class DownloadRequest(BaseModel):
    """Payload para iniciar downloads."""
    tracks: list[str] = Field(..., description="Lista de URLs das faixas")
    output_dir: str = Field(..., description="Pasta de destino")
    format: str = Field("flac", description="Formato de áudio: 'flac' ou 'mp3'")


class DownloadResponse(BaseModel):
    """Resposta do download."""
    success: bool
    downloaded: int = 0
    failed: int = 0
    message: str = ""


# ── Endpoints ──────────────────────────────────────────────────────
@router.post("/download", response_model=DownloadResponse)
async def download_tracks(request: DownloadRequest):
    """Inicia o download (versão REST, sem progresso em tempo real)."""
    async def noop(event):
        pass

    try:
        result = await run_downloader(
            request.tracks, request.output_dir, request.format, noop
        )
        return DownloadResponse(
            success=result["downloaded"] > 0,
            downloaded=result["downloaded"],
            failed=result["failed"],
            message=f"Concluído: {result['downloaded']} baixadas, {result['failed']} erros."
        )
    except Exception as e:
        return DownloadResponse(success=False, message=str(e))


@router.websocket("/ws/download")
async def download_ws(websocket: WebSocket):
    """
    WebSocket para progresso dos downloads em tempo real.

    O frontend envia:
        {"tracks": [...], "output_dir": "C:/...", "format": "flac"}

    O backend responde com eventos:
        {"type": "start",       "index": 1, "total": 13, "url": "..."}
        {"type": "complete",    "index": 1, "total": 13, "title": "...", "artist": "..."}
        {"type": "track_error", "index": 1, "total": 13, "message": "..."}
        {"type": "done",        "downloaded": 13, "failed": 0}
    """
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        tracks = data.get("tracks", [])
        output_dir = data.get("output_dir", "")
        fmt = data.get("format", "flac")

        async def send_event(event):
            try:
                await websocket.send_json(event)
            except Exception:
                pass

        await run_downloader(tracks, output_dir, fmt, send_event)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
