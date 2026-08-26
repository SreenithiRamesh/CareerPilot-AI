from typing import Any

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    resume_id: int = Field(
        gt=0,
    )

    thread_id: str | None = None

    goal: str = Field(
        min_length=1,
        max_length=5000,
    )

    max_iterations: int = Field(
        default=6,
        ge=1,
        le=12,
    )


class AgentStepResponse(BaseModel):
    step_number: int

    planned_action: str

    tool_name: str | None = None

    tool_input: dict[str, Any] = Field(
        default_factory=dict
    )

    result: dict[str, Any] = Field(
        default_factory=dict
    )


class AgentRunResponse(BaseModel):
    agent_run_id: int | None = None

    resume_id: int

    thread_id: str | None = None

    goal: str

    plan: list[str] = Field(
        default_factory=list
    )

    completed_steps: list[str] = Field(
        default_factory=list
    )

    executed_steps: list[
        AgentStepResponse
    ] = Field(
        default_factory=list
    )

    iterations: int

    run_outcome: str | None = None

    task_complete: bool

    final_response: str | None = None