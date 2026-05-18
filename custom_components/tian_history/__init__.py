"""历史上的今天集成 - 天聚数行API版本."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import event

from .const import DOMAIN, API_URL, FORBIDDEN_KEYWORDS, DEFAULT_SCROLL_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置集成入口."""
    hass.data.setdefault(DOMAIN, {})
    
    coordinator = TianHistoryCoordinator(hass, entry)
    await setup_scheduled_updates(hass, coordinator)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def setup_scheduled_updates(hass: HomeAssistant, coordinator) -> None:
    """设置定时更新任务 - 每天0:01分更新."""
    async def scheduled_update(now=None):
        max_retries = 2
        retry_delay = 600
        for attempt in range(max_retries + 1):
            try:
                await coordinator.async_refresh()
                _LOGGER.info("数据更新成功")
                break
            except Exception as err:
                if attempt < max_retries:
                    _LOGGER.warning("数据更新失败，%d分钟后重试: %s", retry_delay // 60, err)
                    await asyncio.sleep(retry_delay)
                else:
                    _LOGGER.error("数据更新失败，已重试%d次: %s", max_retries, err)
    
    async_track_time = event.async_track_time_change(
        hass, scheduled_update, hour=0, minute=1, second=0
    )
    coordinator._scheduled_update = async_track_time


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载集成入口."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN][entry.entry_id]
        if hasattr(coordinator, '_scheduled_update'):
            coordinator._scheduled_update()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class TianHistoryCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(hours=24))
        self.entry = entry
        self.api_key = entry.data["api_key"]
        self.scroll_interval = entry.options.get("scroll_interval", DEFAULT_SCROLL_INTERVAL)
        self.current_scroll_index = 0
        self.filtered_data = []
        self.last_success_time = None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with async_timeout.timeout(15):
                return await self._fetch_today_history()
        except Exception as err:
            raise UpdateFailed(f"获取数据错误: {err}") from err

    async def _fetch_today_history(self) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        today = datetime.now()
        date_str = today.strftime("%m%d")
        url = API_URL
        form_data = {"key": self.api_key, "date": date_str}
        
        async with session.post(url, data=form_data) as response:
            if response.status != 200:
                raise UpdateFailed(f"API请求失败: {response.status}")
            data = await response.json()
            if data.get("code") != 200:
                raise UpdateFailed(f"API返回错误: {data.get('code')} - {data.get('msg')}")
            
            raw_list = data.get("result", {}).get("list", [])
            filtered_list = self._filter_data(raw_list)
            
            import random
            today_item = random.choice(filtered_list) if filtered_list else {}
            
            self.filtered_data = filtered_list
            self.current_scroll_index = 0
            self.last_success_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "title": "历史上的今天",
                "today_item": today_item,
                "history_list": filtered_list,
                "update_time": self.last_success_time,
                "current_date": today.strftime("%Y-%m-%d"),
                "total_count": len(filtered_list)
            }

    def _filter_data(self, data_list: list) -> list:
        filtered = []
        for item in data_list:
            title = item.get("title", "")
            if not any(kw in title for kw in FORBIDDEN_KEYWORDS):
                filtered.append({
                    "title": title,
                    "year": item.get("lsdate", "").split("-")[0] if item.get("lsdate") else "",
                    "lsdate": item.get("lsdate", ""),
                    "content": title
                })
        return filtered

    def get_next_scroll_item(self) -> dict:
        if not self.filtered_data:
            return {"title": "暂无数据", "content": "请等待数据更新", "year": "", "lsdate": "", "lsdate_display": ""}
        item = self.filtered_data[self.current_scroll_index]
        self.current_scroll_index = (self.current_scroll_index + 1) % len(self.filtered_data)
        lsdate = item.get("lsdate", "")
        return {
            "title": item.get("title", ""),
            "year": item.get("year", ""),
            "lsdate": lsdate,
            "lsdate_display": lsdate.split("-")[0] + "年" if lsdate else "",
            "content": item.get("content", "")
        }