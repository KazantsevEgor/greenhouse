from fastapi import APIRouter, Request, HTTPException

from app.schemas.growth_plan import (
    GrowthPlanCreate,
    GrowthPlanResponse,
    DayScheduleSchema,
)
from app.domain.growth_plan import GrowthPlan, DaySchedule, ParameterRange
from app.routers.converters import plan_to_schema
from datetime import datetime

router = APIRouter()


def _gh(request: Request):
    return request.app.state.greenhouse


def _schema_to_range(r) -> ParameterRange:
    return ParameterRange(min_val=r.min_val, max_val=r.max_val, target=r.target)


def _schema_to_day_schedule(s: DayScheduleSchema) -> DaySchedule:
    return DaySchedule(
        day=s.day,
        temperature_day=_schema_to_range(s.temperature_day),
        temperature_night=_schema_to_range(s.temperature_night),
        light_hours=s.light_hours,
        humidity=_schema_to_range(s.humidity),
        ph=_schema_to_range(s.ph),
        nutrient=_schema_to_range(s.nutrient),
    )


@router.get("/", response_model=GrowthPlanResponse, summary="Get current growth plan")
async def get_growth_plan(request: Request):
    gh = _gh(request)
    if not gh.growth_plan:
        raise HTTPException(status_code=404, detail="No growth plan configured.")
    return plan_to_schema(gh.growth_plan)


@router.post("/", response_model=GrowthPlanResponse, status_code=201, summary="Set growth plan")
async def set_growth_plan(body: GrowthPlanCreate, request: Request):
    gh = _gh(request)
    plan = GrowthPlan(
        crop_name=body.crop_name,
        start_date=body.start_date,
        total_days=body.total_days,
    )
    for s in body.schedule:
        plan.add_day_schedule(_schema_to_day_schedule(s))
    gh.set_growth_plan(plan)
    return plan_to_schema(plan)


@router.put(
    "/schedule/{day}",
    response_model=GrowthPlanResponse,
    summary="Update schedule for a specific day",
)
async def update_day_schedule(day: int, body: DayScheduleSchema, request: Request):
    gh = _gh(request)
    if not gh.growth_plan:
        raise HTTPException(status_code=404, detail="No growth plan configured.")
    body.day = day
    gh.growth_plan.add_day_schedule(_schema_to_day_schedule(body))
    return plan_to_schema(gh.growth_plan)


@router.post(
    "/presets/tulips",
    response_model=GrowthPlanResponse,
    status_code=201,
    summary="Load default tulip growing plan",
)
async def load_tulip_preset(request: Request):
    from app.state import create_tulip_plan

    gh = _gh(request)
    plan = create_tulip_plan()
    gh.set_growth_plan(plan)
    return plan_to_schema(plan)
