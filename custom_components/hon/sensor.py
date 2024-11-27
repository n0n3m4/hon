from dataclasses import dataclass, replace

from homeassistant.components import sensor
from homeassistant.const import EntityCategory

from .common import async_setup_entry_factory, Entity, EntityDescription

from typing import ClassVar
from . import units

_DeviceClass = sensor.const.SensorDeviceClass
_StateClass = sensor.const.SensorStateClass


class SensorEntity(
    Entity,
    sensor.SensorEntity,
):
    entity_description: "SensorEntityDescription"

    @property
    def native_value(self):
        return self.entity_description.get_value(self._appliance)

    @property
    def options(self) -> list[str]:
        if count := self.entity_description.options_count:
            return list(range(count))

        return super().options

    @property
    def device_class(self) -> str | None:
        if self.options:
            return _DeviceClass.ENUM

        return super().device_class


@dataclass(frozen=True, kw_only=True)
class SensorEntityDescription(
    EntityDescription,
    sensor.SensorEntityDescription,
):
    entity_cls: ClassVar[type[SensorEntity]] = SensorEntity
    options_count: int | None = None


@dataclass(frozen=True, kw_only=True)
class ConfigSensorEntityDescription(
    SensorEntityDescription,
):
    entity_category: ClassVar[EntityCategory] = EntityCategory.DIAGNOSTIC


def with_zones(*desc: SensorEntityDescription):
    yield from desc
    for i in range(1, 4):
        yield from (replace(d, name=f"{d.name} {i}", key=f"{d.key}Z{i}") for d in desc)

