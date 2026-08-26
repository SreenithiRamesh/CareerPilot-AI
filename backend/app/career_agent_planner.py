import os

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
# STRUCTURED PLANNER OUTPUT
# ============================================================


class AgentPlan(BaseModel):
    """
    Structured execution plan generated from the
    user's high-level career goal.
    """

    reasoning_summary: str = Field(
        description=(
            "Brief explanation of the strategy used "
            "to construct the execution plan."
        )
    )

    steps: list[str] = Field(
        description=(
            "Ordered list of concrete executable "
            "steps required to accomplish the "
            "user's goal."
        )
    )


# ============================================================
# PLANNER MODEL
# ============================================================


planner_model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv(
        "GEMINI_API_KEY"
    ),
)


structured_planner = (
    planner_model.with_structured_output(
        AgentPlan
    )
)


# ============================================================
# PLANNER NODE
# ============================================================


def planner_node(
    state: CareerAgentState,
) -> dict:
    """
    Convert a high-level user goal into a minimal,
    actionable execution plan.

    This node decides WHAT needs to happen.

    It does not execute tools and it does not
    generate the final user-facing answer.
    """

    user_goal = state["user_goal"]

    # ========================================================
    # REPLANNING CONTEXT
    # ========================================================

    replan_reason = state.get(
        "replan_reason"
    )

    observations = state.get(
        "observations",
        [],
    )

    # ========================================================
    # DERIVE UNAVAILABLE TOOLS / RESOURCES
    # ========================================================

    unavailable_tools = []

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
            if (
                tool_name
                not in unavailable_tools
            ):
                unavailable_tools.append(
                    tool_name
                )

    # ========================================================
    # PLANNER PROMPT
    # ========================================================

    prompt = f"""
You are the planning component of CareerPilot Agent.

Your responsibility is to convert the user's career goal
into a short execution plan.

USER GOAL

{user_goal}


PREVIOUS AGENT OBSERVATIONS

{observations}


REPLANNING REASON

{replan_reason or "Initial planning request"}


UNAVAILABLE TOOLS / RESOURCES

{unavailable_tools}


AVAILABLE CAREERPILOT CAPABILITIES

1. Resume evidence retrieval
   - Retrieve factual skills, projects, education,
     experience, certifications and achievements
     from the selected resume.

2. Latest Job Match retrieval
   - Retrieve the candidate's most recent persisted
     resume-to-job analysis.

3. Latest Skill Gap retrieval
   - Retrieve existing skills, missing skills,
     partial skills, priority gaps, learning order,
     practice tasks and proof-of-skill actions.

4. Career planning
   - Assemble Job Match and Skill Gap evidence for
     career preparation.

5. Portfolio project recommendation
   - Retrieve saved proof-of-skill project
     recommendations from the latest Skill Gap analysis.

6. Interview preparation
   - Build interview-preparation focus from Job Match
     and Skill Gap evidence.


PLANNING RULES

- Create only the execution steps actually required to
  accomplish the user's goal.

- Every generated plan step MUST correspond to one of the
  available CareerPilot capabilities.

- Do NOT add a step such as:
  "synthesize the final response",
  "prepare the final answer",
  "summarize the results",
  "combine the evidence",
  "generate the final response",
  or any other final-response step.

- Final answer generation is handled separately by the
  CareerPilot finalizer after all executable steps finish.

- If the user explicitly asks for a portfolio project,
  include a dedicated portfolio-project recommendation step.

- If the user explicitly asks for interview preparation,
  include a dedicated interview-preparation step.

- If the user asks what to learn first based on an existing
  Skill Gap, retrieve the latest Skill Gap before any
  project or interview step.

- If a project recommendation depends on identifying a
  priority skill first, retrieve the Skill Gap before
  requesting the project recommendation.

- If interview preparation depends on project or skill-gap
  evidence, place interview preparation after those steps.

- Reuse persisted CareerPilot analyses whenever possible.

- Use resume retrieval only when factual resume evidence
  is actually required.

- Do not retrieve every available source automatically.

- Do not invent candidate information.

- Do not execute tools yourself.

- Prefer 1 to 5 executable steps.

- Each step should represent exactly one clear action.

- Do not merge project recommendation and interview
  preparation into the same execution step when the user
  explicitly requests both.


REPLANNING RULES

- If REPLANNING REASON is not "Initial planning request",
  create a revised execution plan.

- Use PREVIOUS AGENT OBSERVATIONS when deciding what
  information has already been collected.

- Never select a tool listed in
  UNAVAILABLE TOOLS / RESOURCES unless new evidence
  explicitly indicates that the resource became available.

- If a previous observation confirms a resource is
  unavailable, treat that result as final for the
  current agent run.

- Errors such as:
  "resume_not_indexed",
  "No saved Skill Gap analysis exists",
  "No saved Job Match analysis exists"
  should be treated as unavailable-resource evidence.

- Do not repeat the exact failed action unless new
  evidence makes retrying useful.

- Avoid redundant tool calls when the required evidence
  is already present in previous observations.

- If a saved Skill Gap is unavailable, consider whether
  resume evidence or another available persisted analysis
  can still help accomplish part of the user's goal.

- If resume retrieval is unavailable, do not retry
  get_resume_context again during the same run unless new
  evidence indicates the resume has been indexed.

- If a saved Job Match is unavailable, use other available
  evidence where appropriate rather than repeatedly trying
  the same missing resource.

- If a portfolio recommendation cannot be loaded because no
  Skill Gap exists, first choose an alternative evidence
  source rather than repeatedly requesting the same project.

- If no safe alternative can completely satisfy the goal,
  create the minimum executable plan necessary to gather the
  best remaining evidence.

- Never loop indefinitely around the same missing resource.

- A revised plan should make forward progress toward the
  user's original goal.
"""

    plan = structured_planner.invoke(
        prompt
    )

    # ========================================================
    # CLEAN PLAN
    # ========================================================

    steps = [
        step.strip()
        for step in plan.steps
        if step.strip()
    ]

    # ========================================================
    # REMOVE NON-EXECUTABLE FINALIZATION STEPS
    # ========================================================

    forbidden_phrases = (
        "synthesize",
        "final response",
        "final answer",
        "summarize",
        "summary of results",
        "combine the evidence",
        "combine results",
        "generate the final",
        "prepare the final",
        "present the final",
    )

    steps = [
        step
        for step in steps
        if not any(
            phrase in step.lower()
            for phrase in forbidden_phrases
        )
    ]

    # ========================================================
    # FALLBACK PLAN
    # ========================================================

    if not steps:
        steps = [
            (
                "Retrieve relevant resume evidence "
                "for the user's career goal."
            )
        ]

    # ========================================================
    # RETURN UPDATED AGENT STATE
    # ========================================================

    return {
        "plan": steps,
        "current_step": 0,

        # Preserve completed work during replanning.
        "completed_steps": state.get(
            "completed_steps",
            [],
        ),

        "selected_tool": None,
        "tool_input": {},
        "tool_result": None,

        # Preserve observations during replanning.
        "observations": state.get(
            "observations",
            [],
        ),

        # Clear the old replan reason once
        # a revised plan has been created.
        "replan_reason": None,

        "needs_replanning": False,
        "task_complete": False,
        "final_response": None,
    }