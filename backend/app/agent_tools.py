import json
from typing import Any

from langchain_core.tools import tool
from sqlalchemy import select

from app.database import SessionLocal
from app.models import (
    JobDescription,
    JobMatchResult,
    Resume,
    SkillGapReport,
)
from app.resume_rag import (
    get_resume_vector_store,
    resume_exists,
    search_resume,
)


# ============================================================
# INTERNAL HELPERS
# ============================================================


def _parse_json(value: str | None, default: Any = None) -> Any:
    """
    Safely deserialize JSON stored in MySQL TEXT columns.
    """

    if value is None:
        return default

    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def _get_owned_resume(
    *,
    user_id: int,
    resume_id: int,
) -> Resume | None:
    """
    Return the requested resume only when it belongs
    to the authenticated user.

    This helper is intentionally reused by every
    resume-dependent agent tool.
    """

    db = SessionLocal()

    try:
        return db.scalar(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
        )

    finally:
        db.close()


def _resume_not_found(
    user_id: int,
    resume_id: int,
) -> dict[str, Any]:
    """
    Standard ownership-safe response.

    We intentionally do not reveal whether the resume
    exists for another user.
    """

    return {
        "success": False,
        "error": "resume_not_found",
        "message": (
            "The selected resume could not be found "
            "for the authenticated user."
        ),
        "user_id": user_id,
        "resume_id": resume_id,
    }


# ============================================================
# TOOL 1 — RESUME CONTEXT
# ============================================================


@tool
def get_resume_context(
    user_id: int,
    resume_id: int,
    query: str,
    k: int = 5,
) -> dict[str, Any]:
    """
    Retrieve resume evidence relevant to a question.

    Use this tool whenever reasoning requires information
    about the candidate's skills, projects, education,
    experience, certifications, achievements, or other
    resume-grounded evidence.

    The resume must belong to the supplied user_id.
    """

    resume = _get_owned_resume(
        user_id=user_id,
        resume_id=resume_id,
    )

    if resume is None:
        return _resume_not_found(
            user_id,
            resume_id,
        )

    if not resume_exists(
        str(resume_id),
        user_id=str(user_id),
    ):
        return {
            "success": False,
            "error": "resume_not_indexed",
            "message": (
                "The selected resume does not have "
                "indexed vector content."
            ),
            "resume_id": resume_id,
        }

    vector_store = get_resume_vector_store(
        str(resume_id)
    )

    documents = search_resume(
        vector_store=vector_store,
        query=query,
        k=k,
        user_id=str(user_id),
        resume_id=str(resume_id),
    )

    evidence = [
        {
            "content": document.page_content,
            "metadata": document.metadata,
        }
        for document in documents
    ]

    return {
        "success": True,
        "found": bool(evidence),
        "resume_id": resume_id,
        "filename": resume.original_filename,
        "query": query,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "message": (
            "Resume evidence was retrieved successfully."
            if evidence
            else (
                "The selected resume is indexed, but no "
                "relevant resume evidence was found for "
                "the requested query."
            )
        ),
    }


# ============================================================
# TOOL 2 — LATEST JOB MATCH
# ============================================================


