from typing import Optional, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.device_registry import format_mac
from pyhon.appliances import Appliance

from .const import DOMAIN
from .typedefs import HonEntityDescription


class HonEntity(CoordinatorEntity[DataUpdateCoordinator[dict[str, Any]]]):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        device: Appliance,
        description: Optional[HonEntityDescription] = None,
    ) -> None:
        super().__init__(hass.data[DOMAIN][entry.unique_id]["coordinator"])
        self._hon = hass.data[DOMAIN][entry.unique_id]["hon"]
        self._hass = hass
        self._appliance = device

        if description is not None:
            self.entity_description = description
            self._attr_unique_id = f"{self._appliance_unique_id}{description.key}"
        else:
            self._attr_unique_id = self._appliance_unique_id

    @property
    def _appliance_unique_id(self) -> str:
        return format_mac(self._appliance.mac_address)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._appliance_unique_id)},
            manufacturer=self._appliance.brand,
            name=self._appliance.nick_name,
            model=self._appliance.model_name,
            model_id=self._appliance.model_id,
            sw_version=self._appliance.get("fwVersion", ""),
            serial_number=self._appliance.get("serialNumber", ""),
        )
