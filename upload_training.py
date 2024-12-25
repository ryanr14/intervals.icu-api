import requests
import json
import base64
from datetime import datetime

# Configuration
ATHLETE_ID = "ID"  # Replace with your athlete ID
API_KEY = "API_KEY"        # Replace with your API key
BASE_URL = "https://intervals.icu/api/v1/athlete"

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
        formatted_data.append({
            "start_date_local": training["date"] + "T00:00:00",  # Ensure proper date format
            "category": "WORKOUT",
            "name": training["name"],
            "description": "\n".join(
                [f"- {step['duration']} sec at {step['power']*100}% FTP" for step in training["steps"]]
            ),
            "type": "Ride" if "Bike" in training["name"] else "Run" if "Run" in training["name"] else "Swim",
            "moving_time": sum(step["duration"] for step in training["steps"]),
            "steps": training["steps"]  # Directly include the steps from the JSON
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
        trainings = load_trainings("trainings.json")
        formatted_data = format_training_data(trainings)
        upload_trainings(formatted_data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
