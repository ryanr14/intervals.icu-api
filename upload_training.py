import os
import requests
import json
import base64

# Configuration
ATHLETE_ID = os.environ.get("ATHLETE_ID")
API_KEY = os.environ.get("API_KEY")
if not ATHLETE_ID or not API_KEY:
    raise ValueError("Missing required environment variables: ATHLETE_ID and/or API_KEY.")

BASE_URL = "https://intervals.icu/api/v1/athlete"
ZONE_TYPE = "HR"  # "Pace"

# Encode API key
def encode_auth(api_key):
    return base64.b64encode(api_key.encode("utf-8")).decode("utf-8")

HEADERS = {
    "Authorization": f"Basic {encode_auth(API_KEY)}",
    "Content-Type": "application/json"
}

def load_trainings(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        raise RuntimeError(f"Error loading training file: {e}")

def format_training_data(trainings):
    formatted_data = []
    for training in trainings.get("trainings", []):
        description_lines = []
        for step in training.get("steps", []):
            description_lines.append(f"{step['description']}")
            description_lines.append(f"- {step['duration']} in {step['zone']} {ZONE_TYPE}")
        formatted_data.append({
            "start_date_local": training["date"] + "T00:00:00",
            "category": "WORKOUT",
            "name": training["name"],
            "description": "\n".join(description_lines).strip(),
            "type": "Ride" if "Bike" in training["name"] else "Run" if "Run" in training["name"] else "Swim",
            "moving_time": sum(
                int(step["duration"].replace("km", "").replace("m", "").replace("s", "")) * (60 if "m" in step["duration"] else 1)
                for step in training["steps"]
            ),
            "steps": [
                {
                    "description": step.get("description", ""),
                    "duration": step["duration"],
                    "target_type": "zone",
                    "target_value": step["zone"],
                    "cadence": step.get("cadence", "Free")
                }
                for step in training["steps"]
            ]
        })
    return formatted_data

def upload_trainings(data):
    url = f"{BASE_URL}/{ATHLETE_ID}/events/bulk"
    response = requests.post(url, headers=HEADERS, json=data)
    if 200 <= response.status_code < 300:
        print("Trainings uploaded successfully.")
    else:
        print(f"Failed to upload trainings. Status code: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    try:
        trainings = load_trainings("training.json")
        formatted_data = format_training_data(trainings)
        upload_trainings(formatted_data)
    except Exception as e:
        print(f"Error: {e}")
