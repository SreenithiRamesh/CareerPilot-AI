import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


def split_resume_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    return splitter.split_text(text)


def build_collection_name(resume_id: str) -> str:
    """
    Create a Chroma-safe collection name from resume_id.

    Resume collections are keyed by resume_id so the same
    resume can be reused across multiple Career AI
    conversations without depending on thread_id.
    """

    safe_resume_id = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(resume_id),
    )

    safe_resume_id = safe_resume_id.strip("_-")

    if not safe_resume_id:
        safe_resume_id = "default"

    return f"resume_{safe_resume_id}"


def get_resume_vector_store(
    resume_id: str,
) -> Chroma:
    """
    Open or create the persistent Chroma collection
    associated with the given resume_id.
    """

    collection_name = build_collection_name(
        resume_id
    )

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    return vector_store


def save_resume_vector_store(
    thread_id: str,
    chunks: list[str],
    user_id: str | None = None,
    resume_id: str | None = None,
) -> Chroma:
    """
    Create or replace the indexed resume.

    resume_id is the primary collection identity.

    thread_id is retained only as metadata so CareerPilot
    can track the original upload/indexing thread.

    The signature remains compatible with the existing
    resume upload route.
    """

    collection_identity = (
        str(resume_id)
        if resume_id is not None
        else str(thread_id)
    )

    vector_store = get_resume_vector_store(
        collection_identity
    )

    existing = vector_store.get()
    existing_ids = existing.get("ids", [])

    if existing_ids:
        vector_store.delete(
            ids=existing_ids,
        )

    documents = []
    ids = []

    for index, chunk in enumerate(chunks):
        metadata = {
            "chunk_id": index,
            "source": "resume",
            "thread_id": str(thread_id),
        }

        if user_id is not None:
            metadata["user_id"] = str(user_id)

        if resume_id is not None:
            metadata["resume_id"] = str(resume_id)

        document = Document(
            page_content=chunk,
            metadata=metadata,
        )

        documents.append(document)

        ids.append(
            (
                f"resume-{resume_id}-{index}"
                if resume_id is not None
                else f"{thread_id}-resume-{index}"
            )
        )

    vector_store.add_documents(
        documents=documents,
        ids=ids,
    )

    return vector_store


def search_resume(
    vector_store: Chroma,
    query: str,
    k: int = 3,
    user_id: str | None = None,
    resume_id: str | None = None,
) -> list[Document]:
    """
    Search indexed resume chunks.

    user_id and resume_id metadata filters enforce
    account and selected-resume isolation.
    """

    filters = []

    if user_id is not None:
        filters.append(
            {
                "user_id": {
                    "$eq": str(user_id)
                }
            }
        )

    if resume_id is not None:
        filters.append(
            {
                "resume_id": {
                    "$eq": str(resume_id)
                }
            }
        )

    search_kwargs = {
        "query": query,
        "k": k,
    }

    if len(filters) == 1:
        search_kwargs["filter"] = filters[0]

    elif len(filters) > 1:
        search_kwargs["filter"] = {
            "$and": filters
        }

    return vector_store.similarity_search(
        **search_kwargs
    )


def resume_exists(
    resume_id: str,
    user_id: str | None = None,
) -> bool:
    """
    Check whether a persistent resume collection
    contains indexed chunks.

    If user_id is provided, also verify that the
    indexed resume belongs to that authenticated user.
    """

    vector_store = get_resume_vector_store(
        str(resume_id)
    )

    if user_id is not None:
        data = vector_store.get(
            where={
                "user_id": {
                    "$eq": str(user_id)
                }
            }
        )

    else:
        data = vector_store.get()

    return bool(
        data.get("ids")
    )