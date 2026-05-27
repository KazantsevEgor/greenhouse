from enum import Enum
from typing import Optional
from pydantic import BaseModel, model_validator


class SensorType(str, Enum):
    TEMPERATURE_AIR = "temperature_air"
    TEMPERATURE_WATER = "temperature_water"
    HUMIDITY = "humidity"
    PH = "ph"
    LIGHT = "light"
    NUTRIENT = "nutrient"


class SensorMode(str, Enum):
    PASSIVE = "passive"
    ACTIVE = "active"


class PositionSchema(BaseModel):
    x: float
    y: float


class SensorCreate(BaseModel):
    type: SensorType
    mode: SensorMode = SensorMode.PASSIVE
    position: PositionSchema
    min_range: float
    max_range: float
    target: Optional[float] = None
    threshold: Optional[float] = None

    @model_validator(mode="after")
    def active_requires_target_and_threshold(self) -> "SensorCreate":
        if self.mode == SensorMode.ACTIVE:
            if self.target is None or self.threshold is None:
                raise ValueError("Active sensors require 'target' and 'threshold'.")
        return self


class SensorResponse(BaseModel):
    id: str
    type: SensorType
    mode: SensorMode
    position: PositionSchema
    current_value: float
    unit: str
    is_alert: bool = False
