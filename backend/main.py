from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os

from backend.routers import ingest, search, export, settings as settings_router, notes as notes_router
from backend.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Kevin Second Brain Backend API (FastAPI + 10 Models Support)"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(export.router)
app.include_router(settings_router.router)
app.include_router(notes_router.router)

# Serve Frontend
# Mount frontend folder for potential JS/CSS assets
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    # Return the Single Page Application
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_provider": settings.ai_provider,
        "vault_path": settings.obsidian_vault_path,
        "version": settings.app_version
    }
