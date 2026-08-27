from uuid import uuid4

from fastapi.testclient import TestClient
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from sqlalchemy import select

import app.agent_routes as agent_routes_module
import app.main as main_module
from app.auth.dependencies import get_current_user
from app.database import SessionLocal, get_db
from app.models import (
    Conversation,
    Message,
    Resume,
    User,
)


def _unique_email(label: str) -> str:
    return (
        f"agent-memory-{label}-"
        f"{uuid4().hex}@example.com"
    )


def _create_user_and_resume(
    *,
    email: str,
) -> tuple[User, Resume]:
    db = SessionLocal()

    try:
        user = User(
            email=email,
            password_hash=(
                "agent_memory_test_hash"
            ),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        resume = Resume(
            user_id=user.id,
            original_filename=(
                "agent-memory-resume.pdf"
            ),
            processing_status="completed",
            vector_collection_id=(
                f"agent-memory-{uuid4().hex}"
            ),
        )

        db.add(resume)
        db.commit()

        # The second commit expires user attributes.
        # Refresh and detach both records while their
        # setup session is still active.
        db.refresh(user)
        db.refresh(resume)

        db.expunge(user)
        db.expunge(resume)

        return user, resume

    finally:
        db.close()

def _cleanup_user(*, email: str) -> None:
    db = SessionLocal()

    try:
        db.rollback()

        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if user is not None:
            db.delete(user)
            db.commit()

    finally:
        db.close()


def _build_client(
    *,
    current_user: User,
) -> TestClient:
    def override_get_db():
        request_db = SessionLocal()

        try:
            yield request_db

        finally:
            request_db.close()

    def override_current_user():
        return current_user

    main_module.app.dependency_overrides[
        get_db
    ] = override_get_db

    main_module.app.dependency_overrides[
        get_current_user
    ] = override_current_user

    return TestClient(main_module.app)


def _request_payload(
    *,
    resume_id: int,
    thread_id: str,
    request_id: str,
    goal: str,
) -> dict:
    return {
        "resume_id": resume_id,
        "thread_id": thread_id,
        "request_id": request_id,
        "goal": goal,
        "max_iterations": 4,
    }


class SuccessfulAgentGraph:
    def __init__(self) -> None:
        self.calls = 0
        self.states = []

    def invoke(self, state):
        self.calls += 1
        self.states.append(state)

        goal = state["user_goal"]

        return {
            "agent_run_id": self.calls,
            "plan": [
                "Retrieve the relevant career evidence."
            ],
            "completed_steps": [
                "Retrieve the relevant career evidence."
            ],
            "observations": [
                {
                    "step_index": 0,
                    "step": (
                        "Retrieve the relevant "
                        "career evidence."
                    ),
                    "tool": "test_evidence_tool",
                    "tool_input": {},
                    "result": {
                        "success": True,
                    },
                }
            ],
            "iteration_count": 1,
            "run_outcome": "completed",
            "task_complete": True,
            "final_response": (
                f"Agent guidance for: {goal}"
            ),
        }


class FailOnceAgentGraph(
    SuccessfulAgentGraph
):
    def invoke(self, state):
        self.calls += 1
        self.states.append(state)

        if self.calls == 1:
            raise RuntimeError(
                "Simulated Agent provider failure"
            )

        goal = state["user_goal"]

        return {
            "agent_run_id": 2,
            "plan": ["Retry the Agent goal."],
            "completed_steps": [
                "Retry the Agent goal."
            ],
            "observations": [],
            "iteration_count": 1,
            "run_outcome": "completed",
            "task_complete": True,
            "final_response": (
                f"Recovered Agent guidance for: {goal}"
            ),
        }


def test_agent_turns_are_persisted_and_returned(
    monkeypatch,
):
    email = _unique_email("persistence")
    user, resume = _create_user_and_resume(
        email=email
    )
    graph = SuccessfulAgentGraph()
    client = _build_client(
        current_user=user
    )
    thread_id = f"agent-{uuid4().hex}"

    monkeypatch.setattr(
        agent_routes_module,
        "career_agent_graph",
        graph,
    )

    try:
        response = client.post(
            "/api/agent/run",
            json=_request_payload(
                resume_id=resume.id,
                thread_id=thread_id,
                request_id=(
                    f"request-{uuid4().hex}"
                ),
                goal=(
                    "Give me three Java backend "
                    "priorities."
                ),
            ),
        )

        assert response.status_code == 200
        assert graph.calls == 1

        detail_response = client.get(
            f"/api/conversations/{thread_id}"
        )

        assert detail_response.status_code == 200

        messages = detail_response.json()[
            "messages"
        ]

        assert [
            message["role"]
            for message in messages
        ] == ["user", "assistant"]

        assert [
            message["mode"]
            for message in messages
        ] == ["agent", "agent"]

    finally:
        main_module.app.dependency_overrides.clear()
        _cleanup_user(email=email)


def test_follow_up_receives_previous_agent_turns(
    monkeypatch,
):
    email = _unique_email("history")
    user, resume = _create_user_and_resume(
        email=email
    )
    graph = SuccessfulAgentGraph()
    client = _build_client(
        current_user=user
    )
    thread_id = f"agent-{uuid4().hex}"

    monkeypatch.setattr(
        agent_routes_module,
        "career_agent_graph",
        graph,
    )

    first_goal = (
        "Give me three Java backend priorities."
    )
    second_goal = (
        "Explain the first priority in detail."
    )

    try:
        first_response = client.post(
            "/api/agent/run",
            json=_request_payload(
                resume_id=resume.id,
                thread_id=thread_id,
                request_id=(
                    f"request-{uuid4().hex}"
                ),
                goal=first_goal,
            ),
        )

        second_response = client.post(
            "/api/agent/run",
            json=_request_payload(
                resume_id=resume.id,
                thread_id=thread_id,
                request_id=(
                    f"request-{uuid4().hex}"
                ),
                goal=second_goal,
            ),
        )

        assert first_response.status_code == 200
        assert second_response.status_code == 200
        assert graph.calls == 2

        history = graph.states[1][
            "messages"
        ]

        assert len(history) == 2
        assert isinstance(
            history[0],
            HumanMessage,
        )
        assert history[0].content == first_goal
        assert isinstance(
            history[1],
            AIMessage,
        )
        assert (
            "Agent guidance for:"
            in history[1].content
        )

    finally:
        main_module.app.dependency_overrides.clear()
        _cleanup_user(email=email)


def test_completed_agent_request_is_replayed(
    monkeypatch,
):
    email = _unique_email("replay")
    user, resume = _create_user_and_resume(
        email=email
    )
    graph = SuccessfulAgentGraph()
    client = _build_client(
        current_user=user
    )
    payload = _request_payload(
        resume_id=resume.id,
        thread_id=f"agent-{uuid4().hex}",
        request_id=f"request-{uuid4().hex}",
        goal="Build my Java backend learning plan.",
    )

    monkeypatch.setattr(
        agent_routes_module,
        "career_agent_graph",
        graph,
    )

    try:
        first_response = client.post(
            "/api/agent/run",
            json=payload,
        )
        replay_response = client.post(
            "/api/agent/run",
            json=payload,
        )

        assert first_response.status_code == 200
        assert replay_response.status_code == 200
        assert replay_response.json() == (
            first_response.json()
        )
        assert graph.calls == 1

    finally:
        main_module.app.dependency_overrides.clear()
        _cleanup_user(email=email)


def test_agent_request_id_rejects_different_goal(
    monkeypatch,
):
    email = _unique_email("conflict")
    user, resume = _create_user_and_resume(
        email=email
    )
    graph = SuccessfulAgentGraph()
    client = _build_client(
        current_user=user
    )
    thread_id = f"agent-{uuid4().hex}"
    request_id = f"request-{uuid4().hex}"

    monkeypatch.setattr(
        agent_routes_module,
        "career_agent_graph",
        graph,
    )

    try:
        first_response = client.post(
            "/api/agent/run",
            json=_request_payload(
                resume_id=resume.id,
                thread_id=thread_id,
                request_id=request_id,
                goal="Create my first learning plan.",
            ),
        )

        conflict_response = client.post(
            "/api/agent/run",
            json=_request_payload(
                resume_id=resume.id,
                thread_id=thread_id,
                request_id=request_id,
                goal="Use this ID for another goal.",
            ),
        )

        assert first_response.status_code == 200
        assert conflict_response.status_code == 409
        assert graph.calls == 1

    finally:
        main_module.app.dependency_overrides.clear()
        _cleanup_user(email=email)


def test_failed_agent_request_retries_without_duplicate(
    monkeypatch,
):
    email = _unique_email("retry")
    user, resume = _create_user_and_resume(
        email=email
    )
    graph = FailOnceAgentGraph()
    client = _build_client(
        current_user=user
    )
    thread_id = f"agent-{uuid4().hex}"
    request_id = f"request-{uuid4().hex}"
    payload = _request_payload(
        resume_id=resume.id,
        thread_id=thread_id,
        request_id=request_id,
        goal="Prepare my Java backend priorities.",
    )

    monkeypatch.setattr(
        agent_routes_module,
        "career_agent_graph",
        graph,
    )

    try:
        failed_response = client.post(
            "/api/agent/run",
            json=payload,
        )

        assert failed_response.status_code == 503

        db = SessionLocal()

        try:
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.thread_id
                    == thread_id
                )
            )

            failed_messages = db.scalars(
                select(Message).where(
                    Message.conversation_id
                    == conversation.id,
                    Message.mode == "agent",
                )
            ).all()

            assert len(failed_messages) == 1
            assert failed_messages[0].role == "user"

        finally:
            db.close()

        retry_response = client.post(
            "/api/agent/run",
            json=payload,
        )

        assert retry_response.status_code == 200
        assert graph.calls == 2

        db = SessionLocal()

        try:
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.thread_id
                    == thread_id
                )
            )

            completed_messages = db.scalars(
                select(Message).where(
                    Message.conversation_id
                    == conversation.id,
                    Message.mode == "agent",
                )
            ).all()

            assert len(completed_messages) == 2
            assert sorted(
                message.role
                for message in completed_messages
            ) == ["assistant", "user"]

        finally:
            db.close()

    finally:
        main_module.app.dependency_overrides.clear()
        _cleanup_user(email=email)
