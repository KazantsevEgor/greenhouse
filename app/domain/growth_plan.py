from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class ParameterRange:
    min_val: float
    max_val: float
    target: float


@dataclass
class DaySchedule:
    day: int
    temperature_day: ParameterRange    # target during light hours
    temperature_night: ParameterRange  # target during dark hours
    light_hours: int                   # how many hours of light per day
    humidity: ParameterRange
    ph: ParameterRange
    nutrient: ParameterRange


class GrowthPlan:
    def __init__(
        self,
        crop_name: str,
        start_date: datetime,
        total_days: int,
        plan_id: str | None = None,
    ) -> None:
        self.id: str = plan_id or str(uuid.uuid4())
        self.crop_name = crop_name
        self.start_date = start_date
        self.total_days = total_days
        self._schedule: dict[int, DaySchedule] = {}

    # --- schedule management ---

    def add_day_schedule(self, schedule: DaySchedule) -> None:
        self._schedule[schedule.day] = schedule

    def get_schedule_for_day(self, day: int) -> Optional[DaySchedule]:
        if day in self._schedule:
            return self._schedule[day]
        # fall back to the most recent past schedule entry
        past_days = sorted(d for d in self._schedule if d <= day)
        return self._schedule[past_days[-1]] if past_days else None

    def get_all_schedules(self) -> list[DaySchedule]:
        return [self._schedule[d] for d in sorted(self._schedule)]

    # --- time helpers ---

    @property
    def elapsed_days(self) -> int:
        return (datetime.now() - self.start_date).days

    @property
    def elapsed_hours(self) -> int:
        return int((datetime.now() - self.start_date).seconds / 3600)

    @property
    def current_day(self) -> int:
        return self.elapsed_days + 1

    def get_current_schedule(self) -> Optional[DaySchedule]:
        return self.get_schedule_for_day(self.current_day)

    def is_light_time(self, hour_of_day: int | None = None) -> bool:
        schedule = self.get_current_schedule()
        if not schedule:
            return False
        h = hour_of_day if hour_of_day is not None else datetime.now().hour
        return h < schedule.light_hours
