import asyncio
import json
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.routers.greenhouse import router as greenhouse_router
from app.routers.sensors import router as sensors_router
from app.routers.devices import router as devices_router
from app.routers.growth_plan import router as growth_plan_router
from app import state


class ConnectionManager:
    def __init__(self) -> None:
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self.active.remove(ws)

    async def broadcast(self, message: str) -> None:
        dead: List[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)


manager = ConnectionManager()


def _build_snapshot() -> dict:
    gh = state.get_greenhouse()
    if not gh:
        return {}

    sensors = [
        {
            "id": s.id,
            "type": s.type.value,
            "position": {"x": s.position.x, "y": s.position.y},
            "current_value": s.current_value,
            "unit": s.unit,
            "is_alert": getattr(s, "is_alert", False),
        }
        for s in gh.get_sensors()
    ]
    devices = [
        {
            "id": d.id,
            "type": d.type.value,
            "position": {"x": d.position.x, "y": d.position.y},
            "is_on": d.is_on,
            "name": d.name,
        }
        for d in gh.get_devices()
    ]
    growth_plan = None
    if gh.growth_plan:
        p = gh.growth_plan
        current_schedule = None
        schedule = p.get_current_schedule()
        if schedule:
            def range_dict(r):
                return {
                    "min_val": r.min_val,
                    "max_val": r.max_val,
                    "target": r.target,
                }

            current_schedule = {
                "day": schedule.day,
                "temperature_day": range_dict(schedule.temperature_day),
                "temperature_night": range_dict(schedule.temperature_night),
                "light_hours": schedule.light_hours,
                "humidity": range_dict(schedule.humidity),
                "ph": range_dict(schedule.ph),
                "nutrient": range_dict(schedule.nutrient),
                "is_light_time": p.is_light_time(),
            }

        growth_plan = {
            "id": p.id,
            "crop_name": p.crop_name,
            "start_date": p.start_date.isoformat(),
            "total_days": p.total_days,
            "elapsed_days": p.elapsed_days,
            "elapsed_hours": p.elapsed_hours,
            "current_day": p.current_day,
            "current_schedule": current_schedule,
        }

    return {
        "id": gh.id,
        "name": gh.name,
        "width": gh.width,
        "height": gh.height,
        "is_running": gh.is_running,
        "sensors": sensors,
        "devices": devices,
        "growth_plan": growth_plan,
    }


async def _control_loop() -> None:
    """Background task: run controller tick and broadcast state every 2 s."""
    while True:
        await asyncio.sleep(2)
        ctrl = state.get_controller()
        gh = state.get_greenhouse()
        if ctrl and gh:
            ctrl.tick()
        if manager.active:
            snapshot = json.dumps(_build_snapshot())
            await manager.broadcast(snapshot)


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.initialize()
    # propagate greenhouse to app.state for request-scoped access in routers
    app.state.greenhouse = state.get_greenhouse()
    task = asyncio.create_task(_control_loop())
    yield
    task.cancel()


app = FastAPI(
    title="Greenhouse Management System",
    description="Automated hydroponics greenhouse controller",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(greenhouse_router, prefix="/api/greenhouse", tags=["Greenhouse"])
app.include_router(sensors_router, prefix="/api/sensors", tags=["Sensors"])
app.include_router(devices_router, prefix="/api/devices", tags=["Devices"])
app.include_router(growth_plan_router, prefix="/api/growth-plan", tags=["Growth Plan"])


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial snapshot immediately
        await websocket.send_text(json.dumps(_build_snapshot()))
        while True:
            await websocket.receive_text()  # keep connection alive; client can send pings
    except WebSocketDisconnect:
        manager.disconnect(websocket)
