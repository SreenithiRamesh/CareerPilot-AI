import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy import (
    or_,
    select,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
)
from app.database import get_db
from app.models import (
    CareerPlan,
    JobDescription,
    JobMatchResult,
    Resume,
    SkillGapReport,
    User,
)
from app.schemas.analysis_history import (
    AnalysisHistoryItem,
    AnalysisHistoryResponse,
)


router = APIRouter(
    prefix="/api/analysis",
    tags=["Analysis History"],
)


# ==================================================
# JSON HELPERS
# ==================================================


def _parse_json_list(
    value: str | None,
) -> list:
    """
    Safely convert JSON stored in MySQL TEXT
    columns back into Python lists.
    """

    if not value:
        return []

    try:
        parsed = json.loads(value)

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


def _parse_priority_gaps(
    value: str | None,
) -> dict:
    """
    priority_gaps is stored in the format:

    {
        "high": [...],
        "medium": [...],
        "low": [...]
    }
    """

    if not value:
        return {
            "high": [],
            "medium": [],
            "low": [],
        }

    try:
        parsed = json.loads(
            value
        )

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return {
            "high": [],
            "medium": [],
            "low": [],
        }

    if not isinstance(
        parsed,
        dict,
    ):
        return {
            "high": [],
            "medium": [],
            "low": [],
        }

    return {
        "high":
            parsed.get(
                "high",
                [],
            )
            or [],

        "medium":
            parsed.get(
                "medium",
                [],
            )
            or [],

        "low":
            parsed.get(
                "low",
                [],
            )
            or [],
    }


# ==================================================
# ANALYSIS HISTORY
# ==================================================


