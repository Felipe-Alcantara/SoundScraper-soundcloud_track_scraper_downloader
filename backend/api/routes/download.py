"""
Rota de Download — gerencia o download e conversão de faixas.
"""

import logging
from typing import Literal

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, field_validator

from backend.core.validation import validate_track_url
from backend.services.download_service import run_downloader

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Schemas ────────────────────────────────────────────────────────
class DownloadRequest(BaseModel):
    """Payload para iniciar downloads."""
    tracks: list[str] = Field(..., min_length=1, description="Lista de URLs das faixas")
    output_dir: str = Field(..., min_length=1, max_length=4096, description="Pasta de destino")
    format: Literal["flac", "mp3"] = Field("flac", description="Formato de áudio")

    @field_validator("tracks")
    @classmethod
    def valid_track_urls(cls, values: list[str]) -> list[str]:
        return [validate_track_url(value) for value in values]

    @field_validator("output_dir")
    @classmethod
    def safe_output_dir(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or "\x00" in normalized:
            raise ValueError("A pasta de destino é inválida.")
        return normalized


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
    except Exception:
        logger.exception("Falha inesperada no download REST")
        return DownloadResponse(success=False, message="Não foi possível concluir o download.")


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
    except Exception:
        logger.exception("Falha inesperada no WebSocket de download")
        try:
            await websocket.send_json({"type": "error", "message": "Falha interna no download."})
        except Exception:
            pass
