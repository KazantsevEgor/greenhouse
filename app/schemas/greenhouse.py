from typing import List, Optional
from pydantic import BaseModel

from .sensor import SensorResponse
from .device import DeviceResponse
from .growth_plan import GrowthPlanResponse


class GreenhouseCreate(BaseModel):
    name: str
    width: float = 10.0
    height: float = 8.0


class GreenhouseResponse(BaseModel):
    id: str
    name: str
    width: float
    height: float
    sensors: List[SensorResponse]
    devices: List[DeviceResponse]
    growth_plan: Optional[GrowthPlanResponse]
    is_running: bool
