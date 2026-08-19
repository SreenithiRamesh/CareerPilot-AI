from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation


def get_or_create_owned_conversation(
    db: Session,
    user_id: int,
    thread_id: str,
) -> Conversation:
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.thread_id == thread_id
        )
    )

    # Thread does not exist yet.
    # Create it for the authenticated user.
    if conversation is None:
        conversation = Conversation(
            user_id=user_id,
            thread_id=thread_id,
        )

        db.add(conversation)

        try:
            db.commit()
            db.refresh(conversation)

        except Exception:
            db.rollback()
            raise

        return conversation

    # Thread exists but belongs to another user.
    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to access this conversation."
            ),
        )

    return conversation