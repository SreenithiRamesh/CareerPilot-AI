import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from sqlalchemy.orm import Session

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
from app.database import get_db
from app.models import User
from app.services.conversation_service import (
    get_conversation_message_by_request,
    get_or_create_owned_conversation,
    list_conversation_messages,
    save_conversation_message,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/agent",
    tags=["Career Agent"],
)


def _build_agent_history(
    messages,
    *,
    current_request_id: str,
):
    """
    Convert persisted Agent conversation messages into
    LangChain messages for the next autonomous run.

    Messages belonging to the current request are excluded
    because the current goal is supplied separately through
    user_goal.
    """

    history = []

    for message in messages:
        if (
            message.request_id
            == current_request_id
        ):
            continue

        if message.role == "user":
            history.append(
                HumanMessage(
                    content=message.content
                )
            )

        elif message.role == "assistant":
            history.append(
                AIMessage(
                    content=message.content
                )
            )

    # Prevent an old thread from growing the Agent prompt
    # indefinitely.
    return history[-12:]


def _build_executed_steps(
    observations,
) -> list[AgentStepResponse]:
    """
    Convert internal Agent observations into the
    public API response structure.
    """

    executed_steps = []

    for observation in observations:
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
                    observation.get("step")
                    or "Unknown agent action"
                ),
                tool_name=(
                    observation.get("tool")
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

    return executed_steps


@router.post(
    "/run",
    response_model=AgentRunResponse,
)
def run_career_agent(
    payload: AgentRunRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Execute a persistent CareerPilot autonomous Agent run.

    Agent goals and final responses are stored as conversation
    messages with mode="agent". A completed request can be
    replayed safely using the same request_id without running
    the autonomous workflow again.
    """

    conversation = (
        get_or_create_owned_conversation(
            db,
            user_id=current_user.id,
            thread_id=payload.thread_id,
            resume_id=payload.resume_id,
        )
    )

    try:
        # =====================================================
        # 1. PERSIST OR REUSE THE USER'S AGENT GOAL
        # =====================================================

        save_conversation_message(
            db,
            conversation=conversation,
            role="user",
            content=payload.goal,
            request_id=payload.request_id,
            mode="agent",
        )

        # =====================================================
        # 2. REPLAY AN ALREADY COMPLETED REQUEST
        # =====================================================

        existing_assistant_message = (
            get_conversation_message_by_request(
                db,
                conversation=conversation,
                request_id=payload.request_id,
                role="assistant",
                mode="agent",
            )
        )

        if (
            existing_assistant_message
            is not None
            and existing_assistant_message.response_payload
        ):
            return (
                AgentRunResponse.model_validate_json(
                    existing_assistant_message.response_payload
                )
            )

        # =====================================================
        # 3. LOAD PREVIOUS AGENT CONVERSATION TURNS
        # =====================================================

        (
            _,
            persisted_messages,
        ) = list_conversation_messages(
            db,
            user_id=current_user.id,
            thread_id=payload.thread_id,
            mode="agent",
        )

        agent_history = _build_agent_history(
            persisted_messages,
            current_request_id=(
                payload.request_id
            ),
        )

        # =====================================================
        # 4. CREATE AGENT STATE WITH CONVERSATION MEMORY
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
                messages=agent_history,
            )
        )

        # =====================================================
        # 5. RUN THE AUTONOMOUS LANGGRAPH AGENT
        # =====================================================

        result = career_agent_graph.invoke(
            initial_state
        )

        final_response = result.get(
            "final_response"
        )

        if (
            not isinstance(
                final_response,
                str,
            )
            or not final_response.strip()
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail=(
                    "CareerPilot Agent could not "
                    "generate a complete response. "
                    "Please retry."
                ),
            )

        final_response = (
            final_response.strip()
        )

        # =====================================================
        # 6. BUILD THE STRUCTURED API RESPONSE
        # =====================================================

        response = AgentRunResponse(
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
            executed_steps=(
                _build_executed_steps(
                    result.get(
                        "observations",
                        [],
                    )
                )
            ),
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
            final_response=final_response,
        )

        # =====================================================
        # 7. PERSIST FINAL RESPONSE AND REPLAY PAYLOAD
        # =====================================================

        save_conversation_message(
            db,
            conversation=conversation,
            role="assistant",
            content=final_response,
            request_id=payload.request_id,
            response_payload=(
                response.model_dump_json()
            ),
            mode="agent",
        )

        return response

    except HTTPException:
        raise

    except ValueError as exc:
        logger.warning(
            "CareerPilot Agent request rejected: %s",
            exc,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Log the complete traceback on the backend without
        # exposing implementation details through the API.
        logger.exception(
            "CareerPilot Agent execution failed."
        )

        # The user goal remains persisted, but no misleading
        # assistant message is created. Retrying with the same
        # request_id resumes without duplicating the goal.
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "CareerPilot Agent is temporarily "
                "unable to complete this request. "
                "Please retry."
            ),
        ) from exc