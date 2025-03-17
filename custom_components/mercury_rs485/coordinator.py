#### Поддержка устройства через USB -> RS485. Координатор. ####
from __future__ import annotations

import asyncio
import math
import random
import logging

from typing import Final

from homeassistant import exceptions
from awesomeversion import AwesomeVersion
from homeassistant.exceptions import IntegrationError

from homeassistant.const import (CONF_DEVICE, CONF_MODEL, CONF_DEVICE_ID, 
     ATTR_SW_VERSION, ATTR_HW_VERSION, CONF_ADDRESS)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
     DataUpdateCoordinator, UpdateFailed)

from .const import (DOMAIN, MANUFACTURER, UPDATE_INTERVAL, 
     DEMO_DEVICE_ID, DEMO_VERSION, CONF_NAME_DEF) 
from .mercury import MercuryRs485, EmulatorMercury
from .models import MercuryState

_LOGGER = logging.getLogger(__name__)

type MercuryConfigEntry = ConfigEntry[MercuryDataUpdateCoordinator]

####  Координатор обновления данных. ####
class MercuryDataUpdateCoordinator(DataUpdateCoordinator[None]):

    config_entry: ConfigEntry

    def __init__( self, hass: HomeAssistant, entry:MercuryConfigEntry, ) -> None:

        #### Инициализируем данные координатора (объекта). ####
        super().__init__( hass, _LOGGER, config_entry = entry, name = DOMAIN, update_interval = UPDATE_INTERVAL, )

        #### Сохраняем в переменных точку входа, порт, адрес в сети rs485.  ####
        self._config_entry = entry
        self.dev_path = self._config_entry.data[CONF_DEVICE]
        self.dev_addr = self._config_entry.data[CONF_ADDRESS]
        self.hass = hass
        #### Создаем объект MercuryState (экземпляр класса) массив данных состояния устройства. ####
        #### Данные при создании автоматически заполняется нулевыми значениями по умолчанию.    ####
        self._state = MercuryState()

        #### По серийному номеру устройства определяем, в каком режиме работает устройство. ####
        if self._config_entry.data[CONF_DEVICE_ID] == DEMO_DEVICE_ID:
            self._regim = False
            #### Работа в режиме эмуляции, передаем эмулятору - базу данных состояния. ####
            self.EmuRs485 = EmulatorMercury(self._state)
        else:
            self._regim = True
            #### Работа с реальным устройством, передаем в класс - порт, адрес, базу данных состояния. ####
            self.DevRs485 = MercuryRs485(self.hass, self.dev_path, self.dev_addr, self._state)

    @property
    def device_info(self) -> DeviceInfo:
        #### Возвращаем информацию об устройстве. ####
        return DeviceInfo(
            identifiers = {(DOMAIN, self._config_entry.data[CONF_DEVICE_ID])},
            model = self._config_entry.data[CONF_MODEL],
            manufacturer = MANUFACTURER,
            name = CONF_NAME_DEF,
            hw_version = self._config_entry.data[ATTR_HW_VERSION],
            sw_version = self._config_entry.data[ATTR_SW_VERSION],
            serial_number = self._config_entry.data[CONF_DEVICE_ID],
        )

    async def _async_update_data(self) -> MercuryState:
        #### Вызов функции обновления данных эмулятором или интерфейсом. ####
        if self._config_entry.data[CONF_DEVICE_ID] == DEMO_DEVICE_ID:
            config_m = await self.EmuRs485.async_Emu_Value()
        else:
            config_m = await self.DevRs485.async_Get_Value()
        return self._state

