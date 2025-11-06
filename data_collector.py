import requests
import time
import psycopg2
from psycopg2 import sql
from datetime import datetime

# ------------------------------
# CONFIGURATION
# ------------------------------

DATABASE_URL = "postgresql://iss_data_db_user:65jTTdz567sktVDigL9WKyC9post1yrx@dpg-d468qjc9c44c73ci20b0-a:5432/iss_data_db"
FETCH_INTERVAL = 60  # seconds between requests

# ------------------------------
# DATABASE SETUP
# ------------------------------

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print(f"{datetime.now()} - Connected to Postgres database.", flush=True)
except Exception as e:
    print(f"{datetime.now()} - Failed to connect to database: {e}", flush=True)
    raise

# Create table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS iss_data (
        id SERIAL PRIMARY KEY,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        altitude DOUBLE PRECISION,
        timestamp BIGINT,
        collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# ------------------------------
# DATA COLLECTION LOOP
# ------------------------------

print(f"{datetime.now()} - Starting ISS data acquisition...", flush=True)

while True:
    try:
        # Fetch ISS telemetry
        response = requests.get("https://api.wheretheiss.at/v1/satellites/25544", timeout=10)
        response.raise_for_status()
        data = response.json()

        row = (
            data['latitude'],
            data['longitude'],
            data['altitude'],
            data['timestamp']
        )

        # Insert into Postgres
        cur.execute(
            sql.SQL("INSERT INTO iss_data (latitude, longitude, altitude, timestamp) VALUES (%s, %s, %s, %s)"),
            row
        )
        conn.commit()

        # ------------------------------
        # LOGGING
        # ------------------------------
        # Force immediate print to Render logs
        print(f"{datetime.now()} - Saved row: {row}", flush=True)

        # Optional: write to ephemeral log file (lost on redeploy)
        with open("worker_log.txt", "a") as f:
            f.write(f"{datetime.now()} - Saved row: {row}\n")

    except requests.exceptions.RequestException as e:
        print(f"{datetime.now()} - Request error: {e}", flush=True)

    except Exception as e:
        print(f"{datetime.now()} - Other error: {e}", flush=True)

    # Wait before fetching again
    time.sleep(FETCH_INTERVAL)
