from .const import DOMAIN
from typing import Iterable, TYPE_CHECKING, Callable, Any
from homeassistant.helpers.device_registry import format_mac

from dataclasses import dataclass
from functools import cached_property
from homeassistant.helpers import entity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from pyhon import Hon
    from pyhon.appliances import Appliance
    from pyhon.attributes import Attribute


@dataclass(frozen=True, kw_only=True)
class EntityDescription(entity.EntityDescription):
    entity_cls: type["Entity"]
    # TODO: Make value_picker optional
    # with default as getting attribute by name
    value_picker: Callable[["Appliance"], "Attribute"] | None = None

    key: str | None = None

    @cached_property
    def fallback_key(self) -> str:
        return self.name.lower().replace(" ", "_")

    @cached_property
    def cc_key(self) -> str:
        k = "".join(word.capitalize() for word in self.name.split())
        return f"{k[0].lower()}{k[1:]}"

    # TODO: Optional Cluster parameter:
    # - for getting attribute from specific cluster (attributes or settings)
    # Setting are used for non trivial entity categories
    # After that, remove try-except block from get_value method
    def get(self, appliance: "Appliance"):
        if self.value_picker:
            return self.value_picker(appliance)

        return appliance.attributes[self.key or self.cc_key]

    def get_value(self, appliance: "Appliance"):
        try:
            return self.get(appliance).value
        except AttributeError:
            return self.get(appliance)

    def is_applicable(self, appliance: "Appliance") -> bool:
        try:
            self.get(appliance)
            return True
        except (KeyError, AttributeError):
            return False


# TODO: Fix Coordinator data typing
class Entity(CoordinatorEntity[DataUpdateCoordinator[dict[str, "Any"]]]):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        hass: "HomeAssistant",
        entry: "ConfigEntry",
        appliance: "Appliance",
        description: EntityDescription,
    ) -> None:
        super().__init__(hass.data[DOMAIN][entry.unique_id]["coordinator"])
        mac = format_mac(appliance.mac_address)

        self._attr_unique_id = f"{mac}-{description.key or description.fallback_key}"
        self._attr_translation_key = (
            description.translation_key or description.fallback_key
        )
        self._attr_device_info = entity.DeviceInfo(
            identifiers={(DOMAIN, mac)},
            manufacturer=appliance.brand,
            name=appliance.nick_name,
            model=appliance.model_name,
            model_id=str(appliance.model_id),
            sw_version=appliance.get("fwVersion", ""),
            serial_number=appliance.get("serialNumber", ""),
        )

        self.entity_description = description
        self._appliance = appliance


def async_setup_entry_factory(entitity_descriptions: Iterable["EntityDescription"]):
    async def async_setup_entry(
        hass: "HomeAssistant",
        entry: "ConfigEntry",
        async_add_entities: "AddEntitiesCallback",
    ) -> None:
        hon: "Hon" = hass.data[DOMAIN][entry.unique_id]["hon"]

        async_add_entities(
            description.entity_cls(hass, entry, appliance, description)
            for appliance in hon.appliances
            for description in entitity_descriptions
            if description.is_applicable(appliance)
        )

    return async_setup_entry
