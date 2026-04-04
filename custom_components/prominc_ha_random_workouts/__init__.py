import logging
import random

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, CONF_JSON_URLS

_LOGGER = logging.getLogger(__name__)

# TODO: clean up debug loggingimport logging
import random

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_JSON_URLS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    _LOGGER.debug("Setting up PromInc Random Workouts entry %s", entry.entry_id)

    # Forward to sensor platform and wait for it
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def pick_random_workout(call: ServiceCall):
        category_target = call.data.get("category", "").strip().lower()
        media_player = call.data.get("entity_id")

        category = entry.data.get("category_name","").strip()
        url = entry.data.get("json_url","").strip()

        # TODO: delete me
        _LOGGER.debug("category: %s", category)
        _LOGGER.debug("url: %s", url)
        _LOGGER.debug("category_target: %s", category_target)

        url_map = {}

        url_map[category] = url


        _LOGGER.debug("url_map: %s", url_map)

        target_url = url_map.get(category_target)

        _LOGGER.debug("target_url: %s", target_url)

        if not target_url:
            _LOGGER.error("Category %s not found in config", category_target)
            return

        # session = async_get_clientsession(hass)
        # async with session.get(target_url) as response:
            # workouts = await response.json()
        # workout = random.choice(workouts)

        session = async_get_clientsession(hass)
        try:
            _LOGGER.error("Attempting to fetch workout list from: %s", target_url)
            
            async with session.get(target_url, timeout=10) as response:
                # Capture the raw text first for debugging
                raw_text = await response.text()
                _LOGGER.error("Raw response from server: %s", raw_text)

                if response.status != 200:
                    _LOGGER.error(
                        "Failed to fetch JSON. Status: %s. Response: %s", 
                        response.status, 
                        raw_text[:100] # Log only the first 100 chars to avoid bloat
                    )
                    return

                # Attempt to parse the JSON
                try:
                    collection = await response.json(content_type=None)
                except Exception as json_err:
                    _LOGGER.error("JSON parsing failed. Raw text was: %s. Error: %s", raw_text, json_err)
                    return
                
                _LOGGER.error("collection type: %s", type(collection))

                if not collection or not isinstance(collection, dict):
                    _LOGGER.error("JSON structure is invalid or empty: collection. Expected a dict {}.")
                    return

                workouts = collection.get("entities",{})

                if not workouts or not isinstance(workouts, list):
                    _LOGGER.error("JSON structure is invalid or empty: workouts. Expected a list [].")
                    return

                workout = random.choice(workouts)
                _LOGGER.error("Successfully picked workout: %s", workout.get("ytId"))

                # ... (rest of the event firing and media player logic)
        
        except Exception as e:
            _LOGGER.error("Unexpected error in pick_random_workout: %s", str(e))


        workoutUrl = str( "https://www.youtube.com/watch?v=" ) + str( workout.get("ytId") )

        _LOGGER.error("workoutUrl: %s", workoutUrl)
        
        # TODO: support startTime on URL
        
        workout["url"] = workoutUrl


        hass.bus.async_fire(
            f"{DOMAIN}_update_{category_target}",
            {
                # "title": workout.get("title"),
                "title": "TODO",
                # "video_url": workout.get("url"),
                # "video_id": workout.get("url").split("v=")[-1]
                # if "v=" in workout.get("url")
                # else "",
                "video_id": workout.get("ytId"),
                # "video_url": str( "https://www.youtube.com/watch?v=" ) + str( workout.get("ytId") ),
                "video_url": workoutUrl,
            },
        )

        # TODO: revist this.  Can we detect what type of media  player is being used and use the appropriate logic call?
        # if media_player:
            # await hass.services.async_call(
                # "media_player",
                # "play_media",
                # {
                    # "entity_id": media_player,
                    # "media_content_id": workout.get("url"),
                    # "media_content_type": "url",
                # },
            # )


        # Automation path: Play on Roku YouTube App
        # if media_player:
            # # Roku expects: media_content_id: "837,VIDEO_ID"
            # # and media_content_type: "app"
            # await hass.services.async_call(
              # "media_player",
              # "play_media",
              # {
                # "entity_id": media_player,
                # # "media_content_id": f"837,{video_id}",
                # "media_content_id": f"837,{workout.get("ytId")}",
                # "media_content_type": "app"
              # }
            # )

        # Automation path: Play on Roku YouTube App (ID: 837)
        # if media_player:
            # await hass.services.async_call("media_player", "play_media", {
                # "entity_id": media_player,
                # "media_content_id": "837",      # Launch the YouTube App
                # "media_content_type": "app",
                # "extra": {
                    # "content_id": workout.get("ytId"),    # Deep-link to the specific video
                    # "media_type": "live"       # This tells YouTube to start playback
                # }
            # })









        if media_player:
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
                      "media_type": "live"
                    }
                }

            elif platform in ["google_cast", "cast"]:
                # Strategy: Launch native YouTube App on Chromecast
                # We pass a JSON-formatted string as the ID
                cast_data = json.dumps({
                    "app_name": "youtube",
                    "media_id": workout.get("ytId")
                })
                service_data = {
                    "entity_id": media_player,
                    "media_content_id": cast_data,
                    "media_content_type": "cast"
                }

            else:
                # Strategy: Generic URL (Best for Browser Mod or VLC)
                service_data = {
                    "entity_id": media_player,
                    "media_content_id": workoutUrl,
                    "media_content_type": "url"
                }


            await hass.services.async_call("media_player", "play_media", service_data)
            
            # TODO: test this
            # TODO: add as a configuration option of some sort?
            await hass.services.async_call("media_player", "media_pause", {
                "entity_id": media_player
            })















    hass.services.async_register(DOMAIN, "pick_random", pick_random_workout)

    # IMPORTANT: must return a bool
    return True
