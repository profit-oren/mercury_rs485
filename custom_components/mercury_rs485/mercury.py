#### Считывание данных с устройства через USB - Rs485. Эмуляция для демо режима. ####
from __future__ import annotations

from typing import Any, Final

import random
import asyncio
import logging
import serial
import serial.rs485
import time
import struct

from datetime import date
from homeassistant.const import CONF_DEVICE_ID, ATTR_SW_VERSION, ATTR_HW_VERSION, CONF_ADDRESS
from homeassistant.core import HomeAssistant
from .const import DOMAIN, TIMEOUT_WAIT, TIMEOUT_PORT, BAUDRATE_DEF, TIME_CLOSE, UPDATE_CURRENT
from .models import (MercuryState, SendMercury, ErrorMercury,STAT_FLAG,DATE_FLAG,DEVICE_ID,TIME_REAL,
                VOLTAGEF1,VOLTAGEF2,VOLTAGEF3,AMPERE_F1,AMPERE_F2,AMPERE_F3,POWER_REA,POWER_RF1,
                POWER_RF2,POWER_RF3,ENERGY_TS,ENERGY_PS,ENERGY_PM,ENERGY_TG,ENERGY_PG,ENERGY_AL)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.WARN)

#### Интерфейс Mercury USB -> RS485. ####
class MercuryRs485:

    #### Инициализация класса MercuryRs485. ####
    def __init__(self, hass: HomeAssistant, dev_path: str, addr_net: str, data:MercuryState | None ) -> None:
        #### Запоминаем в созданом экземпляре USB - адаптер последовательного порта типа '/dev/ttyUSB0'. ####
        self._dev_path = dev_path
        #### Запоминаем в созданом экземпляре сетевой адрес сети RS485 (CAN) типа строки '1d'. #### 
        self._hex_addr = int(addr_net,16)
        #### Преобразуем сетевой адрес в формат bytes типа b'\x1d'. ####
        self._addr_net = bytes([self._hex_addr])
        #### Используем протокол сервера при отладке обращения к классу. ####
        '''_LOGGER.warning(" address  -  [%s]  [%s]  ", addr_net, self._addr_net)'''
        #### Создаем в экземпляре класса массив сообщений для устройства. ####
        self._send = SendMercury()
        #### Создаем в экземпляре класса массив ошибок, возможных при работе с устройством через порт. ####
        self._error_M = ErrorMercury()
        #### Запоминаем в экземпляре класса ссылку на массив состояний устройства. ####
        self.data_state = data
        #### Создаем флаг времени открытия канала, для исключения повторного открытия канала. ####  
        self._time_open = 0
        #### Флаг обновления текущих данных по потреблению за день, год, общее (раз в 5 минут). ####
        self._time_u_save = 0
        #### Создаем флаг статуса канала (False - канал недоступен, True - канал включен). ####
        self._flag_status = False
        self.hass = hass

        #### Открываем порт USB - адаптера последовательного порта для связи с устройством. #### 
        self.UsbPort = serial.rs485.RS485(
            port = self._dev_path, 
            baudrate = BAUDRATE_DEF, 
            parity = serial.PARITY_NONE, 
            stopbits = 1, 
            bytesize = 8, 
            xonxoff = False, 
            timeout = TIMEOUT_PORT
        )
        #### Устанавливаем настройки для специфической поддержки Rs485. ####
        self.UsbPort.rs485_mode = serial.rs485.RS485Settings(
            rts_level_for_tx = True,
            rts_level_for_rx = False,
            loopback = False,
            delay_before_tx = None,
            delay_before_rx = None
        )

    #### Проверка работы с устройством, получение серийного номера.####  
    #### Обращение направляется всем устройствам, в канале rs485. ID='00'. ####  
    #### При неудаче возвращаем False, при удаче - массив параметров устройства. ####
    async def async_Test_Get_Sn(self) -> bool | dict[str, str]:
        #### Пробуем открыть канал устройства. ####
        if await self.async_open_channel() == False:
            _LOGGER.warning(self._error_M.test_chan+" [%s]", self._dev_path)
            return False
        #### Считываем данные по устройству серийный номер, сетевой адрес, номера версий. ####
        self._Str_ot = await self.async_write_read_mess_to_port(self._send.pasport, 38)
        if not self._Str_ot:
            _LOGGER.warning(self._error_M.read_data+" [%s]", self._dev_path)
            return False
        self._Otv_str =''
        for i in range(0, 16):
            self._Otv_str += self.byte2_to_str(self._Str_ot.hex()[2+i*2:4+i*2])     
        self._device_id = self._Otv_str[0:8]
        self._hw_version = self._Otv_str[8:10]+'.'+self._Otv_str[10:12]+'.20'+self._Otv_str[12:14]
        self._sw_version = self._Otv_str[14:16]+'.'+self._Otv_str[16:18]+'.'+self._Otv_str[18:20]
        if int(str(self._device_id[5:])) < 240:
            self._address = hex(int(str(self._device_id[5:])))
        else:
            self._address = hex(int(str(self._device_id[6:])))
        await self.async_close_channel()
        return {
            CONF_DEVICE_ID: self._device_id,
            ATTR_HW_VERSION: self._hw_version,
            ATTR_SW_VERSION: self._sw_version,
            CONF_ADDRESS: self._address,
        }

    #### Обновляем данные с устройства с сетевым номером, сохраненным в конфигурации. ####  
    async def async_Get_Value(self) -> bool:

        self._flag_status = False
        #### Если вызывается первый раз или время ожидания канала вышло -> открываем канал. ####  
        #### if self._time_open==0 or (time.time() - self._time_open) > TIME_CLOSE: ####
        if  (time.time() - self._time_open) > TIME_CLOSE:
            if await self.async_open_channel() == False:
                _LOGGER.warning(self._error_M.test_chan+" [%s]", self._dev_path)
                return False
        else:
            #### Сбрасываем счетчик времени при открытии порта. ####
            self._time_open = time.time()
        #### Если нет ссылки на массив данных возвращаем ошибку. Это невозможно, но... ####
        if not self.data_state:
            return False
        #### Данные за прошлый период обновляем при инициализации или раз в сутки при непрерывной работе. ####  
        self.__update = False
        if self.data_state[DATE_FLAG] != date.today().isoformat():
            self.data_state[DATE_FLAG] = date.today().isoformat()
            self.__update = True
        #### Данные по потреблению за день, год, общее обновляем через UPDATE_CURRENT секунд. ####  
        self.__update_st = False
        if (time.time() - self._time_u_save) > UPDATE_CURRENT:
            self.__update_st = True
            self._time_u_save = time.time()

        #### Чистим данные локальных переменных для сбора параметров с устройства. #### 
        self._vlt1 = self._vlt2 = self._vlt3 = self._amp1 = self._amp2 = self._amp3 = self._en_al = None 
        self._en_ts = self._en_ps = self._en_pm = self._en_tg = self._en_pg = None

        #### Считываем данные по напряжению в сети ####
        self._Str_ot = await self.async_write_read_mess_to_port(self._send.voltage, 24)
        if not self._Str_ot:
            _LOGGER.warning(self._error_M.read_data+" [%s]", self._dev_path)
        else:
            self._Otvet = self._Str_ot.hex()
            self._vlt1 = int(self._Otvet[6:8]+self._Otvet[4:6],16)/100
            self._vlt2 = int(self._Otvet[12:14]+self._Otvet[10:12],16)/100
            self._vlt3 = int(self._Otvet[18:20]+self._Otvet[16:18],16)/100

        #### Считываем данные по току в сети ####
        self._Str_ot = await self.async_write_read_mess_to_port(self._send.ampere, 24)
        if not self._Str_ot:
            _LOGGER.warning(self._error_M.read_data+" [%s]", self._dev_path)
        else:
            self._Otvet = self._Str_ot.hex()
            self._amp1 = int(self._Otvet[6:8]+self._Otvet[4:6],16)/1000
            self._amp2 = int(self._Otvet[12:14]+self._Otvet[10:12],16)/1000
            self._amp3 = int(self._Otvet[18:20]+self._Otvet[16:18],16)/1000

        if self.data_state[ENERGY_AL] == 0 or self.__update_st == True:
            #### Считываем данные по общей потребляемой энергии. ####
            self._Str_ot = await self.async_write_read_mess_to_port(self._send.energy_al, 38)
            if not self._Str_ot:
                _LOGGER.warning(self._error_M.read_data+" [%s]", self._dev_path)
            else:
                self._Otvet = self._Str_ot.hex()
                self._en_al = int(self._Otvet[4:6]+self._Otvet[2:4]+self._Otvet[8:10]+self._Otvet[6:8],16)/1000

        if self.data_state[ENERGY_TS] == 0 or self.__update_st == True:        
            #### Считываем данные по потребляемой энергии за текущие сутки. ####
            self._Str_ot = await self.async_write_read_mess_to_port(self._send.energy_ts, 38)
            if not self._Str_ot:
                _LOGGER.warning(self._error_M.read_data+" [%s]", self._dev_path)
            else:
                self._Otvet = self._Str_ot.hex()
                self._en_ts = int(self._Otvet[4:6]+self._Otvet[2:4]+self._Otvet[8:10]+self._Otvet[6:8],16)/1000

        if self.data_state[ENERGY_TG] == 0 or self.__update_st == True:        
            #### Считываем данные по потребляемой энергии за текущий год. ####
            self._Str_ot = await self.async_write_read_mess_to_port(self._send.energy_tg, 38)
            if not self._Str_ot:
                _LOGGER.warning(self._error_M.read_data+" [%s]", self._dev_path)
            else:
                self._Otvet = self._Str_ot.hex()
                self._en_tg = int(self._Otvet[4:6]+self._Otvet[2:4]+self._Otvet[8:10]+self._Otvet[6:8],16)/1000

        #### Считываем данные по потребляемой энергии за прошлые сутки, если они отсутствуют. ####
        if self.data_state[ENERGY_PS] == 0 or self.__update == True:
            self._Str_ot = await self.async_write_read_mess_to_port(self._send.energy_ps, 38)
            if not self._Str_ot:
                _LOGGER.warning(self._error_M.read_data+" [%s]", self._dev_path)
            else:
                self._Otvet = self._Str_ot.hex()
                self._en_ps = int(self._Otvet[4:6]+self._Otvet[2:4]+self._Otvet[8:10]+self._Otvet[6:8],16)/1000

        #### Считываем данные по потребляемой энергии за прошлый месяц, если они отсутствуют. ####
        if self.data_state[ENERGY_PM] == 0 or self.__update == True:
            #### Определяем номер прошлого месяца. ####
            self.pm_m = date.today().month
            if self.pm_m==1:
                self.pm_m = 12
            else:
                self.pm_m = self.pm_m - 1
            #### Формируем новый запрос за выбранный месяц.  ####
            self.send_new = self.send_for_last_month (self._send.energy_pm, self.pm_m)
            self._Str_ot = await self.async_write_read_mess_to_port(self.send_new, 38)
            if not self._Str_ot:
                _LOGGER.warning(self._error_M.read_data+" [%s]", self._dev_path)
            else:
                self._Otvet = self._Str_ot.hex()
                self._en_pm = int(self._Otvet[4:6]+self._Otvet[2:4]+self._Otvet[8:10]+self._Otvet[6:8],16)/1000

        #### Считываем данные по потребляемой энергии за прошлый год, если они отсутствуют. ####
        if self.data_state[ENERGY_PG] == 0 or self.__update == True:
            self._Str_ot = await self.async_write_read_mess_to_port(self._send.energy_pg, 38)
            if not self._Str_ot:
                _LOGGER.warning(self._error_M.read_data+" [%s]", self._dev_path)
            else:
                self._Otvet = self._Str_ot.hex()
                self._en_pg = int(self._Otvet[4:6]+self._Otvet[2:4]+self._Otvet[8:10]+self._Otvet[6:8],16)/1000
        #### Проверяем наличие данных. ####
        if self._vlt1 != None and self._amp1 != None and self._vlt2 != None and self._amp2 != None and self._vlt3 != None and self._amp3 != None:
            #### Устанавливаем статус устройства - подключен. ####
            self._flag_status= True
            #### Запмсываем считанные данные в массив (базу) состояния устройства. ###
            self.data_state[VOLTAGEF1] = self._vlt1
            self.data_state[VOLTAGEF2] = self._vlt2
            self.data_state[VOLTAGEF3] = self._vlt3
            self.data_state[AMPERE_F1] = self._amp1
            self.data_state[AMPERE_F2] = self._amp2
            self.data_state[AMPERE_F3] = self._amp3
            #### Рассчитываем и записывает данные по мощности, если они обновились. ####
            self._power = self._vlt1*self._amp1 + self._vlt2*self._amp2 + self._vlt3*self._amp3
            self._power1 = self._vlt1*self._amp1
            self._power2 = self._vlt2*self._amp2 
            self._power3 = self._vlt3*self._amp3
            self.data_state[POWER_REA] = round(self._power,2)
            self.data_state[POWER_RF1] = round(self._power1,2)
            self.data_state[POWER_RF2] = round(self._power2,2)
            self.data_state[POWER_RF3] = round(self._power3,2)
        #### Заносим данные по энергии в базу сосотояний, если они обновились. ####
        if self._en_al != None: self.data_state[ENERGY_AL] = round(self._en_al,2)
        if self._en_ts != None: self.data_state[ENERGY_TS] = round(self._en_ts,2)
        if self._en_tg != None: self.data_state[ENERGY_TG] = round(self._en_tg,2)
        if self._en_ps != None: self.data_state[ENERGY_PS] = round(self._en_ps,2)
        if self._en_pm != None: self.data_state[ENERGY_PM] = round(self._en_pm,2)
        if self._en_pg != None: self.data_state[ENERGY_PG] = round(self._en_pg,2)
        self.data_state[STAT_FLAG] = self._flag_status
        return True

    #### Формирование сообщения для запроса информации по номеру месяца. #### 
    def send_for_last_month(self, send: bytes, mes: int) -> bytes:
        self._send_n = send.hex()[:3]+hex(mes)[2:]+send.hex()[4:]
        return bytes([int(self._send_n[:2],16)])+bytes([int(self._send_n[2:4],16)])+bytes([int(self._send_n[4:],16)])

    #### Открытие канала обмена с устройством. ####  
    async def async_open_channel(self)-> bool:
        #### Проверка подключения устройства к порту. ####
        self.__Str_ot = await self.async_write_read_mess_to_port(self._send.open_id, 8)
        if not self.__Str_ot:
            _LOGGER.warning(self._error_M.test_chan+" [%s]", self._dev_path)
            return False
        self.__Err= self.__Str_ot.hex()[2:4]
        if int(self.__Err,16) != 0:
            _LOGGER.warning(self._error_M.channel_er+" [%s]", self.__Err)
            return False
        #### Открываем канал под пользователем user с паролем по умолчанию. ####
        self.__Str_ot = await self.async_write_read_mess_to_port(self._send.open_user, 8)
        if not self.__Str_ot:
            _LOGGER.warning(self._error_M.connect_er)
            return False
        self.__Err= self.__Str_ot.hex()[2:4]
        if int(self.__Err,16) != 0:
            _LOGGER.warning(self._error_M.user_conn+" [%s]", self.__Err)
            return False
        self._time_open = time.time()
        return True

    #### Закрытие канала обмена с устройством. Используем при конфигурации интеграции. ####
    async def async_close_channel(self)-> bool:
        self.__Str_ot = await self.async_write_read_mess_to_port(self._send.close_cl, 8)
        if not self.__Str_ot:
            _LOGGER.warning(self._error_M.close_chan+" [%s]", self._dev_path)
            return False
        self.__Err= self.__Str_ot.hex()[2:4]
        if int(self.__Err,16) != 0:
            _LOGGER.warning(self._error_M.channel_er+" [%s]", self.__Err)
            return False
        return True    

    #### Расчет CRC-16-ModBus хэш алгоритм. ####
    def crc16(self, data: bytes) -> bytes:
        data = bytearray(data)
        poly = 0xA001
        crc = 0xFFFF
        for b in data:
            crc ^= (0xFF & b)
            for _ in range(0, 8):
                if (crc & 0x0001):
                    crc = ((crc >> 1) & 0xFFFF) ^ poly
                else:
                    crc = ((crc >> 1) & 0xFFFF)
        return crc

    #### Проверка CRC-16-ModBus в принятом сообщении. ####
    def verify_crc16_mess(self, byte_list) -> bool:
        if not byte_list:
            return False
        self._tail = byte_list[-2:]
        self._head = byte_list[:-2]
        self._crc_t = int(self._tail.hex(),16)
        self._crc_h = int((struct.pack('H',self.crc16(bytearray(self._head)))).hex(),16)
        if self._crc_t == self._crc_h:
            return True
        return False

    #### преобразование 2 байт hex в строку. ####
    def byte2_to_str(self, byte2_data):
        _Str_o = str(int(byte2_data,16))
        return _Str_o if len(_Str_o)==2  else '0'+ _Str_o

    #### Запись сообщения в устройство, получение ответа с проверкой crc. ####
    async def async_write_read_mess_to_port(self, mess: bytes, len_m: int) -> bool | bytes:
        self.__len_m = len_m
        #### Корректируем время ожидания в зависимости от длинны ожидаемого ответа. ####
        if self.__len_m > 7: 
            self.__factor = int (self.__len_m / 8) 
        else: 
            self.__factor = 1
        self._Request = self._addr_net
        self._mess = mess
        self._Request += self._mess
        self._Request += self.crc16(self._Request).to_bytes(2, byteorder='little')
        if not self.UsbPort.is_open:
            self.UsbPort.open()
            if  not self.UsbPort.is_open:
                _LOGGER.warning(self._error_M.open_port+" [%s]", self._dev_path)
                return False
        await write_message(self.hass, self.UsbPort, self._Request)
        await asyncio.sleep(TIMEOUT_WAIT * self.__factor)
        self.Str_ot = await read_message(self.hass, self.UsbPort,self.__len_m)
        if self.verify_crc16_mess(self.Str_ot) == False:
            _LOGGER.warning(self._error_M.crc_data + " [%s] write to port -> [%s]", self.Str_ot.hex(), self._Request.hex())
            return False
        if (len(self.Str_ot.hex())) != self.__len_m:
            _LOGGER.warning(self._error_M.len_answer + " [%s]  -  [%s]", len(self.Str_ot.hex()) ,self.__len_m)
            return False
        return self.Str_ot

