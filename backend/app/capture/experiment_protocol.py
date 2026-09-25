from __future__ import annotations
from dataclasses import asdict,dataclass
from typing import Literal

Scenario=Literal["NORMAL_A","FAULT_B","WIGGLE","CONTROL"]

@dataclass(frozen=True,slots=True)
class ExperimentProtocol:
    scenario:Scenario
    trial:int
    ignition_state:str
    engine_state:str
    battery_voltage_v:float|None
    bitrate:int
    bitrate_source:str
    provider_index:int
    max_frames:int
    timeout_ms:int
    operator_note:str=""

    def validate(self)->None:
        if self.trial<1: raise ValueError("trial must be >= 1")
        if self.bitrate<=0: raise ValueError("bitrate must be explicit and > 0")
        if not self.bitrate_source.strip(): raise ValueError("bitrate_source is required")
        if self.provider_index<0: raise ValueError("provider_index must be >= 0")
        if self.max_frames<=0: raise ValueError("max_frames must be > 0")
        if self.timeout_ms<=0: raise ValueError("timeout_ms must be > 0")
        if self.battery_voltage_v is not None and self.battery_voltage_v<=0:
            raise ValueError("battery_voltage_v must be > 0 when provided")

    def to_dict(self)->dict:
        self.validate()
        return asdict(self)
