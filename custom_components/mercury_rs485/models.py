#### Определения и массивы данных для интеграции Учет электроэнергии. ####
from __future__ import annotations

from typing import Final
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mercury import MercuryRs485
    from .coordinator import MercuryDataUpdateCoordinator

#### Определяем перечень констант связанных с состоянием устройства. ####
STAT_FLAG = "stat_flag"    #### "Статус линии:" ####                         
DATE_FLAG = "date_flag"    #### "Флаг изменения суток:" ####                 
DEVICE_ID = "device_id"    #### "Серийный номер:" ####                       
TIME_REAL = "time_real"    #### "Внутренние часы:" ####                      
VOLTAGEF1 = "voltagef1"    #### "Напряжение фаза 1:" ####                    
VOLTAGEF2 = "voltagef2"    #### "Напряжение фаза 2:" ####                    
VOLTAGEF3 = "voltagef3"    #### "Напряжение фаза 3:" ####                    
AMPERE_F1 = "ampere_f1"    #### "Ток фаза 1:" ####                           
AMPERE_F2 = "ampere_f2"    #### "Ток фаза 2:" ####                           
AMPERE_F3 = "ampere_f3"    #### "Ток фаза 3:" ####                           
POWER_REA = "power_rea"    #### "Мощность потребления:" ####                 
POWER_RF1 = "power_rf1"    #### "Мощность потребления фаза 1:" ####          
POWER_RF2 = "power_rf2"    #### "Мощность потребления фаза 2:" ####          
POWER_RF3 = "power_rf3"    #### "Мощность потребления фаза 3:" ####          
ENERGY_TS = "energy_ts"    #### "Потреблениие текущие сутки (NA+):" ####     
ENERGY_PS = "energy_ps"    #### "Потреблениие предыдущие сутки (NA+):" ####  
ENERGY_PM = "energy_pm"    #### "Потреблениие за прошлый месяц (NA+):" ####  
ENERGY_TG = "energy_tg"    #### "Потреблениие за текущий год (NA+):" ####    
ENERGY_PG = "energy_pg"    #### "Потреблениие за прошлый год (NA+):" ####    
ENERGY_AL = "energy_al"    #### "Общее потреблениие (NA+):" ####             

#### Массив состояний для интеграции Учет электроэнергии ####
@dataclass
class MercuryState:

    def __init__(self):
        self.data: Dict[str, Union[bool, str, float, None]] = {
            STAT_FLAG: bool(), DATE_FLAG: "", DEVICE_ID: "", TIME_REAL: "", VOLTAGEF1: 0.0, VOLTAGEF2: 0.0, VOLTAGEF3: 0.0,      
            AMPERE_F1: 0.0, AMPERE_F2: 0.0, AMPERE_F3: 0.0, POWER_REA: 0.0, POWER_RF1: 0.0, POWER_RF2: 0.0, POWER_RF3: 0.0,      
            ENERGY_TS: 0.0, ENERGY_PS: 0.0, ENERGY_PM: 0.0, ENERGY_TG: 0.0, ENERGY_PG: 0.0, ENERGY_AL: 0.0, 
        }

    def __getitem__(self, key: str) -> Union[bool, str, float]:
        return self.data[key]

    def __setitem__(self, key: str, value: Union[bool, str, float]) -> None:
        if key in self.data:
            self.data[key] = value
        else:
            raise KeyError(f"Key '{key}' not found in MercuryStat")

#### Перечень запросов (команд) приборов учета электроэнергии типа: ####
#### Меркурий 150, 203.2TD, 204, 208, 230, 231, 234, 236, 238, 350  ####
#### Описание системы команд ver-1-ot-2024-08-30 (сайт разработчика)####
class SendMercury (dict):

    open_user : bytes  = b'\x01\x01\x01\x01\x01\x01\x01\x01' #### открытие канала 1 уровня user
    open_admin : bytes = b'\x01\x02\x02\x02\x02\x02\x02\x02' #### открытие канала 2 уровня admin
    voltage : bytes    = b'\x08\x16\x11'                     #### напряжение в сети
    ampere : bytes     = b'\x08\x16\x21'                     #### потребление тока
    energy_al : bytes  = b'\x05\x00\x00'                     #### получение общего потребления
    energy_ts : bytes  = b'\x05\x40\x00'                     #### потребление за текущие сутки
    energy_ps : bytes  = b'\x05\x50\x00'                     #### потребление за предыдущие сутки
    energy_pm : bytes  = b'\x05\x30\x00'                     #### за прошлый месяц (меняется по n месяца)
    energy_tg : bytes  = b'\x05\x10\x00'                     #### потребление за текущий год
    energy_pg : bytes  = b'\x05\x20\x00'                     #### потребление за предыдущий год
    clock_tv : bytes   = b'\x04\x00'                         #### информация часов устройства
    pasport : bytes    = b'\x08\x01'                         #### получение параметров прибора SN и т.д.
    open_id : bytes    = b'\x00'                             #### тестирование канала - получение ответа
    close_cl : bytes   = b'\x02'                             #### закрытие канала устройства 

#### Перечень ошибок для интерфейса Mercury USB -> RS485 (класс MercuryRs485) ####
class ErrorMercury (dict):
    #### "Ошибка отрытия порта" ####
    open_port:  str = "Error opening port."
    #### "Ошибка тестирования канала, устройство не подключено" ####
    test_chan:  str = "Channel test error, device not connected."
    #### "Длинна ответа не соответствует ожидаемой" ####
    len_answer: str = "The length of the response does not match the expected length." 
    #### "Ошибку возвратило устройство" ####
    channel_er: str = "The device returned an error."
    #### "Нет ответа при регистрации пользователя" ####
    connect_er: str = "No response when registering user."
    #### "Ошибка открытия канала связи при регистрации" ####
    user_conn:  str = "Error opening communication channel during registration."
    #### "Ошибка получения данных от устройства" ####
    read_data:  str = "Error receiving data from device."
    #### "Ошибка проверки CRC сообщения от устройства" ####
    crc_data:   str = "Error checking CRC of message from device."
    #### "Нет ответа при закрытие канала" ####
    close_chan: str = "No response when closing channel."

