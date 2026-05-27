from fastapi import APIRouter, Request, HTTPException

from app.schemas.greenhouse import GreenhouseResponse
from app.routers.converters import greenhouse_to_schema

router = APIRouter()


def _gh(request: Request):
    return request.app.state.greenhouse


@router.get("/", response_model=GreenhouseResponse, summary="Full greenhouse state")
async def get_greenhouse(request: Request):
    gh = _gh(request)
    gh.read_all_sensors()
    return greenhouse_to_schema(gh)


@router.post("/start", summary="Start growing cycle")
async def start_cycle(request: Request):
    gh = _gh(request)
    if not gh.growth_plan:
        raise HTTPException(status_code=400, detail="No growth plan configured.")
    gh.start_cycle()
    return {"status": "started", "crop": gh.growth_plan.crop_name}


@router.post("/stop", summary="Stop growing cycle")
async def stop_cycle(request: Request):
    gh = _gh(request)
    gh.stop_cycle()
    # turn off all devices
    for device in gh.get_devices():
        device.turn_off()
    return {"status": "stopped"}
