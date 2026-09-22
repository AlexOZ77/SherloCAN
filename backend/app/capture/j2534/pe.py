from __future__ import annotations
import struct
from pathlib import Path

PE_MACHINE_I386 = 0x014C
PE_MACHINE_AMD64 = 0x8664

def dll_architecture(path: str | Path) -> str:
    """Read PE headers without loading/executing the vendor DLL."""
    p=Path(path)
    with p.open("rb") as f:
        if f.read(2) != b"MZ":
            return "UNKNOWN"
        f.seek(0x3C)
        raw=f.read(4)
        if len(raw)!=4: return "UNKNOWN"
        pe_offset=struct.unpack("<I",raw)[0]
        f.seek(pe_offset)
        if f.read(4) != b"PE\0\0": return "UNKNOWN"
        machine_raw=f.read(2)
        if len(machine_raw)!=2: return "UNKNOWN"
        machine=struct.unpack("<H",machine_raw)[0]
    if machine==PE_MACHINE_I386: return "x86"
    if machine==PE_MACHINE_AMD64: return "x64"
    return f"OTHER_0x{machine:04X}"

def process_architecture() -> str:
    return "x64" if struct.calcsize("P")==8 else "x86"

def architecture_compatible(dll_arch: str) -> bool | None:
    if dll_arch not in {"x86","x64"}: return None
    return dll_arch == process_architecture()
