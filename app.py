import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# -------------------------------
# 0. Streamlit config
# -------------------------------
st.set_page_config(page_title="AgriVision Smart Irrigation", layout="wide")

# -------------------------------
# 1. Static thumbnail URLs
# -------------------------------
ndvi_url = "https://earthengine.googleapis.com/v1/projects/angelic-ivy-473311-b3/thumbnails/44e9619e1c3d149e05c6bf79e087c571-db05b9e550e90b87d78f133c063f198d:getPixels"
smap_url = "https://earthengine.googleapis.com/v1/projects/angelic-ivy-473311-b3/thumbnails/780c354fa689121c0f4480f24c68bcce-01d38391b14d51ae18d3a41ef5174bbc:getPixels"

# -------------------------------
# 2. NASA POWER API: Rainfall (last month) & Forecast
# -------------------------------
lat, lon = 31.51, -9.77
start_date = "20240101"
end_date = "20240131"
parameter = "PRECTOTCORR"

# Historical Rainfall
url_hist = (
    f"https://power.larc.nasa.gov/api/temporal/daily/point?"
    f"parameters={parameter}&start={start_date}&end={end_date}&"
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
data_hist = parameters.get(parameter)

if not data_hist:
    st.warning("⚠️ No precipitation data found — check API request or coordinates.")
    df_hist = pd.DataFrame(columns=["Date", "Rain (mm/day)"])
else:
    df_hist = pd.DataFrame(list(data_hist.items()), columns=["Date", "Rain (mm/day)"])
    df_hist["Date"] = pd.to_datetime(df_hist["Date"], errors="coerce")

# -------------------------------
# 3. Streamlit Layout
# -------------------------------
st.title("🌱 AgriVision Smart Irrigation Assistant")
st.markdown("""
Prototype dashboard combining **satellite crop health (NDVI)**, **soil moisture (SMAP)**, and **rainfall forecasts** to help with irrigation decisions.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌱 NDVI (MODIS 2024)")
    if ndvi_url:
        try:
            st.image(ndvi_url, caption="NDVI Median 2024 - Essaouira", use_container_width=True)
        except Exception as e:
            st.error(f"❌ Failed to load NDVI image: {e}")
    else:
        st.warning("Paste NDVI thumbnail URL from Earth Engine here.")

with col2:
    st.subheader("💧 Soil Moisture (SMAP June 2024)")
    if smap_url:
        try:
            st.image(smap_url, caption="SMAP Soil Moisture - Essaouira", use_container_width=True)
        except Exception as e:
            st.error(f"❌ Failed to load SMAP image: {e}")
    else:
        st.warning("Paste SMAP thumbnail URL from Earth Engine here.")

# -------------------------------
# 4. Rainfall Plot
# -------------------------------
st.subheader("☔ Daily Rainfall (NASA POWER - Jan 2024)")
fig, ax = plt.subplots(figsize=(8, 4))
if not df_hist.empty:
    ax.plot(df_hist["Date"], df_hist["Rain (mm/day)"], color="blue", label="Rainfall")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rain (mm/day)")
    ax.set_title("Daily Rainfall - Essaouira Jan 2024")
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("⚠️ No rainfall data to plot.")

# -------------------------------
# 5. User Inputs for Irrigation Planning
# -------------------------------
st.subheader("💧 Irrigation Planner")

last_irrigation = st.date_input("📅 Select last irrigation date", datetime.date.today())
soil_moisture_threshold = st.slider("Soil moisture threshold (%)", min_value=0.0, max_value=1.0, value=0.3, step=0.05)

days_since_irrigation = (datetime.date.today() - last_irrigation).days

# -------------------------------
# 6. Rain Forecast (simplified example — next 7 days hardcoded for now)
# -------------------------------
forecast_days = pd.date_range(datetime.date.today(), periods=7)
forecast_rain = [0.1, 0.0, 0.5, 0.2, 0.0, 0.0, 0.3]  # Example forecast (replace with API later)
df_forecast = pd.DataFrame({"Date": forecast_days, "Rain (mm/day)": forecast_rain})

st.subheader("🌦 Rain Forecast (Next 7 days)")
st.line_chart(df_forecast.set_index("Date")["Rain (mm/day)"])

avg_rain_forecast = df_forecast["Rain (mm/day)"].mean()

# -------------------------------
# 7. Smart Irrigation Advice
# -------------------------------
st.subheader("📢 Irrigation Recommendation")

soil_moisture_current = 0.25  # Example, replace with SMAP extraction

if avg_rain_forecast < 1 and days_since_irrigation > 3 and soil_moisture_current < soil_moisture_threshold:
    st.error("⚠️ Recommend irrigation now. Rain forecast is low and soil moisture is below threshold.")
else:
    st.success("✅ Irrigation can be delayed — either enough rain is forecast or soil moisture is adequate.")

# -------------------------------
# 8. Educational Tips Section
# -------------------------------
st.subheader("📚 Tips for Sustainable Irrigation")
st.markdown("""
- **Monitor soil moisture** regularly for efficient water use.  
- **Check rain forecasts** to avoid unnecessary irrigation.  
- **Use drip irrigation** to save water.  
- **Schedule irrigation** based on crop needs and soil moisture.  
""")
