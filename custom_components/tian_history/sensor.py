"""传感器平台 - 天聚数行API版本."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import event

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TianHistorySensor(coordinator, entry),
        TianHistoryScrollSensor(coordinator, entry)
    ])


class TianHistorySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = "今日历史"
        self._attr_unique_id = f"{entry.entry_id}_jin_ri_li_shi"
        self._attr_icon = "mdi:calendar-today"
        self._attr_has_entity_name = True
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "info_query")},
            "name": "信息查询",
            "manufacturer": "lambilly",
            "model": "Today History",
            "sw_version": "1.0.0",
        }

    @property
    def native_value(self) -> str:
        return self.coordinator.data.get("current_date", datetime.now().strftime("%Y-%m-%d"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        return {
            "title": data.get("title", ""),
            "today_item": data.get("today_item", {}),
            "history_list": data.get("history_list", []),
            "total_count": data.get("total_count", 0),
            "update_time": data.get("update_time", "")
        }


class TianHistoryScrollSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = "滚动历史"
        self._attr_unique_id = f"{entry.entry_id}_gun_dong_li_shi"
        self._attr_icon = "mdi:calendar-text"
        self._attr_has_entity_name = True
        self._current_item = {}
        self._scroll_index = 0
        self._remove_timer = None
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "info_query")},
            "name": "信息查询",
            "manufacturer": "lambilly",
            "model": "Today History",
            "sw_version": "1.0.0",
        }

    @property
    def native_value(self) -> str:
        return self.coordinator.data.get("current_date", datetime.now().strftime("%Y-%m-%d"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "title": self._current_item.get("title", ""),
            "year": self._current_item.get("year", ""),
            "lsdate": self._current_item.get("lsdate", ""),
            "lsdate_display": self._current_item.get("lsdate_display", ""),
            "content": self._current_item.get("content", ""),
            "scroll_index": self._scroll_index,
            "total_items": len(self.coordinator.filtered_data),
            "scroll_interval": self.coordinator.scroll_interval
        }

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._remove_timer = event.async_track_time_interval(
            self.hass, self._update_scroll_content, timedelta(seconds=self.coordinator.scroll_interval)
        )

    async def async_will_remove_from_hass(self):
        if self._remove_timer:
            self._remove_timer()
        await super().async_will_remove_from_hass()

    async def _update_scroll_content(self, now=None):
        self._current_item = self.coordinator.get_next_scroll_item()
        self._scroll_index = self.coordinator.current_scroll_index
        self.async_write_ha_state()