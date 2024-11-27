from dataclasses import dataclass
from homeassistant.components import binary_sensor

from .common import async_setup_entry_factory, Entity, EntityDescription


class BinarySensorEntity(
    Entity,
    binary_sensor.BinarySensorEntity,
):
    entity_description: "BinarySensorEntityDescription"

    @property
    def is_on(self) -> bool:
        ed = self.entity_description
        return ed.get_value(self._appliance) != ed.inverted


@dataclass(frozen=True, kw_only=True)
class BinarySensorEntityDescription(
    EntityDescription,
    binary_sensor.BinarySensorEntityDescription,
):
    inverted: bool = False
    entity_cls: type[BinarySensorEntity] = BinarySensorEntity


_DeviceClass = binary_sensor.BinarySensorDeviceClass


ENTITIES = [
    BinarySensorEntityDescription(
        name="Connection",
        device_class=_DeviceClass.CONNECTIVITY,
        value_picker=lambda a: a.connected,
    ),
    BinarySensorEntityDescription(
        name="Door",
        device_class=_DeviceClass.DOOR,
        translation_key="door_open",
        key="doorStatus",
    ),
    BinarySensorEntityDescription(
        name="Filter Replacement",
        device_class=_DeviceClass.PROBLEM,
        key="filterChangeStatusLocal",
    ),
    BinarySensorEntityDescription(
        name="Ch2O Cleaning Status",
    ),
    BinarySensorEntityDescription(
        name="Salt Level",
        device_class=_DeviceClass.PROBLEM,
        icon="mdi:shaker-outline",
        key="saltStatus",
    ),
    BinarySensorEntityDescription(
        name="Rinse Aid",
        device_class=_DeviceClass.PROBLEM,
        icon="mdi:spray-bottle",
        key="rinseAidStatus",
    ),
    BinarySensorEntityDescription(
        icon="mdi:snowflake",
        name="Super Cool",
        device_class=_DeviceClass.RUNNING,
        key="quickModeZ1",
    ),
    BinarySensorEntityDescription(
        icon="mdi:snowflake-variant",
        name="Super Freeze",
        device_class=_DeviceClass.RUNNING,
        key="quickModeZ2",
    ),
    *(
        BinarySensorEntityDescription(
            name=f"{name} Door {zone}".strip(),
            device_class=_DeviceClass.DOOR,
            icon=icon,
            translation_key=f"{name.lower()}_door",
            key=f"door{zone}Status{key_suffix}",
        )
        for zone in ("", "2")
        for name, icon, key_suffix in (
            ("Fridge", "mdi:fridge-top", "Z1"),
            ("Freezer", "mdi:fridge-bottom", "Z2"),
        )
    ),
    BinarySensorEntityDescription(
        name="Auto-Set Mode",
        icon="mdi:thermometer-auto",
        device_class=_DeviceClass.RUNNING,
        translation_key="auto_set",
        key="intelligenceMode",
    ),
    BinarySensorEntityDescription(
        name="Holiday Mode",
        icon="mdi:palm-tree",
        device_class=_DeviceClass.RUNNING,
    ),
    BinarySensorEntityDescription(
        name="Hot Status",
        device_class=_DeviceClass.HEAT,
        translation_key="still_hot",
    ),
    BinarySensorEntityDescription(
        name="Pan Status",
        icon="mdi:pot-mix",
    ),
    BinarySensorEntityDescription(
        name="Child Lock",
        device_class=_DeviceClass.LOCK,
        inverted=True,
        key="hobLockStatus",
    ),
    # TODO: Conflict here
    BinarySensorEntityDescription(
        name="On",
        device_class=_DeviceClass.RUNNING,
        icon="mdi:power-cycle",
        value_picker=lambda a: a.attributes["parameters"]["onOffStatus"],
    ),
    BinarySensorEntityDescription(
        name="On",
        device_class=_DeviceClass.RUNNING,
        icon="mdi:power-cycle",
        key="onOffStatus",
    ),
    BinarySensorEntityDescription(
        name="Door Lock",
        device_class=_DeviceClass.LOCK,
        inverted=True,
        key="doorLockStatus",
    ),
]

async_setup_entry = async_setup_entry_factory(ENTITIES)
