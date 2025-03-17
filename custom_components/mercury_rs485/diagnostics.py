#### Диагностическая поддержка для mercury_rs485. ####
from __future__ import annotations

from typing import Any
from dataclasses import asdict
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.diagnostics import async_redact_data
from .const import DOMAIN
from .coordinator import MercuryDataUpdateCoordinator

from . import MercuryConfigEntry

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: MercuryConfigEntry
) -> dict[str, Any]:

    coordinator = entry.runtime_data

    return {
        "entry":   asdict(entry.runtime_data.data),
        "state":   entry.runtime_data.data.data,
        "config":  entry.as_dict(),
    }
