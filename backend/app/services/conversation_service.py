from datetime import datetime

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import (
    exists,
    select,
)
from sqlalchemy.orm import Session

from app.models import (
    Conversation,
    Message,
    Resume,
)


ALLOWED_MESSAGE_ROLES = {
    "user",
    "assistant",
}


def _normalize_message_content(
    content: str,
) -> str:
    cleaned = content.strip()

    if not cleaned:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail="Message content cannot be empty.",
        )

    return cleaned


def _generate_conversation_title(
    content: str,
    max_length: int = 60,
) -> str:
    cleaned = " ".join(
        content.split()
    )

    if not cleaned:
        return "New conversation"

    if len(cleaned) <= max_length:
        return cleaned

    return (
        cleaned[
            : max_length - 1
        ].rstrip()
        + "…"
    )


def get_owned_resume(
    db: Session,
    *,
    user_id: int,
    resume_id: int,
) -> Resume:
    resume = db.scalar(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == user_id,
        )
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    return resume


def get_owned_conversation(
    db: Session,
    *,
    user_id: int,
    thread_id: str,
) -> Conversation:
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.thread_id == thread_id,
            Conversation.user_id == user_id,
        )
    )

    if conversation is not None:
        return conversation

    existing_thread = db.scalar(
        select(Conversation.id).where(
            Conversation.thread_id == thread_id
        )
    )

    if existing_thread is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to access this conversation."
            ),
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Conversation not found.",
    )


def get_or_create_owned_conversation(
    db: Session,
    user_id: int,
    thread_id: str,
    resume_id: int | None = None,
) -> Conversation:
    thread_id = thread_id.strip()

    if not thread_id:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail="Thread ID cannot be empty.",
        )

    conversation = db.scalar(
        select(Conversation).where(
            Conversation.thread_id == thread_id
        )
    )

    if conversation is not None:
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to access this conversation."
                ),
            )

        if resume_id is not None:
            get_owned_resume(
                db,
                user_id=user_id,
                resume_id=resume_id,
            )

            if conversation.resume_id is None:
                conversation.resume_id = resume_id
                conversation.updated_at = (
                    datetime.utcnow()
                )

                try:
                    db.commit()
                    db.refresh(conversation)

                except Exception:
                    db.rollback()
                    raise

            elif (
                conversation.resume_id
                != resume_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "This conversation is already "
                        "associated with a different "
                        "resume."
                    ),
                )

        return conversation

    if resume_id is not None:
        get_owned_resume(
            db,
            user_id=user_id,
            resume_id=resume_id,
        )

    conversation = Conversation(
        user_id=user_id,
        resume_id=resume_id,
        thread_id=thread_id,
        title=None,
    )

    db.add(conversation)

    try:
        db.commit()
        db.refresh(conversation)

    except Exception:
        db.rollback()
        raise

    return conversation


def list_owned_conversations(
    db: Session,
    *,
    user_id: int,
) -> list[Conversation]:
    has_messages = exists(
        select(
            Message.id
        ).where(
            Message.conversation_id
            == Conversation.id
        )
    )

    conversations = db.scalars(
        select(Conversation)
        .where(
            Conversation.user_id
            == user_id,
            has_messages,
        )
        .order_by(
            Conversation.updated_at.desc(),
            Conversation.id.desc(),
        )
    ).all()

    return list(
        conversations
    )

def list_conversation_messages(
    db: Session,
    *,
    user_id: int,
    thread_id: str,
) -> tuple[
    Conversation,
    list[Message],
]:
    conversation = get_owned_conversation(
        db,
        user_id=user_id,
        thread_id=thread_id,
    )

    messages = db.scalars(
        select(Message)
        .where(
            Message.conversation_id
            == conversation.id
        )
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
    ).all()

    return (
        conversation,
        list(messages),
    )


def save_conversation_message(
    db: Session,
    *,
    conversation: Conversation,
    role: str,
    content: str,
) -> Message:
    normalized_role = (
        role.strip().lower()
    )

    if (
        normalized_role
        not in ALLOWED_MESSAGE_ROLES
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail="Unsupported message role.",
        )

    normalized_content = (
        _normalize_message_content(
            content
        )
    )

    message = Message(
        conversation_id=conversation.id,
        role=normalized_role,
        content=normalized_content,
    )

    db.add(message)

    if (
        normalized_role == "user"
        and not conversation.title
    ):
        conversation.title = (
            _generate_conversation_title(
                normalized_content
            )
        )

    conversation.updated_at = (
        datetime.utcnow()
    )

    try:
        db.commit()
        db.refresh(message)
        db.refresh(conversation)

    except Exception:
        db.rollback()
        raise

    return message


def rename_owned_conversation(
    db: Session,
    *,
    user_id: int,
    thread_id: str,
    title: str,
) -> Conversation:
    conversation = get_owned_conversation(
        db,
        user_id=user_id,
        thread_id=thread_id,
    )

    normalized_title = " ".join(
        title.split()
    )

    if not normalized_title:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Conversation title "
                "cannot be empty."
            ),
        )

    conversation.title = (
        normalized_title[:255]
    )

    conversation.updated_at = (
        datetime.utcnow()
    )

    try:
        db.commit()
        db.refresh(conversation)

    except Exception:
        db.rollback()
        raise

    return conversation


def delete_owned_conversation(
    db: Session,
    *,
    user_id: int,
    thread_id: str,
) -> None:
    conversation = get_owned_conversation(
        db,
        user_id=user_id,
        thread_id=thread_id,
    )

    db.delete(conversation)

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise