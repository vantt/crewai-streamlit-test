# src/agents/async_tracked_agent.py
from typing import Optional, Any, Dict
import asyncio
import queue
import threading
from crewai import Agent
from ..models.activity import Activity
from ..state.state_manager import StateManager

class AsyncActivityEmitter:
    """Handles async emission of activities to state manager"""
    _instance = None
    _lock = threading.Lock()
    _global_queue = queue.Queue(maxsize=1000)
    
    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        self._stop_event = threading.Event()

    @classmethod
    def add_activity(cls, activity: Dict[str, Any]):
        """Thread-safe activity addition"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in activity:
                activity['timestamp'] = time.time()
            cls._global_queue.put(activity)
        except Exception as e:
            print(f"Error adding activity to queue: {str(e)}")

    @classmethod
    def get_pending_activities(cls) -> list:
        """Get all pending activities"""
        activities = []
        try:
            while not cls._global_queue.empty():
                activities.append(cls._global_queue.get_nowait())
        except queue.Empty:
            pass
        return activities

    def stop_processing(self):
        """Stops the background processing"""
        self._stop_event.set()

class AsyncTrackedAgent(Agent):
    """Agent that supports both synchronous and asynchronous activity tracking"""
    
    def __init__(self, role: str, goal: str, backstory: str, **kwargs):
        # First initialize the parent Agent class
        super().__init__(role=role, goal=goal, backstory=backstory, **kwargs)
        # Then initialize our AsyncActivityEmitter
        self._activity_emitter = None
        self._initialize_emitter()

    def _initialize_emitter(self):
        """Initialize the activity emitter if not already done"""
        if self._activity_emitter is None:
            self._activity_emitter = AsyncActivityEmitter.get_instance()

    @property
    def activity_emitter(self):
        """Property to ensure activity emitter is always initialized"""
        self._initialize_emitter()
        return self._activity_emitter

    async def _add_activity_async(self, content: str, activity_type: str = "info"):
        """Adds activity asynchronously"""
        activity = Activity(self.role, content, activity_type)
        self.activity_emitter.add_activity(activity.to_dict())

    def _add_activity(self, content: str, activity_type: str = "info"):
        """Synchronous activity addition"""
        activity = Activity(self.role, content, activity_type)
        self.activity_emitter.add_activity(activity.to_dict())

    async def execute_task_async(self, task, context=None, tools=None):
        """Asynchronous task execution with activity tracking"""
        await self._add_activity_async(f"🎯 Starting task: {task.description}")
        try:
            # Execute the task using sync method since CrewAI's execute_task isn't async
            result = self.execute_task(task, context=context, tools=tools)
            chunks = [result[i:i+800] for i in range(0, len(result), 800)]
            for i, chunk in enumerate(chunks):
                prefix = "✅ Output (continued):\n" if i > 0 else "✅ Task output:\n"
                await self._add_activity_async(
                    f"{prefix}{chunk}", 
                    "success" if i == len(chunks)-1 else "info"
                )
            return result
        except Exception as e:
            await self._add_activity_async(f"❌ Error executing task: {str(e)}", "error")
            raise

    def execute_task(self, task, context=None, tools=None):
        """Synchronous task execution with activity tracking"""
        self._add_activity(f"🎯 Starting task: {task.description}")
        try:
            result = super().execute_task(task, context=context, tools=tools)
            chunks = [result[i:i+800] for i in range(0, len(result), 800)]
            for i, chunk in enumerate(chunks):
                prefix = "✅ Output (continued):\n" if i > 0 else "✅ Task output:\n"
                self._add_activity(
                    f"{prefix}{chunk}", 
                    "success" if i == len(chunks)-1 else "info"
                )
            return result
        except Exception as e:
            self._add_activity(f"❌ Error executing task: {str(e)}", "error")
            raise

    def __del__(self):
        """Cleanup resources on deletion"""
        if hasattr(self, '_activity_emitter') and self._activity_emitter:
            self._activity_emitter.stop_processing()