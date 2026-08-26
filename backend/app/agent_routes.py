from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.agent_schemas import (
    AgentRunRequest,
    AgentRunResponse,
    AgentStepResponse,
)
from app.auth.dependencies import (
    get_current_user,
)
from app.career_agent_graph import (
    career_agent_graph,
)
from app.career_agent_state import (
    create_initial_agent_state,
)
from app.models import User


router = APIRouter(
    prefix="/api/agent",
    tags=["Career Agent"],
)


@router.post(
    "/run",
    response_model=AgentRunResponse,
)
def run_career_agent(
    payload: AgentRunRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Execute a CareerPilot autonomous agent run.

    The authenticated user ID is taken from the JWT.
    The client never supplies user_id directly.
    """

    try:
        # =====================================================
        # 1. CREATE INITIAL AGENT STATE
        # =====================================================

        initial_state = (
            create_initial_agent_state(
                user_id=current_user.id,
                resume_id=payload.resume_id,
                thread_id=payload.thread_id,
                user_goal=payload.goal,
                max_iterations=(
                    payload.max_iterations
                ),
            )
        )

        # =====================================================
        # 2. RUN AUTONOMOUS LANGGRAPH AGENT
        # =====================================================

        result = (
            career_agent_graph.invoke(
                initial_state
            )
        )

        # =====================================================
        # 3. CONVERT OBSERVATIONS TO API STEPS
        # =====================================================

        executed_steps = []

        for observation in result.get(
            "observations",
            [],
        ):
            executed_steps.append(
                AgentStepResponse(
                    step_number=(
                        observation.get(
                            "step_index",
                            0,
                        )
                        + 1
                    ),
                    planned_action=(
                        observation.get(
                            "step"
                        )
                        or (
                            "Unknown agent "
                            "action"
                        )
                    ),
                    tool_name=(
                        observation.get(
                            "tool"
                        )
                    ),
                    tool_input=(
                        observation.get(
                            "tool_input",
                            {},
                        )
                    ),
                    result=(
                        observation.get(
                            "result",
                            {},
                        )
                    ),
                )
            )

        # =====================================================
        # 4. RETURN STRUCTURED AGENT RESULT
        # =====================================================

        return AgentRunResponse(
            agent_run_id=result.get(
                "agent_run_id"
            ),

            resume_id=payload.resume_id,

            thread_id=payload.thread_id,

            goal=payload.goal,

            plan=result.get(
                "plan",
                [],
            ),

            completed_steps=result.get(
                "completed_steps",
                [],
            ),

            executed_steps=executed_steps,

            iterations=result.get(
                "iteration_count",
                0,
            ),

            run_outcome=result.get(
                "run_outcome"
            ),

            task_complete=result.get(
                "task_complete",
                False,
            ),

            final_response=result.get(
                "final_response"
            ),
        )

    except ValueError as exc:
        # Common case:
        # resume ownership validation fails during
        # start_agent_run().
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "CareerPilot Agent execution failed."
            ),
        ) from exc