import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.distance import geodesic
import numpy as np
import time

st.set_page_config(layout="wide")
st.title("🚦 Chandigarh Traffic Light Assistant (Map Simulation)")

# -----------------------------
# Dummy Traffic Light Intersections in Chandigarh (lat, lon)
# -----------------------------
intersections = {
    "Madhya Marg & Jan Marg": (30.741482, 76.768066),
    "Sector 17 Plaza": (30.739891, 76.782118),
    "ISBT Sector 43": (30.716509, 76.765597),
    "PGI Chowk": (30.762575, 76.766254),
    "Sector 35 Light Point": (30.726998, 76.765173),
}

# -----------------------------
# Define a dummy route (you can expand this later)
# -----------------------------
route_coords = [
    (30.741482, 76.768066),  # Madhya Marg
    (30.739891, 76.782118),  # Sector 17
    (30.726998, 76.765173),  # Sector 35
    (30.716509, 76.765597),  # ISBT
]

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("Simulation Controls")
step = st.sidebar.slider("Car Position Step", 0, len(route_coords) - 2, 0)
speed = st.sidebar.slider("Current Vehicle Speed (km/h)", 0, 100, 40)
light_cycle_time = st.sidebar.slider("Current Signal Time (0-59 s)", 0, 59, 20)

# -----------------------------
# Map Creation
# -----------------------------
center = route_coords[step]
m = folium.Map(location=center, zoom_start=14)

# Plot traffic lights
for name, loc in intersections.items():
    folium.Marker(
        location=loc,
        popup=f"🚦 {name}",
        icon=folium.Icon(color="red", icon="exclamation-sign"),
    ).add_to(m)

# Plot route line
folium.PolyLine(route_coords, color="blue", weight=5).add_to(m)

# Plot car position
car_position = route_coords[step]
folium.Marker(
    location=car_position,
    popup="🚗 Your Car",
    icon=folium.Icon(color="green", icon="car")
).add_to(m)

# Show the map in Streamlit
st_data = st_folium(m, width=900, height=500)

# -----------------------------
# Simulation Logic
# -----------------------------
next_position = route_coords[step + 1]
distance_to_next = geodesic(car_position, next_position).meters
speed_ms = speed / 3.6

if speed_ms > 0:
    eta = distance_to_next / speed_ms
else:
    eta = float("inf")

arrival_cycle_time = (light_cycle_time + eta) % 60

if arrival_cycle_time < 30:
    phase = "Red"
elif arrival_cycle_time < 35:
    phase = "Yellow"
else:
    phase = "Green"

st.markdown("### 🧠 Simulation Info")
st.write(f"**Distance to next point:** `{distance_to_next:.2f}` meters")
st.write(f"**Estimated Time to Reach:** `{eta:.1f}` seconds")
st.write(f"**Predicted Signal Phase on Arrival:** 🟢 **{phase}** at `{arrival_cycle_time:.1f}` s")

# Suggest speed
def suggest_speed(distance, current_time):
    for s in range(20, 101, 5):
        t = distance / (s / 3.6)
        pred_time = (current_time + t) % 60
        if pred_time >= 35:  # green
            return s
    return None

suggested = suggest_speed(distance_to_next, light_cycle_time)
if suggested:
    st.success(f"✅ Suggested Speed to Catch Green: **{suggested} km/h**")
else:
    st.warning("⚠️ No optimal speed found in 20–100 km/h range.")

# Voice alert using browser's Speech API
if st.button("🔊 Speak Advice"):
    if suggested:
        advice = f"To catch the green light, adjust your speed to {suggested} kilometers per hour."
    else:
        advice = "No optimal speed found. Please reduce your speed and wait."
    st.components.v1.html(f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{advice}");
            window.speechSynthesis.speak(msg);
        </script>
    """, height=0)
