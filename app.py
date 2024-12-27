# app.py
import streamlit as st
from crewai import Task, Crew
from src.config.settings import OPENAI_API_KEY
from src.agents.travel_agents import create_travel_agents
from src.ui.components import (
    render_travel_form,
    render_activities,
    render_final_plan,
    render_feedback
)
from src.ui.session import initialize_session_state

def main():
    st.title("Travel Planning Assistant")
    
    # Check for API key
    if not OPENAI_API_KEY:
        st.error("OpenAI API key not found. Please set it in your .env file.")
        st.stop()

    # Initialize session state
    initialize_session_state()
    
    # Render travel preferences form
    submitted, destination, duration, budget, interests = render_travel_form()

    if submitted:
        st.session_state.agent_activities = []  # Clear previous activities
        
        # Create agents
        travel_planner, local_expert = create_travel_agents()
        
        # Create tasks
        planning_task = Task(
            description=f"Create a {duration}-day {budget} travel plan for {destination} focusing on {', '.join(interests)}",
            expected_output="A detailed day-by-day travel itinerary",
            agent=travel_planner
        )

        review_task = Task(
            description="Review and enhance the travel plan with local insights",
            expected_output="Enhanced plan with local recommendations and their detailed address/contact",
            agent=local_expert
        )

        # Create and execute crew
        crew = Crew(
            agents=[travel_planner, local_expert],
            tasks=[planning_task, review_task],
            verbose=True
        )

        with st.spinner("Creating your travel plan..."):
            try:
                result = crew.kickoff()
                st.session_state.messages.append({"role": "assistant", "content": result})
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Render UI components
    render_activities()
    render_final_plan()
    render_feedback()

if __name__ == "__main__":
    main()