from fastapi import FastAPI
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from app.resume_routes import router as resume_router
from app.router_graph import career_router_graph
from app.tool_agent_graph import tool_agent_graph

app = FastAPI(title="CareerPilot AI")

app.include_router(resume_router)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"

    name: str | None = None
    education: str | None = None
    graduation_year: int | None = None
    skills: list[str] = Field(default_factory=list)
    target_role: str | None = None
    career_goal: str | None = None
    job_description: str | None = None

    history: list[ChatMessage] = Field(default_factory=list)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "CareerPilot AI backend is running",
    }

@app.post("/api/tool-agent-test")
def tool_agent_test(request: ChatRequest):
    result = tool_agent_graph.invoke(
        {
            "thread_id": request.thread_id,
            "job_description": request.job_description or "",
            "messages": [
                HumanMessage(content=request.message)
            ],
        }
    )

    final_message = result["messages"][-1]

    return {
        "response": final_message.content,
        "thread_id": request.thread_id,
    }

@app.post("/api/chat")
def chat(request: ChatRequest):

    # LangGraph uses thread_id to identify the conversation.
    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    # Base graph state for every request.
    graph_input = {
        "message": request.message,
        "intent": "",
        "response": "",
        "thread_id": request.thread_id,

        # Current user turn is added to LangGraph conversation memory.
        "messages": [
            HumanMessage(content=request.message)
        ],
    }

    # Only send profile values when they are actually provided.
    # This prevents blank values from overwriting previously saved state.

    if request.name:
        graph_input["name"] = request.name

    if request.education:
        graph_input["education"] = request.education

    if request.graduation_year:
        graph_input["graduation_year"] = str(
            request.graduation_year
        )

    if request.skills:
        graph_input["skills"] = request.skills

    if request.target_role:
        graph_input["target_role"] = request.target_role

    if request.career_goal:
        graph_input["career_goal"] = request.career_goal

    # Job description is only needed for JD matching requests.
    if request.job_description:
        graph_input["job_description"] = request.job_description

    # Run the complete LangGraph agent workflow.
    result = career_router_graph.invoke(
        graph_input,
        config=config,
    )

    return {
        "intent": result["intent"],
        "response": result["response"],
        "thread_id": request.thread_id,
    }