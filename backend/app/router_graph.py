import os
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from app.resume_rag import (
    get_resume_vector_store,
    resume_exists,
    search_resume,
)


load_dotenv()


model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


class CareerState(TypedDict):
    message: str
    intent: str
    response: str

    thread_id: str
    user_id: int
    resume_id: int | None

    job_description: str
    job_match_analysis: str
    skill_gap_analysis: str
    career_plan: str

    name: str
    education: str
    graduation_year: str
    skills: list[str]
    target_role: str
    career_goal: str

    messages: Annotated[
        list[AnyMessage],
        add_messages,
    ]


def build_conversation_context(
    state: CareerState,
) -> str:
    lines = []

    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            lines.append(
                f"User: {msg.content}"
            )

        elif isinstance(msg, AIMessage):
            lines.append(
                f"Assistant: {msg.content}"
            )

    if not lines:
        return "No previous conversation."

    return "\n".join(lines)


def build_user_context(
    state: CareerState,
) -> str:
    skills = (
        ", ".join(
            state.get("skills", [])
        )
        or "Not provided"
    )

    return f"""
USER PROFILE

Name: {state.get("name") or "Not provided"}
Education: {state.get("education") or "Not provided"}
Graduation Year: {state.get("graduation_year") or "Not provided"}
Skills: {skills}
Target Role: {state.get("target_role") or "Not provided"}
Career Goal: {state.get("career_goal") or "Not provided"}

Use this profile when answering.

Do not ask for information that is already available in this profile.

Do not recommend skills the user already knows unless deeper knowledge
of that skill is genuinely useful.
"""


def normalize_response(
    content,
) -> str:
    if isinstance(content, list):
        text_parts = [
            item.get("text", "")
            for item in content
            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            )
        ]

        return "\n".join(text_parts)

    return str(content)


def get_resume_filters(
    state: CareerState,
) -> dict:
    """
    Build authenticated Chroma filters.

    user_id is always required.

    resume_id is included when the request identifies
    a specific resume.
    """

    user_id = str(
        state["user_id"]
    )

    resume_id = (
        str(state["resume_id"])
        if state.get("resume_id")
        else None
    )

    return {
        "user_id": user_id,
        "resume_id": resume_id,
    }


def intent_router_node(
    state: CareerState,
):
    message = state["message"].lower()

    job_match_keywords = [
        "job match",
        "match my resume",
        "resume match",
        "match this job",
        "matches this job",
        "match this job description",
        "matches this job description",
        "job description match",
        "jd match",
        "compare my resume",
        "compare resume",
        "fit for this role",
        "fit for this job",
        "suitable for this role",
        "suitable for this job",
        "am i suitable",
        "how well my resume matches",
    ]

    career_plan_keywords = [
        "career plan",
        "readiness plan",
        "prepare me for this role",
        "what should i do for this role",
        "roadmap for this job",
        "analyze my readiness",
        "full analysis",
    ]

    skill_gap_keywords = [
        "skill gap",
        "skills gap",
        "missing skills",
        "what skills am i missing",
        "what should i learn for this job",
        "skills i need for this role",
        "gap analysis",
    ]

    resume_keywords = [
        "resume",
        "cv",
        "ats",
        "review my resume",
        "improve my resume",
        "resume review",
    ]

    interview_keywords = [
        "interview",
        "technical round",
        "hr round",
        "mock interview",
        "interview questions",
    ]

    # More-specific intents must be checked first.
    if any(
        keyword in message
        for keyword in career_plan_keywords
    ):
        intent = "career_plan"

    elif any(
        keyword in message
        for keyword in job_match_keywords
    ):
        intent = "job_match"

    elif any(
        keyword in message
        for keyword in skill_gap_keywords
    ):
        intent = "skill_gap"

    elif any(
        keyword in message
        for keyword in resume_keywords
    ):
        intent = "resume"

    elif any(
        keyword in message
        for keyword in interview_keywords
    ):
        intent = "interview"

    else:
        intent = "career"

    return {
        "intent": intent,
    }


def route_intent(
    state: CareerState,
) -> Literal[
    "career_advisor",
    "resume_advisor",
    "interview_advisor",
    "job_match_advisor",
    "skill_gap_advisor",
    "career_plan_start",
]:
    intent = state["intent"]

    if intent == "career":
        return "career_advisor"

    if intent == "career_plan":
        return "career_plan_start"

    if intent == "resume":
        return "resume_advisor"

    if intent == "interview":
        return "interview_advisor"

    if intent == "job_match":
        return "job_match_advisor"

    if intent == "skill_gap":
        return "skill_gap_advisor"

    return "career_advisor"


