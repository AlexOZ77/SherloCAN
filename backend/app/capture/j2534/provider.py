from __future__ import annotations
from dataclasses import dataclass
from importlib.util import find_spec

@dataclass(frozen=True, slots=True)
class ProviderProbe:
    name: str
    installed: bool
    role: str
    note: str

def _has(module: str) -> bool:
    try: return find_spec(module) is not None
    except (ImportError, AttributeError, ValueError): return False

def probe_providers() -> list[ProviderProbe]:
    """Probe optional reusable providers without importing vendor DLLs."""
    j2534_low=_has("J2534")
    j2534_registry=_has("J2534_REGISTRY")
    return [
        ProviderProbe("j2534-api",j2534_low and j2534_registry,"PassThru provider",
                      "Verified package modules: J2534 + J2534_REGISTRY; physical OpenPort validation still required."),
        ProviderProbe("python-can",_has("can"),"CAN abstraction","Normalized CAN/log interoperability."),
        ProviderProbe("cantools",_has("cantools"),"DBC decoder","Provenance-aware DBC decoding."),
        ProviderProbe("udsoncan",_has("udsoncan"),"UDS client","Future explicit active diagnostics mode only."),
        ProviderProbe("python-can-isotp",_has("isotp"),"ISO-TP","Future active diagnostics transport."),
    ]
