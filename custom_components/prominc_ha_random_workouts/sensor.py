from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from .const import DOMAIN, CONF_JSON_URLS


async def async_setup_entry(hass, entry, async_add_entities):
	raw_urls = entry.data.get(CONF_JSON_URLS, "")
	entities = []

	for line in raw_urls.split("\n"):
		if "|" in line:
			name, url = line.split("|", 1)
			entities.append(WorkoutCategorySensor(name.strip(), url.strip()))

	async_add_entities(entities)


class WorkoutCategorySensor(SensorEntity):
	def __init__(self, category, url):
		self._category = category
		self._attr_name = f"Workout {category}"
		self._attr_unique_id = f"{DOMAIN}_{category.lower()}"
		self._state = "Ready"
		self._attributes = {"source_url": url}
		self._event_name = f"{DOMAIN}_update_{category.lower()}"

	async def async_added_to_hass(self):
		self.hass.bus.async_listen(self._event_name, self._handle_update)

	@callback
	def _handle_update(self, event):
		self._state = event.data.get("title")
		self._attributes.update(
			{
				"video_url": event.data.get("video_url"),
				"video_id": event.data.get("video_id"),
			}
		)
		self.async_write_ha_state()

	@property
	def state(self):
		return self._state

	@property
	def extra_state_attributes(self):
		return self._attributes
