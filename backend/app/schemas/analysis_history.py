from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisHistoryItem(BaseModel):
    resume_id: int

    resume_filename: str

    job_description_id: int

    job_title: str | None = None

    company_name: str | None = None

    job_match_result_id: int

    skill_gap_report_id: int | None = None

    career_plan_id: int | None = None

    match_score: int

    strong_matches: list[str] = Field(
        default_factory=list
    )

    high_priority_gaps: list[str] = Field(
        default_factory=list
    )

    readiness_summary: str | None = None

    analyzed_at: datetime


class AnalysisHistoryResponse(BaseModel):
    items: list[
        AnalysisHistoryItem
    ] = Field(
        default_factory=list
    )

    total: int = 0