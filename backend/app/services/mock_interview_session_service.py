import json
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    JobDescription,
    MockInterviewSession,
    Resume,
    SkillGapReport,
)

from app.services.mock_interview_service import (
    evaluate_interview_answer,
    generate_interview_questions,
    generate_interview_summary,
)


# ==================================================
# JSON HELPERS
# ==================================================


def _to_json(
    data: Any,
) -> str:
    """
    Serialize Python data into JSON text
    for MySQL TEXT columns.
    """

    return json.dumps(
        data,
        ensure_ascii=False,
    )


def _from_json_list(
    value: str | None,
) -> list:
    """
    Safely deserialize JSON TEXT fields
    back into Python lists.
    """

    if not value:
        return []

    try:
        parsed = json.loads(
            value
        )

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return []

    return (
        parsed
        if isinstance(
            parsed,
            list,
        )
        else []
    )


# ==================================================
# OWNERSHIP HELPERS
# ==================================================


def get_owned_resume(
    db: Session,
    *,
    user_id: int,
    resume_id: int,
) -> Resume | None:
    """
    Return a resume only when it belongs
    to the authenticated user.
    """

    return db.scalar(
        select(
            Resume
        ).where(
            Resume.id
            == resume_id,

            Resume.user_id
            == user_id,
        )
    )


def get_owned_job_description(
    db: Session,
    *,
    user_id: int,
    job_description_id: int,
) -> JobDescription | None:
    """
    Return a Job Description only when it
    belongs to the authenticated user.
    """

    return db.scalar(
        select(
            JobDescription
        ).where(
            JobDescription.id
            == job_description_id,

            JobDescription.user_id
            == user_id,
        )
    )


def get_owned_skill_gap_report(
    db: Session,
    *,
    user_id: int,
    skill_gap_report_id: int,
) -> SkillGapReport | None:
    """
    Return a Skill Gap report only when it
    belongs to the authenticated user.
    """

    return db.scalar(
        select(
            SkillGapReport
        ).where(
            SkillGapReport.id
            == skill_gap_report_id,

            SkillGapReport.user_id
            == user_id,
        )
    )


def get_owned_mock_interview_session(
    db: Session,
    *,
    user_id: int,
    session_id: int,
) -> MockInterviewSession | None:
    """
    Return a Mock Interview session only
    when it belongs to the authenticated user.
    """

    return db.scalar(
        select(
            MockInterviewSession
        ).where(
            MockInterviewSession.id
            == session_id,

            MockInterviewSession.user_id
            == user_id,
        )
    )


# ==================================================
# SKILL GAP EXTRACTION
# ==================================================


def extract_priority_skill_gaps(
    report: SkillGapReport | None,
) -> list[str]:
    """
    Extract high, medium and low priority
    gaps from SkillGapReport.priority_gaps.

    Stored format:

    {
        "high": [...],
        "medium": [...],
        "low": [...]
    }
    """

    if report is None:
        return []

    if not report.priority_gaps:
        return []

    try:
        parsed = json.loads(
            report.priority_gaps
        )

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return []

    if not isinstance(
        parsed,
        dict,
    ):
        return []

    result: list[str] = []

    for key in (
        "high",
        "medium",
        "low",
    ):
        values = parsed.get(
            key,
            [],
        )

        if not isinstance(
            values,
            list,
        ):
            continue

        for value in values:
            if (
                isinstance(
                    value,
                    str,
                )
                and value.strip()
            ):
                result.append(
                    value.strip()
                )

    return result


# ==================================================
# RESUME CONTEXT
# ==================================================


def build_resume_context(
    resume: Resume,
) -> str:
    """
    Build resume context supplied to
    Mock Interview AI.

    MVP currently uses safe resume metadata.

    This function can later be upgraded to
    CareerPilot's Resume RAG retrieval layer
    without changing Mock Interview session logic.
    """

    return (
        "Candidate resume:\n"
        f"Filename: "
        f"{resume.original_filename}"
    )


# ==================================================
# CREATE QUESTION RECORD
# ==================================================


def _build_question_record(
    question: dict,
) -> dict:
    """
    Normalize an AI-generated question into
    the structure persisted inside the
    questions_answers JSON field.

    generate_interview_questions() already
    returns most of these fields, but this
    helper guarantees a consistent database
    structure.
    """

    return {
        "question_number":
            question[
                "question_number"
            ],

        "question":
            question[
                "question"
            ],

        "skill_target":
            question.get(
                "skill_target"
            ),

        "interview_type":
            question.get(
                "interview_type"
            ),

        "answer":
            question.get(
                "answer"
            ),

        "feedback":
            question.get(
                "feedback"
            ),

        "score":
            question.get(
                "score"
            ),

        "strengths":
            question.get(
                "strengths",
                [],
            ),

        "improvements":
            question.get(
                "improvements",
                [],
            ),

        "better_answer_approach":
            question.get(
                "better_answer_approach"
            ),
    }


# ==================================================
# PUBLIC QUESTION FORMAT
# ==================================================


