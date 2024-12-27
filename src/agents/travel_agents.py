# src/agents/travel_agents.py
from typing import Optional, Tuple
from langchain_openai import ChatOpenAI
from .base import TrackedAgent
from ..config.settings import OPENAI_API_KEY, OPENAI_API_BASE

def create_travel_agents(llm: Optional[ChatOpenAI] = None) -> Tuple[TrackedAgent, TrackedAgent]:
    if llm is None:
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_API_BASE if OPENAI_API_BASE else None
        )

    travel_planner = TrackedAgent(
        role='Travel Planner',
        goal='Create travel plans based on preferences',
        backstory='Expert travel planner with years of experience',
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

    local_expert = TrackedAgent(
        role='Local Expert',
        goal='Enhance plans with local insights',
        backstory='Local expert with destination knowledge',
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

    return travel_planner, local_expert