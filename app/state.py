"""
Module-level singletons. Initialized during FastAPI lifespan startup.
"""

from datetime import datetime
from typing import Optional

from app.domain.sensors import PassiveSensor, ActiveSensor, SensorType, Position
from app.domain.devices import (
    Heater,
    AirConditioner,
    Humidifier,
    FertilizerDispenser,
    NutrientDispenser,
    LightSource,
)
from app.domain.growth_plan import GrowthPlan, DaySchedule, ParameterRange
from app.domain.greenhouse import Greenhouse
from app.domain.controller import GreenhouseController

greenhouse: Optional[Greenhouse] = None
controller: Optional[GreenhouseController] = None


def get_greenhouse() -> Optional[Greenhouse]:
    return greenhouse


def get_controller() -> Optional[GreenhouseController]:
    return controller


def initialize() -> None:
    global greenhouse, controller
    greenhouse = _create_default_greenhouse()
    greenhouse.set_growth_plan(create_tulip_plan())
    controller = GreenhouseController(greenhouse)


# ---------------------------------------------------------------------------
# Default greenhouse layout (mirrors the diagram from the task)
# ---------------------------------------------------------------------------

def _create_default_greenhouse() -> Greenhouse:
    gh = Greenhouse("Теплица №1", width=10.0, height=8.0)

    # --- temperature sensors (air) ---
    for pos in [(0.5, 0.5), (9.5, 0.5), (5.0, 4.0), (0.5, 7.5), (9.5, 7.5)]:
        gh.add_sensor(PassiveSensor(SensorType.TEMPERATURE_AIR, Position(*pos), 18.0, 32.0))

    # --- temperature sensors (water) ---
    for pos in [(3.0, 4.0), (7.0, 4.0)]:
        gh.add_sensor(PassiveSensor(SensorType.TEMPERATURE_WATER, Position(*pos), 16.0, 28.0))

    # --- humidity sensors ---
    for pos in [(0.5, 3.5), (9.5, 3.5)]:
        gh.add_sensor(PassiveSensor(SensorType.HUMIDITY, Position(*pos), 80.0, 100.0))

    # --- pH sensors ---
    for pos in [(3.0, 2.5), (7.0, 2.5), (3.0, 5.5), (7.0, 5.5), (5.0, 4.0)]:
        gh.add_sensor(PassiveSensor(SensorType.PH, Position(*pos), 4.5, 7.5))

    # --- light and nutrient sensors ---
    for pos in [(2.0, 3.8), (8.0, 3.8)]:
        gh.add_sensor(PassiveSensor(SensorType.LIGHT, Position(*pos), 0.0, 12000.0))
    for pos in [(4.0, 2.0), (6.0, 6.0)]:
        gh.add_sensor(PassiveSensor(SensorType.NUTRIENT, Position(*pos), 500.0, 1300.0))

    # --- heaters ---
    for pos in [(2.0, 0.5), (5.0, 0.5), (8.0, 0.5), (2.0, 7.5), (8.0, 7.5)]:
        gh.add_device(Heater(Position(*pos)))

    # --- air conditioners ---
    gh.add_device(AirConditioner(Position(0.0, 2.5)))
    gh.add_device(AirConditioner(Position(10.0, 5.5)))

    # --- humidifiers ---
    gh.add_device(Humidifier(Position(0.5, 5.5)))
    gh.add_device(Humidifier(Position(9.5, 2.0)))

    # --- light sources ---
    for pos in [
        (1.5, 0.5), (4.0, 0.5), (6.0, 0.5), (8.5, 0.5),
        (2.5, 4.0), (5.0, 4.0), (7.5, 4.0),
    ]:
        gh.add_device(LightSource(Position(*pos)))

    # --- fertilizer dispensers ---
    gh.add_device(FertilizerDispenser(Position(2.5, 2.5)))
    gh.add_device(FertilizerDispenser(Position(7.5, 5.5)))

    # --- nutrient solution dispensers ---
    gh.add_device(NutrientDispenser(Position(5.0, 2.0)))
    gh.add_device(NutrientDispenser(Position(5.0, 6.0)))

    return gh


def create_tulip_plan() -> GrowthPlan:
    """
    Tulip growing plan as described in the task specification.
    The cycle starts when the preset is loaded.
    """
    plan = GrowthPlan("Тюльпаны", datetime.now(), 90)

    # Days 1–14: early vegetative growth
    for day in range(1, 15):
        plan.add_day_schedule(DaySchedule(
            day=day,
            temperature_day=ParameterRange(24.0, 28.0, 26.0),
            temperature_night=ParameterRange(20.0, 24.0, 22.0),
            light_hours=14,
            humidity=ParameterRange(85.0, 95.0, 90.0),
            ph=ParameterRange(5.5, 6.5, 6.0),
            nutrient=ParameterRange(800.0, 1200.0, 1000.0),
        ))

    # Day 15: peak temperature (28 °C for 16 h, 22 °C for the rest — spec example)
    plan.add_day_schedule(DaySchedule(
        day=15,
        temperature_day=ParameterRange(26.0, 30.0, 28.0),
        temperature_night=ParameterRange(20.0, 24.0, 22.0),
        light_hours=16,
        humidity=ParameterRange(85.0, 95.0, 90.0),
        ph=ParameterRange(5.5, 6.5, 6.0),
        nutrient=ParameterRange(800.0, 1200.0, 1000.0),
    ))

    # Days 16–90: cooling phase
    for day in range(16, 91):
        plan.add_day_schedule(DaySchedule(
            day=day,
            temperature_day=ParameterRange(20.0, 24.0, 22.0),
            temperature_night=ParameterRange(16.0, 20.0, 18.0),
            light_hours=12,
            humidity=ParameterRange(80.0, 90.0, 85.0),
            ph=ParameterRange(5.5, 6.5, 6.0),
            nutrient=ParameterRange(600.0, 1000.0, 800.0),
        ))

    return plan
