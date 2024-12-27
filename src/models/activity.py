# src/models/activity.py
from typing import Literal, Dict, Any
import time

class Activity:
    def __init__(self, agent_role: str, content: str, activity_type: Literal["info", "success", "error"] = "info"):
        self.type = activity_type
        self.agent = agent_role
        self.content = content
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "agent": self.agent,
            "content": self.content,
            "timestamp": self.timestamp
        }