def career_plan_start_node(
    state: CareerState,
):
    return {
        "job_match_analysis": "",
        "skill_gap_analysis": "",
        "career_plan": "",
    }


def workflow_job_match_node(
    state: CareerState,
):
    user_context = build_user_context(
        state
    )

    thread_id = state["thread_id"]

    job_description = state.get(
        "job_description",
        "",
    )

    if not resume_exists(
        thread_id
    ):
        return {
            "job_match_analysis": (
                "Resume is not indexed "
                "for this conversation."
            )
        }

    if not job_description.strip():
        return {
            "job_match_analysis": (
                "Job description was not provided."
            )
        }

    vector_store = (
        get_resume_vector_store(
            thread_id
        )
    )

    filters = get_resume_filters(
        state
    )

    retrieved_docs = search_resume(
        vector_store,
        job_description,
        k=5,
        user_id=filters["user_id"],
        resume_id=filters["resume_id"],
    )

    if not retrieved_docs:
        return {
            "job_match_analysis": (
                "No resume evidence was found "
                "for the authenticated user "
                "and selected resume."
            )
        }

    resume_context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    prompt = f"""
You are the Job Match Analysis Agent inside CareerPilot AI.

{user_context}

JOB DESCRIPTION

{job_description}

RESUME EVIDENCE

{resume_context}

Analyze the candidate's match for the role.

Return:

- Match score
- Strong matches
- Partial matches
- Missing requirements

Do not invent experience.
"""

    result = model.invoke(
        prompt
    )

    analysis = normalize_response(
        result.content
    )

    return {
        "job_match_analysis": analysis,
    }


