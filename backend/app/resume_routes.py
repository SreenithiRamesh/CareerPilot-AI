from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from pypdf import PdfReader

from app.resume_rag import (
    save_resume_vector_store,
    split_resume_text,
)


router = APIRouter()


@router.post("/api/resume/upload")
async def upload_resume(
    thread_id: str,
    file: UploadFile = File(...),
):
    # 1. Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # 2. Read uploaded PDF
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty.",
        )

    try:
        # 3. Read PDF
        reader = PdfReader(BytesIO(contents))

        # 4. Extract text from every page
        extracted_pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            page_text = page.extract_text() or ""

            if page_text.strip():
                extracted_pages.append(
                    f"--- Page {page_number} ---\n"
                    f"{page_text.strip()}"
                )

        # 5. Combine pages
        extracted_text = "\n\n".join(extracted_pages)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not read the uploaded PDF.",
        ) from exc

    # 6. Validate extracted text
    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text was found in the PDF.",
        )

    # 7. Split resume into chunks
    chunks = split_resume_text(
        extracted_text
    )

    if not chunks:
        raise HTTPException(
            status_code=422,
            detail="Resume could not be split into searchable chunks.",
        )

    # 8. Create embeddings + vector store
    #    and associate this resume with thread_id
    save_resume_vector_store(
        thread_id=thread_id,
        chunks=chunks,
    )

    # 9. Return processing result
    return {
        "thread_id": thread_id,
        "filename": file.filename,
        "pages": len(reader.pages),
        "characters": len(extracted_text),
        "chunks_count": len(chunks),
        "message": "Resume processed and indexed successfully.",
    }