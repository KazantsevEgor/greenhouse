from typing import Optional
import uuid

from .sensors import Sensor, SensorType
from .devices import Device, DeviceType
from .growth_plan import GrowthPlan


class Greenhouse:
    def __init__(
        self,
        name: str,
        width: float = 10.0,
        height: float = 8.0,
        greenhouse_id: str | None = None,
    ) -> None:
        self.id: str = greenhouse_id or str(uuid.uuid4())
        self.name = name
        self.width = width
        self.height = height
        self._sensors: dict[str, Sensor] = {}
        self._devices: dict[str, Device] = {}
        self.growth_plan: Optional[GrowthPlan] = None
        self.is_running: bool = False

    # --- sensors ---

    def add_sensor(self, sensor: Sensor) -> None:
        self._sensors[sensor.id] = sensor

    def remove_sensor(self, sensor_id: str) -> bool:
        return self._sensors.pop(sensor_id, None) is not None

    def get_sensor(self, sensor_id: str) -> Optional[Sensor]:
        return self._sensors.get(sensor_id)

    def get_sensors(self) -> list[Sensor]:
        return list(self._sensors.values())

    def get_sensors_by_type(self, sensor_type: SensorType) -> list[Sensor]:
        return [s for s in self._sensors.values() if s.type == sensor_type]

    # --- devices ---

    def add_device(self, device: Device) -> None:
        self._devices[device.id] = device

    def remove_device(self, device_id: str) -> bool:
        return self._devices.pop(device_id, None) is not None

    def get_device(self, device_id: str) -> Optional[Device]:
        return self._devices.get(device_id)

    def get_devices(self) -> list[Device]:
        return list(self._devices.values())

    def get_devices_by_type(self, device_type: DeviceType) -> list[Device]:
        return [d for d in self._devices.values() if d.type == device_type]

    # --- growth plan ---

    def set_growth_plan(self, plan: GrowthPlan) -> None:
        self.growth_plan = plan

    # --- cycle control ---

    def start_cycle(self) -> None:
        if self.growth_plan:
            self.is_running = True

    def stop_cycle(self) -> None:
        self.is_running = False

    def read_all_sensors(self) -> dict[str, float]:
        return {sid: s.read() for sid, s in self._sensors.items()}
