from app.database import SessionLocal
from app.schemas.ai_outputs import (
    JobMatchOutput,
    SkillGapOutput,
    CareerPlanOutput,
)
from app.services.analysis_service import (
    save_job_match_result,
    save_skill_gap_report,
    save_career_plan,
)


def test_analysis_persistence():
    db = SessionLocal()

    try:
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
                "Add stronger backend project evidence.",
            ],
            priority_actions=[
                "Build a Spring Boot REST API.",
                "Containerize it using Docker.",
            ],
        )

        saved_job_match = save_job_match_result(
            db,
            user_id=2,
            resume_id=1,
            job_description_id=1,
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
                "Build CRUD APIs using Spring Boot.",
            ],
            proof_of_skill_actions=[
                "Push a Spring Boot project to GitHub.",
            ],
            readiness_summary=(
                "Good backend foundation with framework gaps."
            ),
        )

        saved_skill_gap = save_skill_gap_report(
            db,
            user_id=2,
            resume_id=1,
            job_description_id=1,
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
                "Build and containerize a backend API.",
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
            user_id=2,
            job_match_result_id=(
                saved_job_match.id
            ),
            skill_gap_report_id=(
                saved_skill_gap.id
            ),
            result=career_plan,
        )

        print(
            "JOB MATCH ID:",
            saved_job_match.id,
        )

        print(
            "SKILL GAP ID:",
            saved_skill_gap.id,
        )

        print(
            "CAREER PLAN ID:",
            saved_career_plan.id,
        )

        print(
            "STRUCTURED ANALYSIS PERSISTENCE SUCCESS"
        )

    finally:
        db.close()


if __name__ == "__main__":
    test_analysis_persistence()