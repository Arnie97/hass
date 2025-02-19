"""Support for Rituals Perfume Genie binary sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from pyrituals import Diffuser

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RitualsDataUpdateCoordinator
from .entity import DiffuserEntity


@dataclass
class RitualsentityDescriptionMixin:
    """Mixin values for Rituals entities."""

    is_on_fn: Callable[[Diffuser], bool]
    has_fn: Callable[[Diffuser], bool]


@dataclass
class RitualsBinarySensorEntityDescription(
    BinarySensorEntityDescription, RitualsentityDescriptionMixin
):
    """Class describing Rituals binary sensor entities."""


ENTITY_DESCRIPTIONS = (
    RitualsBinarySensorEntityDescription(
        key="charging",
        name="Battery Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda diffuser: diffuser.charging,
        has_fn=lambda diffuser: diffuser.has_battery,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the diffuser binary sensors."""
    coordinators: dict[str, RitualsDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    async_add_entities(
        RitualsBinarySensorEntity(coordinator, description)
        for coordinator in coordinators.values()
        for description in ENTITY_DESCRIPTIONS
        if description.has_fn(coordinator.diffuser)
    )


class RitualsBinarySensorEntity(DiffuserEntity, BinarySensorEntity):
    """Defines a Rituals binary sensor entity."""

    entity_description: RitualsBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: RitualsDataUpdateCoordinator,
        description: RitualsBinarySensorEntityDescription,
    ) -> None:
        """Initialize Rituals binary sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.diffuser.hublot}-{description.key}"
        self._attr_name = f"{coordinator.diffuser.name} {description.name}"

    @property
    def is_on(self) -> bool:
        """Return the state of the binary sensor."""
        return self.entity_description.is_on_fn(self.coordinator.diffuser)
