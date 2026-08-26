from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent_history_schemas import (
    AgentRunDetailResponse,
    AgentRunHistoryItem,
    AgentRunHistoryResponse,
    AgentStepDetail,
)
from app.auth.dependencies import (
    get_current_user,
)
from app.database import get_db
from app.models import (
    AgentRun,
    AgentStep,
    User,
)


router = APIRouter(
    prefix="/api/agent",
    tags=["Career Agent"],
)


# ============================================================
# AGENT RUN HISTORY
# ============================================================


@router.get(
    "/history",
    response_model=AgentRunHistoryResponse,
)
def get_agent_history(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    """
    Return AgentRun records belonging only to
    the authenticated CareerPilot user.

    The API never accepts user_id from the client.
    Ownership comes exclusively from the JWT user.
    """

    runs = db.scalars(
        select(AgentRun)
        .where(
            AgentRun.user_id
            == current_user.id
        )
        .order_by(
            AgentRun.created_at.desc(),
            AgentRun.id.desc(),
        )
    ).all()

    history_items = [
        AgentRunHistoryItem(
            id=run.id,
            resume_id=run.resume_id,
            thread_id=run.thread_id,
            goal=run.goal,
            status=run.status,
            iterations=run.iterations,
            created_at=run.created_at,
            completed_at=run.completed_at,
        )
        for run in runs
    ]

    return AgentRunHistoryResponse(
        runs=history_items,
        total=len(history_items),
    )


# ============================================================
# AGENT RUN DETAIL
# ============================================================


@router.get(
    "/history/{run_id}",
    response_model=AgentRunDetailResponse,
)
def get_agent_run_detail(
    run_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    """
    Return one owned AgentRun together with its
    persisted AgentStep execution trace.

    Missing and unowned runs both return 404 so
    another user's run existence is not disclosed.
    """

    # ========================================================
    # 1. LOAD RUN WITH OWNERSHIP ENFORCEMENT
    # ========================================================

    run = db.scalar(
        select(AgentRun)
        .where(
            AgentRun.id == run_id,
            AgentRun.user_id
            == current_user.id,
        )
    )

    # ========================================================
    # 2. MISSING OR UNOWNED RUN
    # ========================================================

    if run is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Agent run was not found."
            ),
        )

    # ========================================================
    # 3. LOAD ASSOCIATED AGENT STEPS
    # ========================================================

    steps = db.scalars(
        select(AgentStep)
        .where(
            AgentStep.agent_run_id
            == run.id
        )
        .order_by(
            AgentStep.step_number.asc(),
            AgentStep.id.asc(),
        )
    ).all()

    # ========================================================
    # 4. BUILD EXECUTION TRACE
    # ========================================================

    step_details = [
        AgentStepDetail(
            id=step.id,
            step_number=step.step_number,
            planned_action=(
                step.planned_action
            ),
            tool_name=step.tool_name,
            tool_input=step.tool_input,
            observation=step.observation,
            status=step.status,
            created_at=step.created_at,
        )
        for step in steps
    ]

    # ========================================================
    # 5. RETURN RUN DETAIL
    # ========================================================

    return AgentRunDetailResponse(
        id=run.id,
        resume_id=run.resume_id,
        thread_id=run.thread_id,
        goal=run.goal,
        status=run.status,
        iterations=run.iterations,
        final_response=(
            run.final_response
        ),
        created_at=run.created_at,
        completed_at=run.completed_at,
        steps=step_details,
        total_steps=len(
            step_details
        ),
    )