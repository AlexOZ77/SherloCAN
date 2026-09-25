from __future__ import annotations
from datetime import datetime,timezone

def build_evidence_manifest(session:dict,protocol:dict|None=None,acceptance:dict|None=None)->dict:
    evidence=session.get("evidence") or {}
    return {
        "schema":"sherlocan.evidence-manifest.v1",
        "created_at":datetime.now(timezone.utc).isoformat(),
        "session_id":session.get("session_id"),
        "source_kind":"hardware" if session.get("device_opened") is not None else "unknown",
        "protocol":protocol or None,
        "capture":{
            "raw_path":evidence.get("raw_path"),
            "sha256":evidence.get("sha256"),
            "frames_observed":evidence.get("frames_observed"),
            "frames_accepted":evidence.get("frames_accepted"),
            "frames_dropped":evidence.get("frames_dropped"),
            "unique_ids":evidence.get("unique_ids"),
            "capture_data_loss":evidence.get("capture_data_loss"),
        },
        "lifecycle":{
            "device_opened":session.get("device_opened"),
            "channel_connected":session.get("channel_connected"),
            "disconnected_cleanly":session.get("disconnected_cleanly"),
            "device_closed_cleanly":session.get("device_closed_cleanly"),
            "transmit_performed":session.get("transmit_performed"),
        },
        "acceptance":acceptance,
        "claims":{
            "traffic_confirmed":bool(evidence.get("frames_observed")),
            "ecu_ownership":"UNKNOWN",
            "causality":"NOT_ESTABLISHED",
        },
    }
