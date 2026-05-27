from fastapi import APIRouter, Request, HTTPException
from typing import List

from app.schemas.sensor import SensorCreate, SensorResponse, SensorMode
from app.domain.sensors import PassiveSensor, ActiveSensor, SensorType, Position
from app.routers.converters import sensor_to_schema

router = APIRouter()


def _gh(request: Request):
    return request.app.state.greenhouse


@router.get("/", response_model=List[SensorResponse], summary="List all sensors")
async def list_sensors(request: Request):
    gh = _gh(request)
    gh.read_all_sensors()
    return [sensor_to_schema(s) for s in gh.get_sensors()]


@router.get("/{sensor_id}", response_model=SensorResponse, summary="Get sensor by id")
async def get_sensor(sensor_id: str, request: Request):
    gh = _gh(request)
    sensor = gh.get_sensor(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found.")
    sensor.read()
    return sensor_to_schema(sensor)


@router.post("/", response_model=SensorResponse, status_code=201, summary="Add sensor")
async def add_sensor(body: SensorCreate, request: Request):
    gh = _gh(request)
    pos = Position(x=body.position.x, y=body.position.y)
    domain_type = SensorType(body.type.value)

    if body.mode == SensorMode.PASSIVE:
        sensor = PassiveSensor(domain_type, pos, body.min_range, body.max_range)
    else:
        sensor = ActiveSensor(
            domain_type,
            pos,
            body.min_range,
            body.max_range,
            target=body.target,
            threshold=body.threshold,
        )

    gh.add_sensor(sensor)
    return sensor_to_schema(sensor)


@router.delete(
    "/{sensor_id}", status_code=204, summary="Remove sensor"
)
async def delete_sensor(sensor_id: str, request: Request):
    gh = _gh(request)
    if not gh.remove_sensor(sensor_id):
        raise HTTPException(status_code=404, detail="Sensor not found.")
