from __future__ import annotations
from dataclasses import dataclass
from importlib.util import find_spec

@dataclass(frozen=True, slots=True)
class ProviderProbe:
    name: str
    installed: bool
    role: str
    note: str

def probe_providers() -> list[ProviderProbe]:
    """Probe optional reusable providers without importing vendor DLLs."""
    candidates = [
        ("J2534", "j2534-api", "PassThru provider", "Preferred reusable J2534 implementation; bench validation required."),
        ("J2534_REGISTRY", "j2534-api", "registry provider", "Reusable Windows PassThru registry enumeration."),
        ("can", "python-can", "CAN abstraction", "Planned normalized CAN/log interoperability."),
        ("cantools", "cantools", "DBC decoder", "Planned provenance-aware DBC decoding."),
        ("udsoncan", "udsoncan", "UDS client", "Future explicit active diagnostics mode only."),
        ("isotp", "python-can-isotp", "ISO-TP", "Future active diagnostics transport."),
    ]
    result=[]
    for module, package, role, note in candidates:
        try: installed=find_spec(module) is not None
        except (ImportError, AttributeError, ValueError): installed=False
        result.append(ProviderProbe(package,installed,role,note))
    return result
