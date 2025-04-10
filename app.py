import streamlit as st
import numpy as np

st.title("Traffic Light Assistant Simulator")
st.write("This app simulates a Traffic Light Assistant using dummy data for intersections in Chandigarh.")

st.markdown("""
**Assumed Traffic Light Cycle (60 seconds total):**

- **Red:** 0 – 29 seconds  
- **Yellow:** 30 – 34 seconds  
- **Green:** 35 – 59 seconds  
""")

# User Inputs
speed = st.slider("Current Vehicle Speed (km/h):", min_value=0, max_value=120, value=40)
distance = st.number_input("Distance to Intersection (meters):", min_value=0.0, value=200.0, step=1.0)
current_cycle_time = st.number_input("Current Cycle Time (0-59 seconds):", min_value=0.0, max_value=59.0, value=20.0, step=0.1)

st.write("For simulation purposes, we assume each intersection (in Chandigarh) has a 60-second traffic light cycle as above.")

# Calculate estimated arrival time
if speed > 0:
    speed_ms = speed / 3.6  # convert km/h to m/s
    arrival_time = distance / speed_ms
    st.write(f"**Estimated arrival time at the intersection:** {arrival_time:.1f} seconds")
else:
    st.error("Speed must be greater than 0 km/h for calculations.")
    arrival_time = None

if arrival_time is not None:
    # Calculate predicted cycle time at arrival
    predicted_cycle_time = (current_cycle_time + arrival_time) % 60

    if predicted_cycle_time < 30:
        predicted_phase = "Red"
    elif predicted_cycle_time < 35:
        predicted_phase = "Yellow"
    else:
        predicted_phase = "Green"
        
    st.write(f"**Predicted traffic light phase at arrival:** **{predicted_phase}** (Cycle time: {predicted_cycle_time:.1f} s)")

    # Provide advice based on the predicted phase
    if predicted_phase == "Green":
        advice = "Maintain your current speed to pass through the intersection on green."
    elif predicted_phase == "Yellow":
        advice = "You may receive a yellow light; consider slowing down slightly for a smoother passage."
    else:  # Red
        advice = "Reduce your speed to delay your arrival so you might catch a green light and avoid waiting."
    
    st.write(f"**Advice:** {advice}")

    # Attempt to suggest a recommended speed.  
    # We iterate over a range of speeds (from 20 to 120 km/h, step 5) to find one for which the predicted phase is green.
    speeds = np.arange(20, 121, 5)
    recommended_speed = None
    for s in speeds:
        arrival = distance / (s/3.6)
        pred_time = (current_cycle_time + arrival) % 60
        if pred_time >= 35:  # this implies arriving during green
            recommended_speed = s
            break
    if recommended_speed:
        st.write(f"**Suggested speed to catch a green light:** {recommended_speed} km/h")
    else:
        st.write("No recommended speed found in the tested range; consider adjusting your inputs manually.")

    # Voice alert: Using the browser's SpeechSynthesis API via JavaScript
    if st.button("Speak Advice"):
        st.components.v1.html(f"""
            <script>
                var msg = new SpeechSynthesisUtterance("{advice}");
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)
