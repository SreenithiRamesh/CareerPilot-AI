import pytest

from langchain_core.messages import HumanMessage

from app.career_agent_state import (
    DEFAULT_MAX_ITERATIONS,
    CareerAgentState,
    create_initial_agent_state,
)


def test_career_agent_state_shape():
    state: CareerAgentState = (
        create_initial_agent_state(
            user_id=7,
            resume_id=27,
            thread_id="agent-test-thread",
            user_goal=(
                "Prepare me for an entry-level "
                "DevOps role."
            ),
            messages=[
                HumanMessage(
                    content=(
                        "Prepare me for an "
                        "entry-level DevOps role."
                    )
                )
            ],
        )
    )
    assert state["run_outcome"] is None
    assert state["user_id"] == 7
    assert state["resume_id"] == 27

    assert state["user_goal"] != ""

    assert state["plan"] == []
    assert state["current_step"] == 0
    assert state["completed_steps"] == []

    assert state["selected_tool"] is None
    assert state["tool_input"] == {}
    assert state["tool_result"] is None

    assert state["observations"] == []

    assert state["iteration_count"] == 0
    assert (
        state["max_iterations"]
        == DEFAULT_MAX_ITERATIONS
    )

    assert state["needs_replanning"] is False
    assert state["task_complete"] is False
    assert state["final_response"] is None


def test_empty_goal_is_rejected():
    with pytest.raises(
        ValueError,
        match="user_goal must not be empty",
    ):
        create_initial_agent_state(
            user_id=7,
            resume_id=27,
            user_goal="   ",
        )


def test_invalid_max_iterations_is_rejected():
    with pytest.raises(
        ValueError,
        match=(
            "max_iterations must be at least 1"
        ),
    ):
        create_initial_agent_state(
            user_id=7,
            resume_id=27,
            user_goal=(
                "Prepare me for a backend role."
            ),
            max_iterations=0,
        )