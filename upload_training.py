import requests
import json
import base64
from datetime import datetime
import sys
import os

# Configuration
ATHLETE_ID = os.environ.get("ATHLETE_ID")  # Get from environment variable
API_KEY = os.environ.get("API_KEY")        # Get from environment variable
BASE_URL = "https://intervals.icu/api/v1/athlete"
ZONE_TYPE = "HR" #"Pace"

# Check for required environment variables
if not ATHLETE_ID or not API_KEY:
    print("Error: ATHLETE_ID and API_KEY environment variables are required")
    sys.exit(1)

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
    for training in trainings["trainings"]:
        # Generate a formatted description with proper labels and HR for running/swimming
        description_lines = []
        for step in training["steps"]:
            if "Run" in training["name"] or "Swim" in training["name"]:
                description_lines.append(f"{step['description']}")
                description_lines.append(f"- {step['duration']} in {step['zone']} {zone_type}")
            else:
                description_lines.append(f"{step['description']}")
                description_lines.append(f"- {step['duration']} in {step['zone']} {zone_type}")

            description_lines.append("")  # Add blank line after each step for readability

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

# Upload training data
def upload_trainings(data):
    url = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/events/bulk"
    response = requests.post(url, headers={
        "Authorization": f"Basic {encode_auth(API_KEY)}",
        "Content-Type": "application/json"
    }, json=data)
    if response.status_code == 200:
        print("Trainings uploaded successfully.")
    else:
        print(f"Failed to upload trainings. Status code: {response.status_code}")
        print("Response text:", response.text)

# Main function
def main():
    try:
        # Get file path from command line argument, default to "training.json"
        file_path = sys.argv[1] if len(sys.argv) > 1 else "training.json"
        trainings = load_trainings(file_path)
        formatted_data = format_training_data(trainings)
        upload_trainings(formatted_data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
