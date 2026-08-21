import json
import os
from typing import Any

from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)
from pydantic import BaseModel, Field

from app.schemas.mock_interview import (
    InterviewAnswerFeedback,
    InterviewQuestion,
    MockInterviewSummary,
)


# ==================================================
# ENVIRONMENT CONFIGURATION
# ==================================================


load_dotenv()


gemini_api_key = os.getenv(
    "GEMINI_API_KEY"
)


if not gemini_api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing "
        "from the .env file."
    )


# ==================================================
# GEMINI MODEL
# ==================================================
#
# gemini-3.6-flash currently uses fixed
# sampling defaults.
#
# Do not supply temperature here.
# ==================================================


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=gemini_api_key,
)


# ==================================================
# BATCH QUESTION SCHEMA
# ==================================================
#
# InterviewQuestion already exists in our
# application schemas.
#
# This wrapper allows Gemini to generate the
# complete Mock Interview question set in ONE
# request instead of making one request for every
# question.
# ==================================================


class InterviewQuestionBatch(
    BaseModel
):
    questions: list[
        InterviewQuestion
    ] = Field(
        default_factory=list
    )


# ==================================================
# STRUCTURED GEMINI MODELS
# ==================================================


question_llm = (
    llm.with_structured_output(
        InterviewQuestion,
        method="json_schema",
    )
)


question_batch_llm = (
    llm.with_structured_output(
        InterviewQuestionBatch,
        method="json_schema",
    )
)


feedback_llm = (
    llm.with_structured_output(
        InterviewAnswerFeedback,
        method="json_schema",
    )
)


summary_llm = (
    llm.with_structured_output(
        MockInterviewSummary,
        method="json_schema",
    )
)


# ==================================================
# NORMALIZATION HELPERS
# ==================================================


def _normalize_string_list(
    value: Any,
) -> list[str]:
    """
    Return only non-empty strings.
    """

    if not isinstance(
        value,
        list,
    ):
        return []


    result: list[str] = []


    for item in value:

        if not isinstance(
            item,
            str,
        ):
            continue


        cleaned = (
            item.strip()
        )


        if cleaned:
            result.append(
                cleaned
            )


    return result


def _normalize_score(
    value: Any,
    minimum: float,
    maximum: float,
) -> float:
    """
    Convert a score into a bounded float.
    """

    try:
        score = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        score = minimum


    return max(
        minimum,
        min(
            score,
            maximum,
        ),
    )


def _normalize_interview_type(
    value: str | None,
    fallback: str = "technical",
) -> str:
    """
    Ensure question interview type uses one
    of CareerPilot's supported values.
    """

    allowed_types = {
        "technical",
        "behavioral",
        "hr",
    }


    cleaned = (
        value.strip().lower()
        if isinstance(
            value,
            str,
        )
        else ""
    )


    if cleaned in allowed_types:
        return cleaned


    fallback_cleaned = (
        fallback.strip().lower()
        if isinstance(
            fallback,
            str,
        )
        else "technical"
    )


    if fallback_cleaned in allowed_types:
        return fallback_cleaned


    return "technical"


def _build_jd_context(
    job_description: str | None,
) -> str:
    """
    Build safe Job Description context.
    """

    if (
        isinstance(
            job_description,
            str,
        )
        and job_description.strip()
    ):
        return (
            job_description.strip()
        )


    return (
        "No specific job description "
        "provided."
    )


def _build_skill_gap_context(
    skill_gaps: list[str] | None,
) -> str:
    """
    Convert Skill Gap list into prompt context.
    """

    cleaned = (
        _normalize_string_list(
            skill_gaps
        )
    )


    if not cleaned:
        return (
            "No specific skill gaps "
            "are available."
        )


    return ", ".join(
        cleaned
    )


# ==================================================
# GENERATE COMPLETE INTERVIEW QUESTION SET
# ==================================================