def _serialize_question(
    record: dict,
) -> dict:
    """
    Return only question information required
    by the frontend.

    Internal answer/evaluation fields are not
    exposed as part of next_question.
    """

    return {
        "question_number":
            record.get(
                "question_number"
            ),

        "question":
            record.get(
                "question"
            ),

        "skill_target":
            record.get(
                "skill_target"
            ),

        "interview_type":
            record.get(
                "interview_type"
            ),
    }


# ==================================================
# CREATE SESSION
# ==================================================


def create_mock_interview_session(
    db: Session,
    *,
    user_id: int,
    resume: Resume,
    job_description: JobDescription | None,
    skill_gap_report: SkillGapReport | None,
    interview_type: str,
    total_questions: int,
) -> tuple[
    MockInterviewSession,
    dict,
]:
    """
    Create a new Mock Interview session.

    OPTIMIZED FLOW:

    Gemini generates the complete interview
    question set in ONE request.

    All questions are persisted immediately.

    Only Question 1 is returned to the frontend.
    """

    # --------------------------------------------------
    # Build AI grounding context
    # --------------------------------------------------

    resume_context = (
        build_resume_context(
            resume
        )
    )

    job_description_text = (
        job_description.description_text
        if job_description
        else None
    )

    skill_gaps = (
        extract_priority_skill_gaps(
            skill_gap_report
        )
    )

    # --------------------------------------------------
    # Generate ALL interview questions
    # --------------------------------------------------
    #
    # OLD:
    #
    # Gemini -> Q1
    #
    # Then every answer generated another question.
    #
    # NEW:
    #
    # Gemini -> Q1 + Q2 + Q3 + Q4 + Q5
    #
    # This dramatically reduces AI API calls.
    # --------------------------------------------------

    generated_questions = (
        generate_interview_questions(
            interview_type=
                interview_type,

            total_questions=
                total_questions,

            resume_context=
                resume_context,

            job_description=
                job_description_text,

            skill_gaps=
                skill_gaps,
        )
    )

    if (
        len(
            generated_questions
        )
        != total_questions
    ):
        raise ValueError(
            "Mock Interview AI returned "
            "an unexpected number of "
            "questions."
        )

    # --------------------------------------------------
    # Normalize complete question set
    # --------------------------------------------------

    questions_answers = [
        _build_question_record(
            question
        )
        for question
        in generated_questions
    ]

    if not questions_answers:
        raise ValueError(
            "Mock Interview AI did not "
            "generate any questions."
        )

    first_question = (
        _serialize_question(
            questions_answers[0]
        )
    )

    # --------------------------------------------------
    # Persist session
    # --------------------------------------------------

    session = MockInterviewSession(
        user_id=
            user_id,

        resume_id=
            resume.id,

        job_description_id=(
            job_description.id
            if job_description
            else None
        ),

        skill_gap_report_id=(
            skill_gap_report.id
            if skill_gap_report
            else None
        ),

        interview_type=
            interview_type,

        status=
            "in_progress",

        total_questions=
            total_questions,

        # Index zero means Question 1 is active.
        current_question_index=
            0,

        # IMPORTANT:
        # All interview questions are now
        # persisted at session creation.
        questions_answers=
            _to_json(
                questions_answers
            ),
    )

    db.add(
        session
    )

    try:
        db.commit()

        db.refresh(
            session
        )

    except Exception:
        db.rollback()
        raise

    return (
        session,
        first_question,
    )


# ==================================================
# SUBMIT ANSWER
# ==================================================


