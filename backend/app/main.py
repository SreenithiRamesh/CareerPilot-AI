from fastapi import Depends, FastAPI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth_routes import router as auth_router
from app.database import get_db
from app.models import User
from app.resume_routes import router as resume_router
from app.router_graph import career_router_graph
from app.services.conversation_service import (
    get_or_create_owned_conversation,
)
from app.tool_agent_graph import tool_agent_graph


app = FastAPI(
    title="CareerPilot AI"
)

app.include_router(
    resume_router
)

app.include_router(
    auth_router
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str

    resume_id: int | None = None

    thread_id: str = "default"

    name: str | None = None

    education: str | None = None

    graduation_year: int | None = None

    skills: list[str] = Field(
        default_factory=list
    )

    target_role: str | None = None

    career_goal: str | None = None

    job_description: str | None = None

    history: list[ChatMessage] = Field(
        default_factory=list
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": (
            "CareerPilot AI backend is running"
        ),
    }


@app.post("/api/tool-agent-test")
def tool_agent_test(
    request: ChatRequest,
):
    result = tool_agent_graph.invoke(
        {
            "thread_id": request.thread_id,
            "job_description": (
                request.job_description or ""
            ),
            "messages": [
                HumanMessage(
                    content=request.message
                )
            ],
        }
    )

    final_message = (
        result["messages"][-1]
    )

    return {
        "response": final_message.content,
        "thread_id": request.thread_id,
    }


@app.post("/api/chat")
def chat(
    request: ChatRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    # --------------------------------------------------
    # 1. Validate conversation ownership
    # --------------------------------------------------
    #
    # If the thread does not exist, it is created for
    # the authenticated user.
    #
    # If it exists and belongs to another user,
    # conversation_service raises HTTP 403.
    #
    get_or_create_owned_conversation(
        db=db,
        user_id=current_user.id,
        thread_id=request.thread_id,
    )

    # --------------------------------------------------
    # 2. Configure LangGraph conversation identity
    # --------------------------------------------------

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    # --------------------------------------------------
    # 3. Build base graph state
    # --------------------------------------------------

    graph_input = {
        "message": request.message,
        "intent": "",
        "response": "",
        "thread_id": request.thread_id,

        # Authenticated ownership information
        "user_id": current_user.id,
        "resume_id": request.resume_id,

        # Current user turn for LangGraph memory
        "messages": [
            HumanMessage(
                content=request.message
            )
        ],
    }

    # --------------------------------------------------
    # 4. Add profile fields only when supplied
    # --------------------------------------------------
    #
    # This prevents blank values from overwriting
    # profile information already present in the
    # LangGraph state.
    #

    if request.name:
        graph_input["name"] = (
            request.name
        )

    if request.education:
        graph_input["education"] = (
            request.education
        )

    if request.graduation_year:
        graph_input[
            "graduation_year"
        ] = str(
            request.graduation_year
        )

    if request.skills:
        graph_input["skills"] = (
            request.skills
        )

    if request.target_role:
        graph_input[
            "target_role"
        ] = request.target_role

    if request.career_goal:
        graph_input[
            "career_goal"
        ] = request.career_goal

    # --------------------------------------------------
    # 5. Add JD only when provided
    # --------------------------------------------------

    if request.job_description:
        graph_input[
            "job_description"
        ] = request.job_description

    # --------------------------------------------------
    # 6. Execute LangGraph workflow
    # --------------------------------------------------

    result = career_router_graph.invoke(
        graph_input,
        config=config,
    )

    # --------------------------------------------------
    # 7. Return API response
    # --------------------------------------------------

    return {
        "intent": result["intent"],
        "response": result["response"],
        "thread_id": request.thread_id,
    }