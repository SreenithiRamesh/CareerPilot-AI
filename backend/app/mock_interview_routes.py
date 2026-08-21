import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from langchain_google_genai.chat_models import (
    ChatGoogleGenerativeAIError,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
)
from app.database import get_db
from app.models import User
from app.schemas.mock_interview import (
    MockInterviewAnswerRequest,
    MockInterviewStartRequest,
)
from app.services.mock_interview_session_service import (
    create_mock_interview_session,
    get_owned_job_description,
    get_owned_mock_interview_session,
    get_owned_resume,
    get_owned_skill_gap_report,
    process_interview_answer,
    serialize_mock_interview_session,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/interview",
    tags=["Mock Interview"],
)


# ==================================================
# AI ERROR HELPERS
# ==================================================


def _is_quota_error(
    exc: Exception,
) -> bool:
    """
    Detect Gemini quota / rate-limit errors.

    LangChain wraps Gemini provider failures
    inside ChatGoogleGenerativeAIError.

    CareerPilot converts quota failures into
    HTTP 429 responses instead of exposing them
    as generic server errors.
    """

    message = str(
        exc
    ).lower()


    quota_markers = (
        "resource_exhausted",
        "quota exceeded",
        "too many requests",
        "rate limit",
        "429",
    )


    return any(
        marker in message
        for marker
        in quota_markers
    )


def _raise_ai_error(
    exc: Exception,
    *,
    fallback_message: str,
) -> None:
    """
    Convert Gemini provider failures into
    appropriate HTTP responses.

    Quota / rate-limit errors:
        429 Too Many Requests

    Other AI-provider errors:
        502 Bad Gateway
    """

    if _is_quota_error(
        exc
    ):
        raise HTTPException(
            status_code=
                status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "CareerPilot's AI request limit "
                "has been reached temporarily. "
                "Please wait a moment and try again."
            ),
        ) from exc


    raise HTTPException(
        status_code=
            status.HTTP_502_BAD_GATEWAY,
        detail=
            fallback_message,
    ) from exc


# ==================================================
# START INTERVIEW
# ==================================================


@router.post(
    "/start",
    status_code=
        status.HTTP_201_CREATED,
)
def start_mock_interview(
    request: MockInterviewStartRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    """
    Start a new Mock Interview session.

    CareerPilot validates:

    - authenticated ownership
    - resume existence
    - optional Job Description ownership
    - optional Skill Gap ownership
    - provenance consistency

    The session service generates the complete
    interview question set and persists it before
    returning Question 1.
    """

    # --------------------------------------------------
    # 1. Validate owned resume
    # --------------------------------------------------

    resume = get_owned_resume(
        db,
        user_id=
            current_user.id,
        resume_id=
            request.resume_id,
    )


    if resume is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Resume was not found."
            ),
        )


    # --------------------------------------------------
    # 2. Validate optional Job Description
    # --------------------------------------------------

    job_description = None


    if (
        request.job_description_id
        is not None
    ):
        job_description = (
            get_owned_job_description(
                db,
                user_id=
                    current_user.id,
                job_description_id=
                    request.job_description_id,
            )
        )


        if (
            job_description
            is None
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Job description "
                    "was not found."
                ),
            )


    # --------------------------------------------------
    # 3. Validate optional Skill Gap report
    # --------------------------------------------------

    skill_gap_report = None


    if (
        request.skill_gap_report_id
        is not None
    ):
        skill_gap_report = (
            get_owned_skill_gap_report(
                db,
                user_id=
                    current_user.id,
                skill_gap_report_id=
                    request.skill_gap_report_id,
            )
        )


        if (
            skill_gap_report
            is None
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Skill Gap report "
                    "was not found."
                ),
            )


    # --------------------------------------------------
    # 4. Validate provenance consistency
    # --------------------------------------------------

    if (
        skill_gap_report
        is not None
        and
        skill_gap_report.resume_id
        != resume.id
    ):
        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,
            detail=(
                "The selected Skill Gap report "
                "belongs to a different resume."
            ),
        )


    if (
        skill_gap_report
        is not None
        and
        job_description
        is not None
        and
        skill_gap_report.job_description_id
        != job_description.id
    ):
        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,
            detail=(
                "The selected Skill Gap report "
                "belongs to a different "
                "job description."
            ),
        )


    # --------------------------------------------------
    # 5. Create session
    # --------------------------------------------------

    try:
        session, first_question = (
            create_mock_interview_session(
                db,
                user_id=
                    current_user.id,

                resume=
                    resume,

                job_description=
                    job_description,

                skill_gap_report=
                    skill_gap_report,

                interview_type=
                    request.interview_type,

                total_questions=
                    request.total_questions,
            )
        )


    except ChatGoogleGenerativeAIError as exc:
        logger.exception(
            "Mock Interview AI start failed."
        )


        _raise_ai_error(
            exc,
            fallback_message=(
                "CareerPilot's AI provider "
                "could not generate the interview "
                "questions. Please try again."
            ),
        )


    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(
                exc
            ),
        ) from exc


    except Exception as exc:
        logger.exception(
            "Mock Interview start failed."
        )


        raise HTTPException(
            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "CareerPilot could not "
                "start the Mock Interview."
            ),
        ) from exc


    # --------------------------------------------------
    # 6. Response
    # --------------------------------------------------

    return {
        "session_id":
            session.id,

        "status":
            session.status,

        "interview_type":
            session.interview_type,

        "total_questions":
            session.total_questions,

        "current_question":
            first_question,
    }


