import streamlit as st
import numpy as np
import time

# ------------------------------
# SIMULATION SETTINGS & UTILITIES
# ------------------------------

st.title("Chandigarh Traffic Light Assistant Simulation")

st.markdown("""
This simulation models a dummy car traveling on a road network in Chandigarh.  
Traffic lights are assumed to be at every intersection (nodes on a grid).  
The simulation calculates the car’s estimated arrival time at the next traffic light and suggests an optimal speed based on dummy traffic light timing.
""")

# Define dummy intersections (simulate a grid; for simplicity, we use (x,y) coordinates in meters)
# For example, a 3x3 grid. You can adjust these values or generate a random network.
intersections = {
    "A": (0, 0),
    "B": (0, 500),
    "C": (0, 1000),
    "D": (500, 0),
    "E": (500, 500),
    "F": (500, 1000),
    "G": (1000, 0),
    "H": (1000, 500),
    "I": (1000, 1000),
}

# Predefine a route for the dummy car as a list of intersection keys.
# For instance, the car starts at "A" and goes to "E" then "I".
route = ["A", "E", "I"]

# Dummy Traffic Light Cycle (60-second cycle)
# For simplicity, we assume the same cycle for all intersections:
#   Red:   0 - 29 s
#   Yellow: 30 - 34 s
#   Green:  35 - 59 s
cycle_duration = 60  # seconds
def get_traffic_phase(cycle_time):
    if cycle_time < 30:
        return "Red"
    elif cycle_time < 35:
        return "Yellow"
    else:
        return "Green"

# ------------------------------
# USER INPUTS (Simulation Controls)
# ------------------------------

st.sidebar.header("Simulation Controls")

# Car settings:
speed = st.sidebar.slider("Current Vehicle Speed (km/h)", min_value=0, max_value=120, value=40)
# In our simulation, let’s assume the car can sometimes speed up or slow down (this could be randomized).
dynamic_speed = st.sidebar.checkbox("Enable Dynamic Speed Variation", value=False)

# Select current traffic light cycle time at upcoming intersection (dummy input)
current_cycle_time = st.sidebar.number_input("Current Traffic Light Cycle Time (0 to 59 s)", min_value=0.0, max_value=59.0, value=20.0, step=0.1)

# Choose which segment of route to simulate (from current intersection to next)
current_segment = st.sidebar.selectbox("Select Route Segment", options=[f"{route[i]} -> {route[i+1]}" for i in range(len(route)-1)])

# ------------------------------
# SIMULATION LOGIC
# ------------------------------

# For simplicity, compute distance between two intersections using Euclidean distance.
def distance_between(intersection1, intersection2):
    x1, y1 = intersections[intersection1]
    x2, y2 = intersections[intersection2]
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Determine current and next intersection based on selected segment
current_int, next_int = current_segment.split(" -> ")
dist = distance_between(current_int, next_int)

# Convert speed to m/s (km/h to m/s)
speed_ms = speed / 3.6

# If dynamic speed is enabled, we can simulate a small random variation (±10%)
if dynamic_speed:
    variation = np.random.uniform(0.9, 1.1)
    speed_ms = speed_ms * variation

# Estimated time (in seconds) to reach the intersection.
if speed_ms > 0:
    arrival_time = dist / speed_ms
else:
    arrival_time = float('inf')

predicted_cycle_time = (current_cycle_time + arrival_time) % cycle_duration
predicted_phase = get_traffic_phase(predicted_cycle_time)

st.subheader("Simulation Results")
st.write(f"**Route Segment:** {current_segment}")
st.write(f"**Distance to Intersection:** {dist:.1f} meters")
st.write(f"**Current Speed:** {speed:.1f} km/h (≈ {speed_ms:.1f} m/s)")
st.write(f"**Estimated Arrival Time:** {arrival_time:.1f} seconds")
st.write(f"**Predicted Traffic Light Cycle Time on Arrival:** {predicted_cycle_time:.1f} seconds")
st.write(f"**Predicted Traffic Light Phase at Arrival:** **{predicted_phase}**")

# ------------------------------
# SPEED SUGGESTION LOGIC
# ------------------------------
# For example, iterate over a range of speeds (20 to 120 km/h) to see which one would
# yield a green light on arrival.
def suggest_speed(distance, current_cycle_time):
    speeds = np.arange(20, 121, 5)  # possible speeds in km/h
    for s in speeds:
        s_ms = s / 3.6
        arrival = distance / s_ms
        pred_time = (current_cycle_time + arrival) % cycle_duration
        phase = get_traffic_phase(pred_time)
        if phase == "Green":
            return s, pred_time, phase
    return None, None, None

rec_speed, rec_cycle_time, rec_phase = suggest_speed(dist, current_cycle_time)

if rec_speed:
    st.write(f"**Recommended Speed to Catch Green:** {rec_speed} km/h")
    st.write(f"(Estimated arrival cycle time would be {rec_cycle_time:.1f} s, yielding {rec_phase})")
else:
    st.write("No recommended speed found within 20-120 km/h. Try adjusting inputs.")

# ------------------------------
# VOICE ALERT: Using Browser's SpeechSynthesis API
# ------------------------------
if st.button("Speak Speed Suggestion"):
    # Use JavaScript to speak the recommendation:
    if rec_speed:
        advice = f"To catch the green light, adjust your speed to {rec_speed} kilometers per hour."
    else:
        advice = "No optimal speed found. Please adjust your current speed or distance."
    st.components.v1.html(f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{advice}");
            window.speechSynthesis.speak(msg);
        </script>
    """, height=0)

# Optionally, display a static map or diagram of intersections.
st.markdown("### Intersections Map (Dummy)")
st.write("A simplified grid of intersections in Chandigarh is simulated as follows:")
st.table({key: intersections[key] for key in sorted(intersections)})
