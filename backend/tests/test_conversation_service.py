from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.database import SessionLocal
from app.models import (
    Conversation,
    Message,
    Resume,
    User,
)
from app.services.conversation_service import (
    delete_owned_conversation,
    get_or_create_owned_conversation,
    get_owned_conversation,
    list_conversation_messages,
    list_owned_conversations,
    rename_owned_conversation,
    save_conversation_message,
)


def _unique_email(
    label: str,
) -> str:
    return (
        f"careerpilot-{label}-"
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
            "conversation_service_test_hash"
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
            f"test-vector-{uuid4().hex}"
        ),
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


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


def test_conversation_message_persistence():
    db = SessionLocal()

    email = _unique_email(
        "message-persistence"
    )

    try:
        user = _create_user(
            db,
            email=email,
        )

        resume = _create_resume(
            db,
            user_id=user.id,
            filename="persistence-test.pdf",
        )

        thread_id = (
            f"thread-{uuid4().hex}"
        )
        empty_thread_id = (
    f"empty-thread-{uuid4().hex}"
)

        get_or_create_owned_conversation(
    db,
    user_id=user.id,
    thread_id=empty_thread_id,
    resume_id=resume.id,
)

        conversation = (
            get_or_create_owned_conversation(
                db,
                user_id=user.id,
                thread_id=thread_id,
                resume_id=resume.id,
            )
        )

        user_message = (
            save_conversation_message(
                db,
                conversation=conversation,
                role="user",
                content=(
                    "Help me prepare for "
                    "a backend developer role."
                ),
            )
        )

        assistant_message = (
            save_conversation_message(
                db,
                conversation=conversation,
                role="assistant",
                content=(
                    "Start with Java, SQL, "
                    "REST APIs, and Spring Boot."
                ),
            )
        )

        (
            restored_conversation,
            restored_messages,
        ) = list_conversation_messages(
            db,
            user_id=user.id,
            thread_id=thread_id,
        )

        assert (
            restored_conversation.id
            == conversation.id
        )

        assert (
            restored_conversation.resume_id
            == resume.id
        )

        assert restored_conversation.title == (
            "Help me prepare for "
            "a backend developer role."
        )

        assert len(restored_messages) == 2

        assert [
            message.role
            for message
            in restored_messages
        ] == [
            "user",
            "assistant",
        ]

        assert (
            restored_messages[0].id
            == user_message.id
        )

        assert (
            restored_messages[1].id
            == assistant_message.id
        )

        conversations = (
            list_owned_conversations(
                db,
                user_id=user.id,
            )
        )

        assert len(conversations) == 1

        assert (
            conversations[0].thread_id
            == thread_id
        )

    finally:
        _cleanup_users(
            db,
            email,
        )

        db.close()


def test_conversation_ownership_and_resume_lock():
    db = SessionLocal()

    owner_email = _unique_email(
        "conversation-owner"
    )

    other_email = _unique_email(
        "conversation-other"
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
            filename="owner-resume.pdf",
        )

        second_owner_resume = _create_resume(
            db,
            user_id=owner.id,
            filename=(
                "second-owner-resume.pdf"
            ),
        )

        thread_id = (
            f"thread-{uuid4().hex}"
        )

        get_or_create_owned_conversation(
            db,
            user_id=owner.id,
            thread_id=thread_id,
            resume_id=owner_resume.id,
        )

        with pytest.raises(
            HTTPException
        ) as ownership_error:
            get_owned_conversation(
                db,
                user_id=other_user.id,
                thread_id=thread_id,
            )

        assert (
            ownership_error.value.status_code
            == 403
        )

        with pytest.raises(
            HTTPException
        ) as resume_error:
            get_or_create_owned_conversation(
                db,
                user_id=owner.id,
                thread_id=thread_id,
                resume_id=(
                    second_owner_resume.id
                ),
            )

        assert (
            resume_error.value.status_code
            == 409
        )

    finally:
        _cleanup_users(
            db,
            owner_email,
            other_email,
        )

        db.close()


def test_conversation_rename_and_delete():
    db = SessionLocal()

    email = _unique_email(
        "rename-delete"
    )

    try:
        user = _create_user(
            db,
            email=email,
        )

        resume = _create_resume(
            db,
            user_id=user.id,
            filename="delete-test.pdf",
        )

        thread_id = (
            f"thread-{uuid4().hex}"
        )

        conversation = (
            get_or_create_owned_conversation(
                db,
                user_id=user.id,
                thread_id=thread_id,
                resume_id=resume.id,
            )
        )

        message = (
            save_conversation_message(
                db,
                conversation=conversation,
                role="user",
                content="Original title",
            )
        )

        renamed = (
            rename_owned_conversation(
                db,
                user_id=user.id,
                thread_id=thread_id,
                title=(
                    "Backend Career Preparation"
                ),
            )
        )

        assert renamed.title == (
            "Backend Career Preparation"
        )

        message_id = message.id
        conversation_id = conversation.id

        delete_owned_conversation(
            db,
            user_id=user.id,
            thread_id=thread_id,
        )

        deleted_conversation = db.scalar(
            select(Conversation).where(
                Conversation.id
                == conversation_id
            )
        )

        deleted_message = db.scalar(
            select(Message).where(
                Message.id == message_id
            )
        )

        assert deleted_conversation is None
        assert deleted_message is None

        with pytest.raises(
            HTTPException
        ) as missing_error:
            get_owned_conversation(
                db,
                user_id=user.id,
                thread_id=thread_id,
            )

        assert (
            missing_error.value.status_code
            == 404
        )

    finally:
        _cleanup_users(
            db,
            email,
        )

        db.close()