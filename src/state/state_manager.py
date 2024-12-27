# src/state/state_manager.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import streamlit as st

@dataclass
class TravelPreferences:
    destination: str
    duration: int
    budget: str
    interests: List[str]

class StateManager:
    @staticmethod
    def initialize_session_state():
        """Initialize all required session state variables"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'agent_activities' not in st.session_state:
            st.session_state.agent_activities = []
        if 'feedback' not in st.session_state:
            st.session_state.feedback = []

    @staticmethod
    def clear_activities():
        """Clear agent activities"""
        st.session_state.agent_activities = []

    @staticmethod
    def add_message(role: str, content: str):
        """Add a message to the conversation"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({
            "role": role,
            "content": content
        })

    @staticmethod
    def add_activity(activity: Dict[str, Any]):
        """Add an agent activity"""
        if 'agent_activities' not in st.session_state:
            st.session_state.agent_activities = []
        st.session_state.agent_activities.append(activity)

    @staticmethod
    def get_activities():
        """Get all agent activities"""
        return st.session_state.get('agent_activities', [])

    @staticmethod
    def get_messages():
        """Get all messages"""
        return st.session_state.get('messages', [])

    @staticmethod
    def get_feedback():
        """Get all feedback"""
        return st.session_state.get('feedback', [])