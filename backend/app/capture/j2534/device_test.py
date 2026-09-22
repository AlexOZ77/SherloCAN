from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path
from .discovery import discover_j2534_devices
from .pe import dll_architecture, process_architecture, architecture_compatible
from .reuse_provider import status as reusable_status

@dataclass(frozen=True, slots=True)
class DeviceTestResult:
    name: str
    vendor: str
    dll_path: str
    driver_found: bool
    dll_exists: bool
    dll_architecture: str
    process_architecture: str
    architecture_compatible: bool | None
    reusable_provider_installed: bool
    device_opened: bool
    channel_connected: bool
    capture_validated: bool
    next_action: str

    def to_dict(self): return asdict(self)

def run_device_tests() -> list[DeviceTestResult]:
    """Non-invasive preflight. Never opens the J2534 device or vehicle bus."""
    provider=reusable_status()
    results=[]
    for device in discover_j2534_devices():
        exists=Path(device.dll_path).is_file()
        arch=dll_architecture(device.dll_path) if exists else "UNKNOWN"
        compatible=architecture_compatible(arch) if exists else None
        if not exists:
            action="Repair/reinstall the registered J2534 driver DLL."
        elif compatible is False:
            action=f"Use SherloCAN J2534 Bridge {arch}; do not load this DLL in the {process_architecture()} process."
        elif compatible is None:
            action="DLL architecture is unknown; block loading until manually validated."
        elif not provider.installed:
            action="Install the SherloCAN hardware dependency profile, then rerun Device Test."
        else:
            action="Preflight passed. Next gate: controlled PassThruOpen device test."
        results.append(DeviceTestResult(
            name=device.name,vendor=device.vendor,dll_path=device.dll_path,
            driver_found=True,dll_exists=exists,dll_architecture=arch,
            process_architecture=process_architecture(),
            architecture_compatible=compatible,
            reusable_provider_installed=provider.installed,
            device_opened=False,channel_connected=False,capture_validated=False,
            next_action=action,
        ))
    return results
