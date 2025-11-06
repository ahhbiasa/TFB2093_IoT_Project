import requests
import time
import psycopg2
from psycopg2 import sql
from datetime import datetime

# ------------------------------
# CONFIGURATION
# ------------------------------

# Replace this with your actual DATABASE_URL from Render
DATABASE_URL = "postgresql://iss_data_db_user:65jTTdz567sktVDigL9WKyC9post1yrx@dpg-d468qjc9c44c73ci20b0-a:5432/iss_data_db"

FETCH_INTERVAL = 60  # seconds between requests

# ------------------------------
# DATABASE SETUP
# ------------------------------

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print(f"{datetime.now()} - Connected to Postgres database.")
except Exception as e:
    print(f"{datetime.now()} - Failed to connect to database: {e}")
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

print(f"{datetime.now()} - Starting ISS data acquisition...")

while True:
    try:
        # Fetch ISS telemetry
        response = requests.get("https://api.wheretheiss.at/v1/satellites/25544", timeout=10)
        response.raise_for_status()  # Raise exception if request fails
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

        print(f"{datetime.now()} - Saved row: {row}")

    except requests.exceptions.RequestException as e:
        print(f"{datetime.now()} - Request error: {e}")

    except Exception as e:
        print(f"{datetime.now()} - Other error: {e}")

    # Wait before fetching again
    time.sleep(FETCH_INTERVAL)
