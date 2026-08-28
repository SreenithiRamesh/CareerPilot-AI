from io import BytesIO

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Resume, User
from app.resume_rag import (
    save_resume_vector_store,
    split_resume_text,
)


router = APIRouter()

# Maximum allowed resume size: 5 MB
MAX_RESUME_SIZE = 5 * 1024 * 1024



@router.get("/api/resume/{resume_id}")
def get_resume_metadata(
    resume_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Restore metadata for a resume owned by the
    authenticated user.

    Returning 404 for both missing and unowned records
    prevents disclosure of another user's resume IDs.
    """

    resume = db.scalar(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id
            == current_user.id,
        )
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    return {
        "resume_id": resume.id,
        "filename": (
            resume.original_filename
        ),
        "processing_status": (
            resume.processing_status
        ),
        "vector_collection_id": (
            resume.vector_collection_id
        ),
        "upload_timestamp": (
            resume.upload_timestamp
        ),
    }

@router.post("/api/resume/upload")
async def upload_resume(
    thread_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    # 3. Validate file size
    if len(contents) > MAX_RESUME_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Resume PDF must be 5 MB or smaller.",
        )

    try:
        # 4. Read PDF
        reader = PdfReader(BytesIO(contents))

        # 5. Extract text from every page
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

        # 6. Combine extracted pages
        extracted_text = "\n\n".join(
            extracted_pages
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not read the uploaded PDF.",
        ) from exc

    # 7. Validate extracted text
    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text was found in the PDF.",
        )

    # 8. Split resume into chunks
    chunks = split_resume_text(
        extracted_text
    )

    if not chunks:
        raise HTTPException(
            status_code=422,
            detail=(
                "Resume could not be split "
                "into searchable chunks."
            ),
        )

    # 9. Create resume metadata record in MySQL
    resume = Resume(
        user_id=current_user.id,
        original_filename=file.filename,
        s3_object_key=None,
        processing_status="processing",
        vector_collection_id=None,
    )

    db.add(resume)

    try:
        db.commit()
        db.refresh(resume)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Could not create resume record.",
        ) from exc

    try:
        # 10. Create embeddings and persist vectors.
        #
        # resume_id is the Chroma collection identity.
        # thread_id is retained only as upload metadata.
        save_resume_vector_store(
            thread_id=thread_id,
            chunks=chunks,
            user_id=str(current_user.id),
            resume_id=str(resume.id),
        )

        # 11. Mark resume processing as completed
        resume.processing_status = "completed"

        # Keep MySQL metadata aligned with the
        # resume_id-based Chroma collection identity.
        resume.vector_collection_id = (
            f"resume_{resume.id}"
        )

        db.commit()
        db.refresh(resume)

    except Exception as exc:
        db.rollback()

        # Try to record the processing failure.
        try:
            resume.processing_status = "failed"
            db.commit()
        except Exception:
            db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Resume indexing failed.",
        ) from exc

    # 12. Return processing result
    return {
        "resume_id": resume.id,
        "user_id": current_user.id,
        "thread_id": thread_id,
        "filename": file.filename,
        "pages": len(reader.pages),
        "characters": len(extracted_text),
        "chunks_count": len(chunks),
        "processing_status": resume.processing_status,
        "vector_collection_id": (
            resume.vector_collection_id
        ),
        "message": (
            "Resume processed and indexed successfully."
        ),
    }