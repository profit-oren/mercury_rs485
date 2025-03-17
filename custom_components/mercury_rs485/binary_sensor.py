#### Поддержка отслеживания онлайн-статуса устройства ####
from __future__ import annotations

import logging

from typing import Final
from dataclasses import dataclass
from homeassistant.components.binary_sensor import (BinarySensorDeviceClass,
     BinarySensorEntity, BinarySensorEntityDescription,)
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import MercuryConfigEntry
from .coordinator import MercuryDataUpdateCoordinator
from .models import STAT_FLAG

PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)

@dataclass(kw_only=True, frozen=True)
 #### Описание датчика состояния соединения с устройством. ####
class MercuryBinarySensorEntityDescription(BinarySensorEntityDescription):

    available_fn: Callable[[StateType], bool] = lambda _: True

MERCURY_BINARY_SENSOR:  tuple[MercuryBinarySensorEntityDescription, ...] = [
    MercuryBinarySensorEntityDescription(
        key = STAT_FLAG,
        translation_key="online_status",
        device_class=BinarySensorDeviceClass.PLUG,
        entity_registry_enabled_default=True,
        entity_registry_visible_default=True,
        has_entity_name=True,
    ),
]

#### Настраиваем датчик (сенсор) из пользовательских данных конфигурации. ####
async def async_setup_entry(hass: HomeAssistant,config_entry: MercuryConfigEntry,async_add_entities: AddEntitiesCallback,) -> None:
    coordinator = config_entry.runtime_data
    async_add_entities(OnlineStatus(coordinator, description) for description in MERCURY_BINARY_SENSOR)

#### Отображение онлайн-статуса устройства. ####
class OnlineStatus(CoordinatorEntity[MercuryDataUpdateCoordinator], BinarySensorEntity):
    _attr_has_entity_name = True

    #### Инициализируем датчик(бинарный сенсор). ####
    def __init__(self, coordinator: MercuryDataUpdateCoordinator, description: MercuryBinarySensorEntityDescription,) -> None:
        super().__init__(coordinator, description)

        #### Настраиваем уникальный идентификатор и информацию об устройстве. ####
        device_id = coordinator._config_entry.data[CONF_DEVICE_ID]
        self._attr_unique_id = f"{device_id}-{description.key}"
        self.entity_description = description
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        #### Возвращает значение true, если двоичный датчик включен. ####
        return self.coordinator.data[STAT_FLAG]