@tool
def get_latest_job_match(
    user_id: int,
    resume_id: int,
) -> dict[str, Any]:
    """
    Retrieve the latest persisted Job Match analysis for
    the selected resume.

    Use this tool when reasoning requires the candidate's
    most recent resume-to-job comparison.
    """

    resume = _get_owned_resume(
        user_id=user_id,
        resume_id=resume_id,
    )

    if resume is None:
        return _resume_not_found(
            user_id,
            resume_id,
        )

    db = SessionLocal()

    try:
        result = db.scalar(
            select(JobMatchResult)
            .where(
                JobMatchResult.user_id == user_id,
                JobMatchResult.resume_id == resume_id,
            )
            .order_by(
                JobMatchResult.created_at.desc(),
                JobMatchResult.id.desc(),
            )
            .limit(1)
        )

        if result is None:
            return {
                "success": True,
                "found": False,
                "resume_id": resume_id,
                "message": (
                    "No saved Job Match analysis exists "
                    "for this resume."
                ),
            }

        job_description = db.scalar(
            select(JobDescription).where(
                JobDescription.id
                == result.job_description_id,
                JobDescription.user_id == user_id,
            )
        )

        return {
            "success": True,
            "found": True,
            "job_match_result_id": result.id,
            "resume_id": result.resume_id,
            "job_description_id": (
                result.job_description_id
            ),
            "job_description": (
                {
                    "title": job_description.title,
                    "company_name": (
                        job_description.company_name
                    ),
                    "description_text": (
                        job_description.description_text
                    ),
                }
                if job_description is not None
                else None
            ),
            "match_score": result.match_score,
            "strong_matches": _parse_json(
                result.strong_matches,
                [],
            ),
            "partial_matches": _parse_json(
                result.partial_matches,
                [],
            ),
            "missing_skills": _parse_json(
                result.missing_skills,
                [],
            ),
            "resume_improvements": _parse_json(
                result.resume_improvements,
                [],
            ),
            "priority_actions": _parse_json(
                result.priority_actions,
                [],
            ),
            "created_at": (
                result.created_at.isoformat()
                if result.created_at
                else None
            ),
        }

    finally:
        db.close()


# ============================================================
# TOOL 3 — LATEST SKILL GAP
# ============================================================


@tool
def get_latest_skill_gap(
    user_id: int,
    resume_id: int,
) -> dict[str, Any]:
    """
    Retrieve the latest persisted Skill Gap analysis for
    the selected resume.

    Use this tool before recommending learning priorities,
    portfolio projects, preparation plans, or evidence-
    building activities.
    """

    resume = _get_owned_resume(
        user_id=user_id,
        resume_id=resume_id,
    )

    if resume is None:
        return _resume_not_found(
            user_id,
            resume_id,
        )

    db = SessionLocal()

    try:
        report = db.scalar(
            select(SkillGapReport)
            .where(
                SkillGapReport.user_id == user_id,
                SkillGapReport.resume_id == resume_id,
            )
            .order_by(
                SkillGapReport.created_at.desc(),
                SkillGapReport.id.desc(),
            )
            .limit(1)
        )

        if report is None:
            return {
                "success": True,
                "found": False,
                "resume_id": resume_id,
                "message": (
                    "No saved Skill Gap analysis exists "
                    "for this resume."
                ),
            }

        job_description = db.scalar(
            select(JobDescription).where(
                JobDescription.id
                == report.job_description_id,
                JobDescription.user_id == user_id,
            )
        )

        return {
            "success": True,
            "found": True,
            "skill_gap_report_id": report.id,
            "resume_id": report.resume_id,
            "job_description_id": (
                report.job_description_id
            ),
            "job_description": (
                {
                    "title": job_description.title,
                    "company_name": (
                        job_description.company_name
                    ),
                    "description_text": (
                        job_description.description_text
                    ),
                }
                if job_description is not None
                else None
            ),
            "existing_skills": _parse_json(
                report.existing_skills,
                [],
            ),
            "missing_skills": _parse_json(
                report.missing_skills,
                [],
            ),
            "partial_skills": _parse_json(
                report.partial_skills,
                [],
            ),
            "priority_gaps": _parse_json(
                report.priority_gaps,
                {},
            ),
            "learning_order": _parse_json(
                report.learning_order,
                [],
            ),
            "practice_tasks": _parse_json(
                report.practice_tasks,
                [],
            ),
            "proof_of_skill_actions": _parse_json(
                report.proof_of_skill_actions,
                [],
            ),
            "portfolio_project_prompts": _parse_json(
                report.portfolio_project_prompts,
                [],
            ),
            "readiness_summary": (
                report.readiness_summary
            ),
            "created_at": (
                report.created_at.isoformat()
                if report.created_at
                else None
            ),
        }

    finally:
        db.close()


# ============================================================
# TOOL 4 — PROJECT RECOMMENDATION
# ============================================================


