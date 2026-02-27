from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from app.schemas.lead_schema import (
    Action,
    ActionOutput,
    LeadBehavior,
    ProfilingOutput,
)


@CrewBase
class AgentService:

    agents_config = "../core/agents.yaml"
    tasks_config = "../core/tasks.yaml"

    @agent
    def profiling_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["profiling_agent"],
            verbose=True,
        )

    @agent
    def action_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["action_agent"],
            verbose=True,
        )

    @task
    def profiling_task(self) -> Task:
        return Task(
            config=self.tasks_config["profiling_task"],
            output_pydantic=ProfilingOutput,
        )

    @task
    def action_task(self) -> Task:
        return Task(
            config=self.tasks_config["action_task"],
            context=[self.profiling_task()],
            output_pydantic=ActionOutput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.profiling_agent(),
                self.action_agent(),
            ],
            tasks=[
                self.profiling_task(),
                self.action_task(),
            ],
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )

    def run_agent(
        self, lead_behavior: LeadBehavior
    ) -> tuple[ProfilingOutput, list[Action]]:
        result = self.crew().kickoff(inputs={"behavior": lead_behavior})
        profile = result.tasks_output[0].pydantic
        action_output = result.tasks_output[1].pydantic
        return profile, action_output.actions
