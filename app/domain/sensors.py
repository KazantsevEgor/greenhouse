from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List
import random
import uuid


class SensorType(str, Enum):
    TEMPERATURE_AIR = "temperature_air"
    TEMPERATURE_WATER = "temperature_water"
    HUMIDITY = "humidity"
    PH = "ph"
    LIGHT = "light"
    NUTRIENT = "nutrient"


_UNITS: dict[SensorType, str] = {
    SensorType.TEMPERATURE_AIR: "°C",
    SensorType.TEMPERATURE_WATER: "°C",
    SensorType.HUMIDITY: "%",
    SensorType.PH: "pH",
    SensorType.LIGHT: "lux",
    SensorType.NUTRIENT: "mg/L",
}


@dataclass
class Position:
    x: float
    y: float


class Sensor(ABC):
    def __init__(
        self,
        sensor_type: SensorType,
        position: Position,
        min_range: float,
        max_range: float,
        sensor_id: str | None = None,
    ) -> None:
        self.id: str = sensor_id or str(uuid.uuid4())
        self.type = sensor_type
        self.position = position
        self._min_range = min_range
        self._max_range = max_range
        self._current_value: float = round((min_range + max_range) / 2, 1)

    @property
    def current_value(self) -> float:
        return self._current_value

    @property
    def unit(self) -> str:
        return _UNITS.get(self.type, "")

    @abstractmethod
    def read(self) -> float:
        """Read (or emulate) the sensor value and return it."""


class PassiveSensor(Sensor):
    """Reports value only when polled."""

    def read(self) -> float:
        self._current_value = round(
            random.uniform(self._min_range, self._max_range), 1
        )
        return self._current_value


class ActiveSensor(Sensor):
    """Monitors its parameter and notifies observers when deviation exceeds threshold."""

    def __init__(
        self,
        sensor_type: SensorType,
        position: Position,
        min_range: float,
        max_range: float,
        target: float,
        threshold: float,
        sensor_id: str | None = None,
    ) -> None:
        super().__init__(sensor_type, position, min_range, max_range, sensor_id)
        self._target = target
        self._threshold = threshold
        self._current_value = target
        self.is_alert: bool = False
        self._observers: List[Callable[["ActiveSensor"], None]] = []

    def add_observer(self, observer: Callable[["ActiveSensor"], None]) -> None:
        self._observers.append(observer)

    def remove_observer(self, observer: Callable[["ActiveSensor"], None]) -> None:
        self._observers.remove(observer)

    def update_target(self, target: float, threshold: float | None = None) -> None:
        self._target = target
        if threshold is not None:
            self._threshold = threshold

    def read(self) -> float:
        self._current_value = round(
            random.uniform(self._min_range, self._max_range), 1
        )
        if abs(self._current_value - self._target) > self._threshold:
            self.is_alert = True
            for observer in self._observers:
                observer(self)
        else:
            self.is_alert = False
        return self._current_value
