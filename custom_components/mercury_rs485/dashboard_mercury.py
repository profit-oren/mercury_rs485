#### Данные для дашборда интеграции Учет электроэнергии. ####
from __future__ import annotations

from typing import Final
from .const import DOMAIN, FILE_LOGO, FILE_MER230, MANUFACTURER_DB

#### Пример панели дашборда. ####
ItemMercury = {
      "views": [
        {
          "badges": [
            {
              "type": "entity",
              "show_name": True,
              "show_state": True,
              "show_icon": True,
              "entity": "sensor.electricity_meter_current_day_energy",
              "color": "",
              "name": "Текущий день",
              "state_content": "state"
            },
            {
              "type": "entity",
              "show_name": True,
              "show_state": True,
              "show_icon": True,
              "entity": "sensor.electricity_meter_last_day_energy",
              "color": "",
              "name": "Прошлый день",
              "state_content": "state"
            },
            {
              "type": "entity",
              "show_name": False,
              "show_state": True,
              "show_icon": True,
              "entity": "binary_sensor.electricity_meter_online_status",
              "color": "",
              "show_entity_picture": True,
              "icon": "",
              "name": "Сеть",
              "state_content": [
                "state",
                "last_updated"
              ]
            },
            {
              "type": "entity",
              "show_name": True,
              "show_state": True,
              "show_icon": True,
              "entity": "sensor.electricity_meter_current_year_energy",
              "color": "",
              "name": "Текущий год",
              "state_content": "state"
            },
            {
              "type": "entity",
              "show_name": True,
              "show_state": True,
              "show_icon": True,
              "entity": "sensor.electricity_meter_last_year_energy",
              "color": "",
              "name": "Прошлый год",
              "state_content": "state"
            }
          ],
          "sections": [
            {
              "type": "grid",
              "cards": [
                {
                  "type": "heading",
                  "heading": "Текущее состояние",
                  "heading_style": "title",
                  "icon": "mdi:clock-time-nine-outline",
                  "grid_options": {
                    "columns": 24,
                    "rows": 1
                  }
                },
                {
                  "type": "tile",
                  "entity": "sensor.electricity_meter_voltage_1_phase",
                  "name": "U 1 фаза",
                  "state_content": "state",
                  "vertical": True,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  }
                },
                {
                  "type": "tile",
                  "entity": "sensor.electricity_meter_voltage_2_phase",
                  "name": "U 2 фаза",
                  "state_content": "state",
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  },
                  "vertical": True
                },
                {
                  "type": "tile",
                  "entity": "sensor.electricity_meter_voltage_3_phase",
                  "name": "U 3 фаза",
                  "state_content": "state",
                  "vertical": True,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  }
                },
                {
                  "type": "picture",
                  "image": "/local/"+DOMAIN+"/"+FILE_MER230,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  }
                },
                {
                  "type": "tile",
                  "entity": "sensor.electricity_meter_electric_current_1_phase",
                  "name": "I 1 фаза",
                  "vertical": True,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  }
                },
                {
                  "type": "tile",
                  "entity": "sensor.electricity_meter_electric_current_2_phase",
                  "name": "I 2 фаза",
                  "vertical": True,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  }
                },
                {
                  "type": "tile",
                  "entity": "sensor.electricity_meter_electric_current_3_phase",
                  "name": "I 3 фаза",
                  "vertical": True,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  }
                },
                {
                  "type": "tile",
                  "entity": "binary_sensor.electricity_meter_online_status",
                  "name": "Статус",
                  "vertical": True,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  }
                },
                {
                  "type": "tile",
                  "entity": "sensor.electricity_meter_consumption_1_phase",
                  "name": "W 1 фаза",
                  "vertical": True,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  }
                },
                {
                  "type": "tile",
                  "entity": "sensor.electricity_meter_consumption_2_phase",
                  "name": "W 2 фаза",
                  "vertical": True,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  }
                },
                {
                  "type": "tile",
                  "entity": "sensor.electricity_meter_consumption_3_phase",
                  "name": "W 3 фаза",
                  "vertical": True,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  }
                },
                {
                  "type": "tile",
                  "entity": "sensor.electricity_meter_current_day_energy",
                  "vertical": True,
                  "grid_options": {
                    "columns": 3,
                    "rows": 2
                  },
                  "name": "Сегодня"
                },
                {
                  "type": "picture",
                  "grid_options": {
                    "columns": 2,
                    "rows": 1
                  },
                  "image": "local/"+DOMAIN+"/"+FILE_LOGO
                },
                {
                  "type": "heading",
                  "icon": "",
                  "heading": MANUFACTURER_DB,
                  "heading_style": "subtitle",
                  "grid_options": {
                    "columns": 9,
                    "rows": 1
                  }
                }
              ],
              "column_span": 1
            },
            {
              "type": "grid",
              "cards": [
                {
                  "type": "heading",
                  "heading_style": "title",
                  "heading": "Потребление энергии",
                  "icon": "mdi:lightning-bolt-outline"
                },
                {
                  "type": "gauge",
                  "entity": "sensor.electricity_meter_total_consumption",
                  "min": 0,
                  "max": 9000,
                  "needle": True,
                  "name": "Общее",
                  "severity": {
                    "green": 2000,
                    "yellow": 6000,
                    "red": 7500
                  },
                  "grid_options": {
                    "columns": "full"
                  }
                },
                {
                  "type": "entity",
                  "entity": "sensor.electricity_meter_total_energy",
                  "name": "Счетчик(всего) ",
                  "unit": "кВТ/час",
                  "state_color": True
                },
                {
                  "type": "entity",
                  "entity": "sensor.electricity_meter_last_day_energy",
                  "name": "Прошлый день",
                  "unit": "кВТ/час",
                  "state_color": True,
                  "icon": "mdi:lightning-bolt-outline"
                },
                {
                  "type": "entity",
                  "entity": "sensor.electricity_meter_last_month_energy",
                  "name": "Прошлый месяц",
                  "unit": "кВТ/час",
                  "state_color": True,
                  "icon": "mdi:lightning-bolt-outline"
                },
                {
                  "type": "entity",
                  "entity": "sensor.electricity_meter_last_year_energy",
                  "name": "Прошлый год",
                  "unit": "кВТ/час",
                  "state_color": True,
                  "icon": "mdi:lightning-bolt-outline"
                }
              ]
            },
            {
              "type": "grid",
              "cards": [
                {
                  "type": "heading",
                  "heading_style": "title",
                  "heading": "Динамика напряжения и тока",
                  "icon": "mdi:alpha-v-circle-outline"
                },
                {
                  "chart_type": "line",
                  "period": "5minute",
                  "type": "statistics-graph",
                  "entities": [
                    "sensor.electricity_meter_voltage_1_phase",
                    "sensor.electricity_meter_voltage_2_phase",
                    "sensor.electricity_meter_voltage_3_phase"
                  ],
                  "stat_types": [
                    "max"
                  ],
                  "hide_legend": True,
                  "min_y_axis": 200,
                  "max_y_axis": 250,
                  "days_to_show": 1,
                  "logarithmic_scale": False
                },
                {
                  "chart_type": "line",
                  "period": "5minute",
                  "type": "statistics-graph",
                  "entities": [
                    "sensor.electricity_meter_electric_current_1_phase",
                    "sensor.electricity_meter_electric_current_2_phase",
                    "sensor.electricity_meter_electric_current_3_phase"
                  ],
                  "stat_types": [
                    "max"
                  ],
                  "hide_legend": True,
                  "days_to_show": 1
                }
              ]
            }
          ],
          "type": "sections",
          "max_columns": 4,
          "icon": "mdi:transmission-tower",
          "cards": []
        }
      ]
  }
