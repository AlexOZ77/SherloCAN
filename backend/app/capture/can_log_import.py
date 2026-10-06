from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .base import CANFrame

SUPPORTED_EXTENSIONS = {".csv", ".log", ".txt"}
MAX_IMPORT_BYTES = 50 * 1024 * 1024
_CANDUMP = re.compile(
    r"^\s*(?:\((?P<ts>\d+(?:\.\d+)?)\)\s+)?(?P<channel>\S+)\s+(?P<id>[0-9A-Fa-f]{1,8})#(?P<data>[0-9A-Fa-f]*)\s*$"
)


class CANLogImportError(ValueError):
    pass


def _parse_id(value: str) -> int:
    text = value.strip()
    if not text:
        raise CANLogImportError("CAN ID is empty")
    if text.lower().startswith("0x"):
        return int(text, 16)
    # CAN logs commonly write IDs as bare hexadecimal (e.g. 7DF, 1A0).
    base = 16 if any(c in "abcdefABCDEF" for c in text) else 10
    return int(text, base)


def _frame(timestamp: str, can_id: str, data: str, channel: str = "primary_can",
           is_extended: str = "false") -> CANFrame:
    try:
        payload_text = data.replace(" ", "").replace("-", "")
        payload = bytes.fromhex(payload_text)
        cid = _parse_id(can_id)
        ts = float(timestamp)
    except (ValueError, TypeError) as exc:
        raise CANLogImportError(str(exc)) from exc
    if not 0 <= cid <= 0x1FFFFFFF:
        raise CANLogImportError(f"CAN ID out of range: {can_id}")
    if len(payload) > 64:
        raise CANLogImportError("payload exceeds CAN/CAN-FD maximum of 64 bytes")
    return CANFrame(
        timestamp=ts,
        can_id=cid,
        data=payload,
        channel=channel or "primary_can",
        is_extended=str(is_extended).strip().lower() in {"1", "true", "yes"} or cid > 0x7FF,
    )


def _parse_csv(text: str) -> list[CANFrame]:
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise CANLogImportError("CSV header is missing")
    aliases = {name.strip().lower(): name for name in reader.fieldnames}
    ts_key = aliases.get("timestamp") or aliases.get("time")
    id_key = aliases.get("can_id") or aliases.get("id")
    data_key = aliases.get("data") or aliases.get("payload")
    if not (ts_key and id_key and data_key):
        raise CANLogImportError("CSV must contain timestamp/time, can_id/id and data/payload columns")
    channel_key = aliases.get("channel")
    extended_key = aliases.get("is_extended") or aliases.get("extended")
    frames: list[CANFrame] = []
    for line_no, row in enumerate(reader, start=2):
        if not any((v or "").strip() for v in row.values()):
            continue
        try:
            frames.append(_frame(
                row.get(ts_key, ""), row.get(id_key, ""), row.get(data_key, ""),
                row.get(channel_key, "primary_can") if channel_key else "primary_can",
                row.get(extended_key, "false") if extended_key else "false",
            ))
        except CANLogImportError as exc:
            raise CANLogImportError(f"line {line_no}: {exc}") from exc
    return frames


def _parse_candump(text: str) -> list[CANFrame]:
    frames: list[CANFrame] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith(("#", ";")):
            continue
        match = _CANDUMP.match(line)
        if not match:
            raise CANLogImportError(f"line {line_no}: unsupported candump/log syntax")
        frames.append(_frame(
            match.group("ts") or str(len(frames)),
            "0x" + match.group("id"),
            match.group("data"),
            match.group("channel"),
        ))
    return frames


def parse_can_log(filename: str, content: bytes) -> tuple[str, list[CANFrame]]:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise CANLogImportError(f"unsupported CAN log extension: {suffix or '<none>'}")
    if not content:
        raise CANLogImportError("CAN log is empty")
    if len(content) > MAX_IMPORT_BYTES:
        raise CANLogImportError("CAN log exceeds 50 MiB import limit")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CANLogImportError("CAN log must be UTF-8 text") from exc
    if suffix == ".csv":
        frames = _parse_csv(text)
        fmt = "SHERLOCAN_CSV"
    else:
        frames = _parse_candump(text)
        fmt = "CANDUMP_TEXT"
    if not frames:
        raise CANLogImportError("CAN log contains no frames")
    return fmt, frames


def import_can_log(filename: str, content: bytes, dest_root: Path) -> dict:
    fmt, frames = parse_can_log(filename, content)
    session_id = "import-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder = dest_root / "imports" / session_id
    folder.mkdir(parents=True, exist_ok=False)

    source_name = Path(filename).name or "can.log"
    source_path = folder / source_name
    source_path.write_bytes(content)
    source_sha256 = hashlib.sha256(content).hexdigest()

    normalized = folder / "frames.csv"
    with normalized.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "can_id", "data", "channel", "is_extended"])
        for frame in frames:
            writer.writerow([
                f"{frame.timestamp:.9f}", hex(frame.can_id), frame.data.hex().upper(),
                frame.channel, str(frame.is_extended).lower(),
            ])

    timestamps = [f.timestamp for f in frames]
    can_ids = {f.can_id for f in frames}
    meta = {
        "session_id": session_id,
        "source_kind": "CAN_LOG_IMPORT",
        "original_name": source_name,
        "source_format": fmt,
        "source_path": str(source_path),
        "normalized_path": str(normalized),
        "sha256": source_sha256,
        "size_bytes": len(content),
        "frame_count": len(frames),
        "unique_can_ids": len(can_ids),
        "first_timestamp": min(timestamps),
        "last_timestamp": max(timestamps),
        "parsed": True,
        "read_only": True,
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "interpretation": "Imported frames normalized to SherloCAN CANFrame schema; no ECU ownership inferred.",
    }
    (folder / "import.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta
