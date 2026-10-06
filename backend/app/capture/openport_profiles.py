from __future__ import annotations

from dataclasses import dataclass, asdict
from .openport_sd import build_obd01_template, validate_logcfg


@dataclass(frozen=True, slots=True)
class LoggingProfile:
    id: str
    name: str
    description: str
    status: str
    mode: str
    params: tuple[str, ...] = ()
    editable: bool = False
    warning: str = ""

    def to_dict(self) -> dict:
        result = asdict(self)
        result["params"] = list(self.params)
        return result


PROFILES = (
    LoggingProfile("obd-basic", "OBD · базовый контроль", "RPM, скорость и температура ОЖ.", "READY", "ACTIVE_OBD", ("rpm","speed","coolant")),
    LoggingProfile("obd-start", "OBD · запуск двигателя", "RPM и температура ОЖ для короткого сценария запуска.", "READY", "ACTIVE_OBD", ("rpm","coolant")),
    LoggingProfile("obd-road", "OBD · контрольная поездка", "RPM и скорость для продолжительного дорожного лога.", "READY", "ACTIVE_OBD", ("rpm","speed")),
    LoggingProfile("raw-can", "RAW CAN · пассивный", "Заготовка для проверенной standalone RAW CAN конфигурации OpenPort.", "REQUIRES_VERIFIED_CONFIG", "PASSIVE_RAW_CAN", (), True, "SherloCAN does not invent unverified OpenPort RAW CAN syntax."),
    LoggingProfile("custom", "Пользовательский профиль", "Свободный logcfg.txt: вставьте или отредактируйте собственную проверенную конфигурацию.", "CUSTOM", "USER_DEFINED", (), True, "Configuration is validated structurally before SD write; vehicle/protocol correctness remains the operator's responsibility."),
)


def list_profiles() -> list[dict]:
    return [p.to_dict() for p in PROFILES]


def render_profile(profile_id: str) -> dict:
    profile = next((p for p in PROFILES if p.id == profile_id), None)
    if profile is None:
        raise ValueError("unknown logging profile")
    content = build_obd01_template(list(profile.params)) if profile.status == "READY" else ""
    return {**profile.to_dict(), "filename": "logcfg.txt", "content": content}


def validate_custom_profile(text: str) -> dict:
    check = validate_logcfg(text, "logcfg.txt")
    return {
        "valid": check.valid,
        "filename_ok": check.filename_ok,
        "type_name": check.type_name,
        "protocol_id": check.protocol_id,
        "warnings": check.warnings,
        "features": check.features,
        "status": "CUSTOM_VALIDATED" if check.valid else "CUSTOM_INVALID",
        "vehicle_protocol_verified": False,
    }
