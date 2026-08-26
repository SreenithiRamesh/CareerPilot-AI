
import json
import logging
import os

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    status,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from app.conversation_routes import (
    router as conversation_router,
)
from langchain_core.messages import (
    HumanMessage,
)

from pydantic import (
    BaseModel,
    Field,
)
from app.agent_history_routes import (
    router as agent_history_router,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent_routes import (
    router as agent_router,
)
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
from app.models import (
    SkillGapReport,
    User,
)
from app.resume_routes import (
    router as resume_router,
)
from app.router_graph import (
    career_router_graph,
)
from app.services.conversation_service import (
    get_conversation_message_by_request,
    get_or_create_owned_conversation,
    save_conversation_message,
)


logger = logging.getLogger(__name__)

# ============================================================
# PERSISTED SKILL GAP CONTEXT
# ============================================================


def _parse_json_value(
    value: str | None,
    fallback,
):
    """
    Safely deserialize JSON stored in MySQL TEXT columns.
    """

    if not value:
        return fallback

    try:
        parsed = json.loads(
            value
        )

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return fallback

    return parsed


def _load_latest_skill_gap_context(
    db: Session,
    *,
    user_id: int,
    resume_id: int,
) -> tuple[int, str] | None:
    """
    Load the newest Skill Gap report owned by the
    authenticated user for the selected resume.

    The returned JSON string follows the same public
    SkillGapOutput shape used by CareerPilot's graph,
    allowing a fresh Career AI conversation to reuse
    persisted analysis without rerunning Skill Gap.
    """

    report = db.scalar(
        select(
            SkillGapReport
        )
        .where(
            SkillGapReport.user_id
            == user_id,
            SkillGapReport.resume_id
            == resume_id,
        )
        .order_by(
            SkillGapReport.created_at.desc()
        )
        .limit(1)
    )

    if report is None:
        return None

    priority_gaps = (
        _parse_json_value(
            report.priority_gaps,
            {},
        )
    )

    if not isinstance(
        priority_gaps,
        dict,
    ):
        priority_gaps = {}

    context = {
        "existing_skills":
            _parse_json_value(
                report.existing_skills,
                [],
            ),

        "missing_skills":
            _parse_json_value(
                report.missing_skills,
                [],
            ),

        "partially_demonstrated_skills":
            _parse_json_value(
                report.partial_skills,
                [],
            ),

        "high_priority_gaps":
            priority_gaps.get(
                "high",
                [],
            )
            or [],

        "medium_priority_gaps":
            priority_gaps.get(
                "medium",
                [],
            )
            or [],

        "low_priority_gaps":
            priority_gaps.get(
                "low",
                [],
            )
            or [],

        "recommended_learning_order":
            _parse_json_value(
                report.learning_order,
                [],
            ),

        "practice_tasks":
            _parse_json_value(
                report.practice_tasks,
                [],
            ),

        "proof_of_skill_actions":
            _parse_json_value(
                report.proof_of_skill_actions,
                [],
            ),

        "portfolio_project_prompts":
            _parse_json_value(
                report.portfolio_project_prompts,
                [],
            ),

        "readiness_summary":
            report.readiness_summary
            or "",
    }

    return (
        report.id,
        json.dumps(
            context,
            ensure_ascii=False,
            indent=2,
        ),
    )


# ============================================================
# FASTAPI APPLICATION
# ============================================================


app = FastAPI(
    title="CareerPilot AI",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================
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
# ============================================================


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


# ============================================================
# ROUTERS
# ============================================================


app.include_router(
    auth_router
)

app.include_router(
    conversation_router
)
app.include_router(
    resume_router
)
app.include_router(
    agent_history_router
)

app.include_router(
    analysis_history_router
)


app.include_router(
    mock_interview_router
)


# ============================================================
# AGENTIC CAREER AI ROUTER
# ============================================================


app.include_router(
    agent_router
)


# ============================================================
# CHAT SCHEMAS
# ============================================================


class ChatMessage(
    BaseModel
):
    role: str

    content: str


class ChatRequest(
    BaseModel
):
    message: str

    request_id: str = Field(
        min_length=1,
        max_length=64,
    )

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


# ============================================================
# HEALTH CHECK
# ============================================================


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


# ============================================================
# CAREER AI CHAT
# ============================================================


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

    # --------------------------------------------------------
    # 1. Validate conversation ownership
    # --------------------------------------------------------
    #
    # If the thread does not exist, CareerPilot
    # creates it for the authenticated user.
    #
    # If the thread already belongs to another user,
    # the conversation service rejects access.
    # --------------------------------------------------------

    conversation = (
        get_or_create_owned_conversation(
            db=
                db,
            user_id=
                current_user.id,
            thread_id=
                request.thread_id,
            resume_id=
                request.resume_id,
        )
    )


    normalized_request_id = (
        request.request_id.strip()
    )

    save_conversation_message(
        db,
        conversation=conversation,
        role="user",
        content=request.message,
        request_id=normalized_request_id,
    )

    cached_assistant_message = (
        get_conversation_message_by_request(
            db,
            conversation=conversation,
            request_id=normalized_request_id,
            role="assistant",
        )
    )

    if cached_assistant_message is not None:
        if not cached_assistant_message.response_payload:
            logger.error(
                "Assistant message %s has no cached "
                "response payload.",
                cached_assistant_message.id,
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "The cached CareerPilot response "
                    "is unavailable."
                ),
            )

        try:
            cached_response = json.loads(
                cached_assistant_message.response_payload
            )

        except (
            json.JSONDecodeError,
            TypeError,
        ) as exc:
            logger.exception(
                "Could not decode cached chat response "
                "for request %s.",
                normalized_request_id,
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "The cached CareerPilot response "
                    "is invalid."
                ),
            ) from exc

        if not isinstance(cached_response, dict):
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "The cached CareerPilot response "
                    "has an invalid format."
                ),
            )

        return cached_response


    # --------------------------------------------------------
    # 2. Configure LangGraph conversation identity
    # --------------------------------------------------------

    config = {
        "configurable": {
            "thread_id":
                request.thread_id,
        }
    }


    # --------------------------------------------------------
    # 3. Build base graph state
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # 4. Add profile fields only when supplied
    # --------------------------------------------------------
    #
    # This prevents blank request values from
    # overwriting information already stored inside
    # LangGraph conversation state.
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # 5. Add Job Description only when supplied
    # --------------------------------------------------------

    if request.job_description:
        graph_input[
            "job_description"
        ] = request.job_description


    # --------------------------------------------------------
    # 6. Hydrate latest persisted Skill Gap when useful
    # --------------------------------------------------------
    #
    # Career AI general conversations normally send a
    # resume_id but no job_description. In that case,
    # load the newest saved Skill Gap report for the
    # same authenticated user + selected resume.
    #
    # Structured Job Match / Skill Gap / Career Plan
    # requests already send their own job_description,
    # so we intentionally do not inject an older report
    # into those workflows.
    # --------------------------------------------------------

    if (
        request.resume_id is not None
        and not request.job_description
    ):
        latest_skill_gap = (
            _load_latest_skill_gap_context(
                db,
                user_id=
                    current_user.id,
                resume_id=
                    request.resume_id,
            )
        )

        if latest_skill_gap is not None:
            (
                skill_gap_report_id,
                skill_gap_analysis,
            ) = latest_skill_gap

            graph_input[
                "skill_gap_report_id"
            ] = skill_gap_report_id

            graph_input[
                "skill_gap_analysis"
            ] = skill_gap_analysis


    # --------------------------------------------------------
    # 7. Execute LangGraph workflow
    # --------------------------------------------------------

    try:
        result = career_router_graph.invoke(
            graph_input,
            config=config,
        )

    except Exception as exc:
        logger.exception(
            "CareerPilot graph execution failed "
            "for request %s.",
            normalized_request_id,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "CareerPilot could not complete this "
                "request. Please retry using the same "
                "request ID."
            ),
        ) from exc


    # --------------------------------------------------------
    # 8. Standardize API response
    # --------------------------------------------------------
    #
    # Structured analysis intents return nested JSON
    # under "data".
    #
    # Conversational intents return text under
    # "response".
    # --------------------------------------------------------

    intent = result[
        "intent"
    ]


    response = result[
        "response"
    ]


    if isinstance(
        response,
        str,
    ):
        assistant_content = (
            response.strip()
        )

    else:
        assistant_content = (
            json.dumps(
                response,
                ensure_ascii=False,
                default=str,
            )
        )


    if not assistant_content:
        logger.error(
            "CareerPilot returned an empty response "
            "for request %s.",
            normalized_request_id,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "CareerPilot returned an empty "
                "response. Please retry using the "
                "same request ID."
            ),
        )


    response = assistant_content


    def persist_chat_response(
        api_response: dict,
    ) -> dict:
        completed_response = {
            **api_response,
            "request_id": normalized_request_id,
        }

        serialized_response = json.dumps(
            completed_response,
            ensure_ascii=False,
            default=str,
        )

        saved_assistant_message = (
            save_conversation_message(
                db,
                conversation=conversation,
                role="assistant",
                content=assistant_content,
                request_id=normalized_request_id,
                response_payload=serialized_response,
            )
        )

        if saved_assistant_message.response_payload:
            try:
                persisted_response = json.loads(
                    saved_assistant_message.response_payload
                )

            except (
                json.JSONDecodeError,
                TypeError,
            ) as exc:
                logger.exception(
                    "Could not decode persisted chat "
                    "response for request %s.",
                    normalized_request_id,
                )

                raise HTTPException(
                    status_code=(
                        status.HTTP_500_INTERNAL_SERVER_ERROR
                    ),
                    detail=(
                        "CareerPilot saved an invalid "
                        "response payload."
                    ),
                ) from exc

            if isinstance(persisted_response, dict):
                return persisted_response

        return completed_response


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


            # ----------------------------------------------
            # Persisted workflow identifiers
            # ----------------------------------------------

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


            return persist_chat_response(
                api_response
            )


        except (
            json.JSONDecodeError,
            TypeError,
        ):
            # Graceful fallback if an expected
            # structured response cannot be decoded.

            return persist_chat_response(
                {
                    "intent": intent,
                    "response": response,
                    "thread_id": request.thread_id,
                }
            )


    # --------------------------------------------------------
    # 9. Normal conversational response
    # --------------------------------------------------------

    return persist_chat_response(
        {
            "intent": intent,
            "response": response,
            "thread_id": request.thread_id,
        }
    )