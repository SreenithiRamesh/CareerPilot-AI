import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

import app.main as main_module
from app.auth.dependencies import get_current_user
from app.database import SessionLocal, get_db
from app.models import Conversation, Message, User


def _unique_email(label: str) -> str:
    return (
        f"chat-hardening-{label}-"
        f"{uuid4().hex}@example.com"
    )


def _create_user(*, email: str) -> User:
    db = SessionLocal()

    try:
        user = User(
            email=email,
            password_hash="chat_hardening_test_hash",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

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


def _build_chat_client(
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


class SuccessfulGraph:
    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, graph_input, config):
        self.calls += 1

        return {
            "intent": "general",
            "response": "A stable CareerPilot response.",
        }


class FailOnceGraph:
    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, graph_input, config):
        self.calls += 1

        if self.calls == 1:
            raise RuntimeError(
                "Simulated AI provider failure"
            )

        return {
            "intent": "general",
            "response": "Recovered response.",
        }


class EmptyResponseGraph:
    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, graph_input, config):
        self.calls += 1

        return {
            "intent": "general",
            "response": "   ",
        }


def _request_payload(
    *,
    thread_id: str,
    request_id: str,
    message: str = "Help me prepare for interviews.",
) -> dict:
    return {
        "message": message,
        "request_id": request_id,
        "thread_id": thread_id,
    }


def test_completed_request_is_replayed_without_ai_call(
    monkeypatch,
):
    email = _unique_email("replay")
    user = _create_user(email=email)
    graph = SuccessfulGraph()
    thread_id = f"thread-{uuid4().hex}"
    request_id = f"request-{uuid4().hex}"

    monkeypatch.setattr(
        main_module,
        "career_router_graph",
        graph,
    )

    client = _build_chat_client(
        current_user=user
    )

    try:
        payload = _request_payload(
            thread_id=thread_id,
            request_id=request_id,
        )

        first_response = client.post(
            "/api/chat",
            json=payload,
        )
        replay_response = client.post(
            "/api/chat",
            json=payload,
        )

        assert first_response.status_code == 200
        assert replay_response.status_code == 200
        assert replay_response.json() == (
            first_response.json()
        )
        assert first_response.json()["request_id"] == (
            request_id
        )
        assert graph.calls == 1

        db = SessionLocal()

        try:
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.thread_id
                    == thread_id
                )
            )

            messages = db.scalars(
                select(Message)
                .where(
                    Message.conversation_id
                    == conversation.id,
                    Message.request_id
                    == request_id,
                )
                .order_by(Message.id.asc())
            ).all()

            assert [
                message.role
                for message in messages
            ] == [
                "user",
                "assistant",
            ]

            cached_payload = json.loads(
                messages[1].response_payload
            )
            assert cached_payload == first_response.json()

        finally:
            db.close()

    finally:
        main_module.app.dependency_overrides.clear()
        _cleanup_user(email=email)


def test_failed_ai_request_retries_without_duplicate_user(
    monkeypatch,
):
    email = _unique_email("retry")
    user = _create_user(email=email)
    graph = FailOnceGraph()
    thread_id = f"thread-{uuid4().hex}"
    request_id = f"request-{uuid4().hex}"

    monkeypatch.setattr(
        main_module,
        "career_router_graph",
        graph,
    )

    client = _build_chat_client(
        current_user=user
    )

    try:
        payload = _request_payload(
            thread_id=thread_id,
            request_id=request_id,
        )

        failed_response = client.post(
            "/api/chat",
            json=payload,
        )

        assert failed_response.status_code == 503

        recovered_response = client.post(
            "/api/chat",
            json=payload,
        )

        assert recovered_response.status_code == 200
        assert recovered_response.json()["response"] == (
            "Recovered response."
        )
        assert graph.calls == 2

        db = SessionLocal()

        try:
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.thread_id
                    == thread_id
                )
            )

            messages = db.scalars(
                select(Message)
                .where(
                    Message.conversation_id
                    == conversation.id,
                    Message.request_id
                    == request_id,
                )
                .order_by(Message.id.asc())
            ).all()

            assert [
                message.role
                for message in messages
            ] == [
                "user",
                "assistant",
            ]

        finally:
            db.close()

    finally:
        main_module.app.dependency_overrides.clear()
        _cleanup_user(email=email)


def test_request_id_conflict_rejects_different_content(
    monkeypatch,
):
    email = _unique_email("conflict")
    user = _create_user(email=email)
    graph = SuccessfulGraph()
    thread_id = f"thread-{uuid4().hex}"
    request_id = f"request-{uuid4().hex}"

    monkeypatch.setattr(
        main_module,
        "career_router_graph",
        graph,
    )

    client = _build_chat_client(
        current_user=user
    )

    try:
        first_response = client.post(
            "/api/chat",
            json=_request_payload(
                thread_id=thread_id,
                request_id=request_id,
                message="First request content.",
            ),
        )

        conflict_response = client.post(
            "/api/chat",
            json=_request_payload(
                thread_id=thread_id,
                request_id=request_id,
                message="Different request content.",
            ),
        )

        assert first_response.status_code == 200
        assert conflict_response.status_code == 409
        assert graph.calls == 1

    finally:
        main_module.app.dependency_overrides.clear()
        _cleanup_user(email=email)


def test_empty_ai_response_returns_503_without_assistant(
    monkeypatch,
):
    email = _unique_email("empty")
    user = _create_user(email=email)
    graph = EmptyResponseGraph()
    thread_id = f"thread-{uuid4().hex}"
    request_id = f"request-{uuid4().hex}"

    monkeypatch.setattr(
        main_module,
        "career_router_graph",
        graph,
    )

    client = _build_chat_client(
        current_user=user
    )

    try:
        response = client.post(
            "/api/chat",
            json=_request_payload(
                thread_id=thread_id,
                request_id=request_id,
            ),
        )

        assert response.status_code == 503
        assert graph.calls == 1

        db = SessionLocal()

        try:
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.thread_id
                    == thread_id
                )
            )

            messages = db.scalars(
                select(Message).where(
                    Message.conversation_id
                    == conversation.id,
                    Message.request_id
                    == request_id,
                )
            ).all()

            assert len(messages) == 1
            assert messages[0].role == "user"

        finally:
            db.close()

    finally:
        main_module.app.dependency_overrides.clear()
        _cleanup_user(email=email)


@pytest.mark.parametrize(
    "request_id",
    [
        None,
        "",
        "x" * 65,
    ],
)
def test_invalid_request_id_returns_422(
    monkeypatch,
    request_id,
):
    email = _unique_email("validation")
    user = _create_user(email=email)
    graph = SuccessfulGraph()

    monkeypatch.setattr(
        main_module,
        "career_router_graph",
        graph,
    )

    client = _build_chat_client(
        current_user=user
    )

    payload = {
        "message": "Validate this request.",
        "thread_id": f"thread-{uuid4().hex}",
    }

    if request_id is not None:
        payload["request_id"] = request_id

    try:
        response = client.post(
            "/api/chat",
            json=payload,
        )

        assert response.status_code == 422
        assert graph.calls == 0

    finally:
        main_module.app.dependency_overrides.clear()
        _cleanup_user(email=email)
