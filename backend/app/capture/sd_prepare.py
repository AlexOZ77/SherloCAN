from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


class SDPrepError(ValueError):
    pass


def inspect_target(root: Path) -> dict:
    resolved = root.resolve()
    if os.name != "nt":
        return {"root": str(root), "supported": False, "safe_to_format": False, "reason": "SD preparation is supported on Windows only"}
    drive = resolved.drive.upper()
    system_drive = os.environ.get("SystemDrive", "C:").upper()
    if not drive or drive == system_drive:
        return {"root": str(root), "supported": True, "safe_to_format": False, "reason": "system drive or invalid removable target"}
    try:
        usage = shutil.disk_usage(resolved)
    except OSError as exc:
        raise SDPrepError(str(exc)) from exc
    return {"root": drive + "\\", "supported": True, "safe_to_format": True, "reason": "explicit non-system drive", "size_bytes": usage.total}


def format_fat32(root: Path, confirmation: str) -> dict:
    info = inspect_target(root)
    expected = f"FORMAT {info['root']}"
    if not info.get("safe_to_format"):
        raise SDPrepError(info["reason"])
    if confirmation.strip().upper() != expected.upper():
        raise SDPrepError(f"confirmation must exactly match: {expected}")
    drive = Path(info["root"]).drive
    proc = subprocess.run(
        ["format.com", drive, "/FS:FAT32", "/Q", "/V:SHERLOCAN", "/Y"],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0:
        raise SDPrepError((proc.stderr or proc.stdout or "format failed").strip())
    return {**inspect_target(Path(info["root"])), "formatted": True, "filesystem_requested": "FAT32", "label_requested": "SHERLOCAN"}


def write_configuration(root: Path, text: str, filename: str = "logcfg.txt") -> dict:
    info = inspect_target(root)
    if not info.get("supported"):
        raise SDPrepError(info["reason"])
    if filename.lower() != "logcfg.txt":
        raise SDPrepError("configuration filename must be logcfg.txt")
    target = Path(info["root"]) / "logcfg.txt"
    target.write_text(text, encoding="ascii", errors="strict")
    actual = target.read_text(encoding="ascii")
    if actual != text:
        raise SDPrepError("configuration verification failed after write")
    manifest = {
        "prepared_by": "SherloCAN",
        "config": "logcfg.txt",
        "verified_after_write": True,
        "instruction": "Safely eject the card, insert it into OpenPort 2.0, then connect OpenPort to the vehicle for the configured standalone logging mode.",
    }
    (Path(info["root"]) / "sherlocan_sd.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"root": info["root"], "config_path": str(target), "verified": True, "manifest": manifest}
