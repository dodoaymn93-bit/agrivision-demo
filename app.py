# -------------------------------
# 2. NASA POWER API: Rainfall for Essaouira
# -------------------------------
lat, lon = 31.51, -9.77

url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR&start=20240101&end=20241231&latitude={lat}&longitude={lon}&format=JSON"
r = requests.get(url).json()

parameters = r.get('properties', {}).get('parameter', {})
data = parameters.get('PRECTOTCORR')

if data is None:
    st.error("⚠️ PRECTOTCORR data not found — check API request or coordinates.")
    df = pd.DataFrame(columns=["Date", "Rain (mm/day)"])
else:
    df = pd.DataFrame(list(data.items()), columns=["Date", "Rain (mm/day)"])
    df["Date"] = pd.to_datetime(df["Date"])
