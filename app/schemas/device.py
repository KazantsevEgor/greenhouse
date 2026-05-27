from enum import Enum
from pydantic import BaseModel

from .sensor import PositionSchema


class DeviceType(str, Enum):
    HEATER = "heater"
    AIR_CONDITIONER = "air_conditioner"
    HUMIDIFIER = "humidifier"
    FERTILIZER_DISPENSER = "fertilizer_dispenser"
    NUTRIENT_DISPENSER = "nutrient_dispenser"
    LIGHT_SOURCE = "light_source"


class DeviceCreate(BaseModel):
    type: DeviceType
    position: PositionSchema


class DeviceResponse(BaseModel):
    id: str
    type: DeviceType
    position: PositionSchema
    is_on: bool
    name: str
