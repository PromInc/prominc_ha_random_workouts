// v13
class WorkoutCard extends HTMLElement {
  static getConfigElement() {
    return document.createElement("prominc-random-workout-card-editor");
  }

  static getStubConfig() {
    return { entity: "", thumbnail_mode: false };
  }

  setConfig(config) {
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._config || !hass) return;

    const entityId = this._config.entity;
    const stateObj = hass.states[entityId];

    if (!entityId || !stateObj) {
      this.innerHTML = `<ha-card style="padding: 16px;">Please select a sensor.</ha-card>`;
      return;
    }

    const videoId = stateObj.attributes.video_id;
    const startTime = stateObj.attributes.start_time || 0;
    const thumbMode = this._config.thumbnail_mode || false;

    // Check if the video, start time, or mode is different from what we are currently showing
    if (this._currentVideoId === videoId && 
        this._currentStartTime === startTime && 
        this._currentMode === thumbMode) {
      return;
    }

    // Save current state to check against next time
    this._currentVideoId = videoId;
    this._currentStartTime = startTime;
    this._currentMode = thumbMode;

    const title = stateObj.attributes.friendly_name || "Workout";
    const playerHtml = thumbMode 
      ? `<a href="https://www.youtube.com/watch?v=${videoId}&t=${startTime}s" target="_blank">
           <img src="https://img.youtube.com/vi/${videoId}/maxresdefault.jpg" style="width:100%; display:block; border-radius: 4px;">
         </a>`
      : `<iframe width="100%" height="250" 
            src="https://www.youtube.com/embed/${videoId}?start=${startTime}" 
            referrerpolicy="strict-origin-when-cross-origin"
            frameborder="0" allow="autoplay; encrypted-media" allowfullscreen>
         </iframe>`;

    this.innerHTML = `
      <ha-card header="${title}">
        <div class="card-content" style="padding: 0px;">
          ${playerHtml}
          <div style="padding: 16px; text-align: center;">
            <mwc-button raised id="roll-button">Pick Different Workout</mwc-button>
          </div>
        </div>
      </ha-card>`;

    this.querySelector("#roll-button").addEventListener("click", () => {
      const category = entityId.split('.')[1].replace('workout_', '');
      this._hass.callService("prominc_ha_random_workouts", "pick_random", { category });
    });
  }
}

class WorkoutCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized && this._config) {
      this._render();
    }
  }

  async _render() {
    if (!this._hass || !this._config) return;
    this._initialized = true;

    const loadComponents = [
      customElements.whenDefined("ha-select"),
      customElements.whenDefined("ha-switch")
    ];

    const entities = Object.keys(this._hass.states).filter(e => e.startsWith('sensor.workout_'));
    const selectedEntity = this._config.entity || "";

    this.innerHTML = `
      <div class="card-config" style="padding: 16px; display: flex; flex-direction: column; gap: 20px;">
        <ha-select
          label="Select Workout Entity"
          .value="${selectedEntity}"
          fixedMenuPosition
          naturalMenuWidth
          id="entity-select"
          style="width: 100%;"
        >
          ${entities.map(ent => `
            <ha-list-item value="${ent}">${ent}</ha-list-item>
          `).join('')}
        </ha-select>
        
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 0 8px;">
           <span style="font-size: 14px;">Thumbnail Mode (Mobile Friendly)</span>
           <ha-switch 
             id="thumb-switch"
             .checked="${this._config.thumbnail_mode}">
           </ha-switch>
        </div>
      </div>`;

    // Use standard event listeners instead of inline attributes to prevent bubbling issues
    const select = this.querySelector("#entity-select");
    select.addEventListener("closed", (e) => e.stopPropagation());
    select.addEventListener("change", (e) => {
      e.stopPropagation();
      this._updateConfig(e.target.value, 'entity');
    });

    this.querySelector("#thumb-switch").addEventListener("change", (e) => {
      this._updateConfig(e.target.checked, 'thumbnail_mode');
    });
  }

  _updateConfig(value, field) {
    const event = new CustomEvent("config-changed", {
      detail: { config: { ...this._config, [field]: value } },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }
}

customElements.define("prominc-random-workout-card", WorkoutCard);
customElements.define("prominc-random-workout-card-editor", WorkoutCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "prominc-random-workout-card",
  name: "PromInc Workout Card",
  description: "Random workout card with mobile-friendly option."
});