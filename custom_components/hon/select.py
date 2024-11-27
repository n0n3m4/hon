from dataclasses import dataclass
from typing import ClassVar
from homeassistant.components import select, sensor
from homeassistant.helpers.entity import EntityCategory

# from ..utils.state_translation import TranslationTable
from . import units
from .common import async_setup_entry_factory, Entity, EntityDescription

_DeviceClass = sensor.const.SensorDeviceClass


class SelectEntity(Entity, select.SelectEntity):
    entity_description: "SelectEntityDescription"

    @property
    def _setting(self):
        return self.entity_description.get(self._appliance)

    @property
    def options(self):
        return self._setting.values

    @property
    def current_option(self) -> str | None:
        return self._setting.value

    async def async_select_option(self, option):
        self._setting.value = option
        self.async_write_ha_state()


class ConfigSelectEntity(SelectEntity):
    @property
    def available(self) -> bool:
        a = (
            super().available
            and (p := self._appliance.attributes.get("remoteCtrValid")) is not None
            and p.value == 1
        )
        return a

    # TODO: What async_select option should really do?
    # async def async_select_option(self, option: str) -> None:
    #     setting = self._appliance.settings[self.entity_description.key]
    #     setting.value = self._option_to_number(option, setting.values)
    #     command = self.entity_description.key.split(".")[0]
    #     await self._appliance.commands[command].send()
    #     if command != "settings":
    #         self._appliance.sync_command(command, "settings")
    #     self.coordinator.async_set_updated_data({})


@dataclass(frozen=True, kw_only=True)
class SelectEntityDescription(EntityDescription, select.SelectEntityDescription):
    # translation_table: TranslationTable = TranslationTable()
    entity_cls: ClassVar[type[SelectEntity]] = SelectEntity


@dataclass(frozen=True, kw_only=True)
class ConfigSelectEntityDescription(SelectEntityDescription):
    entity_cls: ClassVar[type[ConfigSelectEntity]] = ConfigSelectEntity
    entity_category: ClassVar[EntityCategory] = EntityCategory.CONFIG


ENTITIES = {
    ConfigSelectEntityDescription(
        name="Program",
        # translation_key=f"programs_{slug}",
        value_picker=lambda a: a.settings["startProgram.program"],
    ),
    ConfigSelectEntityDescription(
        name="Temperature",
        icon="mdi:thermometer",
        device_class=_DeviceClass.TEMPERATURE,
        unit_of_measurement=units.CELSIUS,
        value_picker=lambda a: a.settings["startProgram.temp"],
    ),
    ConfigSelectEntityDescription(
        name="Spin speed",
        icon="mdi:numeric",
        unit_of_measurement=units.REVOLUTIONS_PER_MINUTE,
        value_picker=lambda a: a.settings["startProgram.spinSpeed"],
    ),
    ConfigSelectEntityDescription(
        name="Steam level",
        icon="mdi:weather-dust",
        # translation_table=STEAM_LEVEL,
        value_picker=lambda a: a.settings["startProgram.steamLevel"],
    ),
    ConfigSelectEntityDescription(
        name="Dirt level",
        icon="mdi:liquid-spot",
        # translation_table=DIRTY_LEVEL,
        value_picker=lambda a: a.settings["startProgram.dirtyLevel"],
    ),
    ConfigSelectEntityDescription(
        name="Stain Type",
        icon="mdi:liquid-spot",
        value_picker=lambda a: a.settings["startProgram.extendedStainType"],
    ),
    ConfigSelectEntityDescription(
        name="Dry Time",
        icon="mdi:timer",
        unit_of_measurement=units.MINUTES,
        value_picker=lambda a: a.settings["startProgram.dryTimeMM"],
    ),
    ConfigSelectEntityDescription(
        name="Dry level",
        icon="mdi:hair-dryer",
        translation_key="dry_levels",
        # translation_table=DRY_LEVEL,
        value_picker=lambda a: a.settings["startProgram.dryLevel"],
    ),
    ConfigSelectEntityDescription(
        name="Zone",
        icon="mdi:radiobox-marked",
        translation_key="ref_zones",
        value_picker=lambda a: a.settings["startProgram.zone"],
    ),
    SelectEntityDescription(
        name="Temperature",
        icon="mdi:thermometer",
        unit_of_measurement=units.CELSIUS,
        value_picker=lambda a: a.settings["settings.tempSelZ3"],
    ),
    ConfigSelectEntityDescription(
        name="Remaining Time",
        icon="mdi:timer",
        unit_of_measurement=units.MINUTES,
        value_picker=lambda a: a.settings["startProgram.remainingTime"],
    ),
    SelectEntityDescription(
        name="Diffuser Level",
        # translation_table=DIFFUSER_LEVEL,
        translation_key="diffuser",
        icon="mdi:air-purifier",
        value_picker=lambda a: a.settings["aromaStatus"],
    ),
    SelectEntityDescription(
        name="Mode",
        icon="mdi:play",
        # translation_table=MACH_MODE,
        value_picker=lambda a: a.settings["machMode"],
    ),
    SelectEntityDescription(
        key="settings.humanSensingStatus",
        name="Eco Pilot",
        icon="mdi:run",
        # translation_table=HUMAN_SENSE,
        value_picker=lambda a: a.settings["humanSensingStatus"],
    ),
    SelectEntityDescription(
        name="Fan Direction Horizontal",
        icon="mdi:fan",
        translation_key="fan_horizontal",
        # translation_table=POSITION_HORIZONTAL,
        value_picker=lambda a: a.settings["windDirectionHorizontal"],
    ),
    SelectEntityDescription(
        name="Fan Direction Vertical",
        icon="mdi:fan",
        translation_key="fan_vertical",
        # translation_table=POSITION_VERTICAL,
        value_picker=lambda a: a.settings["windDirectionVertical"],
    ),
}


async_setup_entry = async_setup_entry_factory(ENTITIES)
