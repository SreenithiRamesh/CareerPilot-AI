import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


# Temporary in-memory storage for each user's resume vector store.
# Key   -> thread_id
# Value -> InMemoryVectorStore
resume_vector_stores = {}


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


def create_resume_vector_store(
    chunks: list[str],
) -> InMemoryVectorStore:
    documents = []

    for index, chunk in enumerate(chunks):
        document = Document(
            page_content=chunk,
            metadata={
                "chunk_id": index,
                "source": "resume",
            },
        )

        documents.append(document)

    vector_store = InMemoryVectorStore(
        embedding=embeddings,
    )

    vector_store.add_documents(documents)

    return vector_store


def save_resume_vector_store(
    thread_id: str,
    chunks: list[str],
) -> InMemoryVectorStore:
    """
    Create a vector store for the uploaded resume
    and save it using the conversation thread_id.
    """

    vector_store = create_resume_vector_store(chunks)

    resume_vector_stores[thread_id] = vector_store

    return vector_store


def get_resume_vector_store(
    thread_id: str,
) -> InMemoryVectorStore | None:
    """
    Retrieve the resume vector store associated
    with a particular conversation thread.
    """

    return resume_vector_stores.get(thread_id)


def search_resume(
    vector_store: InMemoryVectorStore,
    query: str,
    k: int = 3,
) -> list[Document]:
    """
    Perform semantic similarity search against
    the indexed resume.
    """

    results = vector_store.similarity_search(
        query,
        k=k,
    )

    return results