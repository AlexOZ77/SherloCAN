from __future__ import annotations
from dataclasses import dataclass
from importlib.util import find_spec

@dataclass(frozen=True, slots=True)
class ReusableJ2534Status:
    installed: bool
    registry_module: bool
    low_level_module: bool
    version: str | None
    validated_on_openport: bool = False

def status() -> ReusableJ2534Status:
    """Inspect j2534-api availability without opening hardware or a vendor DLL."""
    low=find_spec("J2534") is not None
    registry=find_spec("J2534_REGISTRY") is not None
    version=None
    if low or registry:
        try:
            from importlib.metadata import version as package_version
            version=package_version("j2534-api")
        except Exception:
            version=None
    return ReusableJ2534Status(
        installed=low and registry,
        registry_module=registry,
        low_level_module=low,
        version=version,
    )

def list_devices() -> list[dict]:
    """Use the reusable package only when installed; no hardware connection occurs."""
    s=status()
    if not s.installed:
        return []
    from J2534_REGISTRY import get_all_j2534_devices
    devices=[]
    for d in get_all_j2534_devices():
        devices.append({
            "name": getattr(d,"name","UNKNOWN"),
            "vendor": getattr(d,"vendor","UNKNOWN"),
            "dll_path": str(getattr(d,"function_library_path","")),
            "source": "j2534-api/J2534_REGISTRY",
        })
    return devices
