# src/ui/components/main.py
import streamlit as st
from typing import List, Dict, Any
import time
import streamlit as st
from typing import Tuple, List
from src.ui.components.activity_thread import render_activity_thread

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
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Plan My Trip")
        with col2:
            async_mode = st.checkbox("Enable real-time updates", 
                                   value=st.session_state.get('async_mode', False),
                                   key='async_mode_toggle')
            
        if async_mode != st.session_state.get('async_mode', False):
            st.session_state.async_mode = async_mode
            if 'agent_activities' not in st.session_state:
                st.session_state.agent_activities = []
            st.rerun()
            
    return submitted, destination, duration, budget, interests


def render_activities():
    """Render the agent activities thread."""
    if 'agent_activities' not in st.session_state:
        st.session_state.agent_activities = []
    
    render_activity_thread()

def render_final_plan():
    """Render the final travel plan."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
    if st.session_state.messages:
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