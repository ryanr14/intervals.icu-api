import os
import requests
import json
import base64
from datetime import datetime

# Configuration
ATHLETE_ID = os.environ.get("ATHLETE_ID")  # Get from GitHub Secrets
API_KEY = os.environ.get("API_KEY")        # Get from GitHub Secrets

# Check if the required environment variables are set
if not ATHLETE_ID or not API_KEY:
    raise ValueError("Missing required environment variables: ATHLETE_ID and/or API_KEY.")

BASE_URL = "https://intervals.icu/api/v1/athlete"
ZONE_TYPE = "HR"  # "Pace"

# Encode "API_KEY:api_key" in Base64 for the Authorization header
def encode_auth(api_key):
    token = f"API_KEY:{api_key}".encode("utf-8")
    return base64.b64encode(token).decode("utf-8")

HEADERS = {
    "Authorization": f"Basic {encode_auth(API_KEY)}",
    "Content-Type": "application/json"
}

# Load training data
def load_trainings(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

# Format training data for API
def format_training_data(trainings):
    formatted_data = []
    for training in trainings.get("trainings", []):  # Use .get() to avoid KeyError
        description_lines = []
        steps = training.get("steps", [])  # Default to an empty list if 'steps' is missing
        for step in steps:
            if "Run" in training["name"] or "Swim" in training["name"]:
                description_lines.append(f"{step['description']}")
                description_lines.append(f"- {step['duration']} in {step['zone']} {ZONE_TYPE}")
            else:
                description_lines.append(f"{step['description']}")
                description_lines.append(f"- {step['duration']} in {step['zone']} {ZONE_TYPE}")

            description_lines.append("")  # Add blank line after each step for readability

        formatted_data.append({
            "start_date_local": training["date"] + "T00:00:00",
            "category": "WORKOUT",
            "name": training["name"],
            "description": "\n".join(description_lines).strip(),
            "type": "Ride" if "Bike" in training["name"] else "Run" if "Run" in training["name"] else "Swim",
            "moving_time": sum(
                int(step["duration"].replace("km", "").replace("m", "").replace("s", "")) * (60 if "m" in step["duration"] else 1)
                for step in steps  # Use the steps variable
            ),
            "steps": [
                {
                    "description": step.get("description", ""),
                    "duration": step["duration"],
                    "target_type": "zone",
                    "target_value": step["zone"],
                    "cadence": step.get("cadence", "Free")
                }
                for step in steps  # Use the steps variable
            ]
        })
    return formatted_data

# Upload training data
def upload_trainings(data):
    url = f"{BASE_URL}/{ATHLETE_ID}/events/bulk"
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 200:
        print("Trainings uploaded successfully.")
    else:
        print(f"Failed to upload trainings. Status code: {response.status_code}")
        print(response.text)

# Main function
def main():
    try:
        trainings = load_trainings("training.json")
        formatted_data = format_training_data(trainings)
        upload_trainings(formatted_data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()