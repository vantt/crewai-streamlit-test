# app.py
import streamlit as st
from crewai import Crew
import asyncio

from src.config.config_manager import ConfigurationManager
from src.state.state_manager import StateManager, TravelPreferences
from src.agents.travel_agents import create_async_travel_agents, create_travel_agents
from src.tasks.travel_tasks import TravelTaskManager
from src.utils.error_handler import handle_error
from src.utils.async_helpers import AsyncToSync, run_coroutine_in_thread
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

async def process_task_async(agent, task):
    """Process a single task asynchronously"""
    await agent._add_activity_async(f"🎯 Starting task: {task.description}")
    try:
        # Use regular execute_task since CrewAI doesn't support async execution
        result = agent.execute_task(task)
        chunks = [result[i:i+800] for i in range(0, len(result), 800)]
        for i, chunk in enumerate(chunks):
            prefix = "✅ Output (continued):\n" if i > 0 else "✅ Task output:\n"
            await agent._add_activity_async(f"{prefix}{chunk}", 
                                         "success" if i == len(chunks)-1 else "info")
        return result
    except Exception as e:
        await agent._add_activity_async(f"❌ Error executing task: {str(e)}", "error")
        raise

async def process_travel_plan_async(preferences: TravelPreferences, config):
    try:
        # Create agents
        travel_planner, local_expert = create_async_travel_agents()
        
        # Create tasks
        tasks = TravelTaskManager.create_travel_tasks(
            agents=(travel_planner, local_expert),
            destination=preferences.destination,
            duration=preferences.duration,
            budget=preferences.budget,
            interests=preferences.interests
        )

        # Process first task and store result
        planner_task = tasks[0]
        planner_result = await process_task_async(planner_task.agent, planner_task)
        
        # Pass result to local expert
        expert_task = tasks[1]
        expert_task.context = planner_result  # Add context from previous task
        final_result = await process_task_async(expert_task.agent, expert_task)

        return final_result

    except Exception as e:
        st.error(f"Error in async processing: {str(e)}")
        raise

def process_travel_plan_sync(preferences: TravelPreferences, config):
    """Process travel plan synchronously"""
    try:
        # Create agents
        travel_planner, local_expert = create_travel_agents()
        
        # Create tasks
        tasks = TravelTaskManager.create_travel_tasks(
            agents=(travel_planner, local_expert),
            destination=preferences.destination,
            duration=preferences.duration,
            budget=preferences.budget,
            interests=preferences.interests
        )
        
        # Create and execute crew
        crew = Crew(
            agents=[travel_planner, local_expert],
            tasks=tasks,
            verbose=config.debug_mode
        )
        return crew.kickoff()

    except Exception as e:
        st.error(f"Error in sync processing: {str(e)}")
        raise

def main():
    st.title("Travel Planning Assistant")
    
    # Initialize application
    config = initialize_app()
    StateManager.initialize_session_state()
    
    # Initialize messages if not exists
    if 'messages' not in st.session_state:
        st.session_state.messages = []

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
        
        # Instead of using create_task directly, use run_coroutine_in_thread
        try:
            # Start processing in background
            st.session_state.processing = True
            
            def background_task():
                try:
                    result = run_coroutine_in_thread(
                        process_travel_plan_async(preferences, config)
                    )
                    # Use thread-safe message addition
                    if result:
                        StateManager.add_message_safe("assistant", result)
                    st.session_state.processing = False
                except Exception as e:
                    print(f"Error in background task: {str(e)}")

            # Run in a thread to not block Streamlit
            import threading
            thread = threading.Thread(target=background_task)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            st.error(f"Error starting processing: {str(e)}")
            st.session_state.processing = False

    # Process any pending messages
    StateManager.process_pending_messages()

    # Render UI components
    render_activities()
    render_final_plan()
    render_feedback()

if __name__ == "__main__":
    main()