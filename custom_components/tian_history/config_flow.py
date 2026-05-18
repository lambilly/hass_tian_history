"""配置流 - 天聚数行API版本."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, DEFAULT_SCROLL_INTERVAL


class TianHistoryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理配置流."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """处理用户步骤."""
        errors = {}

        if user_input is not None:
            api_key = user_input["api_key"].strip()
            if await self._test_api_key(api_key):
                return self.async_create_entry(
                    title="历史上的今天",
                    data={"api_key": api_key},
                    options={"scroll_interval": user_input["scroll_interval"]}
                )
            else:
                errors["base"] = "invalid_api_key"

        data_schema = vol.Schema({
            vol.Required("api_key"): str,
            vol.Optional("scroll_interval", default=DEFAULT_SCROLL_INTERVAL): vol.All(
                vol.Coerce(int), vol.Range(min=5, max=300)
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"api_url": "https://www.tianapi.com/"}
        )

    async def _test_api_key(self, api_key: str) -> bool:
        """测试API密钥是否有效."""
        from datetime import datetime
        import async_timeout
        session = async_get_clientsession(self.hass)
        today = datetime.now()
        date_str = today.strftime("%m%d")
        url = "https://apis.tianapi.com/lishi/index"
        data = {"key": api_key, "date": date_str}
        try:
            async with async_timeout.timeout(10):
                async with session.post(url, data=data) as resp:
                    if resp.status != 200:
                        return False
                    json_data = await resp.json()
                    return json_data.get("code") == 200
        except Exception:
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TianHistoryOptionsFlow(config_entry)


class TianHistoryOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "scroll_interval",
                    default=self.config_entry.options.get("scroll_interval", DEFAULT_SCROLL_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300))
            })
        )