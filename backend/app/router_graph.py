import os
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from app.schemas.ai_outputs import (
    JobMatchOutput,
    SkillGapOutput,
    CareerPlanOutput,
)
from app.resume_rag import (
    get_resume_vector_store,
    resume_exists,
    search_resume,
)
from app.services.workflow_persistence import (
    get_or_create_job_description,
    persist_job_match,
    persist_skill_gap,
    persist_career_plan,
)

load_dotenv()


model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)
job_match_model = model.with_structured_output(
    JobMatchOutput
)
skill_gap_model = model.with_structured_output(
    SkillGapOutput
)
career_plan_model = model.with_structured_output(
    CareerPlanOutput
)

class CareerState(TypedDict):
    message: str
    intent: str
    response: str

    thread_id: str
    user_id: int
    resume_id: int | None

    job_description: str

    # Database IDs created during analysis workflow
    job_description_id: int | None
    job_match_result_id: int | None
    skill_gap_report_id: int | None
    career_plan_id: int | None

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

    # --------------------------------------------------
    # 1. Validate resume availability
    # --------------------------------------------------

    if not resume_exists(
        thread_id
    ):
        return {
            "job_match_analysis": (
                "Resume is not indexed "
                "for this conversation."
            )
        }

    # --------------------------------------------------
    # 2. Validate job description
    # --------------------------------------------------

    if not job_description.strip():
        return {
            "job_match_analysis": (
                "Job description was not provided."
            )
        }

    # --------------------------------------------------
    # 3. Validate resume ID
    # --------------------------------------------------

    resume_id = state.get(
        "resume_id"
    )

    if resume_id is None:
        return {
            "job_match_analysis": (
                "CareerPilot could not run the "
                "job-match workflow because "
                "no resume ID was provided."
            )
        }

    # --------------------------------------------------
    # 4. Open persistent Chroma collection
    # --------------------------------------------------

    vector_store = get_resume_vector_store(
        thread_id
    )

    # --------------------------------------------------
    # 5. Build authenticated ownership filters
    # --------------------------------------------------

    filters = get_resume_filters(
        state
    )

    # --------------------------------------------------
    # 6. Retrieve relevant resume evidence
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 7. Build grounded resume context
    # --------------------------------------------------

    resume_context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    # --------------------------------------------------
    # 8. Build structured Job Match prompt
    # --------------------------------------------------

    prompt = f"""
You are the Job Match Analysis Agent inside CareerPilot AI.

Your responsibility is to compare the candidate's resume
against the provided job description and produce an
evidence-grounded structured job-match assessment.

USER PROFILE

{user_context}

JOB DESCRIPTION

{job_description}

RESUME EVIDENCE

{resume_context}

Analyze the candidate's match for this role.

Evaluate:

- overall match score from 0 to 100
- strongly matched requirements
- partially matched requirements
- missing skills or requirements
- resume improvements
- priority actions

Important rules:

- Use only the retrieved resume evidence.
- Do not invent experience, projects, skills, certifications,
  achievements, or metrics.
- Do not claim that the candidate has a skill unless the
  resume evidence supports it.
- A partial match may be used when related evidence exists,
  but the exact requirement is not clearly demonstrated.
- Keep every result concise and specific.
- The match score must reflect the actual evidence.
- Do not exaggerate the candidate's readiness.
"""

    # --------------------------------------------------
    # 9. Generate structured JobMatchOutput
    # --------------------------------------------------

    try:
        result = job_match_model.invoke(
            prompt
        )

    except Exception:
        return {
            "job_match_analysis": (
                "CareerPilot could not generate "
                "the structured job-match analysis."
            )
        }

    # --------------------------------------------------
    # 10. Persist Job Description + Job Match
    # --------------------------------------------------

    try:
        job_description_id = (
            get_or_create_job_description(
                user_id=state["user_id"],
                description_text=job_description,
            )
        )

        job_match_result_id = (
            persist_job_match(
                user_id=state["user_id"],
                resume_id=resume_id,
                job_description_id=job_description_id,
                result=result,
            )
        )

    except Exception:
        return {
            "job_match_analysis": (
                "CareerPilot generated the job-match "
                "analysis but could not save it."
            )
        }

    # --------------------------------------------------
    # 11. Convert structured result to JSON
    # --------------------------------------------------

    analysis = result.model_dump_json(
        indent=2
    )

    # --------------------------------------------------
    # 12. Return structured result + persistence IDs
    # --------------------------------------------------

    return {
        "job_match_analysis": analysis,
        "job_description_id": (
            job_description_id
        ),
        "job_match_result_id": (
            job_match_result_id
        ),
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

    # --------------------------------------------------
    # 1. Validate resume availability
    # --------------------------------------------------

    if not resume_exists(
        thread_id
    ):
        response_text = (
            "I do not have your resume indexed yet. "
            "Please upload your resume first."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 2. Validate job description
    # --------------------------------------------------

    if not job_description.strip():
        response_text = (
            "Please provide the job description "
            "so I can identify your skill gaps "
            "for that role."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 3. Validate resume ID
    # --------------------------------------------------

    resume_id = state.get(
        "resume_id"
    )

    if resume_id is None:
        response_text = (
            "CareerPilot could not run the skill-gap "
            "analysis because no resume ID was provided."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 4. Open persistent Chroma collection
    # --------------------------------------------------

    vector_store = get_resume_vector_store(
        thread_id
    )

    # --------------------------------------------------
    # 5. Build authenticated ownership filters
    # --------------------------------------------------

    filters = get_resume_filters(
        state
    )

    # --------------------------------------------------
    # 6. Retrieve resume evidence
    # --------------------------------------------------

    retrieved_docs = search_resume(
        vector_store,
        job_description,
        k=5,
        user_id=filters["user_id"],
        resume_id=filters["resume_id"],
    )

    # --------------------------------------------------
    # 7. Handle missing / unauthorized resume evidence
    # --------------------------------------------------

    if not retrieved_docs:
        response_text = (
            "I could not find resume evidence "
            "owned by your account for the selected resume."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 8. Build evidence-grounded resume context
    # --------------------------------------------------

    resume_context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    # --------------------------------------------------
    # 9. Structured Skill Gap prompt
    # --------------------------------------------------

    prompt = f"""
You are the Skill Gap Specialist inside CareerPilot AI.

Your responsibility is to identify the candidate's skill gaps
for the specific job description using only the retrieved
resume evidence.

USER PROFILE

{user_context}

JOB DESCRIPTION

{job_description}

RETRIEVED RESUME EVIDENCE

{resume_context}

CURRENT USER REQUEST

{user_message}

Analyze the candidate's readiness for this role.

Evaluate:

- skills clearly demonstrated in the resume
- required skills that are missing
- skills that are only partially demonstrated
- high-priority skill gaps
- medium-priority skill gaps
- low-priority skill gaps
- recommended learning order
- practical tasks for improving high-priority gaps
- proof-of-skill actions the candidate can add to their portfolio
- 2 to 3 portfolio project recommendations that help close the most important gaps
- a short readiness summary

Portfolio project recommendation requirements:

Each portfolio project recommendation must contain:

- target_skill
- project_title
- project_goal
- suggested_stack
- implementation_steps
- portfolio_evidence

The purpose of these recommendations is to help the candidate
create visible, resume-worthy proof for important missing or
partially demonstrated skills.

Important rules:

- Use only the retrieved resume evidence when deciding what skills
  the candidate currently has.
- Do not invent skills, projects, experience, certifications,
  achievements, or metrics.
- A skill should be considered missing when the job description
  requires it and the resume evidence does not support it.
- A skill may be considered partially demonstrated when related
  evidence exists but the exact requirement is not clearly shown.
- Prioritize gaps based on their importance to this exact job.
- Keep recommendations realistic for an entry-level candidate.
- Do not recommend learning everything at once.
- Recommended learning order should focus on the highest-value
  gaps first.
- Practice tasks should be concrete and achievable.
- Proof-of-skill actions should result in portfolio, GitHub,
  project, deployment, or resume evidence.

Portfolio project rules:

- Generate only 2 to 3 portfolio project recommendations.
- Each project must address one or more important missing or
  partially demonstrated skills.
- Projects must be relevant to this specific job description.
- Do not recommend random generic projects.
- Prefer projects that combine new skills with technologies the
  candidate already demonstrates.
- Keep project scope realistic for an entry-level candidate.
- Avoid requiring too many unfamiliar technologies in one project.
- suggested_stack should normally contain 3 to 6 technologies.
- implementation_steps should be ordered, concise, and practical.
- portfolio_evidence should describe visible proof such as:
  GitHub repositories, README documentation, tests, deployment,
  architecture documentation, screenshots, API documentation,
  or resume-ready project evidence.
- Never claim that a recommended project has already been completed.
- Do not fabricate GitHub links, deployments, metrics, or achievements.
- Keep every list item concise and specific.
"""

    # --------------------------------------------------
    # 10. Generate structured SkillGapOutput
    # --------------------------------------------------

    try:
        result = skill_gap_model.invoke(
            prompt
        )

    except Exception:
        response_text = (
            "CareerPilot could not generate the "
            "structured skill-gap analysis right now."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 11. Resolve / create Job Description row
    # --------------------------------------------------

    job_description_id = state.get(
        "job_description_id"
    )

    try:
        if job_description_id is None:
            job_description_id = (
                get_or_create_job_description(
                    user_id=state["user_id"],
                    description_text=job_description,
                )
            )

        # --------------------------------------------------
        # 12. Persist Skill Gap result into MySQL
        # --------------------------------------------------

        skill_gap_report_id = (
            persist_skill_gap(
                user_id=state["user_id"],
                resume_id=resume_id,
                job_description_id=job_description_id,
                result=result,
            )
        )

    except Exception:
        response_text = (
            "CareerPilot generated the skill-gap analysis "
            "but could not save the result right now."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 13. Convert structured result to predictable JSON
    # --------------------------------------------------

    response_text = result.model_dump_json(
        indent=2
    )

    # --------------------------------------------------
    # 14. Return structured result + database IDs
    # --------------------------------------------------

    return {
        "response": response_text,
        "skill_gap_analysis": response_text,

        "job_description_id": (
            job_description_id
        ),

        "skill_gap_report_id": (
            skill_gap_report_id
        ),

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

    # --------------------------------------------------
    # 1. Validate workflow inputs
    # --------------------------------------------------

    if not job_description.strip():
        return {
            "skill_gap_analysis": (
                "CareerPilot could not run the skill-gap "
                "workflow because no job description was provided."
            )
        }

    if not job_match_analysis.strip():
        return {
            "skill_gap_analysis": (
                "CareerPilot could not run the skill-gap "
                "workflow because no job-match analysis was available."
            )
        }

    resume_id = state.get(
        "resume_id"
    )

    if resume_id is None:
        return {
            "skill_gap_analysis": (
                "CareerPilot could not run the skill-gap "
                "workflow because no resume ID was provided."
            )
        }

    # --------------------------------------------------
    # 2. Build structured Skill Gap prompt
    # --------------------------------------------------

    prompt = f"""
You are the Skill Gap Analysis Agent inside CareerPilot AI.

Your responsibility is to identify the candidate's
skill gaps for this exact job using the completed
job-match analysis.

JOB DESCRIPTION

{job_description}

JOB MATCH ANALYSIS

{job_match_analysis}

Analyze the candidate's readiness for this role.

Evaluate:

- existing skills demonstrated by the candidate
- missing skills required by the job
- partially demonstrated skills
- high-priority gaps
- medium-priority gaps
- low-priority gaps
- recommended learning order
- practical tasks for improving the important gaps
- proof-of-skill actions
- 2 to 3 portfolio project recommendations that help close the most important gaps
- a concise readiness summary

Portfolio project recommendation requirements:

Each portfolio project recommendation must contain:

- target_skill
- project_title
- project_goal
- suggested_stack
- implementation_steps
- portfolio_evidence

Important rules:

- Use the job description and job-match analysis as the evidence base.
- Do not invent requirements that are not present in the job description.
- Do not invent skills or experience for the candidate.
- Prioritize gaps based on their importance to this exact role.
- Keep recommendations realistic for an entry-level candidate.
- Do not recommend learning everything at once.
- Keep every list item concise, practical, and specific.

Portfolio project rules:

- Generate only 2 to 3 portfolio project recommendations.
- Each recommendation must address one or more important missing
  or partially demonstrated skills.
- Projects must directly support this job description.
- Prefer projects that combine missing skills with technologies
  already demonstrated by the candidate.
- Keep project scope achievable for an entry-level candidate.
- Avoid requiring too many unfamiliar technologies at once.
- suggested_stack should normally contain 3 to 6 technologies.
- implementation_steps should be ordered, concrete, and practical.
- portfolio_evidence should describe visible proof that could
  strengthen GitHub, portfolio, deployment, documentation,
  or future resume evidence.
- Do not claim that the candidate has already completed any
  recommended project.
- Do not fabricate metrics, GitHub links, deployments,
  certifications, or achievements.
"""

    # --------------------------------------------------
    # 3. Generate structured SkillGapOutput
    # --------------------------------------------------

    try:
        result = skill_gap_model.invoke(
            prompt
        )

    except Exception:
        return {
            "skill_gap_analysis": (
                "CareerPilot could not generate "
                "the structured skill-gap analysis."
            )
        }

    # --------------------------------------------------
    # 4. Resolve Job Description ID
    # --------------------------------------------------

    job_description_id = state.get(
        "job_description_id"
    )

    try:
        if job_description_id is None:
            job_description_id = (
                get_or_create_job_description(
                    user_id=state["user_id"],
                    description_text=job_description,
                )
            )

        # --------------------------------------------------
        # 5. Persist Skill Gap result
        # --------------------------------------------------

        skill_gap_report_id = (
            persist_skill_gap(
                user_id=state["user_id"],
                resume_id=resume_id,
                job_description_id=job_description_id,
                result=result,
            )
        )

    except Exception:
        return {
            "skill_gap_analysis": (
                "CareerPilot generated the skill-gap "
                "analysis but could not save it."
            )
        }

    # --------------------------------------------------
    # 6. Convert structured result to JSON
    # --------------------------------------------------

    analysis = result.model_dump_json(
        indent=2
    )

    # --------------------------------------------------
    # 7. Return structured output + DB IDs
    # --------------------------------------------------

    return {
        "skill_gap_analysis": analysis,
        "job_description_id": (
            job_description_id
        ),
        "skill_gap_report_id": (
            skill_gap_report_id
        ),
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

    # --------------------------------------------------
    # 1. Validate workflow inputs
    # --------------------------------------------------

    if not job_description.strip():
        response_text = (
            "Please provide the job description "
            "so I can create a role-specific career plan."
        )

        return {
            "career_plan": response_text,
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    if not job_match_analysis.strip():
        response_text = (
            "CareerPilot could not find a completed "
            "job-match analysis for this workflow."
        )

        return {
            "career_plan": response_text,
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    if not skill_gap_analysis.strip():
        response_text = (
            "CareerPilot could not find a completed "
            "skill-gap analysis for this workflow."
        )

        return {
            "career_plan": response_text,
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 2. Build structured career planning prompt
    # --------------------------------------------------

    prompt = f"""
You are the Career Planning Specialist inside CareerPilot AI.

Your responsibility is to create a realistic, prioritized,
and actionable preparation roadmap for an entry-level candidate.

Use the candidate's profile, the job description,
the job-match analysis, and the skill-gap analysis.

USER PROFILE

{user_context}

JOB DESCRIPTION

{job_description}

JOB MATCH ANALYSIS

{job_match_analysis}

SKILL GAP ANALYSIS

{skill_gap_analysis}

Create a practical career preparation roadmap.

Evaluate and return:

- a concise readiness summary
- the candidate's top priorities
- the recommended learning order
- practical learning and implementation tasks
- portfolio evidence the candidate should build
- interview preparation focus
- a realistic 30-day action plan

Important rules:

- Base the roadmap on the supplied job-match and skill-gap evidence.
- Do not invent skills, experience, projects, achievements,
  certifications, or metrics.
- Do not recommend skills the candidate already demonstrates
  unless deeper knowledge is clearly required for the role.
- Prioritize the highest-value gaps first.
- Keep the roadmap realistic for an entry-level candidate.
- Do not overload the candidate with unnecessary technologies.
- Practical tasks should create visible proof of skill.
- Portfolio actions should result in useful GitHub, project,
  deployment, or resume evidence.
- Interview preparation should focus on the candidate's actual
  target role and identified gaps.
- The 30-day plan should be sequential, achievable,
  and focused on job readiness.
- Keep every list item concise and actionable.
"""

    # --------------------------------------------------
    # 3. Generate structured CareerPlanOutput
    # --------------------------------------------------

    try:
        result = career_plan_model.invoke(
            prompt
        )

    except Exception:
        response_text = (
            "CareerPilot could not generate the "
            "structured career plan right now."
        )

        return {
            "career_plan": response_text,
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 4. Read related persisted workflow IDs
    # --------------------------------------------------

    job_match_result_id = state.get(
        "job_match_result_id"
    )

    skill_gap_report_id = state.get(
        "skill_gap_report_id"
    )

    # --------------------------------------------------
    # 5. Persist Career Plan into MySQL
    # --------------------------------------------------

    try:
        career_plan_id = persist_career_plan(
            user_id=state["user_id"],
            job_match_result_id=job_match_result_id,
            skill_gap_report_id=skill_gap_report_id,
            result=result,
        )

    except Exception:
        response_text = (
            "CareerPilot generated the career plan "
            "but could not save it right now."
        )

        return {
            "career_plan": response_text,
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 6. Convert structured result to JSON
    # --------------------------------------------------

    career_plan = result.model_dump_json(
        indent=2
    )

    # --------------------------------------------------
    # 7. Return structured result + DB ID
    # --------------------------------------------------

    return {
        "career_plan": career_plan,
        "career_plan_id": career_plan_id,
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

    # --------------------------------------------------
    # 1. Validate resume availability
    # --------------------------------------------------

    if not resume_exists(
        thread_id
    ):
        response_text = (
            "I do not have your resume indexed yet. "
            "Please upload your resume first."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 2. Validate job description
    # --------------------------------------------------

    if not job_description.strip():
        response_text = (
            "Please provide the job description "
            "so I can compare it with your resume."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 3. Validate resume ID
    # --------------------------------------------------

    resume_id = state.get(
        "resume_id"
    )

    if resume_id is None:
        response_text = (
            "CareerPilot could not run the job-match "
            "analysis because no resume ID was provided."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 4. Open persistent Chroma collection
    # --------------------------------------------------

    vector_store = get_resume_vector_store(
        thread_id
    )

    # --------------------------------------------------
    # 5. Build authenticated ownership filters
    # --------------------------------------------------

    filters = get_resume_filters(
        state
    )

    # --------------------------------------------------
    # 6. Retrieve resume evidence
    # --------------------------------------------------

    retrieved_docs = search_resume(
        vector_store,
        job_description,
        k=5,
        user_id=filters["user_id"],
        resume_id=filters["resume_id"],
    )

    # --------------------------------------------------
    # 7. Handle missing / unauthorized evidence
    # --------------------------------------------------

    if not retrieved_docs:
        response_text = (
            "I could not find resume evidence "
            "owned by your account for the selected resume."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 8. Build grounded resume context
    # --------------------------------------------------

    resume_context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    # --------------------------------------------------
    # 9. Structured Job Match prompt
    # --------------------------------------------------

    prompt = f"""
You are the Job Match Specialist inside CareerPilot AI.

Your responsibility is to compare the candidate's resume evidence
against the provided job description and return an evidence-grounded
job-match assessment.

USER PROFILE

{user_context}

JOB DESCRIPTION

{job_description}

RETRIEVED RESUME EVIDENCE

{resume_context}

CURRENT USER REQUEST

{user_message}

Analyze the candidate's resume against the job description.

Evaluate:

- overall match score from 0 to 100
- strongly matched requirements
- partially matched requirements
- missing skills or requirements
- resume improvements
- priority actions

Important rules:

- Use only the retrieved resume evidence when deciding what the candidate has.
- Do not invent experience, projects, certifications, technologies, or achievements.
- Do not claim that the candidate knows a skill unless the resume evidence supports it.
- A skill may be considered partially matched when related evidence exists but the exact requirement is not clearly demonstrated.
- Keep every list item concise, specific, and useful.
- Resume improvements must describe realistic changes the candidate can make.
- Priority actions should focus on the most important gaps for this specific role.
- The match score must reflect the strength of actual evidence rather than general similarity.
- Do not exaggerate the candidate's readiness.
"""

    # --------------------------------------------------
    # 10. Generate structured JobMatchOutput
    # --------------------------------------------------

    try:
        result = job_match_model.invoke(
            prompt
        )

    except Exception:
        response_text = (
            "CareerPilot could not generate the "
            "structured job-match analysis right now."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 11. Persist JD + Job Match result into MySQL
    # --------------------------------------------------

    try:
        job_description_id = (
            get_or_create_job_description(
                user_id=state["user_id"],
                description_text=job_description,
            )
        )

        job_match_result_id = (
            persist_job_match(
                user_id=state["user_id"],
                resume_id=resume_id,
                job_description_id=job_description_id,
                result=result,
            )
        )

    except Exception:
        response_text = (
            "CareerPilot generated the job-match analysis "
            "but could not save the result right now."
        )

        return {
            "response": response_text,
            "messages": [
                AIMessage(
                    content=response_text
                )
            ],
        }

    # --------------------------------------------------
    # 12. Convert structured result to JSON
    # --------------------------------------------------

    response_text = result.model_dump_json(
        indent=2
    )

    # --------------------------------------------------
    # 13. Return result + database IDs to LangGraph state
    # --------------------------------------------------

    return {
        "response": response_text,
        "job_match_analysis": response_text,

        "job_description_id": (
            job_description_id
        ),

        "job_match_result_id": (
            job_match_result_id
        ),

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


LANGGRAPH_DATABASE_URL = os.getenv(
    "LANGGRAPH_DATABASE_URL"
)

if not LANGGRAPH_DATABASE_URL:
    raise RuntimeError(
        "LANGGRAPH_DATABASE_URL is not configured."
    )


_mysql_saver_context = (
    PyMySQLSaver.from_conn_string(
        LANGGRAPH_DATABASE_URL
    )
)

memory = _mysql_saver_context.__enter__()


career_router_graph = builder.compile(
    checkpointer=memory
)