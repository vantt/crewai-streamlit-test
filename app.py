# app.py
import streamlit as st
from crewai import Crew

from src.config.config_manager import ConfigurationManager
from src.state.state_manager import StateManager, TravelPreferences
from src.agents.travel_agents import create_travel_agents
from src.tasks.travel_tasks import TravelTaskManager
from src.utils.error_handler import handle_error
from src.ui.components import (
    render_travel_form,
    render_activities,
    render_final_plan,
    render_feedback
)

@handle_error("Failed to initialize application")
def initialize_app():
    """Initialize application configuration and state"""
    config = ConfigurationManager.load_config()
    if not ConfigurationManager.validate_config(config):
        st.error("Invalid configuration. Please check your environment variables.")
        st.stop()
    return config

@handle_error("Failed to process travel plan")
def process_travel_plan(preferences: TravelPreferences, config):
    """Process travel plan with crew AI"""
    # Create agents
    agents = create_travel_agents()
    
    # Create tasks
    tasks = TravelTaskManager.create_travel_tasks(
        agents=agents,
        destination=preferences.destination,
        duration=preferences.duration,
        budget=preferences.budget,
        interests=preferences.interests
    )
    
    # Create and execute crew
    crew = Crew(
        agents=list(agents),
        tasks=tasks,
        verbose=config.debug_mode
    )
    
    return crew.kickoff()

def main():
    st.title("Travel Planning Assistant")
    
    # Initialize application
    config = initialize_app()
    StateManager.initialize_session_state()
    
    # Render travel preferences form
    submitted, destination, duration, budget, interests = render_travel_form()

    if submitted and destination and interests:  # Add validation
        # Clear previous activities
        StateManager.clear_activities()
        
        # Create preferences object
        preferences = TravelPreferences(
            destination=destination,
            duration=duration,
            budget=budget,
            interests=interests
        )
        
        with st.spinner("Creating your travel plan..."):
            result = process_travel_plan(preferences, config)
            if result:
                StateManager.add_message("assistant", result)

    # Render UI components
    render_activities()
    render_final_plan()
    render_feedback()

if __name__ == "__main__":
    main()