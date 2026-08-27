from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
)
from app.database import get_db
from app.models import User
from app.schemas.conversation import (
    ConversationDeleteResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationMessageResponse,
    ConversationRenameRequest,
    ConversationSummaryResponse,
)
from app.services.conversation_service import (
    delete_owned_conversation,
    list_conversation_messages,
    list_owned_conversations,
    rename_owned_conversation,
)


router = APIRouter(
    prefix="/api/conversations",
    tags=[
        "Career AI Conversations",
    ],
)


def _conversation_title(
    title: str | None,
) -> str:
    return (
        title
        or "New conversation"
    )


@router.get(
    "",
    response_model=(
        ConversationListResponse
    ),
)
def get_conversations(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    conversations = (
        list_owned_conversations(
            db,
            user_id=current_user.id,
        )
    )

    return ConversationListResponse(
        conversations=[
            ConversationSummaryResponse(
                thread_id=(
                    conversation.thread_id
                ),
                title=_conversation_title(
                    conversation.title
                ),
                resume_id=(
                    conversation.resume_id
                ),
                created_at=(
                    conversation.created_at
                ),
                updated_at=(
                    conversation.updated_at
                ),
            )
            for conversation
            in conversations
        ]
    )


@router.get(
    "/{thread_id}",
    response_model=(
        ConversationDetailResponse
    ),
)
def get_conversation(
    thread_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    (
        conversation,
        messages,
    ) = list_conversation_messages(
        db,
        user_id=current_user.id,
        thread_id=thread_id,
    )

    return ConversationDetailResponse(
        thread_id=conversation.thread_id,
        title=_conversation_title(
            conversation.title
        ),
        resume_id=conversation.resume_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            ConversationMessageResponse(
                id=message.id,
                mode=message.mode,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            for message
            in messages
        ],
    )


@router.patch(
    "/{thread_id}",
    response_model=(
        ConversationSummaryResponse
    ),
)
def rename_conversation(
    thread_id: str,
    request: ConversationRenameRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    conversation = (
        rename_owned_conversation(
            db,
            user_id=current_user.id,
            thread_id=thread_id,
            title=request.title,
        )
    )

    return ConversationSummaryResponse(
        thread_id=conversation.thread_id,
        title=_conversation_title(
            conversation.title
        ),
        resume_id=conversation.resume_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.delete(
    "/{thread_id}",
    response_model=(
        ConversationDeleteResponse
    ),
)
def delete_conversation(
    thread_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    delete_owned_conversation(
        db,
        user_id=current_user.id,
        thread_id=thread_id,
    )

    return ConversationDeleteResponse(
        deleted=True,
        thread_id=thread_id,
    )