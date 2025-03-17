#### Поддержка Mercury через USB порт --> RS485. ####
from __future__ import annotations

import os
import logging
import shutil

from typing import Any, Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (Platform, CONF_DEVICE, CONF_THEN, CONF_MODE, CONF_RESOURCES, 
     CONF_ICON, __version__ as current_version)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.components.lovelace.dashboard import LovelaceStorage, DashboardsCollection
from homeassistant.components.lovelace import  _register_panel, LovelaceData, dashboard
from homeassistant.components.lovelace.const import (CONF_TITLE, MODE_STORAGE, CONF_REQUIRE_ADMIN, 
     CONF_SHOW_IN_SIDEBAR, CONF_URL_PATH)
from homeassistant.util.hass_dict import HassKey
from awesomeversion import AwesomeVersion

from .dashboard_mercury import ItemMercury
from .coordinator import MercuryDataUpdateCoordinator, MercuryConfigEntry
from .const import (DOMAIN, DEMO_DEVICE, SET_DASH, NO_SET_DASH, CONF_DASH_DEF, CONF_ICON_DEF,  
     url_path, MIN_HA_VERSION, FILE_LOGO, FILE_MER230, CONFIG_DIR, CUSTOM_DIR, WWW_DIR)

_LOGGER = logging.getLogger(__name__)

LOVELACE_DATA: HassKey[LovelaceData] = HassKey('lovelace')

#### Определяем используемые платформы. ####
PLATFORMS = (Platform.BINARY_SENSOR, Platform.SENSOR)

type MercuryConfigEntry = ConfigEntry[MercuryDataUpdateCoordinator]

#### Используем данные конфигурации точки входа для настройки функций интеграции. ####
async def async_setup_entry(hass: HomeAssistant, config_entry: MercuryConfigEntry) -> bool:

    dev_path = config_entry.data[CONF_DEVICE]
    then_dash = config_entry.data[CONF_THEN]

    #### Проверяем что установленная версия Home Assistant не ниже рекомендуемой. ####
    if AwesomeVersion(current_version) < AwesomeVersion(MIN_HA_VERSION):
        _LOGGER.warning(f"Version Home Assistant {current_version} below recommended {MIN_HA_VERSION}")

    #### Если не эмулятор устройства проверяем наличие USB-адаптера последовательного порта ####
    if dev_path != DEMO_DEVICE:
        if not await hass.async_add_executor_job(os.path.exists, dev_path):
            raise ConfigEntryNotReady(
                f"Could not find Mercury device with configuration {dev_path}"
            )

    #### Проверяем, выбран режим установки дашборда. ####
    if then_dash == SET_DASH:
        '''_LOGGER.warning("Выбран режим установки дашбоарда ")'''
        src_dir = '/'+CONFIG_DIR+'/'+CUSTOM_DIR+'/'+DOMAIN+'/'
        dst_dir = '/'+CONFIG_DIR+'/'+WWW_DIR+'/'+DOMAIN+'/'
        #### Проверяем наличие директория для публикации. ####
        if not os.path.exists(dst_dir):
            #### Если нет, то создаем директорий для публикации. ####
            itog= await async_makedirs(hass, dst_dir)
            '''_LOGGER.warning('Make dir: [%s] ', itog)'''
        if os.path.exists(dst_dir):
            #### При наличии директория копируем в него изображение, если изображения нет. ####
            if not os.path.isfile(dst_dir+FILE_LOGO):
                itog= await async_copy_file(hass, src_dir+FILE_LOGO, dst_dir+FILE_LOGO)
                '''_LOGGER.warning('Copy file: [%s] ', itog)'''
            if not os.path.isfile(dst_dir+FILE_MER230):
                itog= await async_copy_file(hass, src_dir+FILE_MER230, dst_dir+FILE_MER230)
                '''_LOGGER.warning('Copy file: [%s] ', itog)'''
        #### Формируем конфигурацию дашборда. ####
        mercury_config = {
                 CONF_SHOW_IN_SIDEBAR: True,
                 CONF_TITLE: CONF_DASH_DEF,
                 CONF_REQUIRE_ADMIN: False,
                 CONF_ICON: CONF_ICON_DEF,
                 CONF_MODE: MODE_STORAGE,
                 CONF_URL_PATH: url_path
        }
        #### Вызываем класс коллекции дашбордов. ####
        dashboards_collection = DashboardsCollection(hass)
        '''_LOGGER.warning(f"Коллекция дашбордов : {dashboards_collection}")'''
        #### Загружаем в память коллекцию дашбордов. ####
        data_load = await dashboards_collection.async_load()
        '''_LOGGER.warning(f"Коллекция data_load : {data_load}")'''
        #### Проверка существует дашборд mercury? Если да - не устанавливаем ####
        if not hass.data[LOVELACE_DATA].dashboards.get(url_path):
            #### Добавляем в коллекцию дашборд mercury. ####
            data_creat = await dashboards_collection.async_create_item(mercury_config)  
            '''_LOGGER.warning(f"Коллекция create_item : {data_creat}")'''
            #### Заносим конфигурацию дашборда mercury в lovelace. #### 
            hass.data[LOVELACE_DATA].dashboards[url_path] = LovelaceStorage(hass, data_creat)
            #### Регистрируем дашборд mercury. ####
            _register_panel(hass, url_path, MODE_STORAGE, data_creat, False)
            #### Обращаемся к объекту дашборда mercury. ####
            dashboard = hass.data[LOVELACE_DATA].dashboards.get(url_path)
            #### Загружаем в дашборд содержимое панели дашборда mercury. ####
            await dashboard.async_save(ItemMercury)
            #### Загружаем в память коллекцию дашбордов. ####
            await dashboards_collection.async_load()

    #### Определяем координатора для обновления данных интеграции. ####
    coordinator = MercuryDataUpdateCoordinator(hass, config_entry)

    #### Обновление записи конфигурации, первое для координатора данных. ####
    await coordinator.async_config_entry_first_refresh()

    #### Сохраняем координатор для дальнейшего использования.####
    config_entry.runtime_data = coordinator

    #### Пересылаем записи конфигурации на поддерживаемые платформы.####
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    #### Возвращаем результат работы успех. ####
    return True

#### Выгружаем данные конфигурации для всех установленных платформ. ####
async def async_unload_entry(hass: HomeAssistant, entry: MercuryConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

#### Функция копирования файла, запускаем в отдельном потоке. ####
async def async_copy_file(hass: HomeAssistant, src: str, dst: str) -> Any:
     return await hass.async_add_executor_job(shutil.copyfile, src, dst)

#### Функция создания директория, запускаем в отдельном потоке. ####
async def async_makedirs(hass: HomeAssistant, dst: str) -> Any:
     return await hass.async_add_executor_job(os.makedirs, dst, True)