def generate_interview_questions(
    *,
    interview_type: str,
    total_questions: int,
    resume_context: str,
    job_description: str | None = None,
    skill_gaps: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Generate the complete Mock Interview question
    set using ONE Gemini request.

    This is the optimized question-generation path.

    Instead of:

        Gemini -> Q1
        Gemini -> Q2
        Gemini -> Q3
        Gemini -> Q4
        Gemini -> Q5

    CareerPilot performs:

        Gemini -> Q1 + Q2 + Q3 + Q4 + Q5

    The questions can then be persisted in MySQL
    and served sequentially during the interview.
    """

    if total_questions < 1:
        raise ValueError(
            "total_questions must be "
            "greater than zero."
        )


    # Keep MVP sessions reasonably bounded.

    total_questions = min(
        total_questions,
        10,
    )


    normalized_type = (
        _normalize_interview_type(
            interview_type
        )
    )


    jd_context = (
        _build_jd_context(
            job_description
        )
    )


    gaps_context = (
        _build_skill_gap_context(
            skill_gaps
        )
    )


    prompt = f"""
You are CareerPilot AI's Mock Interviewer.

Create a complete Mock Interview for an
entry-level or fresher candidate.

Generate EXACTLY {total_questions} unique
interview questions in ONE response.


INTERVIEW SETTINGS

Selected interview mode:
{normalized_type}

Total questions:
{total_questions}


RESUME CONTEXT

{resume_context}


TARGET JOB DESCRIPTION

{jd_context}


IDENTIFIED SKILL GAPS

{gaps_context}


QUESTION DESIGN RULES

1. Generate exactly {total_questions} questions.

2. Every question must be appropriate for a
   fresher or entry-level candidate.

3. Never assume professional employment
   experience.

4. Projects, internships, coursework,
   certifications, academics and personal
   learning are valid fresher evidence.

5. Do not generate senior-level architecture or
   system-design questions unless explicitly
   required by the Job Description.

6. Questions must not repeat each other.

7. Each question should test a meaningfully
   different skill, competency or concept.

8. Prioritize important Job Description
   requirements.

9. Use the candidate's resume to keep questions
   relevant.

10. Use identified Skill Gaps where appropriate.

11. Do not focus every question only on Skill
    Gaps. The interview should also test skills
    the candidate already claims.

12. Do not provide answers.

13. Do not provide hints.

14. Do not evaluate the candidate.

15. Keep individual questions clear and concise.

16. skill_target must identify the primary skill
    or competency being tested.


TECHNICAL MODE

For technical interviews:

- prioritize technologies from the resume and JD
- include important identified gaps
- test concepts and practical understanding
- avoid obscure trivia


BEHAVIORAL MODE

For behavioral interviews:

- projects
- teamwork
- challenges
- communication
- learning
- problem solving
- adaptability


HR MODE

For HR interviews:

- motivation
- career goals
- communication
- strengths
- adaptability
- workplace attitude
- learning mindset


MIXED MODE

If the requested interview mode requires a mix,
choose the most appropriate category for each
individual question.


NUMBERING

Questions must be numbered sequentially:

1 through {total_questions}.

The question_number field must match its actual
position in the interview.
"""


    result = (
        question_batch_llm.invoke(
            prompt
        )
    )


    if result is None:
        raise ValueError(
            "Mock Interview AI did not "
            "generate interview questions."
        )


    generated_questions = (
        result.questions
    )


    if not generated_questions:
        raise ValueError(
            "Mock Interview AI returned "
            "an empty question set."
        )


    if (
        len(
            generated_questions
        )
        != total_questions
    ):
        raise ValueError(
            "Mock Interview AI generated "
            f"{len(generated_questions)} "
            "questions instead of "
            f"{total_questions}."
        )


    normalized_questions: list[
        dict[str, Any]
    ] = []


    seen_questions: set[str] = set()


    for index, item in enumerate(
        generated_questions,
        start=1,
    ):

        question = (
            item.question.strip()
            if item.question
            else ""
        )


        if not question:
            raise ValueError(
                "Mock Interview AI generated "
                "an empty question."
            )


        duplicate_key = (
            question.lower()
        )


        if duplicate_key in seen_questions:
            raise ValueError(
                "Mock Interview AI generated "
                "duplicate questions."
            )


        seen_questions.add(
            duplicate_key
        )


        skill_target = (
            item.skill_target.strip()
            if item.skill_target
            else None
        )


        generated_type = (
            _normalize_interview_type(
                item.interview_type,
                fallback=normalized_type,
            )
        )


        normalized_questions.append(
            {
                "question_number":
                    index,

                "question":
                    question,

                "skill_target":
                    skill_target,

                "interview_type":
                    generated_type,

                # Session state fields.
                #
                # These are intentionally prepared
                # here so the session service can
                # persist the complete interview
                # immediately.

                "answer":
                    None,

                "score":
                    None,

                "feedback":
                    None,

                "strengths":
                    [],

                "improvements":
                    [],

                "better_answer_approach":
                    None,
            }
        )


    return normalized_questions


# ==================================================
# GENERATE ONE INTERVIEW QUESTION
# ==================================================
#
# IMPORTANT:
#
# Keep this function for backward compatibility.
#
# Existing services/tests may still call it.
# The optimized Mock Interview session flow should
# use generate_interview_questions(...) instead.
# ==================================================


def generate_interview_question(
    *,
    interview_type: str,
    question_number: int,
    total_questions: int,
    resume_context: str,
    job_description: str | None = None,
    skill_gaps: list[str] | None = None,
    previous_questions: list[str] | None = None,
) -> dict[str, Any]:
    """
    Generate exactly one interview question.

    This function remains available for backward
    compatibility.

    New Mock Interview sessions should prefer
    generate_interview_questions(...).
    """

    skill_gaps = (
        skill_gaps or []
    )


    previous_questions = (
        previous_questions or []
    )


    normalized_type = (
        _normalize_interview_type(
            interview_type
        )
    )


    jd_context = (
        _build_jd_context(
            job_description
        )
    )


    gaps_context = (
        _build_skill_gap_context(
            skill_gaps
        )
    )


    previous_context = (
        "\n".join(
            (
                f"- {question}"
            )
            for question
            in previous_questions
        )
        if previous_questions
        else "None."
    )


    prompt = f"""
You are CareerPilot AI's Mock Interviewer.

Generate exactly ONE interview question for an
entry-level or fresher candidate.


INTERVIEW SETTINGS

Selected interview mode:
{normalized_type}

Current question:
{question_number} of {total_questions}


RESUME CONTEXT

{resume_context}


TARGET JOB DESCRIPTION

{jd_context}


IDENTIFIED SKILL GAPS

{gaps_context}


QUESTIONS ALREADY ASKED

{previous_context}


RULES

1. Generate exactly one question.

2. Keep difficulty appropriate for a fresher or
   entry-level candidate.

3. Never ask senior-level system design questions
   unless the job explicitly requires them.

4. Never assume professional work experience.

5. Projects, internships, academics,
   certifications, coursework and learning
   experiences are valid fresher evidence.

6. For technical interviews:
   prioritize technical requirements from the JD,
   resume and identified skill gaps.

7. For behavioral interviews:
   ask about projects, teamwork, learning,
   challenges, communication or academic work.

8. For HR interviews:
   focus on motivation, adaptability, career
   goals, communication, strengths and workplace
   attitude.

9. Never repeat a previously asked question.

10. Do not provide an answer.

11. Do not provide hints.

12. Do not evaluate the candidate yet.

13. skill_target should identify the main skill
    or competency being evaluated.

14. interview_type must be one of:

    technical
    behavioral
    hr

15. question_number must be exactly:

{question_number}
"""


    result = (
        question_llm.invoke(
            prompt
        )
    )


    if result is None:
        raise ValueError(
            "Mock Interview AI did not "
            "generate a question."
        )


    question = (
        result.question.strip()
        if result.question
        else ""
    )


    if not question:
        raise ValueError(
            "Mock Interview AI generated "
            "an empty question."
        )


    generated_type = (
        _normalize_interview_type(
            result.interview_type,
            fallback=normalized_type,
        )
    )


    return {
        "question_number":
            question_number,

        "question":
            question,

        "skill_target": (
            result.skill_target.strip()
            if result.skill_target
            else None
        ),

        "interview_type":
            generated_type,
    }


# ==================================================
# EVALUATE INTERVIEW ANSWER
# ==================================================


def evaluate_interview_answer(
    *,
    question: str,
    answer: str,
    skill_target: str | None = None,
    interview_type: str = "technical",
    resume_context: str = "",
    job_description: str | None = None,
) -> dict[str, Any]:
    """
    Evaluate one candidate answer.

    The score is constrained between 0 and 10.

    One answer evaluation = one Gemini request.
    """

    normalized_type = (
        _normalize_interview_type(
            interview_type
        )
    )


    jd_context = (
        _build_jd_context(
            job_description
        )
    )


    target = (
        skill_target
        or (
            "General interview "
            "competency"
        )
    )


    prompt = f"""
You are CareerPilot AI's Mock Interview evaluator.

Evaluate this answer fairly at a fresher or
entry-level expectation level.


INTERVIEW TYPE

{normalized_type}


SKILL / COMPETENCY

{target}


QUESTION

{question}


CANDIDATE ANSWER

{answer}


RESUME CONTEXT

{resume_context}


TARGET JOB DESCRIPTION

{jd_context}


EVALUATION RULES

1. Score the answer from 0 to 10.

2. Evaluate at entry-level expectations.

3. Do not penalize the candidate merely for
   lacking professional employment experience.

4. Projects, internships, coursework, academic
   work and certifications are valid evidence.

5. For technical answers evaluate:

   - technical correctness
   - relevance
   - clarity
   - important concepts covered

6. For behavioral answers evaluate:

   - context
   - candidate action
   - outcome
   - learning
   - clarity

7. For HR answers evaluate:

   - communication
   - relevance
   - professionalism
   - self-awareness

8. Never praise technically incorrect statements
   as correct.

9. Clearly identify missing or inaccurate
   concepts.

10. strengths should contain concise positive
    points.

11. improvements should contain concrete,
    actionable improvements.

12. better_answer_approach should explain how the
    candidate could structure a stronger response.

13. Do not invent experience or achievements the
    candidate did not mention.

14. Keep feedback concise enough to be practical.
"""


    result = (
        feedback_llm.invoke(
            prompt
        )
    )


    if result is None:
        raise ValueError(
            "Mock Interview AI could not "
            "evaluate the answer."
        )


    score = (
        _normalize_score(
            result.score,
            minimum=0,
            maximum=10,
        )
    )


    feedback = (
        result.feedback.strip()
        if result.feedback
        else (
            "The answer was evaluated, "
            "but detailed feedback was "
            "not generated."
        )
    )


    better_answer_approach = (
        result
        .better_answer_approach
    )


    if (
        better_answer_approach
        is not None
    ):
        better_answer_approach = (
            better_answer_approach
            .strip()
        ) or None


    return {
        "score":
            score,

        "feedback":
            feedback,

        "strengths":
            _normalize_string_list(
                result.strengths
            ),

        "improvements":
            _normalize_string_list(
                result.improvements
            ),

        "better_answer_approach":
            better_answer_approach,
    }


# ==================================================
# CALCULATE READINESS SCORE
# ==================================================


def calculate_readiness_score(
    questions_answers: list[
        dict[str, Any]
    ],
) -> float:
    """
    Calculate interview readiness deterministically
    from individual question scores.

    Gemini does not control the final numeric
    readiness score.
    """

    scores: list[float] = []


    for record in (
        questions_answers
    ):

        score = record.get(
            "score"
        )


        if score is None:
            continue


        normalized = (
            _normalize_score(
                score,
                minimum=0,
                maximum=10,
            )
        )


        scores.append(
            normalized
        )


    if not scores:
        return 0.0


    return round(
        (
            sum(scores)
            /
            len(scores)
        )
        * 10,
        1,
    )


# ==================================================
# GENERATE FINAL INTERVIEW SUMMARY
# ==================================================


def generate_interview_summary(
    *,
    questions_answers: list[
        dict[str, Any]
    ],
    interview_type: str,
    resume_context: str = "",
    job_description: str | None = None,
) -> dict[str, Any]:
    """
    Generate the final Mock Interview summary.

    CareerPilot calculates readiness_score
    deterministically.

    Gemini only generates qualitative coaching.
    """

    if not questions_answers:
        raise ValueError(
            "Cannot generate interview "
            "summary without answers."
        )


    normalized_type = (
        _normalize_interview_type(
            interview_type
        )
    )


    jd_context = (
        _build_jd_context(
            job_description
        )
    )


    # ==================================================
    # DETERMINISTIC READINESS SCORE
    # ==================================================


    readiness_score = (
        calculate_readiness_score(
            questions_answers
        )
    )


    # ==================================================
    # COMPACT INTERVIEW RECORD
    # ==================================================


    interview_records = []


    for record in (
        questions_answers
    ):

        interview_records.append(
            {
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

                "answer":
                    record.get(
                        "answer"
                    ),

                "score":
                    record.get(
                        "score"
                    ),

                "feedback":
                    record.get(
                        "feedback"
                    ),
            }
        )


    records_json = (
        json.dumps(
            interview_records,
            ensure_ascii=False,
            indent=2,
        )
    )


    prompt = f"""
You are CareerPilot AI's Mock Interview Coach.

The candidate has completed a fresher-level
Mock Interview.


INTERVIEW MODE

{normalized_type}


CAREERPILOT READINESS SCORE

{readiness_score}/100


INTERVIEW RECORDS

{records_json}


RESUME CONTEXT

{resume_context}


TARGET JOB DESCRIPTION

{jd_context}


RULES

1. Analyze patterns across all interview answers.

2. Do NOT recalculate or change the CareerPilot
   readiness score.

3. overall_feedback should summarize the
   candidate's interview performance.

4. strengths must be supported by the interview
   answers.

5. weak_areas must be supported by the interview
   answers.

6. recommended_next_steps should contain
   practical actions the candidate can take next.

7. Keep expectations appropriate for a fresher.

8. Do not invent experience, projects, skills,
   internships, certifications or achievements.

9. Keep recommendations realistic.

10. readiness_score in your structured response
    should be exactly:

{readiness_score}
"""


    result = (
        summary_llm.invoke(
            prompt
        )
    )


    if result is None:
        raise ValueError(
            "Mock Interview AI could not "
            "generate the final summary."
        )


    overall_feedback = (
        result.overall_feedback.strip()
        if result.overall_feedback
        else (
            "Mock Interview completed."
        )
    )


    # ==================================================
    # IMPORTANT
    # ==================================================
    #
    # Never trust an LLM-generated numeric score
    # here.
    #
    # CareerPilot owns the deterministic readiness
    # calculation.
    # ==================================================


    return {
        "readiness_score":
            readiness_score,

        "overall_feedback":
            overall_feedback,

        "strengths":
            _normalize_string_list(
                result.strengths
            ),

        "weak_areas":
            _normalize_string_list(
                result.weak_areas
            ),

        "recommended_next_steps":
            _normalize_string_list(
                result
                .recommended_next_steps
            ),
    }