import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AgriVision Demo", layout="wide")

# -------------------------------
# 1. Static thumbnail URLs (replace with your own from Earth Engine console)
# -------------------------------
ndvi_url = "PASTE_YOUR_NDVI_THUMB_URL_HERE"
smap_url = "PASTE_YOUR_SMAP_THUMB_URL_HERE"

# -------------------------------
# 2. NASA POWER API: Rainfall for Essaouira
# -------------------------------
lat, lon = 31.51, -9.77

url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR&start=20240101&end=20241231&latitude={lat}&longitude={lon}&format=JSON"
r = requests.get(url).json()

data = r['properties']['parameter']['PRECTOTCORR']
df = pd.DataFrame(list(data.items()), columns=["Date", "Rain (mm/day)"])
df["Date"] = pd.to_datetime(df["Date"])

# -------------------------------
# 3. Streamlit Layout
# -------------------------------
st.title("🌍 AgriVision Demo")
st.markdown("Prototype dashboard combining **satellite crop health (NDVI)**, **soil moisture (SMAP)**, and **rainfall (NASA POWER)** for Essaouira.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌱 NDVI (MODIS 2024)")
    if ndvi_url != "PASTE_YOUR_NDVI_THUMB_URL_HERE":
        st.image(ndvi_url, caption="NDVI Median 2024 - Essaouira", use_column_width=True)
    else:
        st.warning("Paste NDVI thumbnail URL from Earth Engine here.")

with col2:
    st.subheader("💧 Soil Moisture (SMAP June 2024)")
    if smap_url != "PASTE_YOUR_SMAP_THUMB_URL_HERE":
        st.image(smap_url, caption="SMAP Soil Moisture - Essaouira", use_column_width=True)
    else:
        st.warning("Paste SMAP thumbnail URL from Earth Engine here.")

st.subheader("☔ Daily Rainfall (NASA POWER)")
fig, ax = plt.subplots(figsize=(8,4))
ax.plot(df["Date"], df["Rain (mm/day)"], color="blue", label="Rainfall")
ax.set_xlabel("Date")
ax.set_ylabel("Rain (mm/day)")
ax.set_title("Daily Rainfall - Essaouira 2024")
ax.legend()
st.pyplot(fig)

# -------------------------------
# 4. Simple advisory message
# -------------------------------
avg_rain = df["Rain (mm/day)"].mean()
if avg_rain < 0.5:
    st.error("⚠️ Low rainfall trend detected → Recommend irrigation soon.")
else:
    st.success("✅ Rainfall sufficient → Irrigation can be delayed.")
