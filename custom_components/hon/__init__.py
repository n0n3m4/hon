import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pyhon import Hon
from pyhon.apis import create_httpx_client


from .const import DOMAIN, PLATFORMS, CONF_REFRESH_TOKEN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
    )

    hon = Hon(
        email=entry.data.get(CONF_EMAIL),
        password=entry.data.get(CONF_PASSWORD),
        refresh_token=entry.data.get(CONF_REFRESH_TOKEN),
        session=await hass.async_add_executor_job(create_httpx_client),
        enable_mqtt=True,
        close_session=True,
    )

    hass.data.setdefault(DOMAIN, {}).update(
        {entry.unique_id: {"hon": hon, "coordinator": coordinator}}
    )
    await hon.setup()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hon: Hon = hass.data[DOMAIN][entry.unique_id]["hon"]
    refresh_token = hon._api._session._auth.refresh_token

    hass.config_entries.async_update_entry(
        entry, data={**entry.data, CONF_REFRESH_TOKEN: refresh_token}
    )
    unload = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload:
        await hon.aclose()
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)
    return unload
