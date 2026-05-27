from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
import uuid

from .sensors import Position


class DeviceType(str, Enum):
    HEATER = "heater"
    AIR_CONDITIONER = "air_conditioner"
    HUMIDIFIER = "humidifier"
    FERTILIZER_DISPENSER = "fertilizer_dispenser"
    NUTRIENT_DISPENSER = "nutrient_dispenser"
    LIGHT_SOURCE = "light_source"


_DISPLAY_NAMES: dict[DeviceType, str] = {
    DeviceType.HEATER: "обогреватель",
    DeviceType.AIR_CONDITIONER: "кондиционер",
    DeviceType.HUMIDIFIER: "увлажнитель",
    DeviceType.FERTILIZER_DISPENSER: "дозатор удобрений",
    DeviceType.NUTRIENT_DISPENSER: "дозатор питательного раствора",
    DeviceType.LIGHT_SOURCE: "источник освещения",
}


class Device(ABC):
    def __init__(
        self,
        device_type: DeviceType,
        position: Position,
        device_id: str | None = None,
    ) -> None:
        self.id: str = device_id or str(uuid.uuid4())
        self.type = device_type
        self.position = position
        self.name: str = _DISPLAY_NAMES[device_type]
        self.is_on: bool = False

    def turn_on(self) -> None:
        self.is_on = True

    def turn_off(self) -> None:
        self.is_on = False

    @abstractmethod
    def device_label(self) -> str:
        """Human-readable label shown in UI."""


class Heater(Device):
    def __init__(self, position: Position, device_id: str | None = None) -> None:
        super().__init__(DeviceType.HEATER, position, device_id)

    def device_label(self) -> str:
        return "обогреватель"


class AirConditioner(Device):
    def __init__(self, position: Position, device_id: str | None = None) -> None:
        super().__init__(DeviceType.AIR_CONDITIONER, position, device_id)

    def device_label(self) -> str:
        return "кондиционер"


class Humidifier(Device):
    def __init__(self, position: Position, device_id: str | None = None) -> None:
        super().__init__(DeviceType.HUMIDIFIER, position, device_id)

    def device_label(self) -> str:
        return "увлажнитель"


class FertilizerDispenser(Device):
    def __init__(self, position: Position, device_id: str | None = None) -> None:
        super().__init__(DeviceType.FERTILIZER_DISPENSER, position, device_id)

    def device_label(self) -> str:
        return "дозатор удобрений"


class NutrientDispenser(Device):
    def __init__(self, position: Position, device_id: str | None = None) -> None:
        super().__init__(DeviceType.NUTRIENT_DISPENSER, position, device_id)

    def device_label(self) -> str:
        return "дозатор питательного раствора"


class LightSource(Device):
    def __init__(self, position: Position, device_id: str | None = None) -> None:
        super().__init__(DeviceType.LIGHT_SOURCE, position, device_id)

    def device_label(self) -> str:
        return "источник освещения"
