from pathlib import Path
from fastapi import APIRouter
from ..capture.anomaly import build_baseline, detect_long_gaps
from ..capture.replay import FileReplayAdapter\nfrom ..capture.j2534 import J2534Adapter
from ..capture.j2534.provider import probe_providers
from ..capture.j2534.device_test import run_device_tests
from ..capture.j2534.open_test import run_open_test
from ..capture.j2534.channel_test import run_channel_test
from ..capture.j2534.controller import CaptureRequest, run_bounded_capture
from ..capture.j2534.atomic_capture import AtomicCaptureRequest, run_atomic_capture
from ..capture.experiments import load_sessions, save_session, compare_sessions

router = APIRouter(prefix="/capture", tags=["capture"])

@router.get("/capabilities")
def capabilities() -> dict:
    return {
        "mode": "application-read-only",
        "adapters": ["file-replay", "j2534"],
        "j2534": "preflight-enabled",
        "arbitrary_can_transmit": False,
    }

@router.get("/adapters")
def adapters() -> list[dict]:
    replay = FileReplayAdapter()
    j2534 = J2534Adapter()
    return [replay.get_status(), j2534.get_status()]

@router.get("/j2534/providers")
def j2534_providers() -> list[dict]:
    return [{"name":p.name,"installed":p.installed,"role":p.role,"note":p.note} for p in probe_providers()]

@router.get("/j2534/devices")
def j2534_devices() -> list[dict]:
    return J2534Adapter().discover()

@router.get("/j2534/device-test")
def j2534_device_test() -> list[dict]:
    return [r.to_dict() for r in run_device_tests()]

@router.post("/j2534/open-test")
def j2534_open_test(provider_index: int = 0) -> dict:
    """Explicit hardware gate: PassThruOpen then immediate PassThruClose. No CAN channel is created."""
    return run_open_test(provider_index).to_dict()

@router.post("/j2534/channel-test")
def j2534_channel_test(provider_index: int = 0, protocol: str = "CAN", bitrate: int | None = None) -> dict:
    """Explicit raw CAN connect/disconnect gate. No diagnostic messages are transmitted."""
    if bitrate is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="bitrate is required; SherloCAN does not guess vehicle bitrate")
    return run_channel_test(provider_index, protocol, bitrate).to_dict()

@router.post("/j2534/capture")
def j2534_capture(provider_index: int, channel_id: int, bitrate: int, timeout_ms: int = 100, max_frames: int = 1000) -> dict:
    """Run one explicit bounded capture against an already-open raw CAN channel."""
    if bitrate <= 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="bitrate must be explicit and > 0")
    request = CaptureRequest(provider_index=provider_index, channel_id=channel_id, bitrate=bitrate, timeout_ms=timeout_ms, max_frames=max_frames)
    root = Path(__file__).resolve().parents[3] / "data" / "captures"
    return run_bounded_capture(request, root)

@router.post("/j2534/atomic-capture")
def j2534_atomic_capture(provider_index: int, bitrate: int, timeout_ms: int = 100, max_frames: int = 1000) -> dict:
    """Own Open→Connect→bounded Capture→Disconnect→Close in one request."""
    request = AtomicCaptureRequest(provider_index=provider_index, bitrate=bitrate, timeout_ms=timeout_ms, max_frames=max_frames)
    root = Path(__file__).resolve().parents[3] / "data" / "captures"
    return run_atomic_capture(request, root)

@router.get("/experiments")
def experiments_list() -> list[dict]:
    root = Path(__file__).resolve().parents[3] / "data" / "captures"
    return load_sessions(root)

@router.post("/experiments/save")
def experiments_save(session_id: str, role: str, note: str = "") -> dict:
    root = Path(__file__).resolve().parents[3] / "data" / "captures"
    session = next((s for s in load_sessions(root) if s["session_id"] == session_id), None)
    if session is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="session not found in experiment registry")
    return save_session(root, session, role, note)

@router.get("/experiments/compare")
def experiments_compare(a_session_id: str, b_session_id: str) -> dict:
    root = Path(__file__).resolve().parents[3] / "data" / "captures"
    sessions = load_sessions(root)
    a = next((s for s in sessions if s["session_id"] == a_session_id), None)
    b = next((s for s in sessions if s["session_id"] == b_session_id), None)
    if not a or not b:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="both registered sessions are required")
    return compare_sessions(a, b)

def _load_fixture(name: str):
    root = Path(__file__).resolve().parents[3]
    adapter = FileReplayAdapter()
    adapter.open(path=root / "sample_data" / name)
    frames = list(adapter.start())
    adapter.close()
    return frames

@router.get("/demo-analysis")
def demo_analysis() -> dict:
    """Runnable synthetic vertical slice. No IDs here represent Nissan mappings."""
    normal = _load_fixture("j11_synthetic_normal.csv")
    fault = _load_fixture("j11_synthetic_fault.csv")
    baseline = build_baseline(normal)
    anomalies = detect_long_gaps(fault, baseline, ratio=3.0)
    return {
        "synthetic": True,
        "vehicle_label": "Nissan Qashqai J11 — synthetic diagnostic fixture",
        "source": "File Replay",
        "safety": "READ-ONLY",
        "baseline": {
            hex(can_id): {
                "count": item.count,
                "median_period_ms": round(item.median_period * 1000, 3) if item.median_period else None,
                "typical_dlc": item.typical_dlc,
            }
            for can_id, item in baseline.items()
        },
        "anomalies": [
            {
                "kind": item.kind,
                "can_id": hex(item.can_id),
                "timestamp": item.timestamp,
                "detail": item.detail,
                "ecu_owner": "UNKNOWN",
            }
            for item in anomalies
        ],
        "interpretation": "Observed timing anomaly only; root cause is not assigned.",
    }
