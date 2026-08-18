from langchain.tools import tool

from app.resume_rag import (
    get_resume_vector_store,
    search_resume,
)

@tool
def analyze_job_description(
    job_description: str,
) -> str:
    """
    Extract the most important requirements from a job description.

    Use this tool when the user asks about job fit,
    skill gaps, or preparation for a specific role.
    """

    if not job_description.strip():
        return "No job description was provided."

    return f"""
JOB DESCRIPTION TO ANALYZE:

{job_description}

Focus on:
- required programming languages
- frameworks
- cloud technologies
- databases
- DevOps tools
- CS fundamentals
- experience expectations
"""

@tool
def retrieve_resume_context(
    thread_id: str,
    query: str,
) -> str:
    """
    Retrieve relevant resume information for a user.

    Use this tool when the user's question requires evidence
    from their uploaded resume.
    """

    vector_store = get_resume_vector_store(thread_id)

    if vector_store is None:
        return (
            "No resume is indexed for this conversation. "
            "Ask the user to upload their resume first."
        )

    retrieved_docs = search_resume(
        vector_store,
        query,
        k=4,
    )

    if not retrieved_docs:
        return "No relevant resume information was found."

    resume_context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    return resume_context