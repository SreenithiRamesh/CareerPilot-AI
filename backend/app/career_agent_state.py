from typing import Annotated, Any

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


DEFAULT_MAX_ITERATIONS = 6


class CareerAgentState(TypedDict):
    # =========================================================
    # AUTHENTICATED CONTEXT
    # =========================================================

    user_id: int
    resume_id: int
    thread_id: str | None

    # Persistent database ID for the current autonomous run.
    agent_run_id: int | None

    # =========================================================
    # USER GOAL
    # =========================================================

    user_goal: str

    # =========================================================
    # CONVERSATION
    # =========================================================

    messages: Annotated[
        list[AnyMessage],
        add_messages,
    ]

    # =========================================================
    # AGENT PLAN
    # =========================================================

    plan: list[str]
    current_step: int
    completed_steps: list[str]

    # =========================================================
    # TOOL EXECUTION STATE
    # =========================================================

    selected_tool: str | None
    tool_input: dict[str, Any]
    tool_result: dict[str, Any] | None

    # =========================================================
    # OBSERVATIONS
    # =========================================================

    observations: list[
        dict[str, Any]
    ]

    # =========================================================
    # ITERATION SAFEGUARDS
    # =========================================================

    iteration_count: int
    max_iterations: int

    # =========================================================
    # CONTROL FLAGS
    # =========================================================

    needs_replanning: bool

    # Explanation for why the evaluator requested replanning.
    #
    # Example:
    # "No saved Skill Gap analysis exists for this resume."
    replan_reason: str | None

    # True when the agent has reached a terminal state.
    task_complete: bool

    # =========================================================
    # RUN OUTCOME
    # =========================================================

    # Final lifecycle outcome of the autonomous run.
    #
    # Expected values:
    #
    # None
    #     → Agent is still running.
    #
    # "completed"
    #     → User goal was successfully satisfied.
    #
    # "incomplete"
    #     → Agent executed safely but could not fully
    #       satisfy the goal because required evidence
    #       or prerequisites were unavailable.
    #
    # "failed"
    #     → Agent execution failed because of an
    #       unrecoverable system/runtime error.
    #
    run_outcome: str | None

    # =========================================================
    # FINAL OUTPUT
    # =========================================================

    final_response: str | None


def create_initial_agent_state(
    *,
    user_id: int,
    resume_id: int,
    user_goal: str,
    messages: (
        list[AnyMessage]
        | None
    ) = None,
    thread_id: str | None = None,
    max_iterations: int = (
        DEFAULT_MAX_ITERATIONS
    ),
) -> CareerAgentState:
    """
    Create a consistent initial state for every
    CareerPilot autonomous agent run.
    """

    # =========================================================
    # VALIDATION
    # =========================================================

    if not user_goal.strip():
        raise ValueError(
            "user_goal must not be empty."
        )

    if max_iterations < 1:
        raise ValueError(
            "max_iterations must be at least 1."
        )

    # =========================================================
    # INITIAL STATE
    # =========================================================

    return {
        # -----------------------------------------------------
        # Authenticated context
        # -----------------------------------------------------

        "user_id": user_id,
        "resume_id": resume_id,
        "thread_id": thread_id,

        # Created later by start_run_node.
        "agent_run_id": None,

        # -----------------------------------------------------
        # Goal
        # -----------------------------------------------------

        "user_goal": user_goal.strip(),

        # -----------------------------------------------------
        # Conversation
        # -----------------------------------------------------

        "messages": (
            messages
            if messages is not None
            else []
        ),

        # -----------------------------------------------------
        # Planning
        # -----------------------------------------------------

        "plan": [],
        "current_step": 0,
        "completed_steps": [],

        # -----------------------------------------------------
        # Tool execution
        # -----------------------------------------------------

        "selected_tool": None,
        "tool_input": {},
        "tool_result": None,

        # -----------------------------------------------------
        # Observations
        # -----------------------------------------------------

        "observations": [],

        # -----------------------------------------------------
        # Safeguards
        # -----------------------------------------------------

        "iteration_count": 0,
        "max_iterations":
            max_iterations,

        # -----------------------------------------------------
        # Control
        # -----------------------------------------------------

        "needs_replanning": False,
        "replan_reason": None,
        "task_complete": False,

        # -----------------------------------------------------
        # Run outcome
        # -----------------------------------------------------

        "run_outcome": None,

        # -----------------------------------------------------
        # Final response
        # -----------------------------------------------------

        "final_response": None,
    }