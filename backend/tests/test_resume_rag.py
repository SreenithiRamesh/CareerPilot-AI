from langchain_core.documents import Document

from app.resume_rag import (
    build_collection_name,
    search_resume,
    split_resume_text,
)


# ==================================================
# TEST: RESUME TEXT SPLITTING
# ==================================================


def test_split_resume_text_returns_chunks():
    """
    Resume text should be split into one or more
    non-empty chunks.
    """

    text = """
    Software Engineer

    Skills:
    Java, React, Node.js, SQL, AWS.

    Projects:
    Built a Learning Management System using
    React, Node.js, Express, and MongoDB.

    Cloud Exposure:
    Worked with EC2, S3, IAM, VPC, and CloudWatch.
    """

    chunks = split_resume_text(
        text
    )

    assert isinstance(
        chunks,
        list,
    )

    assert len(
        chunks
    ) > 0

    assert all(
        isinstance(chunk, str)
        and chunk.strip()
        for chunk in chunks
    )


# ==================================================
# TEST: CHROMA COLLECTION NAME
# ==================================================


def test_build_collection_name_sanitizes_thread_id():
    """
    Thread IDs containing unsupported characters
    should be converted into Chroma-safe names.
    """

    result = build_collection_name(
        "user/thread:123"
    )

    assert result == (
        "resume_user_thread_123"
    )


def test_build_collection_name_handles_empty_value():
    """
    An unusable thread ID should fall back
    to the default collection name.
    """

    result = build_collection_name(
        "///"
    )

    assert result == (
        "resume_default"
    )


# ==================================================
# FAKE VECTOR STORE
# ==================================================


class FakeVectorStore:
    """
    Minimal fake Chroma-like object used to verify
    CareerPilot search parameters without making
    embedding API calls.
    """

    def __init__(self):
        self.received_kwargs = None

    def similarity_search(
        self,
        **kwargs,
    ):
        self.received_kwargs = (
            kwargs
        )

        return [
            Document(
                page_content=(
                    "AWS experience with "
                    "EC2, S3, IAM and VPC."
                ),
                metadata={
                    "source":
                        "resume",
                },
            )
        ]


# ==================================================
# TEST: BASIC RESUME SEARCH
# ==================================================


def test_search_resume_without_filters():
    vector_store = (
        FakeVectorStore()
    )

    results = search_resume(
        vector_store,
        "What AWS experience "
        "does the candidate have?",
        k=2,
    )

    assert (
        vector_store.received_kwargs
        == {
            "query":
                (
                    "What AWS experience "
                    "does the candidate have?"
                ),
            "k":
                2,
        }
    )

    assert len(
        results
    ) == 1

    assert (
        "AWS"
        in results[0].page_content
    )


# ==================================================
# TEST: USER FILTER
# ==================================================


def test_search_resume_with_user_filter():
    vector_store = (
        FakeVectorStore()
    )

    search_resume(
        vector_store,
        "Java experience",
        user_id="12",
    )

    assert (
        vector_store.received_kwargs[
            "filter"
        ]
        == {
            "user_id": {
                "$eq": "12"
            }
        }
    )


# ==================================================
# TEST: USER + RESUME FILTER
# ==================================================


def test_search_resume_with_user_and_resume_filters():
    vector_store = (
        FakeVectorStore()
    )

    search_resume(
        vector_store,
        "Backend experience",
        user_id="12",
        resume_id="45",
    )

    expected_filter = {
        "$and": [
            {
                "user_id": {
                    "$eq": "12"
                }
            },
            {
                "resume_id": {
                    "$eq": "45"
                }
            },
        ]
    }

    assert (
        vector_store.received_kwargs[
            "filter"
        ]
        == expected_filter
    )