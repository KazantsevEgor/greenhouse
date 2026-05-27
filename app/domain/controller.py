from typing import Optional

from .greenhouse import Greenhouse
from .sensors import SensorType
from .devices import DeviceType
from .growth_plan import DaySchedule


class GreenhouseController:
    """
    Automation layer: reads sensor averages and switches devices
    according to the current day's growing schedule.
    """

    def __init__(self, greenhouse: Greenhouse) -> None:
        self.greenhouse = greenhouse

    def tick(self) -> None:
        """One control cycle — read sensors then adjust devices."""
        if not self.greenhouse.is_running or not self.greenhouse.growth_plan:
            return
        schedule = self.greenhouse.growth_plan.get_current_schedule()
        if not schedule:
            return

        self.greenhouse.read_all_sensors()
        self._control_temperature(schedule)
        self._control_humidity(schedule)
        self._control_ph(schedule)
        self._control_nutrients(schedule)
        self._control_lighting()

    # --- private helpers ---

    def _avg(self, sensor_type: SensorType) -> Optional[float]:
        sensors = self.greenhouse.get_sensors_by_type(sensor_type)
        if not sensors:
            return None
        return sum(s.current_value for s in sensors) / len(sensors)

    def _control_temperature(self, schedule: DaySchedule) -> None:
        is_day = self.greenhouse.growth_plan.is_light_time()
        target = schedule.temperature_day if is_day else schedule.temperature_night

        avg = self._avg(SensorType.TEMPERATURE_AIR)
        if avg is None:
            return

        heaters = self.greenhouse.get_devices_by_type(DeviceType.HEATER)
        acs = self.greenhouse.get_devices_by_type(DeviceType.AIR_CONDITIONER)

        if avg < target.min_val:
            for d in heaters:
                d.turn_on()
            for d in acs:
                d.turn_off()
        elif avg > target.max_val:
            for d in heaters:
                d.turn_off()
            for d in acs:
                d.turn_on()
        else:
            for d in heaters:
                d.turn_off()
            for d in acs:
                d.turn_off()

    def _control_humidity(self, schedule: DaySchedule) -> None:
        avg = self._avg(SensorType.HUMIDITY)
        if avg is None:
            return

        heaters = self.greenhouse.get_devices_by_type(DeviceType.HEATER)
        humidifiers = self.greenhouse.get_devices_by_type(DeviceType.HUMIDIFIER)

        if avg < schedule.humidity.min_val:
            for d in heaters:
                d.turn_off()
            for d in humidifiers:
                d.turn_on()
        elif avg > schedule.humidity.max_val:
            for d in heaters:
                d.turn_on()
            for d in humidifiers:
                d.turn_off()
        else:
            for d in humidifiers:
                d.turn_off()

    def _control_ph(self, schedule: DaySchedule) -> None:
        avg = self._avg(SensorType.PH)
        if avg is None:
            return

        dispensers = self.greenhouse.get_devices_by_type(DeviceType.FERTILIZER_DISPENSER)

        if avg < schedule.ph.min_val:
            for d in dispensers:
                d.turn_on()
        elif avg >= schedule.ph.target:
            for d in dispensers:
                d.turn_off()

    def _control_nutrients(self, schedule: DaySchedule) -> None:
        avg = self._avg(SensorType.NUTRIENT)
        if avg is None:
            return

        dispensers = self.greenhouse.get_devices_by_type(DeviceType.NUTRIENT_DISPENSER)

        if avg < schedule.nutrient.min_val:
            for d in dispensers:
                d.turn_on()
        elif avg >= schedule.nutrient.target:
            for d in dispensers:
                d.turn_off()

    def _control_lighting(self) -> None:
        is_day = self.greenhouse.growth_plan.is_light_time()
        for light in self.greenhouse.get_devices_by_type(DeviceType.LIGHT_SOURCE):
            if is_day:
                light.turn_on()
            else:
                light.turn_off()
