from fastapi import APIRouter
from ..capture.replay import FileReplayAdapter

router = APIRouter(prefix="/capture", tags=["capture"])

@router.get("/capabilities")
def capabilities() -> dict:
    return {
        "mode": "application-read-only",
        "adapters": ["file-replay"],
        "j2534": "planned",
        "arbitrary_can_transmit": False,
    }

@router.get("/adapters")
def adapters() -> list[dict]:
    adapter = FileReplayAdapter()
    return [adapter.get_status()]
