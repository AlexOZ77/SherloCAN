from __future__ import annotations

import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path

MAX_IMPORT_BYTES = 25 * 1024 * 1024


class FNIRSIImportError(ValueError):
    pass


def inspect_bmp(filename: str, content: bytes) -> dict:
    if Path(filename).suffix.lower() != ".bmp":
        raise FNIRSIImportError("FNIRSI phase-A importer accepts BMP evidence only")
    if not content:
        raise FNIRSIImportError("FNIRSI artifact is empty")
    if len(content) > MAX_IMPORT_BYTES:
        raise FNIRSIImportError("FNIRSI artifact exceeds 25 MiB import limit")
    if len(content) < 54 or content[:2] != b"BM":
        raise FNIRSIImportError("invalid BMP header")
    declared_size = struct.unpack_from("<I", content, 2)[0]
    pixel_offset = struct.unpack_from("<I", content, 10)[0]
    dib_size = struct.unpack_from("<I", content, 14)[0]
    if dib_size < 40 or len(content) < 14 + dib_size:
        raise FNIRSIImportError("unsupported or truncated BMP DIB header")
    width = struct.unpack_from("<i", content, 18)[0]
    height = struct.unpack_from("<i", content, 22)[0]
    planes = struct.unpack_from("<H", content, 26)[0]
    bits_per_pixel = struct.unpack_from("<H", content, 28)[0]
    compression = struct.unpack_from("<I", content, 30)[0]
    if width <= 0 or height == 0 or planes != 1:
        raise FNIRSIImportError("invalid BMP geometry")
    if pixel_offset >= len(content):
        raise FNIRSIImportError("BMP pixel offset is outside the artifact")
    if declared_size and declared_size > len(content):
        raise FNIRSIImportError("truncated BMP artifact")
    return {
        "artifact_format": "BMP",
        "width_px": width,
        "height_px": abs(height),
        "top_down": height < 0,
        "bits_per_pixel": bits_per_pixel,
        "compression": compression,
        "pixel_offset": pixel_offset,
        "declared_size": declared_size,
    }


def import_fnirsi_bmp(filename: str, content: bytes, dest_root: Path, can_session_id: str | None = None) -> dict:
    bmp = inspect_bmp(filename, content)
    session_id = "fnirsi-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder = dest_root / "fnirsi" / session_id
    folder.mkdir(parents=True, exist_ok=False)

    source_name = Path(filename).name or "fnirsi.bmp"
    source_path = folder / source_name
    source_path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()

    meta = {
        "session_id": session_id,
        "source_kind": "FNIRSI_2C53T_RENDERED_WAVEFORM",
        "device_model": "FNIRSI 2C53T",
        "original_name": source_name,
        "source_path": str(source_path),
        "sha256": digest,
        "size_bytes": len(content),
        "read_only": True,
        "raw_adc_samples": False,
        "interpretation_status": "RENDERED_EVIDENCE",
        "can_session_id": can_session_id,
        "sync_status": "MANUAL_REQUIRED" if can_session_id else "UNLINKED",
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "bmp": bmp,
        "interpretation": "Saved BMP is rendered waveform evidence, not raw ADC samples. Numeric waveform reconstruction and automatic CAN time alignment are not claimed.",
    }
    (folder / "import.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta
