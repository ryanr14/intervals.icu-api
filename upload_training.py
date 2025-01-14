import os
import requests
import json
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuration
ATHLETE_ID = os.getenv("ATHLETE_ID")
API_KEY = os.getenv("API_KEY")
if not ATHLETE_ID or not API_KEY:
    raise ValueError("Missing required environment variables: ATHLETE_ID and/or API_KEY.")

BASE_URL = "https://intervals.icu/api/v1/athlete"
ZONE_TYPE = "HR"  # Can be "HR" or "Pace"

def encode_auth(api_key):
    """
    Encode API key in Base64 for Authorization header.
    """
    return base64.b64encode(api_key.encode("utf-8")).decode("utf-8")

HEADERS = {
    "Authorization": f"Basic {encode_auth(API_KEY)}",
    "Content-Type": "application/json"
}

def load_trainings(file_path):
    """
    Load training data from a JSON file.
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Training file '{file_path}' not found.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from file '{file_path}': {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error loading training file '{file_path}': {e}")
        raise

def parse_duration(duration):
    """
    Parse duration from strings like 'km', 'm', or 's' and convert to seconds.
    """
    try:
        if "km" in duration or "m" in duration:
            return int(duration.replace("km", "").replace("m", "").strip()) * 60
        elif "s" in duration:
            return int(duration.replace("s", "").strip())
        else:
            logging.warning(f"Unrecognized duration format: '{duration}'. Defaulting to 0.")
            return 0
    except ValueError:
        logging.error(f"Failed to parse duration: '{duration}'.")
        return 0

def format_training_data(trainings):
    """
    Format raw training data into the required API format.
    """
    formatted_data = []
    for training in trainings.get("trainings", []):
        description_lines = [
            f"{step['description']}\n- {step['duration']} in {step['zone']} {ZONE_TYPE}"
            for step in training.get("steps", [])
        ]
        formatted_data.append({
            "start_date_local": f"{training['date']}T00:00:00",
            "category": "WORKOUT",
            "name": training["name"],
            "description": "\n".join(description_lines).strip(),
            "type": "Ride" if "Bike" in training["name"] else "Run" if "Run" in training["name"] else "Swim",
            "moving_time": sum(parse_duration(step["duration"]) for step in training.get("steps", [])),
            "steps": [
                {
                    "description": step.get("description", ""),
                    "duration": step["duration"],
                    "target_type": "zone",
                    "target_value": step["zone"],
                    "cadence": step.get("cadence", "Free")
                }
                for step in training.get("steps", [])
            ]
        })
    return formatted_data

def upload_trainings(data):
    """
    Upload formatted training data to the API.
    """
    url = f"{BASE_URL}/{ATHLETE_ID}/events/bulk"
    try:
        logging.info(f"Uploading to URL: {url}")
        logging.info(f"Request Headers: {HEADERS}")
        response = requests.post(url, headers=HEADERS, json=data)
        if 200 <= response.status_code < 300:
            logging.info("Trainings uploaded successfully.")
        else:
            logging.error(f"Failed to upload trainings. Status code: {response.status_code}\n{response.text}")
    except requests.RequestException as e:
        logging.error(f"Error during API request: {e}")
        raise

def main():
    """
    Main function to load, format, and upload training data.
    """
    file_path = "training.json"  # You can make this configurable via CLI args or env vars
    try:
        logging.info("Loading training data...")
        trainings = load_trainings(file_path)
        logging.info("Formatting training data...")
        formatted_data = format_training_data(trainings)
        logging.info("Uploading training data...")
        upload_trainings(formatted_data)
        logging.info("Process completed successfully.")
    except Exception as e:
        logging.error(f"Process failed: {e}")

if __name__ == "__main__":
    main()
