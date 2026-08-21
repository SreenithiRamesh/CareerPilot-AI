import json
import os

from fastapi import (
    Depends,
    FastAPI,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from langchain_core.messages import (
    HumanMessage,
)
from pydantic import (
    BaseModel,
    Field,
)
from sqlalchemy.orm import Session

from app.analysis_history_routes import (
    router as analysis_history_router,
)
from app.auth.dependencies import (
    get_current_user,
)
from app.auth_routes import (
    router as auth_router,
)
from app.database import get_db
from app.mock_interview_routes import (
    router as mock_interview_router,
)
from app.models import User
from app.resume_routes import (
    router as resume_router,
)
from app.router_graph import (
    career_router_graph,
)
from app.services.conversation_service import (
    get_or_create_owned_conversation,
)


# ==================================================
# FASTAPI APPLICATION
# ==================================================


app = FastAPI(
    title="CareerPilot AI",
)


# ==================================================
# CORS CONFIGURATION
# ==================================================
#
# Local development:
#
# CORS_ORIGINS=
# http://localhost:5173,http://127.0.0.1:5173
#
# Production:
#
# CORS_ORIGINS can be replaced with the deployed
# CareerPilot frontend / CloudFront URL without
# modifying application source code.
# ==================================================


cors_origins_raw = os.getenv(
    "CORS_ORIGINS",
    (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    ),
)


origins = [
    origin.strip()
    for origin in cors_origins_raw.split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=
        origins,
    allow_credentials=
        True,
    allow_methods=[
        "*",
    ],
    allow_headers=[
        "*",
    ],
)


# ==================================================
# ROUTERS
# ==================================================


app.include_router(
    auth_router
)


app.include_router(
    resume_router
)


app.include_router(
    analysis_history_router
)


app.include_router(
    mock_interview_router
)


# ==================================================
# CHAT SCHEMAS
# ==================================================


class ChatMessage(
    BaseModel
):
    role: str

    content: str


class ChatRequest(
    BaseModel
):
    message: str

    resume_id: int | None = None

    thread_id: str = "default"

    name: str | None = None

    education: str | None = None

    graduation_year: int | None = None

    skills: list[str] = Field(
        default_factory=list
    )

    target_role: str | None = None

    career_goal: str | None = None

    job_description: str | None = None

    history: list[
        ChatMessage
    ] = Field(
        default_factory=list
    )


# ==================================================
# HEALTH CHECK
# ==================================================


@app.get(
    "/health"
)
def health_check():
    """
    Lightweight application health check.

    Used locally and later by Docker / deployment
    infrastructure to verify that the CareerPilot
    backend is running.
    """

    return {
        "status":
            "ok",

        "message":
            (
                "CareerPilot AI backend "
                "is running"
            ),
    }


# ==================================================
# CAREER AI CHAT
# ==================================================


@app.post(
    "/api/chat"
)
def chat(
    request: ChatRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    """
    Execute the authenticated CareerPilot AI
    conversation workflow.
    """

    # --------------------------------------------------
    # 1. Validate conversation ownership
    # --------------------------------------------------
    #
    # If the thread does not exist, CareerPilot
    # creates it for the authenticated user.
    #
    # If the thread already belongs to another user,
    # the conversation service rejects access.
    # --------------------------------------------------

    get_or_create_owned_conversation(
        db=
            db,
        user_id=
            current_user.id,
        thread_id=
            request.thread_id,
    )


    # --------------------------------------------------
    # 2. Configure LangGraph conversation identity
    # --------------------------------------------------

    config = {
        "configurable": {
            "thread_id":
                request.thread_id,
        }
    }


    # --------------------------------------------------
    # 3. Build base graph state
    # --------------------------------------------------

    graph_input = {
        "message":
            request.message,

        "intent":
            "",

        "response":
            "",

        "thread_id":
            request.thread_id,

        # Workflow persistence IDs
        "job_description_id":
            None,

        "job_match_result_id":
            None,

        "skill_gap_report_id":
            None,

        "career_plan_id":
            None,

        # Authenticated ownership
        "user_id":
            current_user.id,

        "resume_id":
            request.resume_id,

        # Current user turn for LangGraph memory
        "messages": [
            HumanMessage(
                content=
                    request.message
            )
        ],
    }


    # --------------------------------------------------
    # 4. Add profile fields only when supplied
    # --------------------------------------------------
    #
    # This prevents blank request values from
    # overwriting information already stored inside
    # LangGraph conversation state.
    # --------------------------------------------------

    if request.name:
        graph_input[
            "name"
        ] = request.name


    if request.education:
        graph_input[
            "education"
        ] = request.education


    if request.graduation_year:
        graph_input[
            "graduation_year"
        ] = str(
            request.graduation_year
        )


    if request.skills:
        graph_input[
            "skills"
        ] = request.skills


    if request.target_role:
        graph_input[
            "target_role"
        ] = request.target_role


    if request.career_goal:
        graph_input[
            "career_goal"
        ] = request.career_goal


    # --------------------------------------------------
    # 5. Add Job Description only when supplied
    # --------------------------------------------------

    if request.job_description:
        graph_input[
            "job_description"
        ] = request.job_description


    # --------------------------------------------------
    # 6. Execute LangGraph workflow
    # --------------------------------------------------

    result = (
        career_router_graph.invoke(
            graph_input,
            config=
                config,
        )
    )


    # --------------------------------------------------
    # 7. Standardize API response
    # --------------------------------------------------
    #
    # Structured analysis intents return nested JSON
    # under "data".
    #
    # Conversational intents return text under
    # "response".
    # --------------------------------------------------

    intent = result[
        "intent"
    ]


    response = result[
        "response"
    ]


    structured_intents = {
        "job_match",
        "skill_gap",
        "career_plan",
    }


    if (
        intent
        in structured_intents
    ):
        try:
            structured_data = (
                json.loads(
                    response
                )
            )


            api_response = {
                "intent":
                    intent,

                "data":
                    structured_data,

                "thread_id":
                    request.thread_id,
            }


            # ------------------------------------------
            # Persisted workflow identifiers
            # ------------------------------------------

            if (
                result.get(
                    "job_description_id"
                )
                is not None
            ):
                api_response[
                    "job_description_id"
                ] = result[
                    "job_description_id"
                ]


            if (
                result.get(
                    "job_match_result_id"
                )
                is not None
            ):
                api_response[
                    "job_match_result_id"
                ] = result[
                    "job_match_result_id"
                ]


            if (
                result.get(
                    "skill_gap_report_id"
                )
                is not None
            ):
                api_response[
                    "skill_gap_report_id"
                ] = result[
                    "skill_gap_report_id"
                ]


            if (
                result.get(
                    "career_plan_id"
                )
                is not None
            ):
                api_response[
                    "career_plan_id"
                ] = result[
                    "career_plan_id"
                ]


            return api_response


        except (
            json.JSONDecodeError,
            TypeError,
        ):
            # Graceful fallback if an expected
            # structured response cannot be decoded.

            return {
                "intent":
                    intent,

                "response":
                    response,

                "thread_id":
                    request.thread_id,
            }


    # --------------------------------------------------
    # 8. Normal conversational response
    # --------------------------------------------------

    return {
        "intent":
            intent,

        "response":
            response,

        "thread_id":
            request.thread_id,
    }