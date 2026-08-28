from uuid import uuid4

from sqlalchemy import delete

from app.database import SessionLocal
from app.models import (
    JobDescription,
    Resume,
    User,
)
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


def test_analysis_persistence():
    db = SessionLocal()
    user_id = None

    try:
        unique_value = uuid4().hex

        user = User(
            email=(
                "analysis-persistence-"
                f"{unique_value}@example.com"
            ),
            password_hash=(
                "analysis_persistence_test_hash"
            ),
        )

        db.add(user)
        db.flush()

        user_id = user.id

        resume = Resume(
            user_id=user.id,
            original_filename=(
                "analysis-test-resume.pdf"
            ),
            processing_status="completed",
            vector_collection_id=(
                f"analysis-test-{unique_value}"
            ),
        )

        job_description = JobDescription(
            user_id=user.id,
            title="Java Backend Developer",
            company_name="CareerPilot Test",
            description_text=(
                "Build Java backend services using "
                "Spring Boot, SQL, Docker, and AWS."
            ),
        )

        db.add_all(
            [
                resume,
                job_description,
            ]
        )

        db.commit()
        db.refresh(user)
        db.refresh(resume)
        db.refresh(job_description)

        job_match = JobMatchOutput(
            match_score=80,
            strong_matches=[
                "Java",
                "SQL",
                "AWS",
            ],
            partial_matches=[
                "Linux",
            ],
            missing_skills=[
                "Spring Boot",
                "Docker",
            ],
            resume_improvements=[
                (
                    "Add stronger backend project "
                    "evidence."
                ),
            ],
            priority_actions=[
                "Build a Spring Boot REST API.",
                "Containerize it using Docker.",
            ],
        )

        saved_job_match = save_job_match_result(
            db,
            user_id=user.id,
            resume_id=resume.id,
            job_description_id=(
                job_description.id
            ),
            result=job_match,
        )

        skill_gap = SkillGapOutput(
            existing_skills=[
                "Java",
                "SQL",
                "AWS",
            ],
            missing_skills=[
                "Spring Boot",
                "Docker",
            ],
            partially_demonstrated_skills=[
                "Linux",
            ],
            high_priority_gaps=[
                "Spring Boot",
                "Docker",
            ],
            medium_priority_gaps=[
                "Linux",
            ],
            low_priority_gaps=[],
            recommended_learning_order=[
                "Spring Boot",
                "Docker",
                "Linux",
            ],
            practice_tasks=[
                (
                    "Build CRUD APIs using "
                    "Spring Boot."
                ),
            ],
            proof_of_skill_actions=[
                (
                    "Push a Spring Boot project "
                    "to GitHub."
                ),
            ],
            readiness_summary=(
                "Good backend foundation with "
                "framework gaps."
            ),
        )

        saved_skill_gap = save_skill_gap_report(
            db,
            user_id=user.id,
            resume_id=resume.id,
            job_description_id=(
                job_description.id
            ),
            result=skill_gap,
        )

        career_plan = CareerPlanOutput(
            readiness_summary=(
                "Candidate has a solid foundation."
            ),
            top_priorities=[
                "Spring Boot",
                "Docker",
            ],
            recommended_learning_order=[
                "Spring Boot",
                "Docker",
                "Linux",
            ],
            practical_tasks=[
                (
                    "Build and containerize a "
                    "backend API."
                ),
            ],
            portfolio_evidence=[
                "GitHub project",
            ],
            interview_preparation_focus=[
                "Java",
                "Spring Boot",
            ],
            action_plan_30_days=[
                "Days 1-10: Spring Boot",
                "Days 11-20: Docker",
                "Days 21-30: Portfolio",
            ],
        )

        saved_career_plan = save_career_plan(
            db,
            user_id=user.id,
            job_match_result_id=(
                saved_job_match.id
            ),
            skill_gap_report_id=(
                saved_skill_gap.id
            ),
            result=career_plan,
        )

        assert saved_job_match.id is not None
        assert saved_job_match.user_id == user.id
        assert (
            saved_job_match.resume_id
            == resume.id
        )
        assert (
            saved_job_match.job_description_id
            == job_description.id
        )
        assert saved_job_match.match_score == 80

        assert saved_skill_gap.id is not None
        assert saved_skill_gap.user_id == user.id
        assert (
            saved_skill_gap.resume_id
            == resume.id
        )
        assert (
            saved_skill_gap.job_description_id
            == job_description.id
        )

        assert saved_career_plan.id is not None
        assert saved_career_plan.user_id == user.id
        assert (
            saved_career_plan.job_match_result_id
            == saved_job_match.id
        )
        assert (
            saved_career_plan.skill_gap_report_id
            == saved_skill_gap.id
        )

    finally:
        db.rollback()

        if user_id is not None:
            db.execute(
                delete(User).where(
                    User.id == user_id
                )
            )
            db.commit()

        db.close()