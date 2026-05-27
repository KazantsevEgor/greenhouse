"""
Functions that convert domain objects → Pydantic response schemas.
Kept here to avoid circular imports between routers.
"""

from app.domain.sensors import Sensor, ActiveSensor, PassiveSensor
from app.domain.devices import Device
from app.domain.growth_plan import GrowthPlan, DaySchedule, ParameterRange
from app.domain.greenhouse import Greenhouse

from app.schemas.sensor import SensorResponse, SensorMode, SensorType, PositionSchema
from app.schemas.device import DeviceResponse, DeviceType
from app.schemas.growth_plan import (
    GrowthPlanResponse,
    DayScheduleSchema,
    ParameterRangeSchema,
    CurrentScheduleResponse,
)
from app.schemas.greenhouse import GreenhouseResponse


def _pos(obj) -> PositionSchema:
    return PositionSchema(x=obj.position.x, y=obj.position.y)


def sensor_to_schema(s: Sensor) -> SensorResponse:
    mode = SensorMode.ACTIVE if isinstance(s, ActiveSensor) else SensorMode.PASSIVE
    return SensorResponse(
        id=s.id,
        type=SensorType(s.type.value),
        mode=mode,
        position=_pos(s),
        current_value=s.current_value,
        unit=s.unit,
        is_alert=getattr(s, "is_alert", False),
    )


def device_to_schema(d: Device) -> DeviceResponse:
    return DeviceResponse(
        id=d.id,
        type=DeviceType(d.type.value),
        position=_pos(d),
        is_on=d.is_on,
        name=d.name,
    )


def _range_to_schema(r: ParameterRange) -> ParameterRangeSchema:
    return ParameterRangeSchema(min_val=r.min_val, max_val=r.max_val, target=r.target)


def _schedule_to_schema(sc: DaySchedule) -> DayScheduleSchema:
    return DayScheduleSchema(
        day=sc.day,
        temperature_day=_range_to_schema(sc.temperature_day),
        temperature_night=_range_to_schema(sc.temperature_night),
        light_hours=sc.light_hours,
        humidity=_range_to_schema(sc.humidity),
        ph=_range_to_schema(sc.ph),
        nutrient=_range_to_schema(sc.nutrient),
    )


def plan_to_schema(plan: GrowthPlan) -> GrowthPlanResponse:
    cur = plan.get_current_schedule()
    current_schedule = None
    if cur:
        current_schedule = CurrentScheduleResponse(
            **_schedule_to_schema(cur).model_dump(),
            is_light_time=plan.is_light_time(),
        )
    return GrowthPlanResponse(
        id=plan.id,
        crop_name=plan.crop_name,
        start_date=plan.start_date,
        total_days=plan.total_days,
        current_day=plan.current_day,
        elapsed_days=plan.elapsed_days,
        elapsed_hours=plan.elapsed_hours,
        current_schedule=current_schedule,
        schedule=[_schedule_to_schema(s) for s in plan.get_all_schedules()],
    )


def greenhouse_to_schema(gh: Greenhouse) -> GreenhouseResponse:
    return GreenhouseResponse(
        id=gh.id,
        name=gh.name,
        width=gh.width,
        height=gh.height,
        sensors=[sensor_to_schema(s) for s in gh.get_sensors()],
        devices=[device_to_schema(d) for d in gh.get_devices()],
        growth_plan=plan_to_schema(gh.growth_plan) if gh.growth_plan else None,
        is_running=gh.is_running,
    )
