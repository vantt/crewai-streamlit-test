# src/ui/components.py
import streamlit as st
from typing import Tuple, List

def render_travel_form() -> Tuple[bool, str, int, str, List[str]]:
    """Render the travel preferences form."""
    with st.form("travel_preferences"):
        destination = st.text_input("Destination", key="destination_input")
        duration = st.number_input("Duration (days)", min_value=1, max_value=30, key="duration_input")
        budget = st.selectbox("Budget", ["Budget", "Moderate", "Luxury"], key="budget_input")
        interests = st.multiselect(
            "Interests", 
            ["Culture", "Nature", "Food", "Adventure"],
            key="interests_input"
        )
        submitted = st.form_submit_button("Plan My Trip")
        
    return submitted, destination, duration, budget, interests

def render_activities():
    """Render the agent activities thread."""
    st.subheader("Agent Chat Thread")
    
    if 'agent_activities' not in st.session_state:
        st.session_state.agent_activities = []
        
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
    if 'messages' in st.session_state and st.session_state.messages:
        st.subheader("Final Travel Plan")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

def render_feedback():
    """Render the feedback form."""
    if 'messages' in st.session_state and st.session_state.messages:
        with st.form("feedback_form"):
            rating = st.slider(
                "Rate the plan (1-5)", 
                1, 5, 3, 
                key="feedback_rating"
            )
            feedback = st.text_area(
                "Any comments?",
                key="feedback_text"
            )
            submit_feedback = st.form_submit_button("Submit Feedback")
            
            if submit_feedback:
                st.success("Thank you for your feedback!")
                if 'feedback' not in st.session_state:
                    st.session_state.feedback = []
                st.session_state.feedback.append({
                    "rating": rating,
                    "comment": feedback
                })