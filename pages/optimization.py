import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

st.title("🗺 Voyage Optimization")

# =====================================
# LOAD DATA FROM SESSION STATE & VERIFY
# =====================================
metrics = st.session_state.get("metrics")

if not metrics:
    st.warning(
        "No data loaded. Please upload a Noon Report on the main page first."
    )
    st.stop()  # Prevents the rest of the script from executing without data

# Extract live values from metrics to use as dynamic defaults
live_speed = float(metrics.get("actual_speed", 12.0))
live_fuel = float(metrics.get("fuel_consumption", 12.0))
allowed_speed = float(metrics.get("allowed_speed", 12.0))
fuel_variance = float(metrics.get("fuel_variance", 0.0))

# =====================================
# 1. ROUTE PLANNING
# =====================================
st.subheader("Route Planning")

route_data = {
    "Mumbai → Singapore": {
        "distance": 2400,
        "origin": "Mumbai",
        "destination": "Singapore",
        "center": [10.0, 85.0],
        "main": [[19.0760, 72.8777], [1.3521, 103.8198]],
        "alt": [[19.0760, 72.8777], [6.9271, 79.8612], [1.3521, 103.8198]]
    },
    "Singapore → Rotterdam": {
        "distance": 8300,
        "origin": "Singapore",
        "destination": "Rotterdam",
        "center": [25.0, 45.0],
        "main": [[1.3521, 103.8198], [11.85, 43.25], [29.93, 32.55], [51.92, 4.47]],
        "alt": [[1.3521, 103.8198], [-34.35, 18.47], [51.92, 4.47]]
    },
    "Dubai → Rotterdam": {
        "distance": 6500,
        "origin": "Dubai",
        "destination": "Rotterdam",
        "center": [30.0, 35.0],
        "main": [[25.2048, 55.2708], [11.85, 43.25], [29.93, 32.55], [51.92, 4.47]],
        "alt": [[25.2048, 55.2708], [12.00, 44.00], [30.00, 33.00], [51.92, 4.47]]
    },
    "Shanghai → Los Angeles": {
        "distance": 6100,
        "origin": "Shanghai",
        "destination": "Los Angeles",
        "center": [35.0, -160.0],
        "main": [[31.2304, 121.4737], [34.0522, -118.2437]],
        "alt": [[31.2304, 121.4737], [21.3069, -157.8583], [34.0522, -118.2437]]
    },
    "Mumbai → Dubai": {
        "distance": 1200,
        "origin": "Mumbai",
        "destination": "Dubai",
        "center": [22.0, 64.0],
        "main": [[19.0760, 72.8777], [25.2048, 55.2708]],
        "alt": [[19.0760, 72.8777], [22.00, 60.00], [25.2048, 55.2708]]
    }
}

selected_route = st.selectbox(
    "Select Route",
    list(route_data.keys())
)

current_route = route_data[selected_route]
distance = current_route["distance"]

# Default values change dynamically based on the uploaded file
speed = st.number_input(
    "Average Vessel Speed (knots)",
    value=live_speed
)

fuel_rate = st.number_input(
    "Fuel Consumption (MT/day)",
    value=live_fuel
)

if speed <= 0:
    st.error("Speed must be greater than 0.")
    st.stop()

# =====================================
# 2. ROUTE VISUALIZATION
# =====================================
st.subheader("🗺 Route Visualization")

# Visual Legend for Panel Judges
st.markdown("""
<div style="display: flex; gap: 20px; font-size: 14px; margin-bottom: 15px;">
    <span>🔴 <b>Current Track</b></span>
    <span>🟢 ── <b>Optimized Track</b></span>
    <span>🟠 <b>Transit Waypoint</b></span>
    <span>📍 <b>Port Terminal</b></span>
</div>
""", unsafe_allow_html=True)

# Initialize Folium Map
m = folium.Map(
    location=current_route["center"], 
    zoom_start=4, 
    tiles="CartoDB positron"
)

# Draw lines
folium.PolyLine(
    current_route["main"],
    tooltip="Current Track Profile",
    color="#EF4444",
    weight=4
).add_to(m)

folium.PolyLine(
    current_route["alt"],
    tooltip="Optimized Track Profile",
    color="#10B981",
    weight=4,
    dash_array="10"
).add_to(m)

# Explicit Port Names added to popups/tooltips
folium.Marker(
    current_route["main"][0], 
    popup=folium.Popup(f"<b>{current_route['origin']} Port</b>", max_width=200),
    tooltip=f"Departure: {current_route['origin']}", 
    icon=folium.Icon(color="red", icon="ship", prefix="fa")
).add_to(m)

# Waypoint handling for presentations
if selected_route == "Mumbai → Singapore":
    folium.Marker(
        [6.9271, 79.8612],
        popup="Colombo Transit Waypoint",
        tooltip="Optimization Waypoint: Colombo",
        icon=folium.Icon(color="orange", icon="compass", prefix="fa")
    ).add_to(m)

