from typing import Any
from dataclasses import dataclass
from homeassistant.components import lock

from pyhon.parameter import RangeParameter

from .entity import HonEntity

from .common import EntityDescription, Entity, async_setup_entry_factory


class LockEntity(Entity, lock.LockEntity):
    entity_description: "LockEntityDescription"

    @property
    def is_locked(self) -> bool | None:
        return self.entity_description.get_value(self._appliance) == 1

    async def async_set(self, value: int) -> None:
        s = self.entity_description.get(self._appliance)
        s.value = value

        # TODO: Implement command sending
        # await self._appliance.commands[self.entity_description.key.split(".")[0]].send()

    async def async_lock(self, **kwargs: Any) -> None:
        s = self.entity_description.get(self._appliance)
        value = s.max if isinstance(s, RangeParameter) else 1

        await self.async_set(value)

    async def async_unlock(self, **kwargs: Any) -> None:
        s = self.entity_description.get(self._appliance)
        s.value = s.min if isinstance(s, RangeParameter) else 0

        await self.async_set(s.value)


@dataclass(frozen=True, kw_only=True)
class LockEntityDescription(EntityDescription, lock.LockEntityDescription):
    entity_cls: type[LockEntity] = LockEntity


class HonLockEntity(HonEntity, LockEntity):
    entity_description: LockEntityDescription

    # TODO: available property should be mixin?
    # it occurs in every entity which may be controlled remotely
    @property
    def available(self) -> bool:
        a = (
            super().available
            and (p := self._appliance.attributes.get("remoteCtrValid")) is not None
            and p.value == 1
        )
        return a


ENTITIES = {
    LockEntityDescription(
        name="Lock Status",
        translation_key="mode",
    ),
}

async_setup_entry = async_setup_entry_factory(ENTITIES)
