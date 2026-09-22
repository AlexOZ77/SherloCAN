from pathlib import Path
from fastapi import APIRouter
from ..capture.anomaly import build_baseline, detect_long_gaps
from ..capture.replay import FileReplayAdapter\nfrom ..capture.j2534 import J2534Adapter
from ..capture.j2534.provider import probe_providers
from ..capture.j2534.device_test import run_device_tests

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
