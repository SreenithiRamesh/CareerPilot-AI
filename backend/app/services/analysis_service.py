import json

from sqlalchemy.orm import Session

from app.models import (
    CareerPlan,
    JobMatchResult,
    SkillGapReport,
)
from app.schemas.ai_outputs import (
    CareerPlanOutput,
    JobMatchOutput,
    SkillGapOutput,
)


def _to_json(data) -> str:
    """
    Serialize Python lists/dicts into JSON text
    before storing them in MySQL TEXT columns.
    """

    return json.dumps(
        data,
        ensure_ascii=False,
    )


# ==================================================
# JOB MATCH
# ==================================================


def save_job_match_result(
    db: Session,
    *,
    user_id: int,
    resume_id: int,
    job_description_id: int,
    result: JobMatchOutput,
) -> JobMatchResult:
    record = JobMatchResult(
        user_id=user_id,
        resume_id=resume_id,
        job_description_id=job_description_id,

        match_score=result.match_score,

        strong_matches=_to_json(
            result.strong_matches
        ),

        partial_matches=_to_json(
            result.partial_matches
        ),

        missing_skills=_to_json(
            result.missing_skills
        ),

        resume_improvements=_to_json(
            result.resume_improvements
        ),

        priority_actions=_to_json(
            result.priority_actions
        ),
    )

    db.add(record)

    try:
        db.commit()
        db.refresh(record)

    except Exception:
        db.rollback()
        raise

    return record


# ==================================================
# SKILL GAP
# ==================================================


def save_skill_gap_report(
    db: Session,
    *,
    user_id: int,
    resume_id: int,
    job_description_id: int,
    result: SkillGapOutput,
) -> SkillGapReport:
    """
    Persist structured Skill Gap analysis.

    Lists and structured project recommendations
    are serialized into JSON before being stored
    in MySQL TEXT columns.
    """

    priority_gaps = {
        "high": result.high_priority_gaps,
        "medium": result.medium_priority_gaps,
        "low": result.low_priority_gaps,
    }

    # Convert PortfolioProjectPrompt Pydantic models
    # into plain Python dictionaries before JSON storage.

    portfolio_project_prompts = [
        project.model_dump()
        for project in result.portfolio_project_prompts
    ]

    record = SkillGapReport(
        user_id=user_id,
        resume_id=resume_id,
        job_description_id=job_description_id,

        existing_skills=_to_json(
            result.existing_skills
        ),

        missing_skills=_to_json(
            result.missing_skills
        ),

        partial_skills=_to_json(
            result.partially_demonstrated_skills
        ),

        priority_gaps=_to_json(
            priority_gaps
        ),

        learning_order=_to_json(
            result.recommended_learning_order
        ),

        practice_tasks=_to_json(
            result.practice_tasks
        ),

        proof_of_skill_actions=_to_json(
            result.proof_of_skill_actions
        ),

        portfolio_project_prompts=_to_json(
            portfolio_project_prompts
        ),

        readiness_summary=(
            result.readiness_summary
        ),
    )

    db.add(record)

    try:
        db.commit()
        db.refresh(record)

    except Exception:
        db.rollback()
        raise

    return record


# ==================================================
# CAREER PLAN
# ==================================================


def save_career_plan(
    db: Session,
    *,
    user_id: int,
    job_match_result_id: int | None,
    skill_gap_report_id: int | None,
    result: CareerPlanOutput,
) -> CareerPlan:
    record = CareerPlan(
        user_id=user_id,

        job_match_result_id=(
            job_match_result_id
        ),

        skill_gap_report_id=(
            skill_gap_report_id
        ),

        readiness_summary=(
            result.readiness_summary
        ),

        top_priorities=_to_json(
            result.top_priorities
        ),

        learning_order=_to_json(
            result.recommended_learning_order
        ),

        practical_tasks=_to_json(
            result.practical_tasks
        ),

        portfolio_evidence=_to_json(
            result.portfolio_evidence
        ),

        interview_preparation_focus=_to_json(
            result.interview_preparation_focus
        ),

        action_plan_30_days=_to_json(
            result.action_plan_30_days
        ),
    )

    db.add(record)

    try:
        db.commit()
        db.refresh(record)

    except Exception:
        db.rollback()
        raise

    return record