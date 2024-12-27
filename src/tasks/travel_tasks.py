# src/tasks/travel_tasks.py
from typing import List, Tuple
from crewai import Task, Agent

class TravelTaskManager:
    @staticmethod
    def create_travel_tasks(
        agents: Tuple[Agent, Agent],
        destination: str,
        duration: int,
        budget: str,
        interests: List[str]
    ) -> List[Task]:
        travel_planner, local_expert = agents
        
        tasks = [
            Task(
                description=f"Create a {duration}-day {budget} travel plan for {destination} focusing on {', '.join(interests)}",
                expected_output="A detailed day-by-day travel itinerary",
                agent=travel_planner
            ),
            Task(
                description="Review and enhance the travel plan with local insights",
                expected_output="Enhanced plan with local recommendations and their detailed address/contact",
                agent=local_expert
            )
        ]
        return tasks

    @staticmethod
    def create_custom_task(agent: Agent, description: str, expected_output: str) -> Task:
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent
        )