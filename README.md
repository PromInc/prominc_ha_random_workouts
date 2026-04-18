# PromInc Random Workouts 🏋️‍♂️

<!-- A custom Home Assistant integration that pulls workout collections from remote JSON files and selects a random routine for you. Designed for both hands-free automation and interactive dashboard use. -->

A Home Assistant integration that selects a random workout from your hosted JSON lists and plays them on your media players.

## Features
- **Custom Collections:**
   - Input multiple JSON URLs to pool different types of workouts.
   - Support for multiple categories (Yoga, Cardio, Weights, etc.).
- **Automation Ready:** Trigger a random workout via service call and cast it directly to a Smart TV.
- **Smart Dispatcher:** Automatically detects your hardware (Roku, Chromecast, etc.) and uses the native YouTube app for the best experience.
- **Dashboard Support:**
   - Track the current workout title and video via a dedicated sensor.
   - Dashboard-ready sensors for custom UI.

## Hardware Support
This integration is designed to be "plug and play" with the following devices:

### Roku / TCL Smart TVs
- Launches the native **YouTube App (ID: 837)**.
- Uses deep-linking to start the video immediately.
- **Requirement:** Ensure "Network Access" is set to "Default" or "Permissive" in your Roku Settings.

### Google Cast / Chromecasts
- Launches the native YouTube app using the `cast` protocol.

### Generic Media Players
- Falls back to raw URL streaming (ideal for Browser Mod or VLC).

## Installation

### Via HACS (Recommended)
1. Open **HACS** in Home Assistant.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Paste the URL of this GitHub repository.
4. Select **Integration** as the category and click **Add**.
5. Find "PromInc Random Workouts" and click **Download**.
6. Restart Home Assistant.

### Manual
1. Copy the `custom_components/prominc_ha_random_workouts` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration
1. Go to **Settings > Devices & Services**.
2. Click **Add Integration** and search for **PromInc Random Workouts**.
3. Click into **PromInc Random Workouts**.
4. Click the **Add device** button.
5. Enter a **category_name**.  This is the name that will be referenced in the automations.
6. Enter a **json_url** where the list of YouTube videos to play will come from.
7. Click the **Submit** button.

## Usage

### 1. Automation (Smart TV)
To automatically play a workout on your TV (e.g., at 7:00 AM), use the following service call in your automation:

Set the `entity_id` to that of your media player.
Set the `category` to the category defined in one of your entities.

```yaml
action: prominc_ha_random_workouts.pick_random
metadata: {}
data:
  entity_id: media_player.family_room_tv
  category: yoga
```

If editing in visual mode, the following is needed to be set in the **Action Data** section.

```yaml
entity_id: media_player.family_room_tv
category: core
```

### 2. Dashboard
1. Open the desired dashboard in editor mode
2. Click the **+** icon to add a card
3. Search for and select card **PromInc Workout Card**
4. Under the **Config** tab select the workout entity from the dropdown
5. *optional* Select **Thhumbnail mode** to load a clickable thumbnail of the video as opposed to an iframe.  Useful on mobile devices to open the YouTube app.
6. Click **Save**

## NOTES
1. For a Roku TV, it is recommended to enable "Fast TV Start" in the Roku settings. This keeps the network active even when the TV is "off" and often helps bypass the splash screens when a deep link is sent from Home Assistant.
2. TCL Roku TV check: `Settings > System > Advanced System Settings > Control by Mobile Devices > Network Access`
   Ensure this is set to "Default" or "Permissive". If it is set to "Disabled," the TV will reject all API calls from Home Assistant, resulting in that "Invalid Response" error.

### Validate JSON Files
Run this command in a terminal window to validate that the JSON files are formatted correctly.
```
python validate_workouts.py your-list-4.json.
```

## Changelog

### 1.0.3
- Feature: Add dashboard card

### 1.0.2
- Bug Fix: only the first entity would work
- Feature: start videos at specified `startTime` in the JSON
- Enhancement: ensure entity IDs are unique
- Logging and code cleanup

### 1.0.1
- Improve entity creation to accept 2 fields vs pipe delinated.
- Ability to edit an entity configuration

### 1.0.0
- Initial release


## Roadmap / TODOs

### Entites
1. [DONE 1.0.1] Ability to define the category and JSON path in different fields
2. [DONE 1.0.2] Category name is case sensitive.  This should be removed/avoided.

### Videos
1. [DONE 1.0.2] Start at a specific time

### Automation
1. When adding to an automation, need to be able to specify the category
2. Pause video upon load
3. Can we avoid playing ads in anyway? (is this an issue?)

### Dashboards
1. [DONE 1.0.3] Does this work?

### Validation Script
1. Match the format that I use in JSON - not the format that the script is currently formatting to

### Integration Image
Historically, you have to submit your image to a global repo that the image will be pulled from.
https://developers.home-assistant.io/blog/2020/05/08/logos-custom-integrations/

As of 2026.3 it can instead be added to the integration itself!  (I like this)
https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api/

### Documentation
Some exists, does it need improvement??
1. How to build/structure JSON files
2. Example on how to validate JSON