@router.get(
    "/history",
    response_model=AnalysisHistoryResponse,
)
def get_analysis_history(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    """
    Return one clean history item for each
    unique Resume + Job Description pair.

    Why we group this way:

    CareerPilot workflows can persist more than one
    JobMatchResult / SkillGapReport internally while
    generating a Career Plan.

    Listing every database row would therefore show
    duplicate-looking history entries.

    The user-facing history boundary is:

        Resume
            +
        Job Description
    """

    # --------------------------------------------------
    # 1. Load all owned Job Match records
    # --------------------------------------------------

    job_match_rows = db.execute(
        select(
            JobMatchResult,
            Resume,
            JobDescription,
        )
        .join(
            Resume,
            JobMatchResult.resume_id
            == Resume.id,
        )
        .join(
            JobDescription,
            JobMatchResult.job_description_id
            == JobDescription.id,
        )
        .where(
            JobMatchResult.user_id
            == current_user.id,
            Resume.user_id
            == current_user.id,
            JobDescription.user_id
            == current_user.id,
        )
        .order_by(
            JobMatchResult.created_at.desc()
        )
    ).all()


    if not job_match_rows:
        return AnalysisHistoryResponse(
            items=[],
            total=0,
        )


    # --------------------------------------------------
    # 2. Group by Resume + Job Description
    # --------------------------------------------------

    grouped: dict[
        tuple[int, int],
        dict,
    ] = {}


    for (
        job_match,
        resume,
        job_description,
    ) in job_match_rows:

        group_key = (
            job_match.resume_id,
            job_match.job_description_id,
        )


        if (
            group_key
            not in grouped
        ):
            grouped[
                group_key
            ] = {
                "resume":
                    resume,

                "job_description":
                    job_description,

                "job_matches":
                    [],
            }


        grouped[
            group_key
        ][
            "job_matches"
        ].append(
            job_match
        )


    history_items = []


    # --------------------------------------------------
    # 3. Build one user-facing record per group
    # --------------------------------------------------

    for group in grouped.values():

        resume: Resume = (
            group["resume"]
        )

        job_description: JobDescription = (
            group[
                "job_description"
            ]
        )

        job_matches: list[
            JobMatchResult
        ] = group[
            "job_matches"
        ]


        # Latest Job Match for this
        # Resume + JD pair.

        latest_job_match = max(
            job_matches,
            key=lambda item:
                item.created_at,
        )


        job_match_ids = [
            item.id
            for item in job_matches
        ]


        # --------------------------------------------------
        # 4. Find latest Skill Gap for same Resume + JD
        # --------------------------------------------------

        latest_skill_gap = db.scalar(
            select(
                SkillGapReport
            )
            .where(
                SkillGapReport.user_id
                == current_user.id,

                SkillGapReport.resume_id
                == resume.id,

                SkillGapReport.job_description_id
                == job_description.id,
            )
            .order_by(
                SkillGapReport.created_at.desc()
            )
            .limit(1)
        )


        # We also need every Skill Gap ID from this
        # analysis group because Career Plan may point
        # to an internally-created Skill Gap record.

        skill_gap_ids = list(
            db.scalars(
                select(
                    SkillGapReport.id
                )
                .where(
                    SkillGapReport.user_id
                    == current_user.id,

                    SkillGapReport.resume_id
                    == resume.id,

                    SkillGapReport.job_description_id
                    == job_description.id,
                )
            ).all()
        )


        # --------------------------------------------------
        # 5. Find latest Career Plan connected to this group
        # --------------------------------------------------

        career_plan_conditions = []


        if job_match_ids:
            career_plan_conditions.append(
                CareerPlan.job_match_result_id.in_(
                    job_match_ids
                )
            )


        if skill_gap_ids:
            career_plan_conditions.append(
                CareerPlan.skill_gap_report_id.in_(
                    skill_gap_ids
                )
            )


        latest_career_plan = None


        if career_plan_conditions:
            latest_career_plan = db.scalar(
                select(
                    CareerPlan
                )
                .where(
                    CareerPlan.user_id
                    == current_user.id,

                    or_(
                        *career_plan_conditions
                    ),
                )
                .order_by(
                    CareerPlan.created_at.desc()
                )
                .limit(1)
            )


        # --------------------------------------------------
        # 6. Decode structured TEXT fields
        # --------------------------------------------------

        strong_matches = (
            _parse_json_list(
                latest_job_match.strong_matches
            )
        )


        high_priority_gaps = []


        if latest_skill_gap:
            priority_gaps = (
                _parse_priority_gaps(
                    latest_skill_gap.priority_gaps
                )
            )

            high_priority_gaps = (
                priority_gaps[
                    "high"
                ]
            )


        readiness_summary = None


        if (
            latest_career_plan
            and
            latest_career_plan.readiness_summary
        ):
            readiness_summary = (
                latest_career_plan.readiness_summary
            )

        elif (
            latest_skill_gap
            and
            latest_skill_gap.readiness_summary
        ):
            readiness_summary = (
                latest_skill_gap.readiness_summary
            )


        # --------------------------------------------------
        # 7. Determine latest relevant timestamp
        # --------------------------------------------------

        timestamps = [
            latest_job_match.created_at
        ]


        if latest_skill_gap:
            timestamps.append(
                latest_skill_gap.created_at
            )


        if latest_career_plan:
            timestamps.append(
                latest_career_plan.created_at
            )


        analyzed_at = max(
            timestamps
        )


        # --------------------------------------------------
        # 8. Build response
        # --------------------------------------------------

        history_items.append(
            AnalysisHistoryItem(
                resume_id=
                    resume.id,

                resume_filename=
                    resume.original_filename,

                job_description_id=
                    job_description.id,

                job_title=
                    job_description.title,

                company_name=
                    job_description.company_name,

                job_match_result_id=
                    latest_job_match.id,

                skill_gap_report_id=(
                    latest_skill_gap.id
                    if latest_skill_gap
                    else None
                ),

                career_plan_id=(
                    latest_career_plan.id
                    if latest_career_plan
                    else None
                ),

                match_score=
                    latest_job_match.match_score,

                strong_matches=
                    strong_matches,

                high_priority_gaps=
                    high_priority_gaps,

                readiness_summary=
                    readiness_summary,

                analyzed_at=
                    analyzed_at,
            )
        )


    # --------------------------------------------------
    # 9. Newest analysis first
    # --------------------------------------------------

    history_items.sort(
        key=lambda item:
            item.analyzed_at,
        reverse=True,
    )


    return AnalysisHistoryResponse(
        items=history_items,
        total=len(
            history_items
        ),
    )


# ==================================================
# HISTORICAL JOB MATCH DETAIL
# ==================================================


@router.get(
    "/job-match/{job_match_result_id}",
)
def get_historical_job_match(
    job_match_result_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    """
    Return one historical Job Match record
    owned by the authenticated user.
    """

    record = db.scalar(
        select(
            JobMatchResult
        ).where(
            JobMatchResult.id
            == job_match_result_id,

            JobMatchResult.user_id
            == current_user.id,
        )
    )


    if record is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Job Match analysis "
                "was not found."
            ),
        )


    resume = db.scalar(
        select(
            Resume
        ).where(
            Resume.id
            == record.resume_id,

            Resume.user_id
            == current_user.id,
        )
    )


    job_description = db.scalar(
        select(
            JobDescription
        ).where(
            JobDescription.id
            == record.job_description_id,

            JobDescription.user_id
            == current_user.id,
        )
    )


    return {
        "id":
            record.id,

        "resume_id":
            record.resume_id,

        "resume_filename": (
            resume.original_filename
            if resume
            else None
        ),

        "job_description_id":
            record.job_description_id,

        "job_title": (
            job_description.title
            if job_description
            else None
        ),

        "company_name": (
            job_description.company_name
            if job_description
            else None
        ),

        "match_score":
            record.match_score,

        "strong_matches":
            _parse_json_list(
                record.strong_matches
            ),

        "partial_matches":
            _parse_json_list(
                record.partial_matches
            ),

        "missing_skills":
            _parse_json_list(
                record.missing_skills
            ),

        "resume_improvements":
            _parse_json_list(
                record.resume_improvements
            ),

        "priority_actions":
            _parse_json_list(
                record.priority_actions
            ),

        "created_at":
            record.created_at,
    }


