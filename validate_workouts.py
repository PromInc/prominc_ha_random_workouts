import json
import sys
import re

def validate_workout_file(filepath):
    print(f"--- Validating: {filepath} ---")
    
    # Regex for standard 11-character YouTube ID
    yt_id_pattern = re.compile(r'^[a-zA-Z0-9_-]{11}$')

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("❌ ERROR: JSON must be a LIST [].")
            return

        success_count = 0
        for index, item in enumerate(data):
            title = item.get("title", "Unknown Title")
            url = item.get("url", "")
            
            # 1. Check for required keys
            if not url:
                print(f"❌ ERROR at index {index}: Missing 'url'.")
                continue
            
            # 2. Extract and Validate YouTube ID
            video_id = ""
            if "v=" in url:
                video_id = url.split("v=")[-1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("/")[-1]

            if not video_id:
                print(f"⚠️ WARNING: Could not extract ID from '{title}'.")
            elif not yt_id_pattern.match(video_id):
                print(f"❌ ERROR: Invalid YouTube ID '{video_id}' in '{title}'. (Must be 11 chars)")
                continue
            
            print(f"✅ OK: {title} (ID: {video_id})")
            success_count += 1

        print(f"\nSummary: {success_count}/{len(data)} workouts validated successfully.")

    except json.JSONDecodeError as e:
        print(f"❌ CRITICAL: Invalid JSON syntax! Error: {e}")
    except FileNotFoundError:
        print("❌ ERROR: File not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_workouts.py your_file.json")
    else:
        validate_workout_file(sys.argv[1])