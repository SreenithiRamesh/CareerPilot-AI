import json
from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


# ============================================================
# AGENT RUN HISTORY
# ============================================================


class AgentRunHistoryItem(BaseModel):
    id: int
    resume_id: int

    thread_id: str | None = None

    goal: str
    status: str

    iterations: int

    created_at: datetime
    completed_at: datetime | None = None


class AgentRunHistoryResponse(BaseModel):
    runs: list[AgentRunHistoryItem]

    total: int


# ============================================================
# AGENT STEP DETAIL
# ============================================================


class AgentStepDetail(BaseModel):
    id: int

    step_number: int

    planned_action: str

    tool_name: str | None = None

    tool_input: dict[str, Any] | None = None

    observation: dict[str, Any] | None = None

    status: str

    created_at: datetime

    @field_validator(
        "tool_input",
        "observation",
        mode="before",
    )
    @classmethod
    def parse_json_fields(
        cls,
        value: Any,
    ) -> Any:
        """
        AgentStep stores tool_input and observation
        as serialized JSON inside MySQL TEXT columns.

        Convert them back into dictionaries before
        returning them through the API.
        """

        if value is None:
            return None

        if isinstance(
            value,
            dict,
        ):
            return value

        if isinstance(
            value,
            str,
        ):
            try:
                parsed = json.loads(
                    value
                )

                if isinstance(
                    parsed,
                    dict,
                ):
                    return parsed

            except json.JSONDecodeError:
                return {
                    "raw": value,
                }

        return {
            "raw": str(value),
        }


# ============================================================
# AGENT RUN DETAIL
# ============================================================


class AgentRunDetailResponse(BaseModel):
    id: int

    resume_id: int

    thread_id: str | None = None

    goal: str

    status: str

    iterations: int

    final_response: str | None = None

    created_at: datetime

    completed_at: datetime | None = None

    steps: list[AgentStepDetail] = Field(
        default_factory=list
    )

    total_steps: int