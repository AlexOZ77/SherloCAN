from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator

@dataclass(frozen=True, slots=True)
class CANFrame:
    timestamp: float
    can_id: int
    data: bytes
    channel: str = "primary_can"
    is_extended: bool = False

    @property
    def dlc(self) -> int:
        return len(self.data)

class CaptureAdapter(ABC):
    """Read-only capture source contract for SherloCAN."""

    @abstractmethod
    def discover(self) -> list[dict]: ...

    @abstractmethod
    def open(self, **config) -> None: ...

    @abstractmethod
    def start(self) -> Iterator[CANFrame]: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def get_status(self) -> dict: ...

    @abstractmethod
    def get_capabilities(self) -> dict: ...
