import os
from typing import Any

from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)
from pydantic import BaseModel, Field

from app.career_agent_state import (
    CareerAgentState,
)


load_dotenv()


# ============================================================
# ALLOWED AGENT TOOLS
# ============================================================


ALLOWED_TOOLS = {
    "get_resume_context",
    "get_latest_job_match",
    "get_latest_skill_gap",
    "generate_career_plan",
    "recommend_project",
    "prepare_interview_focus",
}


# ============================================================
# STRUCTURED TOOL-SELECTION OUTPUT
# ============================================================


class ToolSelection(BaseModel):
    tool_name: str = Field(
        description=(
            "Exact name of the CareerPilot tool "
            "required for the current execution step."
        )
    )

    reasoning_summary: str = Field(
        description=(
            "Short explanation of why this tool "
            "matches the current step."
        )
    )

    query: str | None = Field(
        default=None,
        description=(
            "Semantic retrieval query when "
            "get_resume_context is selected."
        ),
    )

    target_skill: str | None = Field(
        default=None,
        description=(
            "Specific target skill when "
            "recommend_project is selected."
        ),
    )


# ============================================================
# SELECTOR MODEL
# ============================================================


selector_model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv(
        "GEMINI_API_KEY"
    ),
)


structured_selector = (
    selector_model.with_structured_output(
        ToolSelection
    )
)


# ============================================================
# TOOL SELECTOR NODE
# ============================================================


def tool_selector_node(
    state: CareerAgentState,
) -> dict[str, Any]:
    """
    Select the CareerPilot tool required to execute
    the current plan step.

    This node chooses a tool.

    It does not execute the tool.

    Tools already confirmed unavailable during the
    current agent run are blocked deterministically.
    """

    plan = state["plan"]

    current_step_index = state[
        "current_step"
    ]

    # ========================================================
    # PLAN BOUNDARY CHECK
    # ========================================================

    if (
        current_step_index < 0
        or current_step_index
        >= len(plan)
    ):
        return {
            "selected_tool": None,
            "tool_input": {},
            "task_complete": True,
        }

    current_step = plan[
        current_step_index
    ]

    observations = state.get(
        "observations",
        [],
    )

    # ========================================================
    # DETERMINE UNAVAILABLE TOOLS
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

        # A tool is considered unavailable for the
        # remainder of this run when:
        #
        # - execution failed, OR
        # - persisted evidence was confirmed missing.
        #
        if (
            result.get("success") is False
            or result.get("found") is False
        ):
            unavailable_tools.add(
                tool_name
            )

    # ========================================================
    # SELECTOR PROMPT
    # ========================================================

    prompt = f"""
You are the tool-selection component of
CareerPilot Agent.

Your job is to select exactly ONE CareerPilot
tool that best executes the current plan step.


USER GOAL

{state["user_goal"]}


CURRENT PLAN STEP

{current_step}


PREVIOUS OBSERVATIONS

{observations}


UNAVAILABLE TOOLS

{sorted(unavailable_tools)}


AVAILABLE TOOLS


1. get_resume_context

Purpose:
Retrieve factual evidence from the selected resume.

Use when the current step requires:
- skills
- projects
- education
- experience
- certifications
- achievements
- other resume facts


2. get_latest_job_match

Purpose:
Retrieve the latest persisted Job Match analysis.

Use when the step needs:
- match score
- strong matches
- partial matches
- missing role requirements
- resume improvements
- priority actions


3. get_latest_skill_gap

Purpose:
Retrieve the latest persisted Skill Gap analysis.

Use when the step needs:
- existing skills
- missing skills
- partial skills
- priority gaps
- learning order
- practice tasks
- proof-of-skill actions


4. generate_career_plan

Purpose:
Load the evidence required for CareerPilot's
career-planning workflow.

Use when the step explicitly requires career
planning context or roadmap preparation.


5. recommend_project

Purpose:
Retrieve portfolio project recommendations from
the latest Skill Gap analysis.

Use when the current step requires:
- portfolio project
- proof-of-skill project
- project targeting a missing skill


6. prepare_interview_focus

Purpose:
Build interview-preparation focus from persisted
CareerPilot evidence.

Use when the step requires:
- interview preparation
- interview focus areas
- technical preparation priorities


RULES

- Select exactly one tool.

- tool_name MUST exactly match one of the six
  available tool names.

- Do not invent tool names.

- NEVER select a tool listed in UNAVAILABLE TOOLS.

- A tool appears in UNAVAILABLE TOOLS because a previous
  execution already proved that its required resource does
  not exist or cannot currently be accessed.

- Do not retry an unavailable tool during the same
  CareerPilot Agent run.

- Choose another available CareerPilot capability instead.

- Use get_resume_context only when resume facts
  are actually required.

- If get_resume_context is selected, provide a useful
  semantic retrieval query.

- If recommend_project is selected and previous
  observations reveal a priority skill, place that
  skill in target_skill.

- Do not execute the tool.

- Do not answer the user's goal.

- Only choose the best available tool for the
  current execution step.
"""

    selection = structured_selector.invoke(
        prompt
    )

    # ========================================================
    # VALIDATE TOOL NAME
    # ========================================================

    if (
        selection.tool_name
        not in ALLOWED_TOOLS
    ):
        raise ValueError(
            "Selector chose an unsupported "
            f"tool: {selection.tool_name}"
        )

    # ========================================================
    # HARD BLOCK UNAVAILABLE TOOL
    # ========================================================

    if (
        selection.tool_name
        in unavailable_tools
    ):
        return {
            "selected_tool": None,
            "tool_input": {},
            "needs_replanning": True,
            "replan_reason": (
                f"{selection.tool_name} was already "
                "confirmed unavailable during this "
                "agent run. Choose another available "
                "CareerPilot evidence source."
            ),
        }

    # ========================================================
    # BASE TOOL INPUT
    # ========================================================

    tool_input: dict[str, Any] = {
        "user_id": state["user_id"],
        "resume_id": state["resume_id"],
    }

    # ========================================================
    # RESUME RETRIEVAL INPUT
    # ========================================================

    if (
        selection.tool_name
        == "get_resume_context"
    ):
        tool_input["query"] = (
            selection.query
            or state["user_goal"]
        )

    # ========================================================
    # PROJECT RECOMMENDATION INPUT
    # ========================================================

    if (
        selection.tool_name
        == "recommend_project"
        and selection.target_skill
    ):
        tool_input[
            "target_skill"
        ] = selection.target_skill

    # ========================================================
    # RETURN SELECTION
    # ========================================================

    return {
        "selected_tool":
            selection.tool_name,

        "tool_input":
            tool_input,

        "needs_replanning":
            False,

        "replan_reason":
            None,
    }