def skill_gap_advisor_node(
    state: CareerState,
):
    user_message = state["message"]

    user_context = build_user_context(
        state
    )

    thread_id = state["thread_id"]

    job_description = state.get(
        "job_description",
        "",
    )

    if not resume_exists(
        thread_id
    ):
        return {
            "response": (
                "I do not have your resume "
                "indexed yet. "
                "Please upload your resume first."
            )
        }

    if not job_description.strip():
        return {
            "response": (
                "Please provide the job description "
                "so I can identify your skill gaps "
                "for that role."
            )
        }

    vector_store = (
        get_resume_vector_store(
            thread_id
        )
    )

    filters = get_resume_filters(
        state
    )

    retrieved_docs = search_resume(
        vector_store,
        job_description,
        k=5,
        user_id=filters["user_id"],
        resume_id=filters["resume_id"],
    )

    if not retrieved_docs:
        response_text = (
            "I could not find resume evidence "
            "for the authenticated user and "
            "selected resume."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    resume_context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    prompt = f"""
You are the Skill Gap Specialist inside CareerPilot AI.

{user_context}

JOB DESCRIPTION

{job_description}

RETRIEVED RESUME EVIDENCE

{resume_context}

Your task is to identify the candidate's skill gaps for this specific job.

Return the response in this structure:

1. Existing Relevant Skills
2. Missing Skills
3. Partially Demonstrated Skills
4. Priority Ranking
   - High
   - Medium
   - Low
5. Recommended Learning Order
6. Practice Task for Each High-Priority Gap
7. Proof-of-Skill Project or Resume Evidence to Build
8. Short Readiness Plan

Rules:

- Use only resume evidence provided above.
- Do not invent skills or experience.
- Clearly separate existing skills from missing skills.
- Prioritize gaps based on importance to the job description.
- Keep recommendations realistic for an entry-level candidate.
- Do not recommend learning everything at once.

User request:

{user_message}
"""

    result = model.invoke(
        prompt
    )

    response_text = normalize_response(
        result.content
    )

    return {
        "response": response_text,
        "messages": [
            AIMessage(
                content=response_text
            )
        ],
    }


def career_advisor_node(
    state: CareerState,
):
    user_message = state["message"]

    user_context = build_user_context(
        state
    )

    conversation_context = (
        build_conversation_context(
            state
        )
    )

    prompt = f"""
You are the Career Guidance Specialist inside CareerPilot AI.

{user_context}

CONVERSATION HISTORY

{conversation_context}

Your job is to help students and fresh graduates make practical
software engineering career decisions.

You should:

- use the user's existing skills and background
- use previous conversation context when relevant
- avoid recommending skills they already know unless deeper knowledge is useful
- prioritize what the user should do NEXT
- give realistic entry-level career guidance
- provide clear and actionable next steps
- explain why each recommendation matters
- avoid overwhelming the user with too many technologies
- focus on software engineering, backend, frontend, full-stack,
  cloud, DevOps, and related entry-level technology careers

Important:

- Never ask for information that is already available in USER PROFILE.
- Remember preferences or goals mentioned earlier in the conversation.
- Base recommendations on the user's target role, career goal,
  existing skills, and previous messages.
- If a profile field says "Not provided", ask for it only if it is genuinely needed.
- Do not ignore earlier conversation context when answering follow-up questions.

Current user request:

{user_message}

Provide concise, practical, personalized career guidance.
"""

    result = model.invoke(
        prompt
    )

    response_text = normalize_response(
        result.content
    )

    return {
        "response": response_text,
        "messages": [
            AIMessage(
                content=response_text
            )
        ],
    }


def resume_advisor_node(
    state: CareerState,
):
    user_message = state["message"]

    user_context = build_user_context(
        state
    )

    thread_id = state["thread_id"]

    if not resume_exists(
        thread_id
    ):
        return {
            "response": (
                "I do not have a resume "
                "indexed for this conversation yet. "
                "Please upload your resume PDF first."
            )
        }

    vector_store = (
        get_resume_vector_store(
            thread_id
        )
    )

    filters = get_resume_filters(
        state
    )

    retrieved_docs = search_resume(
        vector_store,
        user_message,
        k=3,
        user_id=filters["user_id"],
        resume_id=filters["resume_id"],
    )

    if not retrieved_docs:
        response_text = (
            "I could not find resume content "
            "owned by your account for the "
            "selected resume."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    resume_context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    prompt = f"""
You are the Resume Analysis Specialist inside CareerPilot AI.

{user_context}

RETRIEVED RESUME CONTEXT

{resume_context}

Your job is to answer the user's resume-related question using
the retrieved resume evidence above.

Important rules:

- Base your answer on the retrieved resume context.
- Do not invent skills, projects, achievements, experience, or metrics.
- Clearly distinguish what is present in the resume from what you recommend.
- Use the user's target role when making improvement suggestions.
- If the retrieved evidence is insufficient, say so.
- Do not claim to have seen information that is not present in the retrieved context.

User request:

{user_message}

Provide practical, specific, evidence-grounded resume guidance.
"""

    result = model.invoke(
        prompt
    )

    response_text = normalize_response(
        result.content
    )

    return {
        "response": response_text,
        "messages": [
            AIMessage(
                content=response_text
            )
        ],
    }


def interview_advisor_node(
    state: CareerState,
):
    user_message = state["message"]

    user_context = build_user_context(
        state
    )

    prompt = f"""
You are the Interview Preparation Specialist inside CareerPilot AI.

{user_context}

The user needs help preparing for a software engineering interview.

You should:

- tailor preparation to the user's existing skills and target role
- prioritize technologies and fundamentals relevant to their profile
- generate technical or behavioral questions when appropriate
- provide practical preparation guidance
- identify important weak areas to revise
- explain concepts clearly
- avoid overwhelming the user
- prioritize immediate preparation if the interview is soon

Important:

- Do not ask for information already available in USER PROFILE.
- Use the user's existing skills when generating technical questions.
- Keep recommendations appropriate for entry-level software engineering roles.

User request:

{user_message}

Provide concise and actionable interview preparation.
"""

    result = model.invoke(
        prompt
    )

    response_text = normalize_response(
        result.content
    )

    return {
        "response": response_text,
        "messages": [
            AIMessage(
                content=response_text
            )
        ],
    }


def workflow_skill_gap_node(
    state: CareerState,
):
    job_description = state.get(
        "job_description",
        "",
    )

    job_match_analysis = state.get(
        "job_match_analysis",
        "",
    )

    prompt = f"""
You are the Skill Gap Analysis Agent inside CareerPilot AI.

JOB DESCRIPTION

{job_description}

JOB MATCH ANALYSIS

{job_match_analysis}

Using this information, identify:

1. Existing relevant skills
2. Missing skills
3. Partially demonstrated skills
4. High-priority gaps
5. Medium-priority gaps

Do not introduce requirements that are not present
in the job description.
"""

    result = model.invoke(
        prompt
    )

    analysis = normalize_response(
        result.content
    )

    return {
        "skill_gap_analysis": analysis,
    }


def career_planner_node(
    state: CareerState,
):
    user_context = build_user_context(
        state
    )

    job_description = state.get(
        "job_description",
        "",
    )

    job_match_analysis = state.get(
        "job_match_analysis",
        "",
    )

    skill_gap_analysis = state.get(
        "skill_gap_analysis",
        "",
    )

    prompt = f"""
You are the Career Planning Agent inside CareerPilot AI.

{user_context}

JOB DESCRIPTION

{job_description}

JOB MATCH ANALYSIS

{job_match_analysis}

SKILL GAP ANALYSIS

{skill_gap_analysis}

Create a practical preparation roadmap for this candidate.

Return:

1. Current Readiness Summary
2. Top 3 Priorities
3. Recommended Learning Order
4. Practical Tasks
5. Portfolio Evidence to Build
6. Interview Preparation Focus
7. 30-Day Action Plan

Rules:

- Do not recommend skills the candidate already has unless
  deeper knowledge is required.
- Focus on gaps relevant to this exact role.
- Keep the plan realistic for an entry-level candidate.
"""

    result = model.invoke(
        prompt
    )

    career_plan = normalize_response(
        result.content
    )

    return {
        "career_plan": career_plan,
        "response": career_plan,
        "messages": [
            AIMessage(
                content=career_plan
            )
        ],
    }


def job_match_advisor_node(
    state: CareerState,
):
    user_message = state["message"]

    user_context = build_user_context(
        state
    )

    thread_id = state["thread_id"]

    job_description = state.get(
        "job_description",
        "",
    )

    if not resume_exists(
        thread_id
    ):
        return {
            "response": (
                "I do not have your resume "
                "indexed yet. "
                "Please upload your resume first."
            )
        }

    if not job_description.strip():
        return {
            "response": (
                "Please provide the job description "
                "so I can compare it with your resume."
            )
        }

    vector_store = (
        get_resume_vector_store(
            thread_id
        )
    )

    filters = get_resume_filters(
        state
    )

    retrieved_docs = search_resume(
        vector_store,
        job_description,
        k=5,
        user_id=filters["user_id"],
        resume_id=filters["resume_id"],
    )

    if not retrieved_docs:
        response_text = (
            "I could not find resume evidence "
            "owned by the authenticated user "
            "for the selected resume."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    resume_context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    prompt = f"""
You are the Job Match Specialist inside CareerPilot AI.

{user_context}

JOB DESCRIPTION

{job_description}

RETRIEVED RESUME EVIDENCE

{resume_context}

Your task is to compare the candidate's resume with the job description.

Return:

1. Overall Match Score from 0 to 100
2. Strongly Matched Requirements
3. Partially Matched Requirements
4. Missing or Weak Requirements
5. Resume Improvements
6. Priority Action Plan

Rules:

- Use only evidence from the retrieved resume context.
- Do not invent experience.
- Do not claim the candidate has skills that are not present.
- Explain the reasoning behind the match score.
- Prioritize realistic improvements for an entry-level candidate.

User request:

{user_message}
"""

    result = model.invoke(
        prompt
    )

    response_text = normalize_response(
        result.content
    )

    return {
        "response": response_text,
        "messages": [
            AIMessage(
                content=response_text
            )
        ],
    }


builder = StateGraph(
    CareerState
)


builder.add_node(
    "career_plan_start",
    career_plan_start_node,
)

builder.add_node(
    "workflow_job_match",
    workflow_job_match_node,
)

builder.add_node(
    "workflow_skill_gap",
    workflow_skill_gap_node,
)

builder.add_node(
    "career_planner",
    career_planner_node,
)

builder.add_node(
    "intent_router",
    intent_router_node,
)

builder.add_node(
    "job_match_advisor",
    job_match_advisor_node,
)

builder.add_node(
    "career_advisor",
    career_advisor_node,
)

builder.add_node(
    "resume_advisor",
    resume_advisor_node,
)

builder.add_node(
    "interview_advisor",
    interview_advisor_node,
)

builder.add_node(
    "skill_gap_advisor",
    skill_gap_advisor_node,
)


builder.add_edge(
    START,
    "intent_router",
)


builder.add_conditional_edges(
    "intent_router",
    route_intent,
)


builder.add_edge(
    "job_match_advisor",
    END,
)

builder.add_edge(
    "skill_gap_advisor",
    END,
)


builder.add_edge(
    "career_plan_start",
    "workflow_job_match",
)

builder.add_edge(
    "workflow_job_match",
    "workflow_skill_gap",
)

builder.add_edge(
    "workflow_skill_gap",
    "career_planner",
)

builder.add_edge(
    "career_planner",
    END,
)


builder.add_edge(
    "career_advisor",
    END,
)

builder.add_edge(
    "resume_advisor",
    END,
)

builder.add_edge(
    "interview_advisor",
    END,
)


memory = InMemorySaver()


career_router_graph = builder.compile(
    checkpointer=memory
)