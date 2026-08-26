from typing import Literal

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.career_agent_evaluator import (
    evaluator_node,
)
from app.career_agent_executor import (
    tool_executor_node,
)
from app.career_agent_finalizer import (
    finalizer_node,
)
from app.career_agent_persistence_nodes import (
    complete_run_node,
    fail_run_node,
    incomplete_run_node,
    persist_step_node,
    start_run_node,
)
from app.career_agent_planner import (
    planner_node,
)
from app.career_agent_selector import (
    tool_selector_node,
)
from app.career_agent_state import (
    CareerAgentState,
)


# ============================================================
# ROUTING AFTER EVALUATION
# ============================================================


def route_after_evaluation(
    state: CareerAgentState,
) -> Literal[
    "selector",
    "planner",
    "finalizer",
]:
    """
    Decide what happens after each executed step.

    - task complete -> finalizer
    - needs replan  -> planner
    - otherwise     -> next tool selection
    """

    if state.get(
        "task_complete",
        False,
    ):
        return "finalizer"

    if state.get(
        "needs_replanning",
        False,
    ):
        return "planner"

    return "selector"


# ============================================================
# ROUTING FINAL RUN OUTCOME
# ============================================================


def route_run_persistence(
    state: CareerAgentState,
) -> Literal[
    "complete_run",
    "incomplete_run",
    "fail_run",
]:
    """
    Route the finished agent execution to the correct
    persistence lifecycle handler.

    completed
        -> user's goal was successfully satisfied.

    incomplete
        -> execution completed safely, but required
           evidence or prerequisites were unavailable.

    failed
        -> unrecoverable execution/system failure.
    """

    run_outcome = state.get(
        "run_outcome"
    )

    if run_outcome == "completed":
        return "complete_run"

    if run_outcome == "failed":
        return "fail_run"

    # Defensive fallback:
    #
    # A terminal run without an explicit successful
    # outcome should never be persisted as completed.
    return "incomplete_run"


# ============================================================
# GRAPH
# ============================================================


builder = StateGraph(
    CareerAgentState
)


# ============================================================
# PERSISTENCE NODES
# ============================================================


builder.add_node(
    "start_run",
    start_run_node,
)

builder.add_node(
    "persist_step",
    persist_step_node,
)

builder.add_node(
    "complete_run",
    complete_run_node,
)

builder.add_node(
    "incomplete_run",
    incomplete_run_node,
)

builder.add_node(
    "fail_run",
    fail_run_node,
)


# ============================================================
# AGENT NODES
# ============================================================


builder.add_node(
    "planner",
    planner_node,
)

builder.add_node(
    "selector",
    tool_selector_node,
)

builder.add_node(
    "executor",
    tool_executor_node,
)

builder.add_node(
    "evaluator",
    evaluator_node,
)

builder.add_node(
    "finalizer",
    finalizer_node,
)


# ============================================================
# START FLOW
# ============================================================


builder.add_edge(
    START,
    "start_run",
)

builder.add_edge(
    "start_run",
    "planner",
)


# ============================================================
# EXECUTION FLOW
# ============================================================


builder.add_edge(
    "planner",
    "selector",
)

builder.add_edge(
    "selector",
    "executor",
)

builder.add_edge(
    "executor",
    "persist_step",
)

builder.add_edge(
    "persist_step",
    "evaluator",
)


# ============================================================
# EVALUATION ROUTING
# ============================================================


builder.add_conditional_edges(
    "evaluator",
    route_after_evaluation,
    {
        "selector": "selector",
        "planner": "planner",
        "finalizer": "finalizer",
    },
)


# ============================================================
# FINALIZATION + RUN OUTCOME ROUTING
# ============================================================


builder.add_conditional_edges(
    "finalizer",
    route_run_persistence,
    {
        "complete_run":
            "complete_run",

        "incomplete_run":
            "incomplete_run",

        "fail_run":
            "fail_run",
    },
)


# ============================================================
# TERMINAL EDGES
# ============================================================


builder.add_edge(
    "complete_run",
    END,
)

builder.add_edge(
    "incomplete_run",
    END,
)

builder.add_edge(
    "fail_run",
    END,
)


# ============================================================
# COMPILE GRAPH
# ============================================================


career_agent_graph = (
    builder.compile()
)