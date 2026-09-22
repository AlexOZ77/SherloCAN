from fastapi import FastAPI
from .api.capture import router as capture_router

app = FastAPI(
    title="SherloCAN API",
    version="0.2.0-alpha",
    description="Evidence-first automotive CAN investigation platform.",
)
app.include_router(capture_router, prefix="/api")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.2.0-alpha"}
