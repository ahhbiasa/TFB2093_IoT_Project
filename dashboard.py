import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk

# --- Ensure DB and table exist ---
def ensure_db():
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

# --- Load data safely ---
def load_data():
    conn = sqlite3.connect("iss_data.db")
    df = pd.read_sql_query("SELECT * FROM iss_data", conn)
    conn.close()
    return df

# --- Helper to create a path suitable for PathLayer ---
def make_path_dataframe(df):
    # PathLayer expects each row to have a list of [lon, lat] points under some column (e.g., 'path')
    path = df[['longitude', 'latitude']].values.tolist()
    path_df = pd.DataFrame({'path': [path]}) if len(path) > 0 else pd.DataFrame({'path': []})
    return path_df

# --- Main Streamlit App ---
st.set_page_config(page_title="ISS Tracker", page_icon="🛰️", layout="wide")
st.title("🛰️ International Space Station Tracker")

# Ensure DB/table exists
ensure_db()

try:
    df = load_data()

    if df.empty:
        st.warning("⚠️ No data collected yet! Run data_collector.py to fetch ISS data first.")
        st.info("Run `python data_collector.py` in another terminal and wait for a few saved lines, then reload this app.")
    else:
        # Convert timestamp to readable time (optional)
        try:
            df['timestamp_readable'] = pd.to_datetime(df['timestamp'], unit='s')
        except Exception:
            df['timestamp_readable'] = df['timestamp']

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Max Longitude", f"{df['longitude'].max():.2f}")
        col2.metric("Min Longitude", f"{df['longitude'].min():.2f}")
        col3.metric("Altitude Change (km)", f"{df['altitude'].max() - df['altitude'].min():.2f}")

        # Map Visualization
        st.subheader("🌍 ISS Path Map (latest position shown)")
        # Latest position for initial center
        last_lat = float(df['latitude'].iloc[-1])
        last_lon = float(df['longitude'].iloc[-1])

        # Scatter for points; PathLayer for the connecting path
        path_df = make_path_dataframe(df)

        deck = pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=last_lat,
                longitude=last_lon,
                zoom=2,
                pitch=0,
            ),
            layers=[
                # scatter of recorded points
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df,
                    get_position='[longitude, latitude]',
                    get_radius=400000,
                    get_fill_color='[255, 0, 0, 160]',
                    pickable=True
                ),
                # single Path connecting all points (one row in path_df)
                pdk.Layer(
                    "PathLayer",
                    data=path_df,
                    get_path='path',
                    get_width=5,
                )
            ],
        )

        st.pydeck_chart(deck)

        # Altitude trend chart
        st.subheader("📈 Altitude Over Time")
        # Use readable timestamp if converted; else original
        if 'timestamp_readable' in df.columns:
            chart_df = df.set_index('timestamp_readable')['altitude']
        else:
            chart_df = df.set_index('timestamp')['altitude']
        st.line_chart(chart_df)

except Exception as e:
    st.error(f"❌ Unexpected error: {e}")
    st.info("Make sure `iss_data.db` is in the same folder and that `iss_data` table exists (run data_collector.py).")