# ==================================================
# HISTORICAL SKILL GAP DETAIL
# ==================================================


@router.get(
    "/skill-gap/{skill_gap_report_id}",
)
def get_historical_skill_gap(
    skill_gap_report_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    """
    Return one historical Skill Gap report
    owned by the authenticated user.
    """

    record = db.scalar(
        select(
            SkillGapReport
        ).where(
            SkillGapReport.id
            == skill_gap_report_id,

            SkillGapReport.user_id
            == current_user.id,
        )
    )


    if record is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Skill Gap analysis "
                "was not found."
            ),
        )


    priority_gaps = (
        _parse_priority_gaps(
            record.priority_gaps
        )
    )


    portfolio_projects = (
        _parse_json_list(
            record.portfolio_project_prompts
        )
    )


    return {
        "id":
            record.id,

        "resume_id":
            record.resume_id,

        "job_description_id":
            record.job_description_id,

        "existing_skills":
            _parse_json_list(
                record.existing_skills
            ),

        "missing_skills":
            _parse_json_list(
                record.missing_skills
            ),

        "partially_demonstrated_skills":
            _parse_json_list(
                record.partial_skills
            ),

        "high_priority_gaps":
            priority_gaps.get(
                "high",
                [],
            ),

        "medium_priority_gaps":
            priority_gaps.get(
                "medium",
                [],
            ),

        "low_priority_gaps":
            priority_gaps.get(
                "low",
                [],
            ),

        "recommended_learning_order":
            _parse_json_list(
                record.learning_order
            ),

        "practice_tasks":
            _parse_json_list(
                record.practice_tasks
            ),

        "proof_of_skill_actions":
            _parse_json_list(
                record.proof_of_skill_actions
            ),

        "portfolio_project_prompts":
            portfolio_projects,

        "readiness_summary":
            record.readiness_summary,

        "created_at":
            record.created_at,
    }


# ==================================================
# HISTORICAL CAREER PLAN DETAIL
# ==================================================


@router.get(
    "/career-plan/{career_plan_id}",
)
def get_historical_career_plan(
    career_plan_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    """
    Return one historical Career Plan
    owned by the authenticated user.
    """

    record = db.scalar(
        select(
            CareerPlan
        ).where(
            CareerPlan.id
            == career_plan_id,

            CareerPlan.user_id
            == current_user.id,
        )
    )


    if record is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Career Plan "
                "was not found."
            ),
        )


    return {
        "id":
            record.id,

        "job_match_result_id":
            record.job_match_result_id,

        "skill_gap_report_id":
            record.skill_gap_report_id,

        "readiness_summary":
            record.readiness_summary,

        "top_priorities":
            _parse_json_list(
                record.top_priorities
            ),

        "recommended_learning_order":
            _parse_json_list(
                record.learning_order
            ),

        "practical_tasks":
            _parse_json_list(
                record.practical_tasks
            ),

        "portfolio_evidence":
            _parse_json_list(
                record.portfolio_evidence
            ),

        "interview_preparation_focus":
            _parse_json_list(
                record.interview_preparation_focus
            ),

        "action_plan_30_days":
            _parse_json_list(
                record.action_plan_30_days
            ),

        "created_at":
            record.created_at,
    }