# TODO: Sort it some way
ENTITIES = {
    # TODO: Should be supported for
    # wm, td, ov, ih, dw, ac, wc
    SensorEntityDescription(
        name="Program",
        icon="mdi:play",
        # TODO: Options
        # device_class=_DeviceClass.ENUM,
        translation_key="programs_wm",
        key="prCode",
    ),
    # TODO: Should be supported for
    # wm, td, dw
    SensorEntityDescription(
        name="Program Phase",
        translation_key="program_phases_wm",
        icon="mdi:washing-machine",
        key="prPhase",
        options_count=28,
    ),
    SensorEntityDescription(
        name="Total Energy",
        translation_key="energy_total",
        state_class=_StateClass.TOTAL_INCREASING,
        device_class=_DeviceClass.ENERGY,
        native_unit_of_measurement=units.KILO_WATT_HOUR,
        key="totalElectricityUsed",
    ),
    SensorEntityDescription(
        name="Total Water",
        translation_key="water_total",
        state_class=_StateClass.TOTAL_INCREASING,
        device_class=_DeviceClass.WATER,
        native_unit_of_measurement=units.LITERS,
        key="totalWaterUsed",
    ),
    SensorEntityDescription(
        name="Total Wash Cycle",
        translation_key="cycles_total",
        icon="mdi:counter",
        state_class=_StateClass.TOTAL_INCREASING,
        key="totalWashCycle",
    ),
    SensorEntityDescription(
        name="Current Cycle Energy",
        translation_key="energy_current",
        device_class=_DeviceClass.ENERGY,
        native_unit_of_measurement=units.KILO_WATT_HOUR,
        key="currentElectricityUsed",
    ),
    SensorEntityDescription(
        name="Current Cycle Water",
        translation_key="water_current",
        device_class=_DeviceClass.WATER,
        state_class=_StateClass.TOTAL_INCREASING,
        native_unit_of_measurement=units.LITERS,
        key="currentWaterUsed",
    ),
    *(
        ConfigSensorEntityDescription(
            name="Suggested Load",
            device_class=_DeviceClass.WEIGHT,
            native_unit_of_measurement=units.KILOGRAMS,
            key=f"startProgram.suggestedLoad{suffix}",
        )
        for suffix in ("", "W", "D")
    ),
    SensorEntityDescription(
        name="Mode",
        translation_key="washing_modes",
        icon="mdi:information",
        key="machMode",
        options_count=10,
    ),
    SensorEntityDescription(
        name="Errors",
        icon="mdi:math-log",
    ),
    SensorEntityDescription(
        name="Remaining Time",
        device_class=_DeviceClass.DURATION,
        native_unit_of_measurement=units.MINUTES,
        key="remainingTimeMM",
    ),
    SensorEntityDescription(
        name="Spin Speed",
        icon="mdi:speedometer",
        native_unit_of_measurement=units.REVOLUTIONS_PER_MINUTE,
        key="spinSpeed",
    ),
    ConfigSensorEntityDescription(
        name="Energy Label",
        icon="mdi:lightning-bolt-circle",
        value_picker=lambda a: a.settings["startProgram.energyLabel"],
    ),
    ConfigSensorEntityDescription(
        name="Liquid Detergent Dose",
        icon="mdi:cup-water",
        translation_key="det_liquid",
        value_picker=lambda a: a.settings["startProgram.liquidDetergentDose"],
    ),
    ConfigSensorEntityDescription(
        name="Powder Detergent Dose",
        icon="mdi:cup",
        translation_key="det_dust",
        value_picker=lambda a: a.settings["startProgram.powderDetergentDose"],
    ),
    ConfigSensorEntityDescription(
        name="Program Time",
        translation_key="remaining_time",
        device_class=_DeviceClass.DURATION,
        native_unit_of_measurement=units.MINUTES,
        value_picker=lambda a: a.settings["startProgram.remainingTime"],
    ),
    SensorEntityDescription(
        name="Dirty level",
        icon="mdi:liquid-spot",
        options_count=4,
    ),
    SensorEntityDescription(
        name="Steam level",
        icon="mdi:weather-dust",
        options_count=4,
    ),
    SensorEntityDescription(
        name="Stain Type",
        icon="mdi:liquid-spot",
        options_count=27,
    ),
    SensorEntityDescription(
        name="Delay time",
        icon="mdi:clock-start",
        native_unit_of_measurement=units.MINUTES,
    ),
    SensorEntityDescription(
        name="CO Level",
        state_class=_StateClass.MEASUREMENT,
        device_class=_DeviceClass.CO,
        native_unit_of_measurement=units.CONCENTRATION_PARTS_PER_MILLION,
    ),
    SensorEntityDescription(
        name="PM 10",
        state_class=_StateClass.MEASUREMENT,
        device_class=_DeviceClass.PM10,
        native_unit_of_measurement=units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        key="pm10ValueIndoor",
    ),
    SensorEntityDescription(
        name="PM 2.5",
        state_class=_StateClass.MEASUREMENT,
        device_class=_DeviceClass.PM25,
        native_unit_of_measurement=units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        key="pm2p5ValueIndoor",
    ),
    SensorEntityDescription(
        name="VOC",
        state_class=_StateClass.MEASUREMENT,
        device_class=_DeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        native_unit_of_measurement=units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        key="vocValueIndoor",
    ),
    *(
        SensorEntityDescription(
            name=f"{e} {area} Temperature".strip(),
            state_class=_StateClass.MEASUREMENT,
            device_class=_DeviceClass.TEMPERATURE,
            native_unit_of_measurement=units.CELSIUS,
            key=f"temp{e}{area}",
        )
        for area in ("Indoor", "Outdoor")
        for e in ("", "Coiler")
    ),
    SensorEntityDescription(
        name="Power",
        state_class=_StateClass.MEASUREMENT,
        device_class=_DeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="tempEnv",
        name="Room Temperature",
        state_class=_StateClass.MEASUREMENT,
        device_class=_DeviceClass.TEMPERATURE,
        native_unit_of_measurement=units.CELSIUS,
    ),
    *with_zones(
        SensorEntityDescription(
            name="Temperature",
            key="temp",
            state_class=_StateClass.MEASUREMENT,
            device_class=_DeviceClass.TEMPERATURE,
            native_unit_of_measurement=units.CELSIUS,
        ),
        SensorEntityDescription(
            name="Humidity",
            device_class=_DeviceClass.HUMIDITY,
            native_unit_of_measurement=units.PERCENTAGE,
            state_class=_StateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="tempSel",
            name="Selected Temperature",
            state_class=_StateClass.MEASUREMENT,
            device_class=_DeviceClass.TEMPERATURE,
            native_unit_of_measurement=units.CELSIUS,
            translation_key="target_temperature",
        ),
    ),
    ConfigSensorEntityDescription(
        name="Steam Type",
        icon="mdi:weather-dust",
    ),
    SensorEntityDescription(
        name="Dry level",
        icon="mdi:hair-dryer",
        translation_key="dry_levels",
        options_count=16,
    ),
    SensorEntityDescription(
        key="tempLevel",
        name="Temperature level",
        icon="mdi:thermometer",
        # TODO: Probably enum
        translation_key="tumbledryertemplevel",
    ),
    ConfigSensorEntityDescription(
        name="Eco Index",
        icon="mdi:sprout",
        state_class=_StateClass.MEASUREMENT,
        value_picker=lambda a: a.settings["startProgram.ecoIndex"],
    ),
    ConfigSensorEntityDescription(
        name="Water Efficiency",
        icon="mdi:water",
        state_class=_StateClass.MEASUREMENT,
        value_picker=lambda a: a.settings["startProgram.waterEfficiency"],
    ),
    ConfigSensorEntityDescription(
        name="Water Saving",
        icon="mdi:water-percent",
        state_class=_StateClass.MEASUREMENT,
        native_unit_of_measurement=units.PERCENTAGE,
        value_picker=lambda a: a.settings["startProgram.waterSaving"],
    ),
    ConfigSensorEntityDescription(
        name="Temperature",
        state_class=_StateClass.MEASUREMENT,
        device_class=_DeviceClass.TEMPERATURE,
        native_unit_of_measurement=units.CELSIUS,
        value_picker=lambda a: a.settings["startProgram.temp"],
    ),
    # TODO: Poor descriptions: consider to remove
    SensorEntityDescription(
        name="Delay time status",
        icon="mdi:clock-start",
    ),
    SensorEntityDescription(
        name="Filter Cleaning Alarm Status",
    ),
    SensorEntityDescription(
        name="Filter Cleaning Status",
    ),
    SensorEntityDescription(
        name="Last Work Time",
        icon="mdi:clock-start",
    ),
    SensorEntityDescription(
        name="Light Status",
        icon="mdi:lightbulb",
    ),
    SensorEntityDescription(
        name="Quick Delay Time Status",
    ),
    SensorEntityDescription(
        name="RGB Light Color",
        icon="mdi:lightbulb",
    ),
    SensorEntityDescription(
        name="RGB Light Status",
        icon="mdi:lightbulb",
    ),
    SensorEntityDescription(
        name="Fan Speed",
        icon="mdi:fan",
    ),
    SensorEntityDescription(
        name="Air Quality",
        icon="mdi:weather-dust",
    ),
    SensorEntityDescription(
        name="Filter Life",
        icon="mdi:air-filter",
        native_unit_of_measurement=units.PERCENTAGE,
    ),
    SensorEntityDescription(
        name="Pre Filter Status",
        icon="mdi:air-filter",
        translation_key="filter_cleaning",
        native_unit_of_measurement=units.PERCENTAGE,
    ),
    SensorEntityDescription(
        name="Total Work Time",
        native_unit_of_measurement=units.MINUTES,
        device_class=_DeviceClass.DURATION,
    ),
    *(
        SensorEntityDescription(
            key=f"temp{n.replace(' ','')}Outdoor",
            name=f"{n} Temperature Outdoor",
            icon="mdi:thermometer",
            state_class=_StateClass.MEASUREMENT,
            device_class=_DeviceClass.TEMPERATURE,
            native_unit_of_measurement=units.CELSIUS,
        )
        for n in ("Air", "Defrost", "In Air")
    ),
    *(
        SensorEntityDescription(
            key=f"humidity{k}",
            name=f"{name} Humidity".strip(),
            state_class=_StateClass.MEASUREMENT,
            device_class=_DeviceClass.HUMIDITY,
            native_unit_of_measurement=units.PERCENTAGE,
            translation_key="humidity",
        )
        for k, name in (
            ("Indoor", ""),
            ("Env", "Room"),
        )
    ),
    SensorEntityDescription(
        name="Humidity Level",
        icon="mdi:water-outline",
        options_count=4,
    ),
}

async_setup_entry = async_setup_entry_factory(ENTITIES)
