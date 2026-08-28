from types import SimpleNamespace

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)

import app.career_agent_finalizer as finalizer_module
import app.career_agent_planner as planner_module
from app.career_agent_planner import AgentPlan
from app.career_agent_state import (
    create_initial_agent_state,
)


CURRENT_GOAL = (
    "Create a practical seven-day Java backend "
    "preparation plan based on my selected resume."
)

OLDER_DEVOPS_GOAL = (
    "Help me prepare for an entry-level "
    "DevOps Engineer role."
)


def _build_conflicting_state():
    state = create_initial_agent_state(
        user_id=1,
        resume_id=10,
        thread_id="goal-priority-thread",
        user_goal=CURRENT_GOAL,
        messages=[
            HumanMessage(
                content=OLDER_DEVOPS_GOAL
            ),
            AIMessage(
                content=(
                    "Your earlier preparation plan "
                    "focused on Docker, CI/CD, "
                    "Kubernetes, and Terraform."
                )
            ),
        ],
        max_iterations=4,
    )

    state["observations"] = [
        {
            "step_index": 0,
            "step": (
                "Retrieve the latest saved "
                "Skill Gap analysis."
            ),
            "tool": "get_latest_skill_gap",
            "tool_input": {},
            "result": {
                "success": True,
                "target_role": "DevOps Engineer",
                "priority_gaps": [
                    "Docker",
                    "CI/CD",
                    "Kubernetes",
                ],
                "existing_skills": [
                    "Java",
                    "SQL",
                    "REST APIs",
                ],
            },
        }
    ]

    return state


class CapturingPlanner:
    def __init__(self):
        self.prompt = None

    def invoke(self, prompt):
        self.prompt = prompt

        return AgentPlan(
            reasoning_summary=(
                "Use the current Java backend goal."
            ),
            steps=[
                (
                    "Retrieve factual evidence from "
                    "the selected resume."
                )
            ],
        )


class CapturingFinalizer:
    def __init__(self):
        self.prompt = None

    def invoke(self, prompt):
        self.prompt = prompt

        return SimpleNamespace(
            content=(
                "Seven-day Java backend "
                "preparation plan."
            )
        )


def _assert_current_goal_precedence_rules(
    prompt: str,
):
    normalized_prompt = " ".join(
        prompt.split()
    )

    assert (
        "CURRENT GOAL PRECEDENCE"
        in normalized_prompt
    )

    assert (
        "USER GOAL is authoritative"
        in normalized_prompt
    )

    assert (
        "target role"
        in normalized_prompt
    )

    assert (
        "historical evidence"
        in normalized_prompt
    )

    assert (
        "must not replace"
        in normalized_prompt
    )

def test_planner_prompt_prioritizes_current_goal(
    monkeypatch,
):
    capturing_planner = CapturingPlanner()

    monkeypatch.setattr(
        planner_module,
        "structured_planner",
        capturing_planner,
    )

    result = planner_module.planner_node(
        _build_conflicting_state()
    )

    assert result["plan"] == [
        (
            "Retrieve factual evidence from "
            "the selected resume."
        )
    ]

    assert capturing_planner.prompt is not None

    assert CURRENT_GOAL in (
        capturing_planner.prompt
    )

    assert OLDER_DEVOPS_GOAL in (
        capturing_planner.prompt
    )

    _assert_current_goal_precedence_rules(
        capturing_planner.prompt
    )


def test_finalizer_prompt_prioritizes_current_goal(
    monkeypatch,
):
    capturing_finalizer = (
        CapturingFinalizer()
    )

    monkeypatch.setattr(
        finalizer_module,
        "finalizer_model",
        capturing_finalizer,
    )

    result = finalizer_module.finalizer_node(
        _build_conflicting_state()
    )

    assert result == {
        "final_response": (
            "Seven-day Java backend "
            "preparation plan."
        ),
        "task_complete": True,
    }

    assert capturing_finalizer.prompt is not None

    assert CURRENT_GOAL in (
        capturing_finalizer.prompt
    )

    assert '"target_role": "DevOps Engineer"' in (
        capturing_finalizer.prompt
    )

    _assert_current_goal_precedence_rules(
        capturing_finalizer.prompt
    )