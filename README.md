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
3. Enter your lists in the following format:
   - `CategoryName|https://yourdomain.com/list.json`

## Usage

### 1. Automation Path (Smart TV)
To automatically play a workout on your TV (e.g., at 7:00 AM), use the following service call in your automation:

```yaml
service: prominc_ha_random_workouts.pick_random
data:
  entity_id: media_player.living_room_tv
```

#### V2
```yaml
action: prominc_ha_random_workouts.pick_random
metadata: {}
data:
  entity_id: media_player.family_room_50_tcl_roku_tv
  category: yoga
```

### 2. Dashboard Path

TODO: fill me out


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

### 1.0.0
- Initial release
