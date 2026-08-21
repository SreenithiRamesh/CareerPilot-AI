from sqlalchemy import select

from app.database import SessionLocal
from app.models import JobDescription
from app.schemas.ai_outputs import (
    CareerPlanOutput,
    JobMatchOutput,
    SkillGapOutput,
)
from app.services.analysis_service import (
    save_career_plan,
    save_job_match_result,
    save_skill_gap_report,
)


def get_or_create_job_description(
    *,
    user_id: int,
    description_text: str,
    title: str | None = None,
    company_name: str | None = None,
) -> int:
    """
    Return an existing matching job-description ID
    for the authenticated user, or create a new row.

    This avoids creating duplicate JD rows every time
    the same analysis workflow runs.
    """

    db = SessionLocal()

    try:
        existing = db.scalar(
            select(JobDescription).where(
                JobDescription.user_id == user_id,
                JobDescription.description_text
                == description_text,
            )
        )

        if existing is not None:
            return existing.id

        job_description = JobDescription(
            user_id=user_id,
            title=title,
            company_name=company_name,
            description_text=description_text,
        )

        db.add(job_description)
        db.commit()
        db.refresh(job_description)

        return job_description.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def persist_job_match(
    *,
    user_id: int,
    resume_id: int,
    job_description_id: int,
    result: JobMatchOutput,
) -> int:
    """
    Persist structured Job Match output
    and return its database ID.
    """

    db = SessionLocal()

    try:
        record = save_job_match_result(
            db,
            user_id=user_id,
            resume_id=resume_id,
            job_description_id=job_description_id,
            result=result,
        )

        return record.id

    finally:
        db.close()


def persist_skill_gap(
    *,
    user_id: int,
    resume_id: int,
    job_description_id: int,
    result: SkillGapOutput,
) -> int:
    """
    Persist structured Skill Gap output
    and return its database ID.
    """

    db = SessionLocal()

    try:
        record = save_skill_gap_report(
            db,
            user_id=user_id,
            resume_id=resume_id,
            job_description_id=job_description_id,
            result=result,
        )

        return record.id

    finally:
        db.close()


def persist_career_plan(
    *,
    user_id: int,
    job_match_result_id: int | None,
    skill_gap_report_id: int | None,
    result: CareerPlanOutput,
) -> int:
    """
    Persist structured Career Plan output
    and return its database ID.
    """

    db = SessionLocal()

    try:
        record = save_career_plan(
            db,
            user_id=user_id,
            job_match_result_id=job_match_result_id,
            skill_gap_report_id=skill_gap_report_id,
            result=result,
        )

        return record.id

    finally:
        db.close()