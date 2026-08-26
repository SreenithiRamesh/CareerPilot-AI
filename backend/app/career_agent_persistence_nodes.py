from typing import Any

from app.career_agent_state import (
    CareerAgentState,
)
from app.services.agent_persistence_service import (
    complete_agent_run,
    fail_agent_run,
    incomplete_agent_run,
    save_agent_step,
    start_agent_run,
)


# ============================================================
# START RUN
# ============================================================


def start_run_node(
    state: CareerAgentState,
) -> dict[str, Any]:
    """
    Create the persistent AgentRun before
    autonomous execution begins.
    """

    run_id = start_agent_run(
        user_id=state["user_id"],
        resume_id=state["resume_id"],
        thread_id=state.get(
            "thread_id"
        ),
        goal=state["user_goal"],
    )

    return {
        "agent_run_id": run_id,
    }


# ============================================================
# PERSIST EXECUTION STEP
# ============================================================


def persist_step_node(
    state: CareerAgentState,
) -> dict[str, Any]:
    """
    Persist the latest autonomous execution step.

    Each tool execution becomes an AgentStep record
    linked to the current AgentRun.
    """

    run_id = state.get(
        "agent_run_id"
    )

    if run_id is None:
        raise ValueError(
            "agent_run_id is missing."
        )

    observations = state.get(
        "observations",
        [],
    )

    if not observations:
        return {}

    observation = observations[-1]

    result = observation.get(
        "result",
        {},
    )

    # --------------------------------------------------------
    # Determine persisted step status
    # --------------------------------------------------------

    if result.get(
        "success"
    ) is False:
        step_status = "failed"

    elif (
        "found" in result
        and result.get(
            "found"
        ) is False
    ):
        # Tool itself executed correctly,
        # but the requested persisted resource
        # was unavailable.
        step_status = "incomplete"

    else:
        step_status = "completed"

    save_agent_step(
        agent_run_id=run_id,

        step_number=(
            observation.get(
                "step_index",
                0,
            )
            + 1
        ),

        planned_action=(
            observation.get(
                "step"
            )
            or "Unknown agent action"
        ),

        tool_name=observation.get(
            "tool"
        ),

        tool_input=observation.get(
            "tool_input"
        ),

        observation=result,

        status=step_status,
    )

    return {}


# ============================================================
# COMPLETE RUN
# ============================================================


def complete_run_node(
    state: CareerAgentState,
) -> dict[str, Any]:
    """
    Persist a successfully completed autonomous run.

    This path is used only when the user's goal was
    successfully satisfied.
    """

    run_id = state.get(
        "agent_run_id"
    )

    if run_id is None:
        return {}

    complete_agent_run(
        agent_run_id=run_id,

        final_response=(
            state.get(
                "final_response"
            )
            or ""
        ),

        iterations=state.get(
            "iteration_count",
            0,
        ),
    )

    return {}


# ============================================================
# INCOMPLETE RUN
# ============================================================


def incomplete_run_node(
    state: CareerAgentState,
) -> dict[str, Any]:
    """
    Persist a safely terminated but incomplete run.

    This path is used when CareerPilot could not fully
    satisfy the user's goal because required evidence
    or prerequisites were unavailable.

    Examples:
    - no indexed resume context
    - no saved Job Match
    - no saved Skill Gap
    - maximum iteration limit reached
    """

    run_id = state.get(
        "agent_run_id"
    )

    if run_id is None:
        return {}

    incomplete_agent_run(
        agent_run_id=run_id,

        final_response=(
            state.get(
                "final_response"
            )
            or (
                "CareerPilot Agent could not fully "
                "complete the requested goal because "
                "required evidence was unavailable."
            )
        ),

        iterations=state.get(
            "iteration_count",
            0,
        ),
    )

    return {}


# ============================================================
# FAILED RUN
# ============================================================


def fail_run_node(
    state: CareerAgentState,
) -> dict[str, Any]:
    """
    Persist an unrecoverably failed autonomous run.

    This path should be reserved for real execution
    or system failures rather than missing data.
    """

    run_id = state.get(
        "agent_run_id"
    )

    if run_id is None:
        return {}

    fail_agent_run(
        agent_run_id=run_id,

        error_message=(
            state.get(
                "final_response"
            )
            or (
                "CareerPilot Agent encountered an "
                "unrecoverable execution error."
            )
        ),

        iterations=state.get(
            "iteration_count",
            0,
        ),
    )

    return {}