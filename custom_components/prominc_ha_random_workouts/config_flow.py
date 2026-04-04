import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class PromIncRandomWorkoutsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup flow."""
        errors = {}
        if user_input is not None:
            # We use the Category Name as the title of the integration entry
            return self.async_create_entry(
                title=user_input["category_name"], 
                data=user_input
            )

        # Show two distinct fields
        data_schema = vol.Schema({
            vol.Required("category_name"): str,
            vol.Required("json_url"): str,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )

    async def async_step_reconfigure(self, user_input=None):
        """Handle reconfiguration of an existing entry."""
        # Get the existing entry we are editing
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        
        if user_input is not None:
            # Update the entry with new data and reload the integration
            return self.async_update_reload_and_abort(entry, data=user_input)

        # Pre-fill the form with existing values
        data_schema = vol.Schema({
            vol.Required("category_name", default=entry.data.get("category_name")): str,
            vol.Required("json_url", default=entry.data.get("json_url")): str,
        })

        return self.async_show_form(step_id="reconfigure", data_schema=data_schema)