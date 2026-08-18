import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import (
    AnyMessage,
    SystemMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from app.agent_tools import (
    retrieve_resume_context,
    analyze_job_description,
)


load_dotenv()


class ToolAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

    thread_id: str
    job_description: str


tools = [
    retrieve_resume_context,
    analyze_job_description,
]


model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


model_with_tools = model.bind_tools(tools)

def agent_node(state: ToolAgentState):
    system_prompt = """
You are CareerPilot AI.

You are an intelligent career assistant for students and fresh graduates.

You have access to tools.

Rules:

- If the user asks about their resume, use the resume retrieval tool.
- If the user asks whether they match a job, inspect both the resume
  and job description.
- If the user asks about missing skills for a role, use resume evidence
  and job requirements before answering.
- Do not invent resume information.
- Do not call tools unnecessarily.
- If you already have enough information, answer directly.
"""

    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"],
    ]

    response = model_with_tools.invoke(messages)

    return {
        "messages": [response]
    }

tool_node = ToolNode(tools)

def should_continue(state: ToolAgentState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


builder = StateGraph(ToolAgentState)

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

tool_agent_graph = builder.compile()