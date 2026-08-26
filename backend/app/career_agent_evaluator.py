from typing import Any

from app.career_agent_state import (
    CareerAgentState,
)


# ============================================================
# CORE EVIDENCE TOOLS
# ============================================================


CORE_EVIDENCE_TOOLS = {
    "get_resume_context",
    "get_latest_job_match",
    "get_latest_skill_gap",
}


def evaluator_node(
    state: CareerAgentState,
) -> dict[str, Any]:
    """
    Evaluate the latest tool execution and decide whether
    the agent should:

    - continue to the next planned step,
    - request replanning,
    - or terminate safely.

    Deterministic conditions stay in Python instead of
    being delegated to the LLM.
    """

    iteration_count = state.get(
        "iteration_count",
        0,
    )

    max_iterations = state.get(
        "max_iterations",
        6,
    )

    plan = state.get(
        "plan",
        [],
    )

    current_step = state.get(
        "current_step",
        0,
    )

    tool_result = state.get(
        "tool_result"
    )

    completed_steps = list(
        state.get(
            "completed_steps",
            [],
        )
    )

    observations = state.get(
        "observations",
        [],
    )

    # ========================================================
    # 1. DETERMINE UNAVAILABLE CORE EVIDENCE TOOLS
    # ========================================================

    unavailable_tools: set[str] = set()

    for observation in observations:
        result = observation.get(
            "result",
            {},
        )

        tool_name = observation.get(
            "tool"
        )

        if not tool_name:
            continue

        if (
            result.get("success") is False
            or result.get("found") is False
        ):
            unavailable_tools.add(
                tool_name
            )

    # ========================================================
    # 2. NO VALID CORE EVIDENCE PATH REMAINS
    # ========================================================

    if CORE_EVIDENCE_TOOLS.issubset(
        unavailable_tools
    ):
        return {
            "task_complete": True,
            "needs_replanning": False,
            "replan_reason": None,

            "selected_tool": None,
            "tool_input": {},
            "tool_result": None,

            "run_outcome": "incomplete",

            "final_response": (
                "CareerPilot Agent could not complete "
                "this goal because no indexed resume "
                "context, saved Job Match analysis, "
                "or saved Skill Gap analysis is "
                "available for the selected resume."
            ),
        }

    # ========================================================
    # 3. ITERATION SAFETY LIMIT
    # ========================================================

    if iteration_count >= max_iterations:
        return {
            "task_complete": True,
            "needs_replanning": False,
            "replan_reason": None,

            "selected_tool": None,
            "tool_input": {},
            "tool_result": None,

            "run_outcome": "incomplete",

            "final_response": (
                "CareerPilot Agent stopped safely "
                "because the maximum execution-step "
                "limit was reached."
            ),
        }

    # ========================================================
    # 4. NO TOOL RESULT
    # ========================================================

    if tool_result is None:
        return {
            "needs_replanning": True,
            "task_complete": False,

            "replan_reason": (
                "The current execution step produced "
                "no tool result."
            ),

            "run_outcome": None,
        }

    # ========================================================
    # 5. TOOL EXECUTION FAILURE
    # ========================================================

    if not tool_result.get(
        "success",
        False,
    ):
        return {
            "needs_replanning": True,
            "task_complete": False,

            "replan_reason": (
                tool_result.get(
                    "message"
                )
                or tool_result.get(
                    "error"
                )
                or (
                    "The selected CareerPilot tool "
                    "failed during execution."
                )
            ),

            "run_outcome": None,
        }

    # ========================================================
    # 6. REQUIRED DATA NOT FOUND
    # ========================================================

    if (
        "found" in tool_result
        and tool_result.get(
            "found"
        ) is False
    ):
        return {
            "needs_replanning": True,
            "task_complete": False,

            "replan_reason": (
                tool_result.get(
                    "message"
                )
                or (
                    "The required persisted "
                    "CareerPilot evidence "
                    "was not found."
                )
            ),

            "run_outcome": None,
        }

    # ========================================================
    # 7. MARK CURRENT STEP COMPLETE
    # ========================================================

    if (
        0 <= current_step
        < len(plan)
    ):
        completed_step = plan[
            current_step
        ]

        if (
            completed_step
            not in completed_steps
        ):
            completed_steps.append(
                completed_step
            )

    next_step = (
        current_step + 1
    )

    # ========================================================
    # 8. ALL PLAN STEPS COMPLETE
    # ========================================================

    if next_step >= len(plan):
        return {
            "completed_steps":
                completed_steps,

            "current_step":
                next_step,

            "selected_tool":
                None,

            "tool_input":
                {},

            "tool_result":
                None,

            "needs_replanning":
                False,

            "replan_reason":
                None,

            "task_complete":
                True,

            "run_outcome":
                "completed",
        }

    # ========================================================
    # 9. CONTINUE TO NEXT STEP
    # ========================================================

    return {
        "completed_steps":
            completed_steps,

        "current_step":
            next_step,

        "selected_tool":
            None,

        "tool_input":
            {},

        "tool_result":
            None,

        "needs_replanning":
            False,

        "replan_reason":
            None,

        "task_complete":
            False,

        "run_outcome":
            None,
    }