# ==================================================
# SUBMIT ANSWER
# ==================================================


@router.post(
    "/answer",
)
def submit_mock_interview_answer(
    request: MockInterviewAnswerRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    """
    Evaluate the current interview answer.

    Questions before the final question return:

        feedback
        next_question

    The final question returns:

        feedback
        summary
    """

    # --------------------------------------------------
    # 1. Load owned session
    # --------------------------------------------------

    session = (
        get_owned_mock_interview_session(
            db,
            user_id=
                current_user.id,
            session_id=
                request.session_id,
        )
    )


    if session is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Mock Interview session "
                "was not found."
            ),
        )


    # --------------------------------------------------
    # 2. Validate session status
    # --------------------------------------------------

    if (
        session.status
        == "completed"
    ):
        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,
            detail=(
                "This Mock Interview "
                "has already been completed."
            ),
        )


    if (
        session.status
        != "in_progress"
    ):
        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,
            detail=(
                "This Mock Interview "
                "is not currently active."
            ),
        )


    # --------------------------------------------------
    # 3. Load linked resume
    # --------------------------------------------------

    resume = get_owned_resume(
        db,
        user_id=
            current_user.id,
        resume_id=
            session.resume_id,
    )


    if resume is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Resume linked to this "
                "interview was not found."
            ),
        )


    # --------------------------------------------------
    # 4. Load optional Job Description
    # --------------------------------------------------

    job_description = None


    if (
        session.job_description_id
        is not None
    ):
        job_description = (
            get_owned_job_description(
                db,
                user_id=
                    current_user.id,
                job_description_id=
                    session.job_description_id,
            )
        )


        if (
            job_description
            is None
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Job description linked "
                    "to this interview "
                    "was not found."
                ),
            )


    # --------------------------------------------------
    # 5. Load optional Skill Gap report
    # --------------------------------------------------

    skill_gap_report = None


    if (
        session.skill_gap_report_id
        is not None
    ):
        skill_gap_report = (
            get_owned_skill_gap_report(
                db,
                user_id=
                    current_user.id,
                skill_gap_report_id=
                    session.skill_gap_report_id,
            )
        )


        if (
            skill_gap_report
            is None
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Skill Gap report linked "
                    "to this interview "
                    "was not found."
                ),
            )


    # --------------------------------------------------
    # 6. Evaluate answer
    # --------------------------------------------------

    try:
        result = (
            process_interview_answer(
                db,
                session=
                    session,

                answer=
                    request.answer,

                resume=
                    resume,

                job_description=
                    job_description,

                skill_gap_report=
                    skill_gap_report,
            )
        )


    except ChatGoogleGenerativeAIError as exc:
        logger.exception(
            "Mock Interview AI answer "
            "evaluation failed."
        )


        _raise_ai_error(
            exc,
            fallback_message=(
                "CareerPilot's AI provider "
                "could not evaluate this answer. "
                "Please try again."
            ),
        )


    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,
            detail=str(
                exc
            ),
        ) from exc


    except Exception as exc:
        logger.exception(
            "Mock Interview answer "
            "processing failed."
        )


        raise HTTPException(
            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "CareerPilot could not "
                "evaluate this interview answer."
            ),
        ) from exc


    # --------------------------------------------------
    # 7. Response
    # --------------------------------------------------

    return {
        "session_id":
            session.id,

        "interview_type":
            session.interview_type,

        **result,
    }


# ==================================================
# GET INTERVIEW SESSION
# ==================================================


@router.get(
    "/{session_id}",
)
def get_mock_interview(
    session_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve one Mock Interview session
    owned by the authenticated user.
    """

    session = (
        get_owned_mock_interview_session(
            db,
            user_id=
                current_user.id,
            session_id=
                session_id,
        )
    )


    if session is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Mock Interview session "
                "was not found."
            ),
        )


    return (
        serialize_mock_interview_session(
            session
        )
    )