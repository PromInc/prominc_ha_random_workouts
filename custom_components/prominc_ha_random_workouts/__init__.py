import logging
import random

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import entity_registry as er
from .const import DOMAIN, CONF_JSON_URLS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    _LOGGER.debug("Setting up PromInc Random Workouts entry %s", entry.entry_id)

    # Forward to sensor platform and wait for it
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def pick_random_workout(call: ServiceCall):
        # 1. Get the category requested by the user
        category_target = call.data.get("category", "").strip().lower()
        media_player = call.data.get("entity_id")

        # 2. SCAN ALL ENTRIES for the matching category
        target_url = None
        all_entries = hass.config_entries.async_entries(DOMAIN)

        for e in all_entries:
            # Check the 'category_name' in each config entry's data
            e_category = e.data.get("category_name", "").strip().lower()

            _LOGGER.debug("e_category: %s", e_category)

            if e_category == category_target:
                target_url = e.data.get("json_url")
                break

        if not target_url:
            _LOGGER.error("Category '%s' not found in any integration entry", category_target)
            return

        # 3. Fetch JSON
        session = async_get_clientsession(hass)
        try:
            _LOGGER.debug("Attempting to fetch workout list from: %s", target_url)

            async with session.get(target_url, timeout=10) as response:
                # Capture the raw text first for debugging
                raw_text = await response.text()
                _LOGGER.debug("Raw response from server: %s", raw_text)

                if response.status != 200:
                    _LOGGER.error(
                        "Failed to fetch JSON. Status: %s. Response (truncated): %s", 
                        response.status, 
                        raw_text[:100]
                    )
                    return

                # Attempt to parse the JSON
                try:
                    collection = await response.json(content_type=None)
                except Exception as json_err:
                    _LOGGER.error("JSON parsing failed. Raw text was: %s. Error: %s", raw_text, json_err)
                    return

                if not collection or not isinstance(collection, dict):
                    _LOGGER.error("JSON structure is invalid or empty: collection. Expected a dict {}.")
                    return

                workouts = collection.get("entities",{})
                if not workouts or not isinstance(workouts, list):
                    _LOGGER.error("JSON structure is invalid or empty: workouts. Expected a list [].")
                    return

                workout = random.choice(workouts)
                _LOGGER.info("Successfully picked workout: %s", workout.get("ytId"))

        except Exception as e:
            _LOGGER.error("Unexpected error in pick_random_workout: %s", str(e))

        workoutUrl = str( "https://www.youtube.com/watch?v=" ) + str( workout.get("ytId") )
        workout["url"] = workoutUrl

        hass.bus.async_fire(
            f"{DOMAIN}_update_{category_target}",
            {
                "title": "TODO",
                "video_id": workout.get("ytId"),
                "video_url": workoutUrl,
            },
        )

        if media_player:
            start_time = workout.get("startTime", 0)

            registry = er.async_get(hass)
            entity_entry = registry.async_get(media_player)
            platform = entity_entry.platform if entity_entry else "unknown"

            if platform == "roku":
                # Strategy: Deep-link to Roku YouTube App
                service_data = {
                    "entity_id": media_player,
                    "media_content_id": "837",
                    "media_content_type": "app",
                    "extra": {
                      "content_id": workout.get("ytId"),
                      "media_type": "live",
                      "t": str(start_time)
                    }
                }

            elif platform in ["google_cast", "cast"]:
                # Strategy: Launch native YouTube App on Chromecast
                # We pass a JSON-formatted string as the ID
                cast_data = json.dumps({
                    "app_name": "youtube",
                    "media_id": workout.get("ytId"),
                    "startTime": start_time
                })
                service_data = {
                    "entity_id": media_player,
                    "media_content_id": cast_data,
                    "media_content_type": "cast"
                }

            else:
                # Strategy: Generic URL (Best for Browser Mod or VLC)
                timestamped_url = f"{video_url}&t={start_time}s"
                service_data = {
                    "entity_id": media_player,
                    "media_content_id": timestamped_url,
                    "media_content_type": "url"
                }

            await hass.services.async_call("media_player", "play_media", service_data)

            # TODO: test this
            # TODO: add as a configuration option of some sort?
            await hass.services.async_call("media_player", "media_pause", {
                "entity_id": media_player
            })

    # Only register the service if it hasn't been registered yet
    if not hass.services.has_service(DOMAIN, "pick_random"):
        hass.services.async_register(DOMAIN, "pick_random", pick_random_workout)

    return True
