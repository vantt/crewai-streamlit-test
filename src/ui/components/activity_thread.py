# src/ui/components/activity_thread.py
import streamlit as st
from typing import List, Dict, Any
import time
from src.agents.async_tracked_agent import AsyncActivityEmitter

def render_activity_thread() -> None:
    """Render the agent activities thread.
    
    Args:
        activities: List of activity dictionaries containing agent messages and metadata
    """
    st.subheader("Agent Chat Thread")
        
     # Update activities from queue
    update_activities()
    
    # Create a container for activities
    activities_container = st.empty()
    
    # Sort activities by timestamp
    sorted_activities = sorted(
        st.session_state.agent_activities,
        key=lambda x: x.get("timestamp", 0)
    )

    # Render in container for efficient updates
    with activities_container.container():
        for activity in sorted_activities:
            with st.chat_message(activity["agent"].lower()):
                display_activity(activity)
    
    # Auto-refresh while processing
    if st.session_state.get('processing', False):
        time.sleep(0.1)  # Small delay to prevent too frequent updates
        st.rerun()

def update_activities():
    """Update activities from the queue to session state"""
    if 'agent_activities' not in st.session_state:
        st.session_state.agent_activities = []
        
    # Get pending activities from the queue
    new_activities = AsyncActivityEmitter.get_pending_activities()
    if new_activities:
        st.session_state.agent_activities.extend(new_activities)

def display_activity(activity: Dict[str, Any]):
    """Display a single activity with appropriate formatting."""
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