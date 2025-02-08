import logging
from pathlib import Path
from typing import Any

from aiohttp.client_exceptions import ClientConnectorCertificateError
from pyhon import Hon
import voluptuous as vol  # type: ignore[import-untyped]

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client, config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_REFRESH_TOKEN, DOMAIN, PLATFORMS
from .ssl import update_certifi_certificates

_LOGGER = logging.getLogger(__name__)

HON_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema(vol.All(cv.ensure_list, [HON_SCHEMA]))},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = aiohttp_client.async_get_clientsession(hass)
    if (config_dir := hass.config.config_dir) is None:
        raise ValueError("Missing Config Dir")
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    refresh_token = entry.data.get(CONF_REFRESH_TOKEN)
    try:
        hon = await Hon(
            email=email,
            password=password,
            session=session,
            mqtt=True,
            test_data_path=Path(config_dir),
            refresh_token=refresh_token,
        ).setup()
    except ClientConnectorCertificateError:
        await update_certifi_certificates(hass)
        return


    if (new_refresh_token := hon.auth.refresh_token) != refresh_token:
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_REFRESH_TOKEN: new_refresh_token}
        )

    coordinator: DataUpdateCoordinator[dict[str, Any]] = DataUpdateCoordinator(
        hass, _LOGGER, name=DOMAIN
    )
    hon.subscribe_updates(coordinator.async_update_listeners)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.unique_id] = {"hon": hon, "coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload:
        await hass.data[DOMAIN].pop(entry.unique_id)["hon"].aclose()

        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload
