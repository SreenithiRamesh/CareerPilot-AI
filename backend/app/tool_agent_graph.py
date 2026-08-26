import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import (
    AnyMessage,
    SystemMessage,
)
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.graph.message import (
    add_messages,
)
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from app.agent_tools import (
    CAREERPILOT_AGENT_TOOLS,
)


load_dotenv()


# ============================================================
# AGENT STATE
# ============================================================


class ToolAgentState(TypedDict):
    messages: Annotated[
        list[AnyMessage],
        add_messages,
    ]

    user_id: int
    resume_id: int

    thread_id: str | None
    job_description: str | None


# ============================================================
# TOOL REGISTRY
# ============================================================


tools = CAREERPILOT_AGENT_TOOLS


# ============================================================
# LLM
# ============================================================


model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv(
        "GEMINI_API_KEY"
    ),
)


model_with_tools = model.bind_tools(
    tools
)


# ============================================================
# AGENT NODE
# ============================================================


def agent_node(
    state: ToolAgentState,
):
    system_prompt = f"""
You are CareerPilot Agent.

You are an AI career assistant for students and
fresh graduates preparing for software engineering roles.

You have access to specialized CareerPilot tools.

AUTHENTICATED CONTEXT

User ID:
{state["user_id"]}

Resume ID:
{state["resume_id"]}

Job Description:
{state.get("job_description") or "Not provided"}

AVAILABLE CAPABILITIES

You can:

- retrieve resume evidence
- inspect the latest Job Match
- inspect the latest Skill Gap analysis
- prepare career planning context
- recommend portfolio projects
- prepare interview focus

TOOL RULES

- Use get_resume_context when you need factual evidence
  about the candidate's resume.

- Use get_latest_job_match when you need the candidate's
  latest saved role-alignment analysis.

- Use get_latest_skill_gap when you need existing,
  partial, missing, or priority skill gaps.

- Use generate_career_plan when you need to determine
  whether enough persisted evidence exists for career
  planning.

- Use recommend_project when the goal requires
  proof-of-skill or portfolio project recommendations.

- Use prepare_interview_focus when the user wants
  interview preparation grounded in existing analysis.

IMPORTANT BEHAVIOR

- Never invent resume information.
- Never invent previous analyses.
- Use tools when information should come from CareerPilot
  data rather than general knowledge.
- Do not call the same tool repeatedly unless new
  information makes another call necessary.
- Respect the authenticated user_id and resume_id.
- If required information is missing, explain what is
  missing instead of fabricating it.
- Once sufficient evidence is available, answer the user
  directly and concisely.
"""

    messages = [
        SystemMessage(
            content=system_prompt
        ),
        *state["messages"],
    ]

    response = (
        model_with_tools.invoke(
            messages
        )
    )

    return {
        "messages": [
            response
        ]
    }


# ============================================================
# TOOL NODE
# ============================================================


tool_node = ToolNode(
    tools
)


# ============================================================
# ROUTING
# ============================================================


def should_continue(
    state: ToolAgentState,
):
    last_message = (
        state["messages"][-1]
    )

    if getattr(
        last_message,
        "tool_calls",
        None,
    ):
        return "tools"

    return END


# ============================================================
# GRAPH
# ============================================================


builder = StateGraph(
    ToolAgentState
)


builder.add_node(
    "agent",
    agent_node,
)


builder.add_node(
    "tools",
    tool_node,
)


builder.add_edge(
    START,
    "agent",
)


builder.add_conditional_edges(
    "agent",
    should_continue,
)


builder.add_edge(
    "tools",
    "agent",
)


tool_agent_graph = (
    builder.compile()
)