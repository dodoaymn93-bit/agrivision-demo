import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# 0. Streamlit config
# -------------------------------
st.set_page_config(page_title="AgriVision Demo", layout="wide")

# -------------------------------
# 1. Static thumbnail URLs
# -------------------------------
ndvi_url = "https://earthengine.googleapis.com/v1/projects/angelic-ivy-473311-b3/thumbnails/44e9619e1c3d149e05c6bf79e087c571-db05b9e550e90b87d78f133c063f198d:getPixels"
smap_url = "https://earthengine.googleapis.com/v1/projects/angelic-ivy-473311-b3/thumbnails/44e9619e1c3d149e05c6bf79e087c571-db05b9e550e90b87d78f133c063f198d:getPixels"

# -------------------------------
# 2. NASA POWER API: Rainfall for Essaouira
# -------------------------------
lat, lon = 31.51, -9.77
start_date = "20240101"
end_date = "20240131"
parameter = "PRECTOTCORR"  # fixed parameter

url = (
    f"https://power.larc.nasa.gov/api/temporal/daily/point?"
    f"parameters={parameter}&start={start_date}&end={end_date}&"
    f"latitude={lat}&longitude={lon}&community=AG&format=JSON"
)

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    r = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"❌ API request failed: {e}")
    r = {}

parameters = r.get("properties", {}).get("parameter", {})
data = parameters.get(parameter)

if not data:
    st.warning("⚠️ No precipitation data found — check API request or coordinates.")
    df = pd.DataFrame(columns=["Date", "Rain (mm/day)"])
else:
    df = pd.DataFrame(list(data.items()), columns=["Date", "Rain (mm/day)"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# -------------------------------
# 3. Streamlit Layout
# -------------------------------
st.title("🌍 AgriVision Demo")
st.markdown(
    "Prototype dashboard combining **satellite crop health (NDVI)**, "
    "**soil moisture (SMAP)**, and **rainfall (NASA POWER)** for Essaouira."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌱 NDVI (MODIS 2024)")
    if ndvi_url:
        try:
            st.image(ndvi_url, caption="NDVI Median 2024 - Essaouira", use_column_width=True)
        except Exception as e:
            st.error(f"❌ Failed to load NDVI image: {e}")
    else:
        st.warning("Paste NDVI thumbnail URL from Earth Engine here.")

with col2:
    st.subheader("💧 Soil Moisture (SMAP June 2024)")
    if smap_url:
        try:
            st.image(smap_url, caption="SMAP Soil Moisture - Essaouira", use_column_width=True)
        except Exception as e:
            st.error(f"❌ Failed to load SMAP image: {e}")
    else:
        st.warning("Paste SMAP thumbnail URL from Earth Engine here.")

# -------------------------------
# 4. Rainfall Plot
# -------------------------------
st.subheader("☔ Daily Rainfall (NASA POWER)")
fig, ax = plt.subplots(figsize=(8, 4))

if not df.empty:
    ax.plot(df["Date"], df["Rain (mm/day)"], color="blue", label="Rainfall")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rain (mm/day)")
    ax.set_title("Daily Rainfall - Essaouira 2024")
    ax.legend()
    st.pyplot(fig)

    # -------------------------------
    # 5. Simple advisory message
    # -------------------------------
    avg_rain = df["Rain (mm/day)"].mean()
    if avg_rain < 0.5:
        st.error("⚠️ Low rainfall trend detected → Recommend irrigation soon.")
    else:
        st.success("✅ Rainfall sufficient → Irrigation can be delayed.")
else:
    st.warning("⚠️ No rainfall data to plot.")
