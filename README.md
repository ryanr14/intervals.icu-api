# Intervals.icu

A Python script to send training events from a JSON file to the [Intervals.icu](https://intervals.icu) API. This script automates the process of uploading training schedules for athletes.

## Features
- Uploads multiple training events in bulk to the Intervals.icu calendar.
- Supports cycling, swimming, and running workouts.
- Easy-to-configure JSON input file for flexible scheduling.

## Prerequisites
- Python 3.6 or higher
- An Intervals.icu account with API access
- Your **API Key** and **Athlete ID**

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/h3xh0und/intervals.icu.git
   cd intervals.icu
   ```
2. **Install Dependencies**
3. No additional libraries are required, but you can use pip to install requests if it's not already installed:
   ```bash
   pip install requests
   ````
4. **Configure the Script**
   - Open the upload_trainings.py file.
   - Replace the placeholders:
      your_api_key with your API key from Intervals.icu.
      your_athlete_id with your athlete ID.

6. **Prepare Your JSON File**

    Create a trainings.json file in the repository folder following this structure:

        {
            "trainings": [
                {
                    "date": "2025-01-14",
                    "name": "Bike - VO2 Max Intervals",
                    "steps": [
                        {"duration": 600, "power": 0.6},
                        {"duration": 180, "power": 1.2},
                        {"duration": 180, "power": 0.5}
                    ]
                }
            ]
        }

## Usage

1. **Run the Script**
   ```
   python3 upload_trainings.py
   ```
2. **Verify on Intervals.icu**
   - Log in to your Intervals.icu account.
   - Check the calendar for the uploaded events.

## Year Planning and Training Schedule
I used ChatGPT to generate a full year planning and monthly training schedules in JSON format. This ensures a structured approach to achieving cycling, swimming, and running goals, aligned with specific events throughout the year.

## Support Intervals.icu
Make sure to subscribe to Intervals.icu to support the hard work David Tinker puts into maintaining this incredible tool for athletes!

## Contributing
Feel free to contribute to the project by submitting issues or pull requests. Contributions are welcome!

## License
This project is licensed under the MIT License.
