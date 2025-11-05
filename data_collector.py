import requests
import sqlite3
import time

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("iss_data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS iss_data (
            latitude REAL,
            longitude REAL,
            altitude REAL,
            timestamp INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Fetch ISS data from the API
def fetch_iss_data():
    url = "https://api.wheretheiss.at/v1/satellites/25544"
    response = requests.get(url)
    data = response.json()
    return (data['latitude'], data['longitude'], data['altitude'], data['timestamp'])

# Save the data to the database
def save_data(data):
    conn = sqlite3.connect("iss_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO iss_data VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

# Run continuously (every minute)
if __name__ == "__main__":
    init_db()
    while True:
        iss_data = fetch_iss_data()
        save_data(iss_data)
        print("Saved:", iss_data)
        time.sleep(60)  # wait 1 minute before next fetch
