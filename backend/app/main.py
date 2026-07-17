from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .agent import discover
from .models import DiscoverRequest, DiscoverResult

app = FastAPI(title="Jobnova Company Career Agent", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
frontend = Path(__file__).resolve().parents[2] / "frontend"
if frontend.exists(): app.mount("/static", StaticFiles(directory=frontend), name="static")

@app.get("/api/v1/health")
def health(): return {"status": "ok", "version": "3.0.0"}

@app.post("/api/v1/discover", response_model=DiscoverResult)
async def discover_route(request: DiscoverRequest):
    return await discover(str(request.linkedin_url), request.show_browser)

@app.get("/")
def index(): return FileResponse(frontend / "index.html")
