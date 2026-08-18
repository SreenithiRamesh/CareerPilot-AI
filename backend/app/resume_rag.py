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


def build_collection_name(thread_id: str) -> str:
    """
    Create a Chroma-safe collection name from thread_id.
    """

    safe_thread_id = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        thread_id,
    )

    safe_thread_id = safe_thread_id.strip("_-")

    if not safe_thread_id:
        safe_thread_id = "default"

    return f"resume_{safe_thread_id}"


def get_resume_vector_store(
    thread_id: str,
) -> Chroma:
    """
    Open or create a persistent Chroma collection
    associated with the given conversation thread.
    """

    collection_name = build_collection_name(
        thread_id
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
    Create or replace the indexed resume for this thread.

    user_id and resume_id are optional for now.
    They will become required after authentication/MySQL
    are implemented.
    """

    vector_store = get_resume_vector_store(
        thread_id
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
            "thread_id": thread_id,
        }

        if user_id:
            metadata["user_id"] = user_id

        if resume_id:
            metadata["resume_id"] = resume_id

        document = Document(
            page_content=chunk,
            metadata=metadata,
        )

        documents.append(document)

        ids.append(
            f"{thread_id}-resume-{index}"
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

    Metadata filters will enforce user/resume isolation
    once authentication is implemented.
    """

    filters = []

    if user_id:
        filters.append(
            {
                "user_id": {
                    "$eq": user_id
                }
            }
        )

    if resume_id:
        filters.append(
            {
                "resume_id": {
                    "$eq": resume_id
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
    thread_id: str,
) -> bool:
    """
    Check whether a persistent resume collection
    contains any indexed chunks.
    """

    vector_store = get_resume_vector_store(
        thread_id
    )

    data = vector_store.get()

    return bool(
        data.get("ids")
    )