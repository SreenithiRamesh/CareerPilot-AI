from typing import Any

from app.agent_tools import (
    get_latest_job_match,
    get_latest_skill_gap,
    get_resume_context,
    generate_career_plan,
    prepare_interview_focus,
    recommend_project,
)
from app.career_agent_state import (
    CareerAgentState,
)


# ============================================================
# SAFE TOOL REGISTRY
# ============================================================


TOOL_REGISTRY = {
    "get_resume_context":
        get_resume_context,

    "get_latest_job_match":
        get_latest_job_match,

    "get_latest_skill_gap":
        get_latest_skill_gap,

    "generate_career_plan":
        generate_career_plan,

    "recommend_project":
        recommend_project,

    "prepare_interview_focus":
        prepare_interview_focus,
}


# ============================================================
# TOOL EXECUTOR NODE
# ============================================================


def tool_executor_node(
    state: CareerAgentState,
) -> dict[str, Any]:
    """
    Execute the tool selected by the selector node.

    This node:
    - validates the tool name,
    - executes only registered CareerPilot tools,
    - stores the tool result,
    - records an observation,
    - increments the iteration counter.
    """

    selected_tool = state.get(
        "selected_tool"
    )

    tool_input = state.get(
        "tool_input",
        {},
    )

    if not selected_tool:
        return {
            "tool_result": None,
            "needs_replanning": True,
        }

    tool = TOOL_REGISTRY.get(
        selected_tool
    )

    if tool is None:
        raise ValueError(
            "Unsupported CareerPilot agent tool: "
            f"{selected_tool}"
        )

    current_step_index = state.get(
        "current_step",
        0,
    )

    plan = state.get(
        "plan",
        [],
    )

    current_step = (
        plan[current_step_index]
        if (
            0 <= current_step_index
            < len(plan)
        )
        else None
    )

    try:
        result = tool.invoke(
            tool_input
        )

    except Exception as exc:
        result = {
            "success": False,
            "error": "tool_execution_failed",
            "tool": selected_tool,
            "message": str(exc),
        }

    observation = {
        "step_index":
            current_step_index,

        "step":
            current_step,

        "tool":
            selected_tool,

        "tool_input":
            tool_input,

        "result":
            result,
    }

    previous_observations = (
        state.get(
            "observations",
            [],
        )
    )

    new_observations = [
        *previous_observations,
        observation,
    ]

    return {
        "tool_result":
            result,

        "observations":
            new_observations,

        "iteration_count":
            state.get(
                "iteration_count",
                0,
            )
            + 1,
    }