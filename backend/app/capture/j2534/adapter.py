from __future__ import annotations
from typing import Iterator
from ..base import CANFrame, CaptureAdapter
from .discovery import discover_j2534_devices

class J2534Adapter(CaptureAdapter):
    """Hardware boundary. Discovery works first; capture stays gated until DLL/API validation."""
    def __init__(self):
        self.device=None
        self._state="closed"

    def discover(self)->list[dict]:
        return [x.to_dict() for x in discover_j2534_devices()]

    def open(self,**config)->None:
        dll_path=config.get("dll_path")
        if not dll_path: raise ValueError("dll_path is required")
        matches=[x for x in discover_j2534_devices() if x.dll_path==dll_path]
        if not matches: raise RuntimeError("J2534 DLL is not registered/available")
        self.device=matches[0]
        self._state="discovered"

    def start(self)->Iterator[CANFrame]:
        raise NotImplementedError("Live J2534 capture is gated pending PassThru API/device validation")

    def stop(self)->None: self._state="stopped"
    def close(self)->None: self.device=None; self._state="closed"
    def get_status(self)->dict:
        return {"id":"j2534","name":self.device.name if self.device else "J2534 PassThru","state":self._state}
    def get_capabilities(self)->dict:
        return {"read":False,"transmit":False,"discovery":True,"live_capture":"VALIDATION_REQUIRED"}
