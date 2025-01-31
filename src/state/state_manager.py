# src/state/state_manager.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import streamlit as st
import asyncio
import threading
from queue import Queue

@dataclass
class TravelPreferences:
    destination: str
    duration: int
    budget: str
    interests: List[str]

class AsyncStateManager:
    """Handles async state management operations"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AsyncStateManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        """Initialize async state manager"""
        self.activity_queue = Queue(maxsize=1000)
        self._stop_event = threading.Event()
        self._processor_thread = None

    def start_processing(self):
        """Start background processing of activities"""
        if self._processor_thread is None or not self._processor_thread.is_alive():
            self._stop_event.clear()
            self._processor_thread = threading.Thread(target=self._process_queue)
            self._processor_thread.daemon = True
            self._processor_thread.start()

    def stop_processing(self):
        """Stop background processing"""
        self._stop_event.set()
        if self._processor_thread:
            self._processor_thread.join(timeout=1.0)

    def _process_queue(self):
        """Process queued activities"""
        while not self._stop_event.is_set():
            try:
                while not self.activity_queue.empty():
                    activity = self.activity_queue.get_nowait()
                    StateManager.add_activity(activity)
                    self.activity_queue.task_done()
                threading.Event().wait(0.1)  # Prevent busy waiting
            except Exception as e:
                print(f"Error processing activity queue: {str(e)}")

class StateManager:
    """Manages application state using Streamlit session state"""
    
    _async_manager = None

    @classmethod
    def get_async_manager(cls) -> AsyncStateManager:
        """Get or create async state manager"""
        if cls._async_manager is None:
            cls._async_manager = AsyncStateManager()
        return cls._async_manager

    @staticmethod
    def initialize_session_state():
        """Initialize all required session state variables"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'agent_activities' not in st.session_state:
            st.session_state.agent_activities = []
        if 'feedback' not in st.session_state:
            st.session_state.feedback = []
        if 'async_mode' not in st.session_state:
            st.session_state.async_mode = False

        # Start async processing if needed
        if st.session_state.async_mode:
            StateManager.get_async_manager().start_processing()

    @staticmethod
    def enable_async_mode():
        """Enable async processing mode"""
        st.session_state.async_mode = True
        StateManager.get_async_manager().start_processing()

    @staticmethod
    def disable_async_mode():
        """Disable async processing mode"""
        st.session_state.async_mode = False
        StateManager.get_async_manager().stop_processing()

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

    @classmethod
    async def add_activity_async(cls, activity: Dict[str, Any]):
        """Add an agent activity asynchronously"""
        if st.session_state.async_mode:
            async_manager = cls.get_async_manager()
            async_manager.activity_queue.put(activity)
        else:
            cls.add_activity(activity)

    @staticmethod
    def get_activities() -> List[Dict[str, Any]]:
        """Get all agent activities"""
        return st.session_state.get('agent_activities', [])

    @staticmethod
    def get_messages() -> List[Dict[str, str]]:
        """Get all messages"""
        return st.session_state.get('messages', [])
    
    @staticmethod
    def add_message_safe(role: str, content: str):
        """Thread-safe message addition using queue"""
        if not hasattr(StateManager, '_message_queue'):
            StateManager._message_queue = Queue()
        StateManager._message_queue.put({
            "role": role,
            "content": content
        })

    @staticmethod
    def process_pending_messages():
        """Process any pending messages in the queue"""
        if hasattr(StateManager, '_message_queue'):
            while not StateManager._message_queue.empty():
                try:
                    message = StateManager._message_queue.get_nowait()
                    if 'messages' not in st.session_state:
                        st.session_state.messages = []
                    st.session_state.messages.append(message)
                except Empty:
                    break