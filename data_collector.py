import requests
import time
import csv
import os
from datetime import datetime

# Create a folder to store CSVs
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# CSV file name includes timestamp to make it unique
CSV_FILE = os.path.join(DATA_FOLDER, f"iss_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

# Create CSV and write headers
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["latitude", "longitude", "altitude", "timestamp"])

print(f"Starting ISS data acquisition, saving to {CSV_FILE}...")

while True:
    try:
        response = requests.get("https://api.wheretheiss.at/v1/satellites/25544", timeout=10)
        response.raise_for_status()
        data = response.json()
        row = [data['latitude'], data['longitude'], data['altitude'], data['timestamp']]

        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        print(f"{datetime.now()} - Saved row: {row}", flush=True)

    except requests.exceptions.RequestException as e:
        print(f"{datetime.now()} - Request error: {e}")
    except Exception as e:
        print(f"{datetime.now()} - Other error: {e}")

    time.sleep(60)

