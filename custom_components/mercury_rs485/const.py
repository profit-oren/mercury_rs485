#### Константы используемые для интеграции Учет электроэнергии. ####
#### Интеграция работает с отдельными устройствами типа Mercury. ####

from typing import Final
from datetime import timedelta

#### Директорий установки Home Assistant. ####
CONFIG_DIR = "config"

#### Директорий для пользовательских интеграций. ####
CUSTOM_DIR = "custom_components"

#### Директорий для публикаций (для HA local). ####
WWW_DIR = "www"

#### Рекомендуемая версия Home Assistant, не ниже. ####
MIN_HA_VERSION = "2025.1.0"

#### Идентификатор интеграции и имя каталога хранения файлов в HA. ####
DOMAIN = "mercury_rs485"

#### Производитель устройств. ####
MANUFACTURER = "Incotex Electronics Group"

#### Производитель устройств, надпись на панели дашборда. ####
MANUFACTURER_DB ="МЕРКУРИЙ ЭЛЕКТРОНИКС"

#### Имя устройства по умолчанию. ####
CONF_NAME_DEF = "Electricity meter"

#### Имя дашборда по умолчанию. ####
CONF_DASH_DEF = "Mercury"

#### Имя пути для дашборда. ####
url_path = "dashboard-mercury"

#### Иконка дашборда по умолчанию. ####
CONF_ICON_DEF = "mdi:meteor" 

#### Логотип производителя устройств (счетчиков). ####
FILE_LOGO = 'logo_mercury.png'

#### Изображение счетчика для панели дашборда. ####
FILE_MER230 = 'mercury230.png'

#### Конфигурация устройства для демонстрационного режима. ####
DEMO_DEVICE = "/dev/demoUSB"
DEMO_VERSION = "demo-версия"
DEMO_DEVICE_ID = "99999999"

#### Перечень типов устройств для которых работает интеграция. ####
model_list = { "Mercury 230 ART-01 PQRSIN", "Mercury 230 АМ-01 5 RS" }

#### Флаг установки дашборда. Если "Да" - устанавливаем. ####
SET_DASH = "Yes"
NO_SET_DASH = "No"
question = [NO_SET_DASH, SET_DASH,]

#### Интервал обновления данных для координатора (отправка запросов). ####
UPDATE_INTERVAL = timedelta(seconds= 30)

#### Если запросов нет в течение 240 секунд, устройство закрывает канал. #### 
TIME_CLOSE = 220

#### Интервал обновления данных по потреблению за день, год, общему. ####
UPDATE_CURRENT = 300

#### Универсальный сетевой адрес - отвечает любое устройство в сети RS485 (CAN). ####
ADDRESS_FOR_ALL: str = '00'

#### Скорость 9600 бод для многих устройств является скоростю по умолчанию. ####
BAUDRATE_DEF = 9600 

#### Для скорости 9600 бод таймаут порта 5-25 мс. ####
TIMEOUT_PORT: float = .05

#### Для скорости 9600 бод время ожидания ответа, 150-750 мс (max - 33750 мс). ####
#### Время ожидания ответа увеличиваем программно в соответствии с длинной ответа. #### 
TIMEOUT_WAIT: float = .2

