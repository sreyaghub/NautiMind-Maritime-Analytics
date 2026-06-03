import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.title("🌦 Weather Analysis")

# =====================================
# LOAD DATA FROM SESSION STATE & VERIFY
# =====================================
metrics = st.session_state.get("metrics")

if not metrics:
    st.warning(
        "No data loaded. Please upload a Noon Report on the main page first."
    )
    st.stop()  # Prevents the rest of the script from executing without data

# Extract active route spatial information if available from session state
selected_route = st.session_state.get("selected_route", "Mumbai → Singapore")

route_view_db = {
    "Mumbai → Singapore": {"center": [10.0, 85.0], "bounds": [[19.0760, 72.8777], [1.3521, 103.8198]]},
    "Singapore → Rotterdam": {"center": [25.0, 45.0], "bounds": [[1.3521, 103.8198], [51.92, 4.47]]},
    "Dubai → Rotterdam": {"center": [30.0, 35.0], "bounds": [[25.2048, 55.2708], [51.92, 4.47]]},
    "Shanghai → Los Angeles": {"center": [35.0, -160.0], "bounds": [[31.2304, 121.4737], [34.0522, -118.2437]]},
    "Mumbai → Dubai": {"center": [22.0, 64.0], "bounds": [[19.0760, 72.8777], [25.2048, 55.2708]]}
}

active_view = route_view_db.get(selected_route, route_view_db["Mumbai → Singapore"])

# =====================================
# 1. WEATHER KPI SECTION
# =====================================
st.subheader("📊 Weather KPIs")

wind_speed = float(metrics.get("wind_speed", 0.0))
beaufort_scale = metrics.get("beaufort_scale", 0)
weather_risk = metrics.get("weather_risk", "LOW")

# Dynamic Wave Height empirical evaluation (Vessel Hydrodynamics parameter)
wave_height = round(wind_speed * 0.15, 1)

if wave_height < 1.5:
    sea_state = "Calm"
elif wave_height < 3.0:
    sea_state = "Moderate"
else:
    sea_state = "Rough"

# IMPROVEMENT 2: Unified Weather Risk Scoring Logic
if weather_risk == "LOW":
    weather_score = 92
elif weather_risk == "MEDIUM":
    weather_score = 70
else:
    weather_score = 45

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Wind Speed", f"{wind_speed} kn")

with col2:
    st.metric("Wave Height", f"{wave_height} m")

with col3:
    st.metric("Sea State", sea_state)

with col4:
    st.metric("Beaufort Scale", beaufort_scale)

with col5:
    st.metric("Weather Risk", weather_risk)

with col6:
    # Displays the calculated safety score out of 100
    st.metric("Weather Score", f"{weather_score}/100")

# =====================================
# 2. OCEAN CONDITIONS
# =====================================
st.subheader("🌊 Ocean Conditions")

st.info(
    f"""
    * **Sea State Profile:** {sea_state} ({wave_height}m Significant Wave Height)
    * **Current Strength:** Weak (0.4 kn counter-current interaction)
    * **Swell Direction:** South-West (SW)
    * **Visibility Range:** Good (>10 Nautical Miles)
    """
)

# =====================================
# 3. FORECAST SECTION
# =====================================
st.subheader("📈 Weather Forecast Along Route")

# Modeled forecast increments shifting relative to the raw report baseline
forecast_df = pd.DataFrame({
    "Day": ["Today", "+1 Day", "+2 Days", "+3 Days", "+4 Days"],
    "Wind Velocity (kn)": [int(wind_speed), int(wind_speed * 1.1), int(wind_speed * 1.2), int(wind_speed * 1.1), int(wind_speed * 0.8)],
    "Wave Height (m)": [wave_height, round(wave_height * 1.1, 1), round(wave_height * 1.3, 1), round(wave_height * 1.0, 1), round(wave_height * 0.8, 1)]
})

st.dataframe(forecast_df, use_container_width=True)

# Visual multi-metric trend tracking
st.line_chart(forecast_df.set_index("Day"))

# =====================================
# 4. WEATHER MAP (WITH LEGEND & AUTO-BOUNDS)
# =====================================
st.subheader("🗺 Route Weather Conditions")

# IMPROVEMENT 1: Visual Map Legend for Corporate Review
st.markdown("""
<div style="display: flex; gap: 20px; font-size: 14px; margin-bottom: 15px;">
    <span>🟢 <b>Low Weather Risk Zone</b></span>
    <span>🟡 <b>Moderate Swell Zone</b></span>
    <span>🔴 <b>Severe Weather Zone</b></span>
</div>
""", unsafe_allow_html=True)

# Initialize Folium Map
m = folium.Map(
    location=active_view["center"],
    zoom_start=4,
    tiles="CartoDB positron"
)

# Plot interactive environmental warning rings
folium.Circle(
    location=[8.0, 85.0],
    radius=120000,
    popup="Low Risk Boundary Zone",
    color="#10B981",
    fill=True,
    fill_color="#10B981",
    fill_opacity=0.2
).add_to(m)

folium.Circle(
    location=[10.0, 90.0],
    radius=150000,
    popup="Moderate Swell Advisory Active",
    color="#F59E0B",
    fill=True,
    fill_color="#F59E0B",
    fill_opacity=0.25
).add_to(m)

# Focus viewport tightly around the active passage plan vectors
m.fit_bounds(active_view["bounds"])

# Render responsive full-width map window
st_folium(m, use_container_width=True, height=450, key="weather_analytics_map")

# =====================================
# 5. AI WEATHER ADVISORY
# =====================================
st.subheader("🤖 AI Weather Advisory")

# Contextual adaptive advice paths based on metrics
if weather_risk == "HIGH" or sea_state == "Rough":
    st.error(
        f"""
        **CRITICAL METOCEAN NOTICE:**
        * Elevated wave activity ({wave_height}m) and rough seas detected along current trajectory headings.
        * **Recommendation:** Execute the alternative track provided in the Voyage Optimization interface to avoid excessive engine torque stress and hull slamming.
        * Expected weather-induced fuel overhead expansion: **+12.4%**.
        """
    )
elif weather_risk == "MEDIUM" or sea_state == "Moderate":
    st.warning(
        f"""
        **OPERATIONAL WEATHER ADVISORY:**
        * Moderate swell patterns developed. Slight speed attenuation observed due to wave resistance profile.
        * **Recommendation:** Maintain current course headings but transition propulsion loops into eco-trim mode. Monitor ship motions closely.
        * Expected weather-induced fuel overhead expansion: **Minimal (+3.5%)**.
        """
    )
else:
    st.success(
        f"""
        **NOMINAL ENVIRONMENT CONDITIONS:**
        * Current wind conditions ({wind_speed} kn) and sea states remain fully within optimal operational safety thresholds.
        * **Recommendation:** No course deviations required. Proceed along the standard passage plan profile.
        * Weather impact on overall fuel burn efficiency remains completely negligible.
        """
    )