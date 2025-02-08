import asyncio
import logging
from pathlib import Path
import shutil

import certifi
from homeassistant.core import HomeAssistant


_LOGGER = logging.getLogger(__name__)


# Heavily based on https://github.com/Athozs/hass-additional-ca/blob/c9499d39a4b4d7175336d1d31c4e1b6d9bd6932f/custom_components/additional_ca/__init__.py#L125
async def update_certifi_certificates(hass: HomeAssistant) -> bool:
    """Update CA certificates in Certifi bundle."""

    certifi_bundle_path = Path(certifi.where())
    _LOGGER.debug(f"Certifi CA bundle path: {certifi_bundle_path}")

    certifi_backup_path = certifi_bundle_path.with_suffix(
        certifi_bundle_path.suffix + ".bak"
    )

    rapidssl_ca_path = Path(__file__).with_name("RapidSSL_TLS_RSA_CA_G1.crt")

    if certifi_backup_path.exists():
        # reset Certifi bundle
        await hass.async_add_executor_job(
            shutil.copyfile, certifi_backup_path, certifi_bundle_path
        )
    else:
        # backup Certifi bundle
        await hass.async_add_executor_job(
            shutil.copyfile, certifi_bundle_path, certifi_backup_path
        )

    _LOGGER.info("Certifi bundle CA ready.")

    cacerts, rapidssl_ca = await asyncio.gather(
        *(
            hass.async_add_executor_job(path.read_text)
            for path in (certifi_bundle_path, rapidssl_ca_path)
        )
    )

    if rapidssl_ca not in cacerts:
        cert_name = rapidssl_ca_path.stem.replace("_", " ")
        cacerts += f"\n# Haier hOn: {cert_name}\n"
        cacerts += rapidssl_ca
        await hass.async_add_executor_job(certifi_bundle_path.write_text, cacerts)

        _LOGGER.info(
            f"{cert_name} -> loaded into Certifi CA bundle. Restart Home Assistant to apply changes."
        )

    return True
