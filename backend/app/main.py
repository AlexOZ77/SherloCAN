from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api.capture import router as capture_router

app = FastAPI(title="SherloCAN", version="0.2.0-alpha")
app.include_router(capture_router)

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": "SherloCAN", "version": "0.2.0-alpha"}

static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    assets = static_dir / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        candidate = static_dir / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(static_dir / "index.html")
