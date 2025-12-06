import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Set page config
st.set_page_config(
    page_title="Earthquake Analytics System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "api_error" not in st.session_state:
    st.session_state.api_error = None

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def display_error(message: str):
    """Display error message"""
    st.error(f"❌ {message}")

def display_success(message: str):
    """Display success message"""
    st.success(f"✅ {message}")

# Header
st.title("Earthquake Analytics System")
st.markdown("---")

# Sidebar Navigation
st.sidebar.title("Navigation")
query_type = st.sidebar.radio(
    "Select Query Type",
    [
        "1. Earthquakes in Region",
        "2. Average Magnitude",
        "3. Nearby Earthquakes",
        "4. Most Active Regions",
        "5. High Magnitude Earthquakes",
        "6. Regions with Min Quakes",
        "7. Above Average Activity",
        "8. Multi-Criteria Search",
        "9. High Population Regions",
        "10. Region Risk Summary"
    ]
)
with st.sidebar.expander("Regions", expanded=True):
    st.write("1. California Margin\n"
    "2. Alaska/Aleutian Margin\n" 
    "3. NW Pacific Margin (Japan/Russia)\n" 
    "4. Chile Subduction Zone\n" 
    "5. Indonesia/Philippines/PNG Arc\n" 
    "6. New Zealand and SW Pacific\n" 
    "7. Mediterranean Zone\n"
    "8. Himalaya/Central Asia Belt\n" 
    "9. Caribbean Arc (Puerto Rico / USVI)\n" 
    "10. Other" )
st.sidebar.markdown("---")
api_status = "🟢 Online" if check_api_health() else "🔴 Offline"
st.sidebar.write(f"**API Status:** {api_status}")

# Main content area
if not check_api_health():
    display_error("API is not responding. Please ensure the backend is running on http://127.0.0.1:8000")
    st.stop()

# Query 1: Earthquakes in Region
if query_type == "1. Earthquakes in Region":
    st.header("Earthquakes in Region")
    col1, col2 = st.columns(2)
    
    with col1:
        region_id = st.number_input("Enter Region ID", min_value=1, step=1)
    
    if st.button("Fetch Earthquakes", key="q1"):
        try:
            response = requests.get(f"{API_BASE_URL}/regions/{region_id}/earthquakes")
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    display_success(f"Found {len(data)} earthquakes in region {region_id}")
                else:
                    st.info("No earthquakes found for this region")
            else:
                display_error(response.json().get("detail", "Failed to fetch data"))
        except Exception as e:
            display_error(str(e))

# Query 2: Average Magnitude in Region
elif query_type == "2. Average Magnitude":

    st.header("Average Magnitude in Region")
    col1, col2 = st.columns(2)
    
    with col1:
        region_id = st.number_input("Enter Region ID", min_value=1, step=1, key="q2_region")
    
    if st.button("Calculate Average", key="q2"):
        try:
            response = requests.get(f"{API_BASE_URL}/regions/{region_id}/stats/avg-magnitude")
            if response.status_code == 200:
                data = response.json()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average Magnitude", f"{data.get('avg_magnitude', 'N/A'):.2f}" if isinstance(data.get('avg_magnitude'), (int, float)) else "N/A")
                display_success(f"Statistics calculated for region {region_id}")
            else:
                display_error(response.json().get("detail", "Failed to fetch data"))
        except Exception as e:
            display_error(str(e))

# Query 3: Nearby Earthquakes
elif query_type == "3. Nearby Earthquakes":
    st.header("Earthquakes Near a Location")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, key="q3_lat")
    with col2:
        longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, key="q3_lon")
    with col3:
        radius = st.number_input("Radius (km)", min_value=0.0, value=100.0, key="q3_radius")
    
    if st.button("Search Nearby", key="q3"):
        try:
            response = requests.get(
                f"{API_BASE_URL}/analytics/nearby",
                params={"lat": latitude, "lon": longitude, "radius_km": radius}
            )
            if response.status_code == 200:
                data = response.json()
                st.metric("Earthquakes Found", data.get("quake_count", 0))
                display_success("Search completed")
            else:
                display_error("Failed to fetch data")
        except Exception as e:
            display_error(str(e))

# Query 4: Most Active Regions
elif query_type == "4. Most Active Regions":
    st.header("Most Seismically Active Regions")
    col1, col2 = st.columns(2)
    
    with col1:
        top_n = st.slider("Number of regions to show", min_value=1, max_value=50, value=5, key="q4_top")
    
    if st.button("Get Active Regions", key="q4"):
        try:
            response = requests.get(f"{API_BASE_URL}/analytics/regions/most-active", params={"top_n": top_n})
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    display_success(f"Retrieved top {top_n} active regions")
                else:
                    st.info("No data available")
            else:
                display_error("Failed to fetch data")
        except Exception as e:
            display_error(str(e))

