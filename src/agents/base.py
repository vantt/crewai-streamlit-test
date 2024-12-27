# src/agents/base.py
from crewai import Agent
from ..models.activity import Activity
from typing import Optional, Any

class TrackedAgent(Agent):
    def execute_task(self, task, context=None, tools=None):
        self._add_activity(f"🎯 Starting task: {task.description}")
        try:
            result = super().execute_task(task, context=context, tools=tools)
            # Split result into smaller chunks if it's too long
            chunks = [result[i:i+800] for i in range(0, len(result), 800)]
            for i, chunk in enumerate(chunks):
                prefix = "✅ Output (continued):\n" if i > 0 else "✅ Task output:\n"
                self._add_activity(f"{prefix}{chunk}", "success" if i == len(chunks)-1 else "info")
            return result
        except Exception as e:
            self._add_activity(f"❌ Error executing task: {str(e)}", "error")
            raise

    def _add_activity(self, content: str, activity_type: str = "info"):
        """Helper method to add activities to session state."""
        import streamlit as st
        activity = Activity(self.role, content, activity_type)
        if 'agent_activities' not in st.session_state:
            st.session_state.agent_activities = []
        st.session_state.agent_activities.append(activity.to_dict())