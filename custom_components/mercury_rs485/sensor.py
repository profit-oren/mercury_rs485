#### Поддержка датчиков устройства. ####
from __future__ import annotations

import logging

from typing import Final
from dataclasses import dataclass
from collections.abc import Callable
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity,
     SensorEntityDescription, SensorStateClass,)
from homeassistant.const import (UnitOfElectricCurrent, UnitOfElectricPotential,
     UnitOfPower, UnitOfEnergy, CONF_DEVICE_ID)

from . import MercuryConfigEntry
from .coordinator import MercuryDataUpdateCoordinator
from .models import (VOLTAGEF1,VOLTAGEF2,VOLTAGEF3,AMPERE_F1,AMPERE_F2,AMPERE_F3,POWER_REA,POWER_RF1,
                POWER_RF2,POWER_RF3,ENERGY_TS,ENERGY_PS,ENERGY_PM,ENERGY_TG,ENERGY_PG,ENERGY_AL)

PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)

@dataclass(kw_only=True, frozen=True)
 #### Описание датчиков устройства, пользовательские данные. ####
class MemorySensorEntityDescription(SensorEntityDescription):

    value_fn: Callable[[StateType], StateType | datetime] = lambda x: x
    available_fn: Callable[[StateType], bool] = lambda _: True

MERCURY_SENSOR_TYPES = (
    MemorySensorEntityDescription(
        key=AMPERE_F1,
        translation_key="ampere_1_phase",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MemorySensorEntityDescription(
        key=AMPERE_F2,
        translation_key="ampere_2_phase",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
       state_class=SensorStateClass.MEASUREMENT,
   ),
    MemorySensorEntityDescription(
        key=AMPERE_F3,
        translation_key="ampere_3_phase",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MemorySensorEntityDescription(
        key=VOLTAGEF1,
        translation_key="voltage_1_phase",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MemorySensorEntityDescription(
        key=VOLTAGEF2,
        translation_key="voltage_2_phase",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MemorySensorEntityDescription(
        key=VOLTAGEF3,
        translation_key="voltage_3_phase",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MemorySensorEntityDescription(
        key=POWER_REA,
        translation_key="power_consumption",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    MemorySensorEntityDescription(
        key=POWER_RF1,
        translation_key="power_consumption_f1",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    MemorySensorEntityDescription(
        key=POWER_RF2,
        translation_key="power_consumption_f2",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    MemorySensorEntityDescription(
        key=POWER_RF3,
        translation_key="power_consumption_f3",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    MemorySensorEntityDescription(
        key=ENERGY_TS,
        translation_key="current_day_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    MemorySensorEntityDescription(
        key=ENERGY_PS,
        translation_key="last_day_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    MemorySensorEntityDescription(
        key=ENERGY_PM,
        translation_key="last_month_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    MemorySensorEntityDescription(
        key=ENERGY_TG,
        translation_key="current_year_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    MemorySensorEntityDescription(
        key=ENERGY_PG,
        translation_key="last_year_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    MemorySensorEntityDescription(
        key=ENERGY_AL,
        translation_key="total_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
)
    
#### Используем данные конфигурации, точки входа для настройки датчиков. ####
async def async_setup_entry(hass: HomeAssistant, config_entry: MercuryConfigEntry, async_add_entities: AddEntitiesCallback,) -> None:
    #### Создаем (добавляем) датчики (сенсоры) на основе пользовательских данных конфигурации. ####
    coordinator = config_entry.runtime_data
    async_add_entities(MercurySensor(coordinator, description)
        for description in MERCURY_SENSOR_TYPES
    )
    
#### Класс представления сущности датчика для значений состояния устройства ####
class MercurySensor(CoordinatorEntity[MercuryDataUpdateCoordinator], SensorEntity):
    
    _attr_entity_registry_enabled_default=True
    _attr_entity_registry_visible_default=True
    _attr_has_entity_name = True
        
    def __init__(self, coordinator: MercuryDataUpdateCoordinator, description: SensorEntityDescription, ) -> None:

        #### Инициализируем  датчик. ####
        super().__init__(coordinator, description)

        #### Настраиваем уникальный идентификатор и информацию об устройстве. ####
        device_id = coordinator._config_entry.data[CONF_DEVICE_ID]
        self._attr_unique_id = f"{device_id}-{description.key}"
        self.entity_description = description
        self._attr_device_info = coordinator.device_info
        #### Проводим обновление атрибутов. ####
        self._update_attrs()

    @callback
    def _handle_coordinator_update(self) -> None:
        #### Обрабатываем обновленные данные по команде координатора. ####
        self._update_attrs()
        self.async_write_ha_state()

    def _update_attrs(self) -> None:
        #### Обновляем атрибуты датчика на основе данных координатора. ####
        key = self.entity_description.key
        self._attr_native_value  = self.coordinator.data[key]
