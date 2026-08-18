import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END


load_dotenv()


class CareerState(TypedDict):
    message: str
    response: str


model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


SYSTEM_PROMPT = """
You are CareerPilot AI.

You are a career assistant for students and fresh graduates preparing
for software engineering careers.

Provide practical, personalized, and actionable career guidance.

When responding:
- Understand the user's goal.
- Prioritize what they should do next.
- Explain why your recommendation matters.
- Avoid overwhelming the user.
- Focus on realistic entry-level software engineering preparation.
"""


def career_advisor_node(state: CareerState):
    user_message = state["message"]

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    ai_response = model.invoke(messages)

    content = ai_response.content

    if isinstance(content, list):
        text_parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]

        content = "\n".join(text_parts)

    return {
        "response": content
    }


builder = StateGraph(CareerState)

builder.add_node(
    "career_advisor",
    career_advisor_node,
)

builder.add_edge(
    START,
    "career_advisor",
)

builder.add_edge(
    "career_advisor",
    END,
)

career_graph = builder.compile()