@tool
def recommend_project(
    user_id: int,
    resume_id: int,
    target_skill: str | None = None,
) -> dict[str, Any]:
    """
    Recommend portfolio projects from the candidate's latest
    persisted Skill Gap analysis.

    Use this tool when the user wants a project that closes
    an identified skill gap or creates proof-of-skill
    evidence.

    If target_skill is supplied, prioritize recommendations
    related to that skill.
    """

    skill_gap = get_latest_skill_gap.invoke(
        {
            "user_id": user_id,
            "resume_id": resume_id,
        }
    )

    if not skill_gap.get("success"):
        return skill_gap

    if not skill_gap.get("found"):
        return {
            "success": True,
            "found": False,
            "error": "skill_gap_required",
            "resume_id": resume_id,
            "message": (
                "A Skill Gap analysis is required before "
                "CareerPilot can recommend a gap-grounded "
                "portfolio project."
            ),
        }

    projects = skill_gap.get(
        "portfolio_project_prompts",
        [],
    )

    if not isinstance(projects, list):
        projects = []

    selected_projects = projects

    if target_skill:
        normalized_target = target_skill.lower().strip()

        matching_projects = []

        for project in projects:
            if not isinstance(project, dict):
                continue

            searchable_values = [
                str(project.get("target_skill", "")),
                str(project.get("project_title", "")),
                str(project.get("project_goal", "")),
                " ".join(
                    str(item)
                    for item in project.get(
                        "suggested_stack",
                        [],
                    )
                ),
            ]

            searchable_text = " ".join(
                searchable_values
            ).lower()

            if normalized_target in searchable_text:
                matching_projects.append(project)

        if matching_projects:
            selected_projects = matching_projects

    return {
        "success": True,
        "found": bool(selected_projects),
        "resume_id": resume_id,
        "skill_gap_report_id": skill_gap.get(
            "skill_gap_report_id"
        ),
        "target_skill": target_skill,
        "priority_gaps": skill_gap.get(
            "priority_gaps",
            {},
        ),
        "projects": selected_projects,
        "message": (
            "Portfolio recommendations were loaded from "
            "the latest persisted Skill Gap analysis."
            if selected_projects
            else (
                "No saved portfolio project recommendation "
                "matched the requested skill."
            )
        ),
    }


# ============================================================
# TOOL 5 — CAREER PLAN CONTEXT
# ============================================================


@tool
def generate_career_plan(
    user_id: int,
    resume_id: int,
) -> dict[str, Any]:
    """
    Assemble the latest evidence required for CareerPilot's
    career-planning workflow.

    This tool does not fabricate a plan. It loads the
    candidate's latest persisted Job Match and Skill Gap
    analyses so the agent can decide whether sufficient
    evidence exists to generate a grounded career plan.

    The actual plan-generation workflow can consume this
    structured context.
    """

    resume = _get_owned_resume(
        user_id=user_id,
        resume_id=resume_id,
    )

    if resume is None:
        return _resume_not_found(
            user_id,
            resume_id,
        )

    job_match = get_latest_job_match.invoke(
        {
            "user_id": user_id,
            "resume_id": resume_id,
        }
    )

    skill_gap = get_latest_skill_gap.invoke(
        {
            "user_id": user_id,
            "resume_id": resume_id,
        }
    )

    has_job_match = (
        job_match.get("success", False)
        and job_match.get("found", False)
    )

    has_skill_gap = (
        skill_gap.get("success", False)
        and skill_gap.get("found", False)
    )

    ready_for_generation = (
        has_job_match and has_skill_gap
    )

    missing_prerequisites: list[str] = []

    if not has_job_match:
        missing_prerequisites.append(
            "job_match"
        )

    if not has_skill_gap:
        missing_prerequisites.append(
            "skill_gap"
        )

    return {
        "success": True,
        "found": ready_for_generation,
        "error": (
            None
            if ready_for_generation
            else "career_plan_prerequisites_missing"
        ),
        "resume_id": resume_id,
        "filename": resume.original_filename,
        "ready_for_generation": ready_for_generation,
        "missing_prerequisites": missing_prerequisites,
        "job_match": (
            job_match
            if has_job_match
            else None
        ),
        "skill_gap": (
            skill_gap
            if has_skill_gap
            else None
        ),
        "message": (
            "Career planning context is ready."
            if ready_for_generation
            else (
                "Career planning requires both a saved "
                "Job Match analysis and Skill Gap analysis."
            )
        ),
    }


