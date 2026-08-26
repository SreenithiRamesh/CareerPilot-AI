import json
import os
from typing import Any

from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)

from app.career_agent_state import (
    CareerAgentState,
)


load_dotenv()


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
    evidence collected during autonomous execution.

    The finalizer must use tool observations as the
    source of truth and must not invent career evidence.
    """

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

Your job is to answer the user's original goal using
ONLY the evidence collected from those tools.

USER GOAL

{state["user_goal"]}


AGENT EXECUTION EVIDENCE

{evidence_text}


FINAL RESPONSE RULES

- Use the execution evidence as the source of truth.

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