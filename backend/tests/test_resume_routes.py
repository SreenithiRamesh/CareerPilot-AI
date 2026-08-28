from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.dependencies import (
    get_current_user,
)
from app.database import (
    SessionLocal,
    get_db,
)
from app.models import (
    Resume,
    User,
)
from app.resume_routes import (
    router as resume_router,
)


def _unique_email(
    label: str,
) -> str:
    return (
        f"resume-route-{label}-"
        f"{uuid4().hex}@example.com"
    )


def _create_user(
    *,
    email: str,
) -> User:
    db = SessionLocal()

    try:
        user = User(
            email=email,
            password_hash=(
                "resume_route_test_hash"
            ),
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)

        return user

    finally:
        db.close()


def _create_resume(
    *,
    user_id: int,
    filename: str,
) -> Resume:
    db = SessionLocal()

    try:
        resume = Resume(
            user_id=user_id,
            original_filename=filename,
            processing_status="completed",
            vector_collection_id=(
                f"resume-route-"
                f"{uuid4().hex}"
            ),
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)
        db.expunge(resume)

        return resume

    finally:
        db.close()


def _cleanup_users(
    *emails: str,
) -> None:
    db = SessionLocal()

    try:
        db.rollback()

        users = db.scalars(
            select(User).where(
                User.email.in_(emails)
            )
        ).all()

        for user in users:
            db.delete(user)

        db.commit()

    finally:
        db.close()


def _build_client(
    *,
    current_user: User,
) -> TestClient:
    app = FastAPI()

    app.include_router(
        resume_router
    )

    def override_get_db():
        request_db = SessionLocal()

        try:
            yield request_db

        finally:
            request_db.close()

    def override_current_user():
        return current_user

    app.dependency_overrides[
        get_db
    ] = override_get_db

    app.dependency_overrides[
        get_current_user
    ] = override_current_user

    return TestClient(app)


def test_owner_can_restore_resume_metadata():
    email = _unique_email("owner")
    user = _create_user(
        email=email
    )

    resume = _create_resume(
        user_id=user.id,
        filename="sreenithi-resume.pdf",
    )

    client = _build_client(
        current_user=user
    )

    try:
        response = client.get(
            f"/api/resume/{resume.id}"
        )

        assert response.status_code == 200

        payload = response.json()

        assert payload["resume_id"] == (
            resume.id
        )

        assert payload["filename"] == (
            "sreenithi-resume.pdf"
        )

        assert (
            payload["processing_status"]
            == "completed"
        )

        assert (
            payload["vector_collection_id"]
            == resume.vector_collection_id
        )

        assert payload[
            "upload_timestamp"
        ]

    finally:
        _cleanup_users(email)


def test_resume_metadata_is_hidden_from_other_user():
    owner_email = _unique_email(
        "record-owner"
    )

    other_email = _unique_email(
        "other-user"
    )

    owner = _create_user(
        email=owner_email
    )

    other_user = _create_user(
        email=other_email
    )

    resume = _create_resume(
        user_id=owner.id,
        filename="private-resume.pdf",
    )

    client = _build_client(
        current_user=other_user
    )

    try:
        response = client.get(
            f"/api/resume/{resume.id}"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Resume not found."
        }

    finally:
        _cleanup_users(
            owner_email,
            other_email,
        )


def test_missing_resume_returns_404():
    email = _unique_email("missing")
    user = _create_user(
        email=email
    )

    client = _build_client(
        current_user=user
    )

    try:
        response = client.get(
            "/api/resume/999999999"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Resume not found."
        }

    finally:
        _cleanup_users(email)