import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from datetime import datetime
import numpy as np

# Configure the page
st.set_page_config(
    page_title="ISS Tracker Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv('iss_data_3days_sampled.csv')
    df['collected_at'] = pd.to_datetime(df['collected_at'])
    df['date_only'] = pd.to_datetime(df['date_only'])
    df = df.sort_values('collected_at')
    return df

def create_iss_map(df, latest_position=None):
    """Create a Folium map with ISS path and current position"""
    # Center map on the mean coordinates
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=2,
        tiles='OpenStreetMap'
    )
    
    # Add ISS path as a line
    path_coords = [[row['latitude'], row['longitude']] for _, row in df.iterrows()]
    folium.PolyLine(
        path_coords,
        color='blue',
        weight=2,
        opacity=0.6,
        popup='ISS Path'
    ).add_to(m)
    
    # Add markers for significant points
    folium.Marker(
        [df.iloc[0]['latitude'], df.iloc[0]['longitude']],
        popup=f"Start: {df.iloc[0]['collected_at'].strftime('%Y-%m-%d %H:%M')}",
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)
    
    folium.Marker(
        [df.iloc[-1]['latitude'], df.iloc[-1]['longitude']],
        popup=f"End: {df.iloc[-1]['collected_at'].strftime('%Y-%m-%d %H:%M')}",
        icon=folium.Icon(color='red', icon='stop')
    ).add_to(m)
    
    # Add current position marker if provided
    if latest_position is not None and not latest_position.empty:
        folium.Marker(
            [latest_position['latitude'], latest_position['longitude']],
            popup=f"Current Position\nLat: {latest_position['latitude']:.4f}\nLon: {latest_position['longitude']:.4f}",
            icon=folium.Icon(color='orange', icon='star', prefix='fa')
        ).add_to(m)
    
    return m

def create_altitude_chart(df):
    """Create altitude over time chart"""
    fig = px.line(
        df, 
        x='collected_at', 
        y='altitude',
        title='ISS Altitude Over Time',
        labels={'collected_at': 'Time', 'altitude': 'Altitude (km)'}
    )
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Altitude (km)',
        hovermode='x unified'
    )
    return fig

def create_speed_analysis(df):
    """Calculate and visualize speed between points"""
    df_sorted = df.sort_values('collected_at').copy()
    df_sorted['time_diff'] = df_sorted['collected_at'].diff().dt.total_seconds()
    
    # Calculate approximate distance using Haversine formula
    def calculate_distance(lat1, lon1, lat2, lon2):
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        radius_earth = 6371  # Earth radius in km
        return radius_earth * c
    
    # Calculate distances
    distances = []
    for i in range(1, len(df_sorted)):
        dist = calculate_distance(
            df_sorted.iloc[i-1]['latitude'], df_sorted.iloc[i-1]['longitude'],
            df_sorted.iloc[i]['latitude'], df_sorted.iloc[i]['longitude']
        )
        distances.append(dist)
    
    # Add NaN for first row to match length
    distances.insert(0, np.nan)
    df_sorted['distance_km'] = distances
    
    # Calculate speed (km/s)
    df_sorted['speed_km_s'] = df_sorted['distance_km'] / df_sorted['time_diff']
    
    fig = px.line(
        df_sorted, 
        x='collected_at', 
        y='speed_km_s',
        title='ISS Speed Over Time (Approximate)',
        labels={'collected_at': 'Time', 'speed_km_s': 'Speed (km/s)'}
    )
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Speed (km/s)',
        hovermode='x unified'
    )
    return fig

def main():
    st.title("🛰️ International Space Station Tracker Dashboard")
    st.markdown("### Real-time ISS Position and Historical Data Visualization")
    
    # Load data
    try:
        df = load_data()
        st.sidebar.success(f"Data loaded: {len(df)} records")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Sidebar
    st.sidebar.title("Dashboard Controls")
    st.sidebar.markdown("### Filter Data")
    
    # Date filter
    min_date = df['date_only'].min().date()
    max_date = df['date_only'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter data based on date selection
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[
            (df['date_only'] >= pd.to_datetime(start_date)) & 
            (df['date_only'] <= pd.to_datetime(end_date))
        ]
    else:
        filtered_df = df
    
    # Get latest position - handle empty case
    if len(filtered_df) > 0:
        latest_position = filtered_df.iloc[-1]
    else:
        latest_position = None
        st.warning("No data available for selected date range.")
    
    # Main dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🌍 ISS Trajectory Map")
        if len(filtered_df) > 0:
            iss_map = create_iss_map(filtered_df, latest_position)
            folium_static(iss_map, width=700, height=500)
        else:
            st.warning("No data available for selected date range.")
    
    with col2:
        st.markdown("### 📊 Current Status")
        if latest_position is not None and not latest_position.empty:
            st.metric("Latest Timestamp", latest_position['collected_at'].strftime('%Y-%m-%d %H:%M:%S'))
            st.metric("Latitude", f"{latest_position['latitude']:.4f}°")
            st.metric("Longitude", f"{latest_position['longitude']:.4f}°")
            st.metric("Altitude", f"{latest_position['altitude']:.2f} km")
            
            st.markdown("### 📈 Quick Stats")
            st.write(f"Total data points: {len(filtered_df)}")
            st.write(f"Altitude range: {filtered_df['altitude'].min():.2f} - {filtered_df['altitude'].max():.2f} km")
        else:
            st.warning("No position data available.")
    
    # Charts section
    st.markdown("---")
    st.markdown("## 📊 Data Analysis")
    
    if len(filtered_df) > 0:
        # Row 1: Altitude and Speed charts
        col1, col2 = st.columns(2)
        
        with col1:
            alt_chart = create_altitude_chart(filtered_df)
            st.plotly_chart(alt_chart, use_container_width=True)
        
        with col2:
            try:
                speed_chart = create_speed_analysis(filtered_df)
                st.plotly_chart(speed_chart, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating speed chart: {e}")
        
        # Additional statistics
        st.markdown("### 🔍 Additional Insights")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_altitude = filtered_df['altitude'].mean()
            st.metric("Average Altitude", f"{avg_altitude:.2f} km")
        
        with col2:
            total_points = len(filtered_df)
            st.metric("Data Points", f"{total_points}")
        
        with col3:
            date_range_days = (filtered_df['collected_at'].max() - filtered_df['collected_at'].min()).days
            st.metric("Days Covered", f"{date_range_days + 1}")
        
        with col4:
            max_speed = filtered_df['altitude'].max()
            st.metric("Max Altitude", f"{max_speed:.2f} km")
    
    else:
        st.warning("No data available for visualization with current filters.")
    
    # Data table
    st.markdown("---")
    st.markdown("## 📋 Raw Data Preview")
    if len(filtered_df) > 0:
        st.dataframe(filtered_df.head(100), use_container_width=True)
        
        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name=f"iss_data_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data to display.")

if __name__ == "__main__":
    main()  