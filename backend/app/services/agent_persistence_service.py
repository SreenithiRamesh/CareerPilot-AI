import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.database import SessionLocal
from app.models import (
    AgentRun,
    AgentStep,
    Resume,
)


# ============================================================
# INTERNAL HELPERS
# ============================================================


def _to_json(
    value: Any,
) -> str:
    """
    Safely serialize agent execution data for
    MySQL TEXT columns.
    """

    return json.dumps(
        value,
        ensure_ascii=False,
        default=str,
    )


def _utc_now_naive() -> datetime:
    """
    Return the current UTC time as a naive datetime.

    The existing MySQL DateTime columns are timezone-naive,
    so timezone information is removed before persistence.
    """

    return datetime.now(
        timezone.utc
    ).replace(
        tzinfo=None
    )


def _validate_owned_resume(
    *,
    user_id: int,
    resume_id: int,
) -> None:
    """
    Ensure the selected resume belongs to the
    authenticated user before creating an AgentRun.
    """

    db = SessionLocal()

    try:
        resume = db.scalar(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
        )

        if resume is None:
            raise ValueError(
                "Selected resume does not belong "
                "to the authenticated user."
            )

    finally:
        db.close()


def _get_agent_run(
    db,
    *,
    agent_run_id: int,
) -> AgentRun:
    """
    Retrieve an AgentRun or raise a consistent error.
    """

    run = db.scalar(
        select(AgentRun).where(
            AgentRun.id == agent_run_id
        )
    )

    if run is None:
        raise ValueError(
            "Agent run was not found."
        )

    return run


# ============================================================
# START AGENT RUN
# ============================================================


def start_agent_run(
    *,
    user_id: int,
    resume_id: int,
    goal: str,
    thread_id: str | None = None,
) -> int:
    """
    Create a persistent AgentRun before autonomous
    execution begins.
    """

    if not goal.strip():
        raise ValueError(
            "Agent goal must not be empty."
        )

    _validate_owned_resume(
        user_id=user_id,
        resume_id=resume_id,
    )

    db = SessionLocal()

    try:
        run = AgentRun(
            user_id=user_id,
            resume_id=resume_id,
            thread_id=thread_id,
            goal=goal.strip(),
            status="running",
            final_response=None,
            iterations=0,
            completed_at=None,
        )

        db.add(run)
        db.commit()
        db.refresh(run)

        return run.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# SAVE AGENT STEP
# ============================================================


def save_agent_step(
    *,
    agent_run_id: int,
    step_number: int,
    planned_action: str,
    tool_name: str | None,
    tool_input: dict[str, Any] | None,
    observation: dict[str, Any] | None,
    status: str = "completed",
) -> int:
    """
    Persist one autonomous execution step.
    """

    if step_number < 1:
        raise ValueError(
            "step_number must be at least 1."
        )

    db = SessionLocal()

    try:
        _get_agent_run(
            db,
            agent_run_id=agent_run_id,
        )

        step = AgentStep(
            agent_run_id=agent_run_id,
            step_number=step_number,
            planned_action=planned_action,
            tool_name=tool_name,
            tool_input=(
                _to_json(tool_input)
                if tool_input is not None
                else None
            ),
            observation=(
                _to_json(observation)
                if observation is not None
                else None
            ),
            status=status,
        )

        db.add(step)
        db.commit()
        db.refresh(step)

        return step.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# COMPLETE AGENT RUN
# ============================================================


def complete_agent_run(
    *,
    agent_run_id: int,
    final_response: str,
    iterations: int,
) -> None:
    """
    Mark an AgentRun as successfully completed.

    Use this only when the user's goal was satisfied.
    """

    db = SessionLocal()

    try:
        run = _get_agent_run(
            db,
            agent_run_id=agent_run_id,
        )

        run.status = "completed"

        run.final_response = (
            final_response
        )

        run.iterations = max(
            iterations,
            0,
        )

        run.completed_at = (
            _utc_now_naive()
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# INCOMPLETE AGENT RUN
# ============================================================


def incomplete_agent_run(
    *,
    agent_run_id: int,
    final_response: str,
    iterations: int,
) -> None:
    """
    Mark an AgentRun as incomplete.

    An incomplete run means the agent executed safely,
    but could not fully satisfy the user's goal because
    required evidence, persisted analyses, or another
    prerequisite was unavailable.

    This is different from a failed run because no
    unrecoverable system exception necessarily occurred.
    """

    db = SessionLocal()

    try:
        run = _get_agent_run(
            db,
            agent_run_id=agent_run_id,
        )

        run.status = "incomplete"

        run.final_response = (
            final_response
        )

        run.iterations = max(
            iterations,
            0,
        )

        run.completed_at = (
            _utc_now_naive()
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# FAIL AGENT RUN
# ============================================================


def fail_agent_run(
    *,
    agent_run_id: int,
    error_message: str,
    iterations: int = 0,
) -> None:
    """
    Mark an AgentRun as failed.

    Use this for unrecoverable execution or system errors,
    rather than normal missing-evidence termination.
    """

    db = SessionLocal()

    try:
        run = _get_agent_run(
            db,
            agent_run_id=agent_run_id,
        )

        run.status = "failed"

        run.final_response = (
            error_message
        )

        run.iterations = max(
            iterations,
            0,
        )

        run.completed_at = (
            _utc_now_naive()
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()