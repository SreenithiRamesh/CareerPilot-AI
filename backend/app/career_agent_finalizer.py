import json
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)

from app.career_agent_state import (
    CareerAgentState,
)


load_dotenv()


def _format_conversation_history(
    state: CareerAgentState,
    *,
    limit: int = 12,
) -> str:
    """
    Format recent persisted Agent conversation turns
    for final response continuity.
    """

    messages = state.get(
        "messages",
        [],
    )

    formatted_messages = []

    for message in messages[-limit:]:
        content = getattr(
            message,
            "content",
            "",
        )

        if not content:
            continue

        if isinstance(
            message,
            HumanMessage,
        ):
            role = "User"

        elif isinstance(
            message,
            AIMessage,
        ):
            role = "CareerPilot"

        else:
            continue

        formatted_messages.append(
            f"{role}: {content}"
        )

    if not formatted_messages:
        return (
            "No previous Agent conversation "
            "is available."
        )

    return "\n\n".join(
        formatted_messages
    )


finalizer_model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv(
        "GEMINI_API_KEY"
    ),
)


def finalizer_node(
    state: CareerAgentState,
) -> dict[str, Any]:
    """
    Generate the final user-facing answer from the
    persisted conversation context and evidence collected
    during autonomous execution.

    Tool observations remain the source of truth for
    candidate-specific career evidence.
    """

    conversation_history = (
        _format_conversation_history(
            state
        )
    )

    observations = state.get(
        "observations",
        [],
    )

    evidence = []

    for observation in observations:
        evidence.append(
            {
                "step": observation.get(
                    "step"
                ),
                "tool": observation.get(
                    "tool"
                ),
                "result": observation.get(
                    "result"
                ),
            }
        )

    evidence_text = json.dumps(
        evidence,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    prompt = f"""
You are the final response component of
CareerPilot Agent.

The agent has already executed the required tools.

Your job is to answer the user's latest goal using
the conversation context and verified execution evidence.

PREVIOUS AGENT CONVERSATION

{conversation_history}


USER GOAL

{state["user_goal"]}


AGENT EXECUTION EVIDENCE

{evidence_text}


FINAL RESPONSE RULES

- Use PREVIOUS AGENT CONVERSATION to resolve references
  such as "first priority", "that recommendation",
  "the previous plan", "explain it", and "revise it".

- Treat USER GOAL as the newest instruction and answer
  it in the context of the earlier Agent turns.

- Use conversation history for continuity and reference
  resolution.

- Use execution evidence as the source of truth for
  resume facts, persisted analyses, skills, projects,
  and career recommendations.

- Never invent facts merely because they appeared in
  an earlier generated response.

- Do not repeat the complete previous answer unless the
  newest goal explicitly requests it.

- Do not invent skills, projects, experience,
  certifications, job-match results, or skill gaps.

- Do not mention internal tool names unless useful.

- Do not describe the internal planning process.

- Answer the user's actual career goal directly.

- If Skill Gap evidence identifies a learning order,
  clearly explain what the user should learn first.

- If project recommendations were retrieved,
  recommend the most relevant project and explain why.

- If interview preparation evidence exists,
  provide clear interview focus areas.

- Prefer evidence-backed recommendations over
  generic career advice.

- Keep the response practical and structured.

- Do not claim the user has completed a recommended
  project unless the evidence explicitly says so.

- If required evidence is missing, state that clearly.
"""

    response = finalizer_model.invoke(
        prompt
    )

    content = response.content

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if (
                isinstance(item, dict)
                and item.get("type")
                == "text"
            ):
                text_parts.append(
                    item.get(
                        "text",
                        "",
                    )
                )

        content = "\n".join(
            text_parts
        )

    return {
        "final_response": str(content),
        "task_complete": True,
    }