def process_interview_answer(
    db: Session,
    *,
    session: MockInterviewSession,
    answer: str,
    resume: Resume,
    job_description: JobDescription | None,
    skill_gap_report: SkillGapReport | None,
) -> dict:
    """
    Evaluate the current interview answer.

    OPTIMIZED FLOW:

    Question generation no longer happens here.

    Questions were already generated and persisted
    when the session started.

    For Questions 1-4:
        evaluate answer
        advance index
        return next stored question

    For final question:
        evaluate answer
        generate final summary
        complete session
    """

    # --------------------------------------------------
    # Validate session state
    # --------------------------------------------------

    if (
        session.status
        != "in_progress"
    ):
        raise ValueError(
            "This Mock Interview is "
            "not currently active."
        )

    records = (
        _from_json_list(
            session.questions_answers
        )
    )

    if not records:
        raise ValueError(
            "Interview session has no "
            "questions."
        )

    # --------------------------------------------------
    # Validate persisted question count
    # --------------------------------------------------

    if (
        len(records)
        < session.total_questions
    ):
        raise ValueError(
            "Interview session question "
            "set is incomplete."
        )

    current_index = (
        session.current_question_index
    )

    if (
        current_index < 0
        or
        current_index
        >= len(records)
    ):
        raise ValueError(
            "Interview session state "
            "is invalid."
        )

    current_record = (
        records[
            current_index
        ]
    )

    if (
        current_record.get(
            "answer"
        )
        is not None
    ):
        raise ValueError(
            "The current interview "
            "question has already "
            "been answered."
        )

    cleaned_answer = (
        answer.strip()
        if isinstance(
            answer,
            str,
        )
        else ""
    )

    if not cleaned_answer:
        raise ValueError(
            "Interview answer cannot "
            "be empty."
        )

    # --------------------------------------------------
    # Build AI grounding context
    # --------------------------------------------------

    resume_context = (
        build_resume_context(
            resume
        )
    )

    job_description_text = (
        job_description.description_text
        if job_description
        else None
    )

    # --------------------------------------------------
    # Evaluate current answer
    # --------------------------------------------------
    #
    # This is now the ONLY Gemini request needed
    # during Questions 1-4.
    # --------------------------------------------------

    feedback = (
        evaluate_interview_answer(
            question=
                current_record[
                    "question"
                ],

            answer=
                cleaned_answer,

            skill_target=
                current_record.get(
                    "skill_target"
                ),

            interview_type=(
                current_record.get(
                    "interview_type"
                )
                or
                session.interview_type
            ),

            resume_context=
                resume_context,

            job_description=
                job_description_text,
        )
    )

    # --------------------------------------------------
    # Persist answer + evaluation locally
    # --------------------------------------------------

    current_record[
        "answer"
    ] = cleaned_answer

    current_record[
        "feedback"
    ] = feedback[
        "feedback"
    ]

    current_record[
        "score"
    ] = feedback[
        "score"
    ]

    current_record[
        "strengths"
    ] = feedback[
        "strengths"
    ]

    current_record[
        "improvements"
    ] = feedback[
        "improvements"
    ]

    current_record[
        "better_answer_approach"
    ] = feedback[
        "better_answer_approach"
    ]

    answered_number = (
        current_index + 1
    )

    # ==================================================
    # INTERVIEW COMPLETE
    # ==================================================

    if (
        answered_number
        >= session.total_questions
    ):
        summary = (
            generate_interview_summary(
                questions_answers=
                    records,

                interview_type=
                    session.interview_type,

                resume_context=
                    resume_context,

                job_description=
                    job_description_text,
            )
        )

        session.status = (
            "completed"
        )

        session.readiness_score = (
            summary[
                "readiness_score"
            ]
        )

        session.overall_feedback = (
            summary[
                "overall_feedback"
            ]
        )

        session.strengths = (
            _to_json(
                summary[
                    "strengths"
                ]
            )
        )

        session.weak_areas = (
            _to_json(
                summary[
                    "weak_areas"
                ]
            )
        )

        session.questions_answers = (
            _to_json(
                records
            )
        )

        session.completed_at = (
            datetime.utcnow()
        )

        # Keep index pointing at final question.
        session.current_question_index = (
            current_index
        )

        try:
            db.commit()

            db.refresh(
                session
            )

        except Exception:
            db.rollback()
            raise

        return {
            "completed":
                True,

            "answered_question_number":
                answered_number,

            "feedback":
                feedback,

            "next_question":
                None,

            "summary":
                summary,
        }

    # ==================================================
    # MOVE TO PRE-GENERATED NEXT QUESTION
    # ==================================================
    #
    # IMPORTANT:
    #
    # No Gemini question-generation call occurs here.
    #
    # We simply read the next question that was
    # generated when the interview session started.
    # ==================================================

    next_index = (
        current_index + 1
    )

    if (
        next_index
        >= len(records)
    ):
        raise ValueError(
            "The next interview question "
            "is unavailable."
        )

    next_record = (
        records[
            next_index
        ]
    )

    next_question = (
        _serialize_question(
            next_record
        )
    )

    # --------------------------------------------------
    # Advance persistent session state
    # --------------------------------------------------

    session.questions_answers = (
        _to_json(
            records
        )
    )

    session.current_question_index = (
        next_index
    )

    try:
        db.commit()

        db.refresh(
            session
        )

    except Exception:
        db.rollback()
        raise

    return {
        "completed":
            False,

        "answered_question_number":
            answered_number,

        "feedback":
            feedback,

        "next_question":
            next_question,

        "summary":
            None,
    }


# ==================================================
# SERIALIZE SESSION
# ==================================================


def serialize_mock_interview_session(
    session: MockInterviewSession,
) -> dict:
    """
    Convert a persisted MockInterviewSession
    into frontend-ready structured data.
    """

    return {
        "id":
            session.id,

        "resume_id":
            session.resume_id,

        "job_description_id":
            session.job_description_id,

        "skill_gap_report_id":
            session.skill_gap_report_id,

        "interview_type":
            session.interview_type,

        "status":
            session.status,

        "total_questions":
            session.total_questions,

        "current_question_index":
            session.current_question_index,

        "questions_answers":
            _from_json_list(
                session.questions_answers
            ),

        "overall_feedback":
            session.overall_feedback,

        "readiness_score":
            session.readiness_score,

        "strengths":
            _from_json_list(
                session.strengths
            ),

        "weak_areas":
            _from_json_list(
                session.weak_areas
            ),

        "created_at":
            session.created_at,

        "completed_at":
            session.completed_at,
    }