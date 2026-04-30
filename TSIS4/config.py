import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "snake_color": [0, 255, 0],
    "grid_overlay": True,
    "sound": True
}

def load_settings():
    # If file doesn't exist, create it with defaults
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE, "r") as f:
            user_settings = json.load(f)
        
        # FIX: Ensure all default keys exist in the loaded dictionary
        updated = False
        for key, value in DEFAULT_SETTINGS.items():
            if key not in user_settings:
                user_settings[key] = value
                updated = True
        
        if updated:
            save_settings(user_settings)
            
        return user_settings
    except (json.JSONDecodeError, Exception):
        # If the file is broken/corrupted, overwrite with defaults
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)