# src/agents/tracking/activity_tracker.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ActivityTracker(ABC):
    @abstractmethod
    def track_activity(self, activity: Dict[str, Any]):
        pass
    
    @abstractmethod
    def get_activities(self) -> List[Dict[str, Any]]:
        pass

class StreamlitActivityTracker(ActivityTracker):
    def track_activity(self, activity: Dict[str, Any]):
        import streamlit as st
        if 'agent_activities' not in st.session_state:
            st.session_state.agent_activities = []
        st.session_state.agent_activities.append(activity)
    
    def get_activities(self) -> List[Dict[str, Any]]:
        import streamlit as st
        return st.session_state.get('agent_activities', [])