"""
SoundScraper — FastAPI Application
Ponto de entrada do backend. Serve a API REST + WebSocket
e, em produção, serve os arquivos estáticos do frontend.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import scraper, download, config


logger = logging.getLogger(__name__)


# ── Lifecycle ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup / shutdown do servidor."""
    logger.info("SoundScraper API iniciada")
    yield
    logger.info("SoundScraper API encerrada")


# ── App ────────────────────────────────────────────────────────────
app = FastAPI(
    title="SoundScraper API",
    description="Backend do SoundScraper — coleta e download de faixas do SoundCloud",
    version="3.0.0",
    lifespan=lifespan,
)

# ── CORS (permite o Vite dev server em localhost:5173) ─────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev
        "http://127.0.0.1:5173",
        "http://localhost:8000",   # Produção
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# ── Rotas da API ───────────────────────────────────────────────────
app.include_router(scraper.router, prefix="/api", tags=["Scraper"])
app.include_router(download.router, prefix="/api", tags=["Download"])
app.include_router(config.router, prefix="/api", tags=["Config"])

# ── Frontend estático (produção) ──────────────────────────────────
# Em produção o frontend buildado fica em frontend/dist/
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
