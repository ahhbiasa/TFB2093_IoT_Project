import requests
import time
import csv
import os
from datetime import datetime

CSV_FILE = "iss_data.csv"

# If file doesn't exist, create and write headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["latitude", "longitude", "altitude", "timestamp"])

print("Starting ISS data acquisition...")

while True:
    try:
        response = requests.get("https://api.wheretheiss.at/v1/satellites/25544", timeout=10)
        response.raise_for_status()  # raise exception if status code not 200
        data = response.json()
        row = [data['latitude'], data['longitude'], data['altitude'], data['timestamp']]

        # Append row to CSV
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        print(f"{datetime.now()} - Saved row: {row}")

    except requests.exceptions.RequestException as e:
        print(f"{datetime.now()} - Request error: {e}")
    except Exception as e:
        print(f"{datetime.now()} - Other error: {e}")

    time.sleep(60)  # Wait 1 minute before next fetch
