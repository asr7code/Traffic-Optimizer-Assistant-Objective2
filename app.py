import streamlit as st
from streamlit_folium import st_folium
import folium
import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
import numpy as np

st.set_page_config(layout="wide")
st.title("🚦 Chandigarh Traffic Assistant – Streamlit Version (Offline Roads)")

# ✅ Load road graph from local file (no API call)
@st.cache_resource
def load_graph():
    return ox.load_graphml("chandigarh.graphml")

G = load_graph()

# Dummy Traffic Lights (lat, lon)
intersections = {
    "ISBT Sector 43": (30.7165, 76.7656),
    "Madhya Marg & Jan Marg": (30.7415, 76.7680),
    "Sector 17 Plaza": (30.7399, 76.7821),
    "PGI Chowk": (30.7625, 76.7662),
    "Sector 35": (30.7270, 76.7651),
}

# Sidebar
st.sidebar.header("Simulation Controls")
start_lat = st.sidebar.number_input("Start Latitude", value=30.7270, format="%.5f")
start_lon = st.sidebar.number_input("Start Longitude", value=76.7651, format="%.5f")
end_lat = st.sidebar.number_input("Destination Latitude", value=30.7165, format="%.5f")
end_lon = st.sidebar.number_input("Destination Longitude", value=76.7656, format="%.5f")
speed = st.sidebar.slider("Vehicle Speed (km/h)", 10, 100, 40)
cycle_time = st.sidebar.slider("Current Signal Time (0–59s)", 0, 59, 20)

try:
    orig_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
    dest_node = ox.distance.nearest_nodes(G, end_lon, end_lat)

    route = nx.shortest_path(G, orig_node, dest_node, weight='length')
    route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]

    m = folium.Map(location=route_coords[0], zoom_start=14)
    folium.PolyLine(route_coords, color="blue", weight=5, popup="Route").add_to(m)
    folium.Marker(route_coords[0], icon=folium.Icon(color="green"), popup="Start").add_to(m)
    folium.Marker(route_coords[-1], icon=folium.Icon(color="red"), popup="Destination").add_to(m)

    for name, loc in intersections.items():
        folium.Marker(loc, icon=folium.Icon(color="orange", icon="exclamation-sign"), popup=f"🚦 {name}").add_to(m)

    st_data = st_folium(m, height=500, width=900)

    # Speed logic
    speed_ms = speed / 3.6
    total_distance = sum(
        geodesic(route_coords[i], route_coords[i+1]).meters for i in range(len(route_coords)-1)
    )
    eta = total_distance / speed_ms
    arrival_cycle = (cycle_time + eta) % 60

    if arrival_cycle < 30:
        phase = "Red"
    elif arrival_cycle < 35:
        phase = "Yellow"
    else:
        phase = "Green"

    st.markdown("### 🧠 Simulation Output")
    st.write(f"**Distance:** `{total_distance:.2f}` meters")
    st.write(f"**ETA:** `{eta:.1f}` seconds")
    st.write(f"**Predicted Phase on Arrival:** **{phase}** at `{arrival_cycle:.1f}`s")

    def suggest_speed(distance, current_time):
        for s in range(20, 101, 5):
            t = distance / (s / 3.6)
            pred = (current_time + t) % 60
            if pred >= 35: return s
        return None

    suggested = suggest_speed(total_distance, cycle_time)
    if suggested:
        st.success(f"✅ Suggested Speed: {suggested} km/h")
    else:
        st.warning("⚠️ No speed found to match green phase.")

    if st.button("🔊 Speak Suggestion"):
        msg = f"Adjust your speed to {suggested} kilometers per hour." if suggested else "Slow down or wait."
        st.components.v1.html(f"""
            <script>
                var msg = new SpeechSynthesisUtterance("{msg}");
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)

except Exception as e:
    st.error("Error calculating route.")
    st.code(str(e))
