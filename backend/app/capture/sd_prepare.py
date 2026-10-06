from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


class SDPrepError(ValueError):
    pass


def inspect_target(root: Path) -> dict:
    resolved = root.resolve()
    if os.name != "nt":
        return {"root": str(root), "supported": False, "safe_target": False, "reason": "SD preparation is supported on Windows only"}
    drive = resolved.drive.upper()
    system_drive = os.environ.get("SystemDrive", "C:").upper()
    if not drive or drive == system_drive:
        return {"root": str(root), "supported": True, "safe_target": False, "reason": "system drive or invalid removable target"}
    try:
        usage = shutil.disk_usage(resolved)
    except OSError as exc:
        raise SDPrepError(str(exc)) from exc
    return {
        "root": drive + "\\", "supported": True, "safe_target": True,
        "reason": "explicit non-system drive", "size_bytes": usage.total,
        "formatting": {
            "automatic": False, "required_filesystem": "FAT32",
            "label_suggestion": "SHERLOCAN",
            "windows_steps": [
                "Open File Explorer and confirm the selected drive letter.",
                "Right-click the microSD drive and choose Format.",
                "Select FAT32 when available; do not select another drive.",
                "Optionally set volume label SHERLOCAN, then start formatting.",
                "After Windows reports completion, return to SherloCAN and click Re-check SD.",
            ],
        },
    }


def write_configuration(root: Path, text: str, filename: str = "logcfg.txt") -> dict:
    info = inspect_target(root)
    if not info.get("supported") or not info.get("safe_target"):
        raise SDPrepError(info["reason"])
    if filename.lower() != "logcfg.txt":
        raise SDPrepError("configuration filename must be logcfg.txt")
    target = Path(info["root"]) / "logcfg.txt"
    target.write_text(text, encoding="ascii", errors="strict")
    actual = target.read_text(encoding="ascii")
    if actual != text:
        raise SDPrepError("configuration verification failed after write")
    manifest = {
        "prepared_by": "SherloCAN", "config": "logcfg.txt",
        "verified_after_write": True, "automatic_formatting": False,
        "instruction": "Safely eject the card, insert it into OpenPort 2.0, then connect OpenPort to the vehicle for the configured standalone logging mode.",
    }
    (Path(info["root"]) / "sherlocan_sd.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"root": info["root"], "config_path": str(target), "verified": True, "manifest": manifest}