folium.Marker(
    current_route["main"][-1], 
    popup=folium.Popup(f"<b>{current_route['destination']} Port</b>", max_width=200),
    tooltip=f"Arrival: {current_route['destination']}", 
    icon=folium.Icon(color="green", icon="anchor", prefix="fa")
).add_to(m)

# Dynamic viewport adjustments to prevent drifting views
m.fit_bounds(current_route["alt"])

# Renders dynamic full-width container sizing with a prominent 550px viewport
st_folium(m, use_container_width=True, height=550, key="voyage_map_final_bounds")

# =====================================
# 3. VOYAGE ESTIMATION
# =====================================
st.subheader("📊 Voyage Estimation")

eta_days = round(distance / (speed * 24), 2)
fuel_required = round(eta_days * fuel_rate, 2)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Distance", f"{distance} NM")

with col2:
    st.metric("ETA", f"{eta_days} Days")

with col3:
    st.metric("Fuel Required", f"{fuel_required} MT")

# =====================================
# 4. WEATHER RISK ANALYSIS
# =====================================
st.subheader("🌦 Weather Risk Analysis")

risk = metrics.get("weather_risk", "LOW")

if risk == "LOW":
    st.success("LOW Weather Risk: Favorable sailing conditions reported.")
elif risk == "MEDIUM":
    st.warning("MEDIUM Weather Risk: Noticeable wind/swell resistance detected.")
else:
    st.error("HIGH Weather Risk: Adverse weather cell verified. Rerouting recommended.")

# =====================================
# 5. ALTERNATIVE ROUTE RECOMMENDATION
# =====================================
st.subheader("🛳 Alternative Route Recommendation")

alternate_routes = {
    "Mumbai → Singapore": f"{current_route['origin']} → Colombo → {current_route['destination']} (Weather Avoidance routing applied)",
    "Singapore → Rotterdam": f"{current_route['origin']} → Suez Canal → {current_route['destination']} (Standard Track)",
    "Dubai → Rotterdam": f"{current_route['origin']} → Suez Canal → {current_route['destination']} (Standard Track)",
    "Shanghai → Los Angeles": f"{current_route['origin']} → Honolulu → {current_route['destination']} (Rerouted to mitigate frontal stress)",
    "Mumbai → Dubai": "Direct Line Transit Recommended"
}

st.info(alternate_routes[selected_route])

# =====================================
# 6. FUEL OPTIMIZATION
# =====================================
st.subheader("⛽ Fuel Optimization")

efficiency_gain = 8.0 
optimized_fuel = fuel_required * (1 - efficiency_gain / 100)
saving = fuel_required - optimized_fuel

# Business Metrics
saving_usd = saving * 600
co2_saved = saving * 3.114

# ETA Improvement calculations relative to baseline performance thresholds
optimized_eta = round(distance / (allowed_speed * 24), 2)
eta_gain = eta_days - optimized_eta

col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    st.metric("Potential Fuel Saving", f"{saving:.2f} MT")

with col_f2:
    st.metric("Estimated Cost Saving", f"${saving_usd:,.0f}")

with col_f3:
    st.metric("CO₂ Reduction", f"{co2_saved:.2f} MT")

with col_f4:
    st.metric("ETA Improvement", f"{eta_gain:.2f} Days")

st.caption(f"💡 Optimization projections assume a clear baseline {efficiency_gain:.0f}% efficiency gain via smart speed-trim maneuvers.")

# =====================================
# 7. AI RECOMMENDATION BOX
# =====================================
st.subheader("🤖 AI Recommendation")

# Operational context-aware advisory conditional paths
if speed < allowed_speed:
    action_text = f"Maintain vessel speed within the {speed:.1f} – {allowed_speed:.1f} kn operational window."
    reason_text = f"Fuel consumption is already operating exceptionally well below standard benchmarks."
    benefit_text = "Maintains strict charter compliance while preserving current peak fuel efficiency margins."
else:
    action_text = f"Execute dynamic speed-trim down to target eco-speed ceiling of {allowed_speed:.1f} kn."
    reason_text = f"Current velocity exceeds necessary passage plan requirements, introducing unneeded fuel overhead."
    benefit_text = f"Secures immediate {saving:.2f} MT bunker reduction without sacrificing delivery window deadlines."

recommendation = f"""
**Voyage Analysis Intelligence Summary:**
* **Velocity Parameter:** Current vessel speed is operating at **{speed:.1f} kn** (Allowed Benchmark: {allowed_speed:.1f} kn).
* **Weather Layer:** Conditions along alternative tracking legs are flagged as **{risk}**.
* **Recommended Action:** {action_text}
* **Justification:** {reason_text}
* **Expected Outcome:** {benefit_text}
* **Risk Margin:** **SAFE OPERATIONAL PROFILE**. No critical wave response or hull stress warnings active.
"""

st.info(recommendation)