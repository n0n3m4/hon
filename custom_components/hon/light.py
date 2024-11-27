from dataclasses import dataclass
from typing import Any

from homeassistant.components import light

from .common import EntityDescription, Entity, async_setup_entry_factory


class LightEntity(Entity, light.LightEntity):
    entity_description: "LightEntityDescription"

    @property
    def supported_color_modes(self) -> set[str]:
        return (
            {light.ColorMode.ONOFF}
            if len(self.entity_description.get(self._appliance).values) == 2
            else {light.ColorMode.BRIGHTNESS}
        )

    @property
    def is_on(self) -> bool:
        return self.entity_description.get_value(self._appliance) > 0

    @property
    def brightness(self) -> int | None:
        s = self.entity_description.get(self._appliance)
        return round(s.value / s.max * 255)

    async def async_set(self, value: int) -> None:
        setting = self.entity_description.get(self._appliance)
        setting.value = value

        # TODO: Implement command sending
        # await self._appliance.commands[self.entity_description.key.split(".")[0]].send()

    async def async_turn_on(self, **kwargs: Any) -> None:
        setting = self.entity_description.get(self._appliance)

        percent = kwargs.get(light.ATTR_BRIGHTNESS, 255) / 255
        value = round(setting.max * percent)

        await self.async_set(value)

    async def async_turn_off(self, **kwargs: Any) -> None:
        value = self.entity_description.get(self._appliance).min

        await self.async_set(value)


@dataclass(frozen=True, kw_only=True)
class LightEntityDescription(EntityDescription, light.LightEntityDescription):
    entity_cls: type["LightEntity"] = LightEntity


ENTITIES = {
    LightEntityDescription(
        name="Light",
        value_picker=lambda a: a.settings["lightStatus"],
    ),
}


async_setup_entry = async_setup_entry_factory(ENTITIES)
