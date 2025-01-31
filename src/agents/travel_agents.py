# src/agents/travel_agents.py
from typing import Optional, Tuple
from langchain_openai import ChatOpenAI
from .base import TrackedAgent
from .async_tracked_agent import AsyncTrackedAgent
from ..config.settings import OPENAI_API_KEY, OPENAI_API_BASE

def create_travel_agents() -> Tuple[TrackedAgent, TrackedAgent]:
    """Create synchronous travel agents"""
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_API_BASE if OPENAI_API_BASE else None
    )

    travel_planner = TrackedAgent(
        role='Travel Planner',
        goal='Create detailed travel plans based on preferences',
        backstory='Expert travel planner with years of experience in crafting personalized itineraries',
        verbose=True,
        llm=llm
    )

    local_expert = TrackedAgent(
        role='Local Expert',
        goal='Enhance travel plans with local insights',
        backstory='Local expert with deep knowledge of destinations and hidden gems',
        verbose=True,
        llm=llm
    )

    return travel_planner, local_expert

def create_async_travel_agents() -> Tuple[AsyncTrackedAgent, AsyncTrackedAgent]:
    """Create asynchronous travel agents"""
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_API_BASE if OPENAI_API_BASE else None
    )

    travel_planner = AsyncTrackedAgent(
        role='Travel Planner',
        goal='Create detailed travel plans based on preferences',
        backstory='Expert travel planner with years of experience in crafting personalized itineraries',
        verbose=True,
        llm=llm
    )

    local_expert = AsyncTrackedAgent(
        role='Local Expert',
        goal='Enhance travel plans with local insights',
        backstory='Local expert with deep knowledge of destinations and hidden gems',
        verbose=True,
        llm=llm
    )

    return travel_planner, local_expert