#### Функцию чтения из порта, запускаем в отдельном потоке. ####
async def read_message(hass: HomeAssistant, merc: serial.serialposix.Serial, len_m: int) -> bytes:
     return await hass.async_add_executor_job(merc.read,len_m)

#### Функцию запись в порт, запускаем в отдельном потоке. ####
async def write_message(hass: HomeAssistant, merc: serial.serialposix.Serial, mess: bytes) -> Any:
     return await hass.async_add_executor_job(merc.write, mess)

#### Класс обновления данных для демонстрационного режима. ####
class EmulatorMercury: 

    def __init__(self, data:MercuryState) -> None:
        #### Инициализация класса EmulatordMercury. ####
        self.data_state = data

    async def async_Emu_Value(self) -> None:
        #### Допускаем 10% на недоступность канала. ####
        if random.random() > 0.1:
            self.data_state[STAT_FLAG] = True
        else:
            self.data_state[STAT_FLAG] = False                                                 
        #### Заполняем условными данными с учетом случайных корректировок. ####
        ___v1 = (random.random()*330 + 2080)/10
        ___v2 = (random.random()*299 + 2003)/10
        ___v3 = (random.random()*225 + 1986)/10
        ___t1 = (random.random()*43)/10
        ___t2 = (random.random()*76)/10
        ___t3 = (random.random()*23)/10
        self.data_state[VOLTAGEF1] = round(___v1,2)
        self.data_state[VOLTAGEF2] = round(___v2,2)
        self.data_state[VOLTAGEF3] = round(___v3,2)
        self.data_state[AMPERE_F1] = round(___t1,2)
        self.data_state[AMPERE_F2] = round(___t2,2)
        self.data_state[AMPERE_F3] = round(___t3,2)
        self.data_state[POWER_REA] = round((___v1*___t1 + ___v2*___t2 +___v3*___t3),2)
        self.data_state[POWER_RF1] = round(___v1*___t1,2)
        self.data_state[POWER_RF2] = round(___v2*___t2,2)
        self.data_state[POWER_RF3] = round(___v3*___t3,2)
        ___sets = self.data_state[ENERGY_TS]
        ___ets = (random.random()*8)/10 + ___sets
        self.data_state[ENERGY_TS] = round(___ets,2)
        self.data_state[ENERGY_PS] = 16.0
        self.data_state[ENERGY_PM] = round((261 + ___ets),2)
        self.data_state[ENERGY_TG] = round((1044 + ___ets),2)
        self.data_state[ENERGY_PG] = 6276.0
        self.data_state[ENERGY_AL] = round((18828 + ___ets),2)
