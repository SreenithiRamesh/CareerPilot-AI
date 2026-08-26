from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import select

from app.auth.dependencies import (
    get_current_user,
)
from app.auth.security import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    create_access_token,
)
from app.conversation_routes import (
    router as conversation_router,
)
from app.database import (
    SessionLocal,
    get_db,
)
from app.models import (
    Conversation,
    Message,
    Resume,
    User,
)
from app.services.conversation_service import (
    get_or_create_owned_conversation,
    save_conversation_message,
)


def _unique_email(
    label: str,
) -> str:
    return (
        f"conversation-route-{label}-"
        f"{uuid4().hex}@example.com"
    )


def _create_user(
    db,
    *,
    email: str,
) -> User:
    user = User(
        email=email,
        password_hash=(
            "conversation_route_test_hash"
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def _create_resume(
    db,
    *,
    user_id: int,
    filename: str,
) -> Resume:
    resume = Resume(
        user_id=user_id,
        original_filename=filename,
        processing_status="completed",
        vector_collection_id=(
            f"route-test-{uuid4().hex}"
        ),
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


def _create_populated_conversation(
    db,
    *,
    user: User,
    resume: Resume,
    title_message: str,
) -> Conversation:
    conversation = (
        get_or_create_owned_conversation(
            db,
            user_id=user.id,
            thread_id=(
                f"route-thread-"
                f"{uuid4().hex}"
            ),
            resume_id=resume.id,
        )
    )

    save_conversation_message(
        db,
        conversation=conversation,
        role="user",
        content=title_message,
    )

    save_conversation_message(
        db,
        conversation=conversation,
        role="assistant",
        content=(
            "CareerPilot route-test "
            "assistant response."
        ),
    )

    return conversation


def _cleanup_users(
    db,
    *emails: str,
) -> None:
    db.rollback()

    users = db.scalars(
        select(User).where(
            User.email.in_(emails)
        )
    ).all()

    for user in users:
        db.delete(user)

    db.commit()


def _build_test_client(
    *,
    current_user: User | None = None,
    use_real_auth: bool = False,
) -> TestClient:
    app = FastAPI()

    app.include_router(
        conversation_router
    )

    def override_get_db():
        request_db = SessionLocal()

        try:
            yield request_db

        finally:
            request_db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    if not use_real_auth:
        if current_user is None:
            raise ValueError(
                "current_user is required "
                "when authentication is overridden."
            )

        def override_current_user():
            return current_user

        app.dependency_overrides[
            get_current_user
        ] = override_current_user

    return TestClient(app)


def _expired_access_token(
    *,
    subject: str,
) -> str:
    payload = {
        "sub": subject,
        "exp": (
            datetime.now(
                timezone.utc
            )
            - timedelta(
                minutes=5
            )
        ),
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def test_list_conversations_returns_only_owned_non_empty():
    db = SessionLocal()

    owner_email = _unique_email(
        "list-owner"
    )

    other_email = _unique_email(
        "list-other"
    )

    try:
        owner = _create_user(
            db,
            email=owner_email,
        )

        other_user = _create_user(
            db,
            email=other_email,
        )

        owner_resume = _create_resume(
            db,
            user_id=owner.id,
            filename="owner-list.pdf",
        )

        other_resume = _create_resume(
            db,
            user_id=other_user.id,
            filename="other-list.pdf",
        )

        owned_conversation = (
            _create_populated_conversation(
                db,
                user=owner,
                resume=owner_resume,
                title_message=(
                    "Owned conversation"
                ),
            )
        )

        get_or_create_owned_conversation(
            db,
            user_id=owner.id,
            thread_id=(
                f"empty-{uuid4().hex}"
            ),
            resume_id=owner_resume.id,
        )

        _create_populated_conversation(
            db,
            user=other_user,
            resume=other_resume,
            title_message=(
                "Other user conversation"
            ),
        )

        client = _build_test_client(
            current_user=owner
        )

        response = client.get(
            "/api/conversations"
        )

        assert response.status_code == 200

        payload = response.json()

        assert len(
            payload["conversations"]
        ) == 1

        assert (
            payload[
                "conversations"
            ][0]["thread_id"]
            == owned_conversation.thread_id
        )

        assert (
            payload[
                "conversations"
            ][0]["title"]
            == "Owned conversation"
        )

    finally:
        _cleanup_users(
            db,
            owner_email,
            other_email,
        )

        db.close()


def test_get_conversation_returns_ordered_messages():
    db = SessionLocal()

    email = _unique_email(
        "detail"
    )

    try:
        user = _create_user(
            db,
            email=email,
        )

        resume = _create_resume(
            db,
            user_id=user.id,
            filename="detail.pdf",
        )

        conversation = (
            _create_populated_conversation(
                db,
                user=user,
                resume=resume,
                title_message=(
                    "Detail route test"
                ),
            )
        )

        client = _build_test_client(
            current_user=user
        )

        response = client.get(
            (
                "/api/conversations/"
                f"{conversation.thread_id}"
            )
        )

        assert response.status_code == 200

        payload = response.json()

        assert payload["thread_id"] == (
            conversation.thread_id
        )

        assert payload["resume_id"] == (
            resume.id
        )

        assert [
            message["role"]
            for message
            in payload["messages"]
        ] == [
            "user",
            "assistant",
        ]

        assert (
            payload["messages"][0][
                "content"
            ]
            == "Detail route test"
        )

    finally:
        _cleanup_users(
            db,
            email,
        )

        db.close()


def test_rename_conversation_route():
    db = SessionLocal()

    email = _unique_email(
        "rename"
    )

    try:
        user = _create_user(
            db,
            email=email,
        )

        resume = _create_resume(
            db,
            user_id=user.id,
            filename="rename.pdf",
        )

        conversation = (
            _create_populated_conversation(
                db,
                user=user,
                resume=resume,
                title_message=(
                    "Original route title"
                ),
            )
        )

        client = _build_test_client(
            current_user=user
        )

        response = client.patch(
            (
                "/api/conversations/"
                f"{conversation.thread_id}"
            ),
            json={
                "title": (
                    "Renamed through API"
                )
            },
        )

        assert response.status_code == 200

        assert (
            response.json()["title"]
            == "Renamed through API"
        )

        verification_db = SessionLocal()

        try:
            stored = verification_db.get(
                Conversation,
                conversation.id,
            )

            assert stored is not None

            assert stored.title == (
                "Renamed through API"
            )

        finally:
            verification_db.close()

    finally:
        _cleanup_users(
            db,
            email,
        )

        db.close()


def test_delete_conversation_route_cascades_messages():
    db = SessionLocal()

    email = _unique_email(
        "delete"
    )

    try:
        user = _create_user(
            db,
            email=email,
        )

        resume = _create_resume(
            db,
            user_id=user.id,
            filename="delete.pdf",
        )

        conversation = (
            _create_populated_conversation(
                db,
                user=user,
                resume=resume,
                title_message=(
                    "Delete route test"
                ),
            )
        )

        conversation_id = (
            conversation.id
        )

        message_ids = db.scalars(
            select(Message.id).where(
                Message.conversation_id
                == conversation_id
            )
        ).all()

        client = _build_test_client(
            current_user=user
        )

        response = client.delete(
            (
                "/api/conversations/"
                f"{conversation.thread_id}"
            )
        )

        assert response.status_code == 200

        assert response.json() == {
            "deleted": True,
            "thread_id": (
                conversation.thread_id
            ),
        }

        verification_db = SessionLocal()

        try:
            assert (
                verification_db.get(
                    Conversation,
                    conversation_id,
                )
                is None
            )

            deleted_messages = (
                verification_db.scalars(
                    select(Message).where(
                        Message.id.in_(
                            message_ids
                        )
                    )
                ).all()
            )

            assert deleted_messages == []

        finally:
            verification_db.close()

    finally:
        _cleanup_users(
            db,
            email,
        )

        db.close()


@pytest.mark.parametrize(
    (
        "method",
        "payload",
    ),
    [
        (
            "get",
            None,
        ),
        (
            "patch",
            {
                "title": (
                    "Unauthorized rename"
                )
            },
        ),
        (
            "delete",
            None,
        ),
    ],
)
def test_cross_user_conversation_access_returns_403(
    method,
    payload,
):
    db = SessionLocal()

    owner_email = _unique_email(
        f"cross-owner-{method}"
    )

    other_email = _unique_email(
        f"cross-other-{method}"
    )

    try:
        owner = _create_user(
            db,
            email=owner_email,
        )

        other_user = _create_user(
            db,
            email=other_email,
        )

        resume = _create_resume(
            db,
            user_id=owner.id,
            filename=(
                f"cross-{method}.pdf"
            ),
        )

        conversation = (
            _create_populated_conversation(
                db,
                user=owner,
                resume=resume,
                title_message=(
                    "Private conversation"
                ),
            )
        )

        client = _build_test_client(
            current_user=other_user
        )

        path = (
            "/api/conversations/"
            f"{conversation.thread_id}"
        )

        if method == "get":
            response = client.get(
                path
            )

        elif method == "patch":
            response = client.patch(
                path,
                json=payload,
            )

        else:
            response = client.delete(
                path
            )

        assert response.status_code == 403

    finally:
        _cleanup_users(
            db,
            owner_email,
            other_email,
        )

        db.close()


def test_unknown_conversation_returns_404():
    db = SessionLocal()

    email = _unique_email(
        "missing"
    )

    try:
        user = _create_user(
            db,
            email=email,
        )

        client = _build_test_client(
            current_user=user
        )

        response = client.get(
            (
                "/api/conversations/"
                f"missing-{uuid4().hex}"
            )
        )

        assert response.status_code == 404

    finally:
        _cleanup_users(
            db,
            email,
        )

        db.close()


def test_valid_bearer_token_is_accepted():
    db = SessionLocal()

    email = _unique_email(
        "valid-token"
    )

    try:
        user = _create_user(
            db,
            email=email,
        )

        client = _build_test_client(
            use_real_auth=True
        )

        token = create_access_token(
            subject=str(user.id)
        )

        response = client.get(
            "/api/conversations",
            headers={
                "Authorization": (
                    f"Bearer {token}"
                )
            },
        )

        assert response.status_code == 200

    finally:
        _cleanup_users(
            db,
            email,
        )

        db.close()


def test_missing_bearer_token_returns_401():
    client = _build_test_client(
        use_real_auth=True
    )

    response = client.get(
        "/api/conversations"
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "token",
    [
        "not-a-valid-jwt",
        None,
    ],
)
def test_invalid_or_expired_token_returns_401(
    token,
):
    db = SessionLocal()

    email = _unique_email(
        "invalid-token"
    )

    try:
        user = _create_user(
            db,
            email=email,
        )

        client = _build_test_client(
            use_real_auth=True
        )

        request_token = (
            token
            if token is not None
            else _expired_access_token(
                subject=str(user.id)
            )
        )

        response = client.get(
            "/api/conversations",
            headers={
                "Authorization": (
                    f"Bearer {request_token}"
                )
            },
        )

        assert response.status_code == 401

    finally:
        _cleanup_users(
            db,
            email,
        )

        db.close()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {
            "title": "",
        },
        {
            "title": "x" * 256,
        },
    ],
)
def test_invalid_rename_payload_returns_422(
    payload,
):
    db = SessionLocal()

    email = _unique_email(
        "invalid-rename"
    )

    try:
        user = _create_user(
            db,
            email=email,
        )

        resume = _create_resume(
            db,
            user_id=user.id,
            filename=(
                "invalid-rename.pdf"
            ),
        )

        conversation = (
            _create_populated_conversation(
                db,
                user=user,
                resume=resume,
                title_message=(
                    "Rename validation"
                ),
            )
        )

        client = _build_test_client(
            current_user=user
        )

        response = client.patch(
            (
                "/api/conversations/"
                f"{conversation.thread_id}"
            ),
            json=payload,
        )

        assert response.status_code == 422

    finally:
        _cleanup_users(
            db,
            email,
        )

        db.close()
