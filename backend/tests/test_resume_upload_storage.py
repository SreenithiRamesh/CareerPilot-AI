from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

import app.resume_routes as resume_routes
from app.auth.dependencies import (
    get_current_user,
)
from app.database import (
    SessionLocal,
    get_db,
)
from app.models import Resume, User
from app.services.resume_storage import (
    ResumeStorageError,
)


class FakePdfPage:
    def extract_text(self) -> str:
        return (
            "Sreenithi Ramesh\n"
            "Java Backend Engineer\n"
            "Spring Boot REST API SQL"
        )


class FakePdfReader:
    def __init__(
        self,
        _stream,
    ) -> None:
        self.pages = [
            FakePdfPage(),
        ]


def _unique_email(
    label: str,
) -> str:
    return (
        f"resume-storage-route-{label}-"
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
                "resume_storage_route_hash"
            ),
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)

        return user

    finally:
        db.close()


def _get_latest_resume(
    *,
    user_id: int,
) -> Resume | None:
    db = SessionLocal()

    try:
        resume = db.scalar(
            select(Resume)
            .where(
                Resume.user_id == user_id
            )
            .order_by(
                Resume.id.desc()
            )
        )

        if resume is not None:
            db.expunge(resume)

        return resume

    finally:
        db.close()


def _cleanup_user(
    *,
    email: str,
) -> None:
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
    app = FastAPI()

    app.include_router(
        resume_routes.router
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


def _configure_pdf_processing(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        resume_routes,
        "PdfReader",
        FakePdfReader,
    )

    monkeypatch.setattr(
        resume_routes,
        "split_resume_text",
        lambda _text: [
            "Java backend resume chunk",
        ],
    )


def test_upload_stores_original_pdf_and_object_key(
    monkeypatch,
):
    email = _unique_email("success")

    user = _create_user(
        email=email
    )

    client = _build_client(
        current_user=user
    )

    uploaded = {}
    indexed = {}

    _configure_pdf_processing(
        monkeypatch
    )

    def fake_upload_resume_pdf(
        *,
        contents,
        user_id,
        resume_id,
    ):
        object_key = (
            f"users/{user_id}/"
            f"resumes/{resume_id}/"
            "original.pdf"
        )

        uploaded.update({
            "contents": contents,
            "user_id": user_id,
            "resume_id": resume_id,
            "object_key": object_key,
        })

        return object_key

    def fake_save_resume_vector_store(
        **kwargs,
    ):
        indexed.update(kwargs)

    monkeypatch.setattr(
        resume_routes,
        "upload_resume_pdf",
        fake_upload_resume_pdf,
    )

    monkeypatch.setattr(
        resume_routes,
        "save_resume_vector_store",
        fake_save_resume_vector_store,
    )

    try:
        response = client.post(
            "/api/resume/upload",
            params={
                "thread_id": (
                    "resume-storage-success"
                ),
            },
            files={
                "file": (
                    "sreenithi-resume.pdf",
                    b"%PDF-1.4 private resume",
                    "application/pdf",
                ),
            },
        )

        assert response.status_code == 200

        payload = response.json()

        assert (
            payload["processing_status"]
            == "completed"
        )

        assert (
            payload["original_file_stored"]
            is True
        )

        assert payload["message"] == (
            "Resume securely stored, "
            "processed, and indexed "
            "successfully."
        )

        resume = _get_latest_resume(
            user_id=user.id
        )

        assert resume is not None

        expected_key = (
            f"users/{user.id}/"
            f"resumes/{resume.id}/"
            "original.pdf"
        )

        assert (
            resume.s3_object_key
            == expected_key
        )

        assert uploaded == {
            "contents": (
                b"%PDF-1.4 private resume"
            ),
            "user_id": user.id,
            "resume_id": resume.id,
            "object_key": expected_key,
        }

        assert indexed[
            "thread_id"
        ] == "resume-storage-success"

        assert indexed[
            "user_id"
        ] == str(user.id)

        assert indexed[
            "resume_id"
        ] == str(resume.id)

    finally:
        _cleanup_user(
            email=email
        )


def test_indexing_failure_deletes_stored_pdf(
    monkeypatch,
):
    email = _unique_email(
        "index-failure"
    )

    user = _create_user(
        email=email
    )

    client = _build_client(
        current_user=user
    )

    deleted_keys = []

    _configure_pdf_processing(
        monkeypatch
    )

    def fake_upload_resume_pdf(
        *,
        contents,
        user_id,
        resume_id,
    ):
        del contents

        return (
            f"users/{user_id}/"
            f"resumes/{resume_id}/"
            "original.pdf"
        )

    def fail_vector_indexing(
        **_kwargs,
    ):
        raise RuntimeError(
            "Simulated indexing failure"
        )

    def fake_delete_resume_pdf(
        *,
        object_key,
    ):
        deleted_keys.append(
            object_key
        )

    monkeypatch.setattr(
        resume_routes,
        "upload_resume_pdf",
        fake_upload_resume_pdf,
    )

    monkeypatch.setattr(
        resume_routes,
        "save_resume_vector_store",
        fail_vector_indexing,
    )

    monkeypatch.setattr(
        resume_routes,
        "delete_resume_pdf",
        fake_delete_resume_pdf,
    )

    try:
        response = client.post(
            "/api/resume/upload",
            params={
                "thread_id": (
                    "resume-index-failure"
                ),
            },
            files={
                "file": (
                    "failure-resume.pdf",
                    b"%PDF-1.4 failure resume",
                    "application/pdf",
                ),
            },
        )

        assert response.status_code == 500

        assert response.json() == {
            "detail": (
                "Resume indexing failed."
            ),
        }

        resume = _get_latest_resume(
            user_id=user.id
        )

        assert resume is not None

        expected_key = (
            f"users/{user.id}/"
            f"resumes/{resume.id}/"
            "original.pdf"
        )

        assert deleted_keys == [
            expected_key,
        ]

        assert (
            resume.processing_status
            == "failed"
        )

        assert resume.s3_object_key is None

        assert (
            resume.vector_collection_id
            is None
        )

    finally:
        _cleanup_user(
            email=email
        )


def test_storage_failure_returns_controlled_error(
    monkeypatch,
):
    email = _unique_email(
        "storage-failure"
    )

    user = _create_user(
        email=email
    )

    client = _build_client(
        current_user=user
    )

    indexing_called = False

    _configure_pdf_processing(
        monkeypatch
    )

    def fail_storage(
        **_kwargs,
    ):
        raise ResumeStorageError(
            "Simulated storage failure"
        )

    def track_indexing(
        **_kwargs,
    ):
        nonlocal indexing_called
        indexing_called = True

    monkeypatch.setattr(
        resume_routes,
        "upload_resume_pdf",
        fail_storage,
    )

    monkeypatch.setattr(
        resume_routes,
        "save_resume_vector_store",
        track_indexing,
    )

    try:
        response = client.post(
            "/api/resume/upload",
            params={
                "thread_id": (
                    "resume-storage-failure"
                ),
            },
            files={
                "file": (
                    "storage-failure.pdf",
                    b"%PDF-1.4 storage failure",
                    "application/pdf",
                ),
            },
        )

        assert response.status_code == 502

        assert response.json() == {
            "detail": (
                "Resume file storage is "
                "temporarily unavailable."
            ),
        }

        assert indexing_called is False

        resume = _get_latest_resume(
            user_id=user.id
        )

        assert resume is not None

        assert (
            resume.processing_status
            == "failed"
        )

        assert resume.s3_object_key is None

        assert (
            resume.vector_collection_id
            is None
        )

    finally:
        _cleanup_user(
            email=email
        )