from fastapi import APIRouter, Request, HTTPException
from typing import List

from app.schemas.device import DeviceCreate, DeviceResponse, DeviceType
from app.domain.devices import (
    Heater,
    AirConditioner,
    Humidifier,
    FertilizerDispenser,
    NutrientDispenser,
    LightSource,
)
from app.domain.sensors import Position
from app.routers.converters import device_to_schema

router = APIRouter()

_DEVICE_FACTORIES = {
    DeviceType.HEATER: Heater,
    DeviceType.AIR_CONDITIONER: AirConditioner,
    DeviceType.HUMIDIFIER: Humidifier,
    DeviceType.FERTILIZER_DISPENSER: FertilizerDispenser,
    DeviceType.NUTRIENT_DISPENSER: NutrientDispenser,
    DeviceType.LIGHT_SOURCE: LightSource,
}


def _gh(request: Request):
    return request.app.state.greenhouse


@router.get("/", response_model=List[DeviceResponse], summary="List all devices")
async def list_devices(request: Request):
    return [device_to_schema(d) for d in _gh(request).get_devices()]


@router.get("/{device_id}", response_model=DeviceResponse, summary="Get device by id")
async def get_device(device_id: str, request: Request):
    gh = _gh(request)
    device = gh.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found.")
    return device_to_schema(device)


@router.post("/", response_model=DeviceResponse, status_code=201, summary="Add device")
async def add_device(body: DeviceCreate, request: Request):
    gh = _gh(request)
    factory = _DEVICE_FACTORIES[body.type]
    device = factory(Position(x=body.position.x, y=body.position.y))
    gh.add_device(device)
    return device_to_schema(device)


@router.post("/{device_id}/toggle", response_model=DeviceResponse, summary="Toggle device on/off")
async def toggle_device(device_id: str, request: Request):
    gh = _gh(request)
    device = gh.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found.")
    if device.is_on:
        device.turn_off()
    else:
        device.turn_on()
    return device_to_schema(device)


@router.delete("/{device_id}", status_code=204, summary="Remove device")
async def delete_device(device_id: str, request: Request):
    gh = _gh(request)
    if not gh.remove_device(device_id):
        raise HTTPException(status_code=404, detail="Device not found.")
