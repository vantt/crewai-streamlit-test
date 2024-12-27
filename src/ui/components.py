# src/ui/components.py
import streamlit as st

def render_travel_form():
    """Render the travel preferences form."""
    with st.form("travel_preferences"):
        destination = st.text_input("Destination")
        duration = st.number_input("Duration (days)", min_value=1, max_value=30)
        budget = st.selectbox("Budget", ["Budget", "Moderate", "Luxury"])
        interests = st.multiselect("Interests", ["Culture", "Nature", "Food", "Adventure"])
        submitted = st.form_submit_button("Plan My Trip")
        
    return submitted, destination, duration, budget, interests

def render_activities():
    """Render the agent activities thread."""
    st.subheader("Agent Chat Thread")
    
    activities = sorted(
        st.session_state.agent_activities,
        key=lambda x: x.get("timestamp", 0)
    )

    for activity in activities:
        with st.chat_message(activity["agent"].lower()):
            if activity["type"] == "error":
                st.error(activity["content"])
            elif activity["type"] == "success":
                st.success(activity["content"])
            elif "output" in activity["content"].lower():
                if "Travel Planner" in activity["agent"]:
                    st.info(activity["content"])
                elif "Local Expert" in activity["agent"]:
                    st.success(activity["content"])
                else:
                    st.write(activity["content"])
            else:
                st.write(activity["content"])

def render_final_plan():
    """Render the final travel plan."""
    if st.session_state.messages:
        st.subheader("Final Travel Plan")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

def render_feedback():
    """Render the feedback form."""
    if st.session_state.messages:
        with st.form("feedback"):
            rating = st.slider("Rate the plan (1-5)", 1, 5, 3)
            feedback = st.text_area("Any comments?")
            if st.form_submit_button("Submit Feedback"):
                st.success("Thank you for your feedback!")