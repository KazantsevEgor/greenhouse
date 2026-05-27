from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator


class ParameterRangeSchema(BaseModel):
    min_val: float
    max_val: float
    target: float


class DayScheduleSchema(BaseModel):
    day: int
    temperature_day: ParameterRangeSchema
    temperature_night: ParameterRangeSchema
    light_hours: int
    humidity: ParameterRangeSchema
    ph: ParameterRangeSchema
    nutrient: ParameterRangeSchema


class GrowthPlanCreate(BaseModel):
    crop_name: str
    start_date: datetime
    total_days: int
    schedule: List[DayScheduleSchema]


class CurrentScheduleResponse(BaseModel):
    day: int
    temperature_day: ParameterRangeSchema
    temperature_night: ParameterRangeSchema
    light_hours: int
    humidity: ParameterRangeSchema
    ph: ParameterRangeSchema
    nutrient: ParameterRangeSchema
    is_light_time: bool


class GrowthPlanResponse(BaseModel):
    id: str
    crop_name: str
    start_date: datetime
    total_days: int
    current_day: int
    elapsed_days: int
    elapsed_hours: int
    current_schedule: Optional[CurrentScheduleResponse]
    schedule: List[DayScheduleSchema]
