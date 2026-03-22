from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from .const import DOMAIN, CONF_JSON_URLS

class PromIncRandomWorkoutsConfigFlow(ConfigFlow, domain=DOMAIN):
	VERSION = 1

	async def async_step_user(
		self, user_input: dict[str, Any] | None = None
	) -> ConfigFlowResult:
		if user_input is not None:
			return self.async_create_entry(
				title="PromInc Random Workouts",
				data=user_input,
			)

		return self.async_show_form(
			step_id="user",
			data_schema=vol.Schema(
				{
					vol.Required(CONF_JSON_URLS): str,
				}
			),
		)
