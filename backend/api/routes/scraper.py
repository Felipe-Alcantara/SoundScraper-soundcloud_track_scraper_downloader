"""
Rota de Scraping — coleta links de faixas do SoundCloud.
Expõe endpoints REST e um WebSocket para progresso em tempo real.
"""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, field_validator

from backend.services.scraper_service import run_scraper

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Schemas ────────────────────────────────────────────────────────
class ScrapeRequest(BaseModel):
    """Payload para iniciar uma coleta de faixas."""
    url: str = Field(..., min_length=1, max_length=2048, description="URL do perfil/playlist do SoundCloud")
    choice: str = Field("3", pattern=r"^[1-7]$", description="Opção de coleta de 1 a 7")

    @field_validator("url")
    @classmethod
    def url_without_control_chars(cls, value: str) -> str:
        if any(ord(char) < 32 for char in value):
            raise ValueError("A URL contém caracteres de controle.")
        return value.strip()


class ScrapeResponse(BaseModel):
    """Resposta com os links coletados."""
    success: bool
    tracks: list[str] = Field(default_factory=list)
    total: int = 0
    message: str = ""


# ── Endpoints ──────────────────────────────────────────────────────
@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_tracks(request: ScrapeRequest):
    """Inicia a coleta de faixas (versão REST, sem progresso em tempo real)."""
    collected = []

    async def collect_event(event):
        if event.get("type") == "track":
            collected.append(event["url"])

    try:
        result = await run_scraper(request.url, request.choice, collect_event)
        return ScrapeResponse(
            success=bool(result),
            tracks=result,
            total=len(result),
            message=f"Coleta concluída: {len(result)} faixa(s)."
        )
    except Exception:
        logger.exception("Falha inesperada na coleta REST")
        return ScrapeResponse(success=False, message="Não foi possível concluir a coleta.")


@router.websocket("/ws/scrape")
async def scrape_ws(websocket: WebSocket):
    """
    WebSocket para progresso do scraping em tempo real.

    O frontend envia:
        {"url": "soundcloud.com/artista", "choice": "3"}

    O backend responde com eventos:
        {"type": "log",   "message": "..."}
        {"type": "stage", "stage": "selenium|http_api", "message": "..."}
        {"type": "track", "url": "...", "index": 1, "total": 18}
        {"type": "done",  "tracks": [...], "total": 18}
        {"type": "error", "message": "..."}
    """
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        url = data.get("url", "")
        choice = data.get("choice", "3")

        async def send_event(event):
            try:
                await websocket.send_json(event)
            except Exception:
                pass

        await run_scraper(url, choice, send_event)

    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("Falha inesperada no WebSocket de coleta")
        try:
            await websocket.send_json({"type": "error", "message": "Falha interna na coleta."})
        except Exception:
            pass