# ============================================================
# TOOL 6 — INTERVIEW PREPARATION FOCUS
# ============================================================


@tool
def prepare_interview_focus(
    user_id: int,
    resume_id: int,
) -> dict[str, Any]:
    """
    Build grounded interview-preparation context from the
    candidate's latest Job Match and Skill Gap analyses.

    Use this tool before generating targeted interview
    questions or preparation guidance.
    """

    resume = _get_owned_resume(
        user_id=user_id,
        resume_id=resume_id,
    )

    if resume is None:
        return _resume_not_found(
            user_id,
            resume_id,
        )

    job_match = get_latest_job_match.invoke(
        {
            "user_id": user_id,
            "resume_id": resume_id,
        }
    )

    skill_gap = get_latest_skill_gap.invoke(
        {
            "user_id": user_id,
            "resume_id": resume_id,
        }
    )

    focus = {
        "strong_areas": [],
        "partial_areas": [],
        "priority_gaps": {},
        "missing_skills": [],
        "priority_actions": [],
        "practice_tasks": [],
    }

    if (
        job_match.get("success")
        and job_match.get("found")
    ):
        focus["strong_areas"] = (
            job_match.get(
                "strong_matches",
                [],
            )
        )

        focus["partial_areas"] = (
            job_match.get(
                "partial_matches",
                [],
            )
        )

        focus["missing_skills"] = (
            job_match.get(
                "missing_skills",
                [],
            )
        )

        focus["priority_actions"] = (
            job_match.get(
                "priority_actions",
                [],
            )
        )

    if (
        skill_gap.get("success")
        and skill_gap.get("found")
    ):
        focus["priority_gaps"] = (
            skill_gap.get(
                "priority_gaps",
                {},
            )
        )

        focus["practice_tasks"] = (
            skill_gap.get(
                "practice_tasks",
                [],
            )
        )

        if not focus["missing_skills"]:
            focus["missing_skills"] = (
                skill_gap.get(
                    "missing_skills",
                    [],
                )
            )

    has_job_match = bool(
        job_match.get("success")
        and job_match.get("found")
    )

    has_skill_gap = bool(
        skill_gap.get("success")
        and skill_gap.get("found")
    )

    has_any_evidence = (
        has_job_match or has_skill_gap
    )

    complete_context = (
        has_job_match and has_skill_gap
    )

    missing_prerequisites: list[str] = []

    if not has_job_match:
        missing_prerequisites.append(
            "job_match"
        )

    if not has_skill_gap:
        missing_prerequisites.append(
            "skill_gap"
        )

    return {
        "success": True,
        "found": has_any_evidence,
        "error": (
            None
            if has_any_evidence
            else "interview_evidence_missing"
        ),
        "resume_id": resume_id,
        "filename": resume.original_filename,
        "has_job_match": has_job_match,
        "has_skill_gap": has_skill_gap,
        "complete_context": complete_context,
        "missing_prerequisites": missing_prerequisites,
        "interview_focus": focus,
        "message": (
            "Interview preparation context assembled "
            "from both Job Match and Skill Gap evidence."
            if complete_context
            else (
                "Partial interview preparation context "
                "was assembled from the available "
                "persisted CareerPilot evidence."
                if has_any_evidence
                else (
                    "Interview preparation requires a "
                    "saved Job Match analysis or Skill "
                    "Gap analysis before targeted focus "
                    "can be generated."
                )
            )
        ),
    }


# ============================================================
# AGENT TOOL REGISTRY
# ============================================================


CAREERPILOT_AGENT_TOOLS = [
    get_resume_context,
    get_latest_job_match,
    get_latest_skill_gap,
    generate_career_plan,
    recommend_project,
    prepare_interview_focus,
]