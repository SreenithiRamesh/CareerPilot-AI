from pydantic import BaseModel, Field


class JobMatchOutput(BaseModel):
    match_score: int = Field(
        ge=0,
        le=100,
    )

    strong_matches: list[str] = Field(
        default_factory=list
    )

    partial_matches: list[str] = Field(
        default_factory=list
    )

    missing_skills: list[str] = Field(
        default_factory=list
    )

    resume_improvements: list[str] = Field(
        default_factory=list
    )

    priority_actions: list[str] = Field(
        default_factory=list
    )


class SkillGapOutput(BaseModel):
    existing_skills: list[str] = Field(
        default_factory=list
    )

    missing_skills: list[str] = Field(
        default_factory=list
    )

    partially_demonstrated_skills: list[str] = Field(
        default_factory=list
    )

    high_priority_gaps: list[str] = Field(
        default_factory=list
    )

    medium_priority_gaps: list[str] = Field(
        default_factory=list
    )

    low_priority_gaps: list[str] = Field(
        default_factory=list
    )

    recommended_learning_order: list[str] = Field(
        default_factory=list
    )

    practice_tasks: list[str] = Field(
        default_factory=list
    )

    proof_of_skill_actions: list[str] = Field(
        default_factory=list
    )

    readiness_summary: str = ""


class CareerPlanOutput(BaseModel):
    readiness_summary: str

    top_priorities: list[str] = Field(
        default_factory=list
    )

    recommended_learning_order: list[str] = Field(
        default_factory=list
    )

    practical_tasks: list[str] = Field(
        default_factory=list
    )

    portfolio_evidence: list[str] = Field(
        default_factory=list
    )

    interview_preparation_focus: list[str] = Field(
        default_factory=list
    )

    action_plan_30_days: list[str] = Field(
        default_factory=list
    )