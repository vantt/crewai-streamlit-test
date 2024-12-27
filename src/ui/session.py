# src/ui/session.py
import streamlit as st
from typing import Dict, List, Any

def initialize_session_state():
    """Initialize the session state with required variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages: List[Dict[str, str]] = []
    if 'agent_activities' not in st.session_state:
        st.session_state.agent_activities: List[Dict[str, Any]] = []