# Query 5: High Magnitude Earthquakes
elif query_type == "5. High Magnitude Earthquakes":
    
    st.header("High Magnitude Earthquakes")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        min_magnitude = st.number_input("Minimum Magnitude", min_value=0.0, value=6.0, step=0.1, key="q5_mag")
    with col2:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), key="q5_start")
    with col3:
        end_date = st.date_input("End Date", value=datetime.now(), key="q5_end")
    with col4:
        limit = st.number_input("Limit Results", min_value=1, max_value=500, value=50, key="q5_limit")
    
    if st.button("Search Earthquakes", key="q5"):
        try:
            response = requests.get(
                f"{API_BASE_URL}/analytics/high-magnitude",
                params={
                    "min_magnitude": min_magnitude,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "limit": limit
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    display_success(f"Found {len(data)} earthquakes matching criteria")
                else:
                    st.info("No earthquakes found matching criteria")
            else:
                display_error("Failed to fetch data")
        except Exception as e:
            display_error(str(e))

# Query 6: Regions with Minimum Quakes
elif query_type == "6. Regions with Min Quakes":

    st.header("Regions with Minimum Earthquake Count")
    col1, col2 = st.columns(2)
    
    with col1:
        min_quakes = st.number_input("Minimum Number of Earthquakes", min_value=1, value=10, step=1, key="q6_min")
    
    if st.button("Get Regions", key="q6"):
        try:
            response = requests.get(f"{API_BASE_URL}/analytics/regions/with-min-quakes", params={"min_quakes": min_quakes})
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    display_success(f"Found {len(data)} regions with at least {min_quakes} earthquakes")
                else:
                    st.info("No regions found matching criteria")
            else:
                display_error("Failed to fetch data")
        except Exception as e:
            display_error(str(e))

# Query 7: Above Average Activity
elif query_type == "7. Above Average Activity":
    st.header("Regions with Above Average Activity")
    
    if st.button("Get Regions", key="q7"):
        try:
            response = requests.get(f"{API_BASE_URL}/analytics/regions/above-average-activity")
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    display_success(f"Found {len(data)} regions with above-average activity")
                else:
                    st.info("No regions found")
            else:
                display_error("Failed to fetch data")
        except Exception as e:
            display_error(str(e))

# Query 8: Multi-Criteria Search
elif query_type == "8. Multi-Criteria Search":
    st.header("Multi-Criteria Earthquake Search")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_magnitude = st.number_input("Minimum Magnitude", min_value=0.0, value=5.5, step=0.1, key="q8_mag")
    with col2:
        min_risk_level = st.slider("Minimum Risk Level", min_value=1, max_value=5, value=4, key="q8_risk")
    with col3:
        min_population = st.number_input("Minimum Population", min_value=0, value=10000000, step=1000000, key="q8_pop")
    
    if st.button("Search", key="q8"):
        try:
            response = requests.get(
                f"{API_BASE_URL}/analytics/multi-criteria",
                params={
                    "min_magnitude": min_magnitude,
                    "min_risk_level": min_risk_level,
                    "min_population": min_population
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    display_success(f"Found {len(data)} earthquakes matching criteria")
                else:
                    st.info("No earthquakes found matching criteria")
            else:
                display_error("Failed to fetch data")
        except Exception as e:
            display_error(str(e))

# Query 9: High Population Regions
elif query_type == "9. High Population Regions":
    st.header("Earthquakes in High Population Regions")
    col1, col2 = st.columns(2)
    
    with col1:
        min_population = st.number_input("Minimum Population", min_value=0, value=10000000, step=1000000, key="q9_pop")
    
    if st.button("Get Data", key="q9"):
        try:
            response = requests.get(
                f"{API_BASE_URL}/analytics/high-population-regions",
                params={"min_population": min_population}
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    display_success(f"Retrieved data for {len(data)} high-population regions")
                else:
                    st.info("No regions found")
            else:
                display_error("Failed to fetch data")
        except Exception as e:
            display_error(str(e))

# Query 10: Region Risk Summary
elif query_type == "10. Region Risk Summary":
    st.header("Region Risk Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        region_id = st.number_input("Enter Region ID", min_value=1, step=1, key="q10_region")
    
    if st.button("Get Risk Summary", key="q10"):
        try:
            response = requests.get(f"{API_BASE_URL}/regions/{region_id}/risk-summary")
            if response.status_code == 200:
                data = response.json()
                
                # Display summary in columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Region Name", data.get("region_name", "N/A"))
                with col2:
                    st.metric("Zone Name", data.get("zone_name", "N/A"))
                with col3:
                    st.metric("Risk Level", data.get("risk_level", "N/A"))
                
                st.divider()
                
                # Display full data
                st.json(data)
                display_success("Risk summary retrieved")
            else:
                display_error(response.json().get("detail", "Failed to fetch data"))
        except Exception as e:
            display_error(str(e))

st.markdown("---")
st.caption("This page is powered by Streamlit and communicates with a FastAPI backend. The base code was provided by Claude Haiku 4.5.")
