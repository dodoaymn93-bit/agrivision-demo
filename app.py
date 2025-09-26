import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# -------------------------------
# 0. Streamlit Config
# -------------------------------
st.set_page_config(page_title="AgriVision Smart Irrigation", layout="wide")

# -------------------------------
# 1. Static Thumbnail URLs
# -------------------------------
ndvi_url = "https://earthengine.googleapis.com/v1/projects/angelic-ivy-473311-b3/thumbnails/44e9619e1c3d149e05c6bf79e087c571-db05b9e550e90b87d78f133c063f198d:getPixels"
smap_url = "https://earthengine.googleapis.com/v1/projects/angelic-ivy-473311-b3/thumbnails/780c354fa689121c0f4480f24c68bcce-01d38391b14d51ae18d3a41ef5174bbc:getPixels"

# -------------------------------
# 2. Plant Irrigation Profiles
# -------------------------------
plant_irrigation_profiles = {
    "Tomato": {"interval_days": 3, "water_mm_per_day": 10},
    "Rose": {"interval_days": 2, "water_mm_per_day": 8},
    "Olive Tree": {"interval_days": 7, "water_mm_per_day": 20},
    "Basil": {"interval_days": 1, "water_mm_per_day": 5},
    "Lettuce": {"interval_days": 2, "water_mm_per_day": 6}
}

# -------------------------------
# 3. NASA POWER API: Rainfall
# -------------------------------
lat, lon = 31.51, -9.77

# Historical rainfall
start_date_hist = "20240101"
end_date_hist = "20240131"
parameter_hist = "PRECTOTCORR"

url_hist = (
    f"https://power.larc.nasa.gov/api/temporal/daily/point?"
    f"parameters={parameter_hist}&start={start_date_hist}&end={end_date_hist}&"
    f"latitude={lat}&longitude={lon}&community=AG&format=JSON"
)

try:
    response = requests.get(url_hist, timeout=10)
    response.raise_for_status()
    r_hist = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"❌ API request failed: {e}")
    r_hist = {}

parameters = r_hist.get("properties", {}).get("parameter", {})
data_hist = parameters.get(parameter_hist)

if not data_hist:
    st.warning("⚠️ No precipitation data found — check API request or coordinates.")
    df_hist = pd.DataFrame(columns=["Date", "Rain (mm/day)"])
else:
    df_hist = pd.DataFrame(list(data_hist.items()), columns=["Date", "Rain (mm/day)"])
    df_hist["Date"] = pd.to_datetime(df_hist["Date"], errors="coerce")

# Forecast rainfall (next 7 days from NASA POWER API)
start_date_forecast = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y%m%d')
end_date_forecast = (datetime.date.today() + datetime.timedelta(days=7)).strftime('%Y%m%d')
parameter_forecast = "PRECTOT"

url_forecast = (
    f"https://power.larc.nasa.gov/api/temporal/daily/point?"
    f"parameters={parameter_forecast}&start={start_date_forecast}&end={end_date_forecast}&"
    f"latitude={lat}&longitude={lon}&community=AG&format=JSON"
)

try:
    response_forecast = requests.get(url_forecast, timeout=10)
    response_forecast.raise_for_status()
    r_forecast = response_forecast.json()
except requests.exceptions.RequestException as e:
    st.error(f"❌ Forecast API request failed: {e}")
    r_forecast = {}

parameters_forecast = r_forecast.get("properties", {}).get("parameter", {})
data_forecast = parameters_forecast.get(parameter_forecast)

if not data_forecast:
    df_forecast = pd.DataFrame(columns=["Date", "Rain (mm/day)"])
else:
    df_forecast = pd.DataFrame(list(data_forecast.items()), columns=["Date", "Rain (mm/day)"])
    df_forecast["Date"] = pd.to_datetime(df_forecast["Date"], errors="coerce")

# -------------------------------
# 4. Streamlit Layout
# -------------------------------
st.title("🌱 AgriVision Smart Irrigation Assistant")
st.markdown("""
A complete tool for farmers, gardeners, and schools to manage irrigation using **NDVI**, **SMAP**, **NASA POWER rainfall forecasts**, and **plant-specific recommendations**.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌱 NDVI (MODIS 2024)")
    if ndvi_url:
        st.image(ndvi_url, caption="NDVI Median 2024 - Essaouira", use_container_width=True)
    else:
        st.warning("Paste NDVI thumbnail URL from Earth Engine here.")

with col2:
    st.subheader("💧 Soil Moisture (SMAP June 2024)")
    if smap_url:
        st.image(smap_url, caption="SMAP Soil Moisture - Essaouira", use_container_width=True)
    else:
        st.warning("Paste SMAP thumbnail URL from Earth Engine here.")

# Rainfall plot
st.subheader("☔ Daily Rainfall (NASA POWER - Historical)")
fig, ax = plt.subplots(figsize=(8, 4))
if not df_hist.empty:
    ax.plot(df_hist["Date"], df_hist["Rain (mm/day)"], color="blue", label="Rainfall")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rain (mm/day)")
    ax.set_title("Daily Rainfall - Essaouira Jan 2024")
    ax.legend()
    st.pyplot(fig)

# Rain forecast plot
st.subheader("🌦 Rain Forecast (Next 7 Days)")
if not df_forecast.empty:
    st.line_chart(df_forecast.set_index("Date")["Rain (mm/day)"])
else:
    st.warning("⚠️ No forecast data available.")

# -------------------------------
# 5. Plant Selection and Irrigation Planner
# -------------------------------
st.subheader("💧 Irrigation Planner")

selected_plant = st.selectbox("Choose your plant", list(plant_irrigation_profiles.keys()))
last_irrigation = st.date_input("📅 Select last irrigation date", datetime.date.today())
soil_moisture_threshold = st.slider("Soil moisture threshold (%)", min_value=0.0, max_value=1.0, value=0.3, step=0.05)

interval = plant_irrigation_profiles[selected_plant]["interval_days"]
water_amount = plant_irrigation_profiles[selected_plant]["water_mm_per_day"]
next_irrigation_date = last_irrigation + datetime.timedelta(days=interval)
days_since_irrigation = (datetime.date.today() - last_irrigation).days

# -------------------------------
# 6. Irrigation Recommendation
# -------------------------------
st.subheader("📢 Irrigation Recommendation")

avg_rain_forecast = df_forecast["Rain (mm/day)"].mean() if not df_forecast.empty else 0.0
soil_moisture_current = 0.25  # Example placeholder; replace with SMAP actual data later

if days_since_irrigation >= interval:
    st.error(f"⚠️ Irrigation overdue! You should water {selected_plant} today (~{water_amount} mm/day).")
elif avg_rain_forecast >= water_amount:
    st.info(f"🌧 Rain forecast before next irrigation may be sufficient → consider skipping irrigation.")
else:
    st.success(f"✅ Next irrigation for {selected_plant} is on {next_irrigation_date.strftime('%Y-%m-%d')} (~{water_amount} mm/day).")

# -------------------------------
# 7. Educational Tips
# -------------------------------
st.subheader("📚 Tips for Sustainable Irrigation")
st.markdown("""
- **Monitor soil moisture** regularly for efficient water use.  
- **Check rain forecasts** to avoid unnecessary irrigation.  
- **Use drip irrigation** to save water.  
- **Schedule irrigation** based on crop needs and soil moisture.
""")
