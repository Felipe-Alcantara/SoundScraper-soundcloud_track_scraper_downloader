"""
Rota de Scraping — coleta links de faixas do SoundCloud.
Expõe endpoints REST e um WebSocket para progresso em tempo real.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from backend.services.scraper_service import run_scraper

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────
class ScrapeRequest(BaseModel):
    """Payload para iniciar uma coleta de faixas."""
    url: str = Field(..., description="URL do perfil/playlist do SoundCloud")
    choice: str = Field("3", description="Opção: 1=Todas, 2=Populares, 3=Faixas, 4=Álbuns, 5=Playlists, 6=Reposts, 7=Curtidas")


class ScrapeResponse(BaseModel):
    """Resposta com os links coletados."""
    success: bool
    tracks: list[str] = []
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
    except Exception as e:
        return ScrapeResponse(success=False, message=str(e))


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
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
