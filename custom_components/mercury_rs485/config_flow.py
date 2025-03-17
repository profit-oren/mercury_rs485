#### Конфигурационный поток для интеграции Учет электроэнергии ####
from __future__ import annotations

import asyncio
import logging
import serial
import json
import voluptuous as vol
import serial.tools.list_ports

from typing import Any
from typing import Final
from homeassistant.components import usb
from homeassistant import exceptions

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (CONF_DEVICE, CONF_MODEL, CONF_DEVICE_ID,  
     ATTR_SW_VERSION, ATTR_HW_VERSION, CONF_ADDRESS, CONF_THEN)
from homeassistant.helpers import config_validation as cv, selector
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from homeassistant.exceptions import HomeAssistantError
from homeassistant.exceptions import IntegrationError

from .const import (DOMAIN, DEMO_DEVICE, DEMO_VERSION, DEMO_DEVICE_ID,  
     ADDRESS_FOR_ALL, model_list, question,CONFIG_DIR, CUSTOM_DIR)
from .mercury import MercuryRs485
from .models import MercuryState

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.WARN)

#### Отработчик потока конфигурации пользовательской интеграции Учет электроэнергии (Mercury). ####
class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any]) -> ConfigFlowResult:

        errors = {}
        #### Определяем список присутствующих на сервере USB портов. ####
        ports = await get_usb_ports(self.hass)
        #### Дополнительно в список включаем несуществующий порт, для демонстрационного режима ####
        ports[DEMO_DEVICE] = 'Port: demoUSB, USB VID:PID=demo:demo LOCATION=0-0, Demo-Serial'
        #### Позволяем пользователю выбрать порт, устройство и флаг установки панели дашборда. ####
        schema = vol.Schema(
            { 
            vol.Required(CONF_MODEL): vol.In(model_list), 
            vol.Required(CONF_DEVICE): vol.In(ports), 
            vol.Required(CONF_THEN): SelectSelector(
                        SelectSelectorConfig(
                            options=question,
                            translation_key=CONF_THEN,
                            mode=SelectSelectorMode.DROPDOWN,
                            )
                        )
            }
        )
        #### Выполняем первый этап настройки. ####
        if user_input:
             #### Сохраняем устройство, выбранный порт, флаг установки дашборда в переменные. ####
            dev_path = user_input[CONF_DEVICE]
            model = user_input[CONF_MODEL]
            then = user_input[CONF_THEN]
            _LOGGER.info("Input dev_path [%s]", dev_path)
            _LOGGER.info("Input model [%s]", model)
            #### Прерываем работу, если присутствует запись с такой же конфигурацией. ####
            self._async_abort_entries_match({CONF_DEVICE: dev_path})
            try:
                if dev_path != DEMO_DEVICE: 
                    #### Создаем экземпляр объкта класса интерфейса с устройством. ####
                    self.DevRs485 = MercuryRs485(self.hass, dev_path, ADDRESS_FOR_ALL, None)
                    #### Проверяем соединение с устройством и получаем данные. ####
                    config_m = await self.DevRs485.async_Test_Get_Sn()
                    if  config_m != False:
                        device_id=config_m[CONF_DEVICE_ID] 
                        address=config_m[CONF_ADDRESS]
                        sw_version=config_m[ATTR_SW_VERSION]
                        hw_version=config_m[ATTR_HW_VERSION]
                    else:
                        errors = {"base": "cannot_connect"}
                        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
                else:
                    device_id = DEMO_DEVICE_ID
                    hw_version = DEMO_VERSION
                    sw_version = DEMO_VERSION
                    address = "ff"
                #### Создаем словарь конфигурационных данных для создания конфигурационной записи. ####
                #### Для ключей словаря берем типовые константы компонентов Home Assistant. ####
                config_data = {
                    CONF_DEVICE: dev_path,
                    CONF_MODEL: model,
                    CONF_DEVICE_ID: device_id,
                    CONF_ADDRESS: address,
                    ATTR_SW_VERSION: sw_version,
                    ATTR_HW_VERSION: hw_version, 
                    CONF_THEN: then,
                }
                #### Используем серийный номер устройства в качестве уникального ID. ####
                #### Прерваeм поток если выполняется другой поток, с таким же ID. ####
                existing_entry = await self.async_set_unique_id(device_id)
                #### Поток найден - прерваемся. #### 
                self._abort_if_unique_id_configured()
                #### Поток не найден должны создавать новую запись. #### 
                #### Формируем название устройства. ####
                title = model+ " №:" + device_id + " port:" + dev_path
                #### Создаем новую запись (entries) в реестре конфигураций (config entries). ####
                return self.async_create_entry(title=title, data=config_data)
            except Exception:
                #### Исключение для остальных случаев (обычно сбои в программе, смотрим протокол) ####
                _LOGGER.exception("Unexpected error")
                errors["base"] = "unknown"
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

#### Возвращает список портов USB в удобочитаемом виде. ####
async def get_usb_ports(hass: HomeAssistant) -> dict[str, str]:
    usb_ports = {}
    ports = await hass.async_add_executor_job(serial.tools.list_ports.comports)
    for port in ports:
        if 'USB' in port.hwid:
            usb_ports[port.device] ='Port: '+ port.name +', '+ port.hwid + ', '+ port.description 
    return usb_ports

class CannotConnect(HomeAssistantError):
    """Ошибка, указывающая на невозможность подключения."""
