from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)


class ConversationMessageResponse(
    BaseModel
):
    id: int

    mode: str

    role: str

    content: str

    created_at: datetime


class ConversationSummaryResponse(
    BaseModel
):
    thread_id: str

    title: str

    resume_id: int | None = None

    created_at: datetime

    updated_at: datetime


class ConversationListResponse(
    BaseModel
):
    conversations: list[
        ConversationSummaryResponse
    ] = Field(
        default_factory=list
    )


class ConversationDetailResponse(
    BaseModel
):
    thread_id: str

    title: str

    resume_id: int | None = None

    created_at: datetime

    updated_at: datetime

    messages: list[
        ConversationMessageResponse
    ] = Field(
        default_factory=list
    )


class ConversationRenameRequest(
    BaseModel
):
    title: str = Field(
        min_length=1,
        max_length=255,
    )


class ConversationDeleteResponse(
    BaseModel
):
    deleted: bool

    thread_id: str