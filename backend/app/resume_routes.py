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

from app.auth.dependencies import (
    get_current_user,
)
from app.database import get_db
from app.models import Resume, User
from app.resume_rag import (
    save_resume_vector_store,
    split_resume_text,
)
from app.services.resume_storage import (
    ResumeStorageError,
    delete_resume_pdf,
    upload_resume_pdf,
)


router = APIRouter()

# Maximum allowed resume size: 5 MB
MAX_RESUME_SIZE = 5 * 1024 * 1024


def _mark_resume_failed(
    *,
    resume: Resume,
    db: Session,
) -> None:
    """
    Best-effort persistence of a failed processing state.
    """

    try:
        resume.processing_status = "failed"
        db.commit()

    except Exception:
        db.rollback()


def _delete_stored_resume_safely(
    *,
    object_key: str | None,
) -> None:
    """
    Best-effort cleanup after an incomplete upload flow.

    The original exception remains the user-facing error
    even if cleanup encounters a separate storage issue.
    """

    if not object_key:
        return

    try:
        delete_resume_pdf(
            object_key=object_key
        )

    except ResumeStorageError:
        pass


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
    current_user: User = Depends(
        get_current_user
    ),
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
            detail=(
                "Resume PDF must be "
                "5 MB or smaller."
            ),
        )

    try:
        # 4. Read PDF
        reader = PdfReader(
            BytesIO(contents)
        )

        # 5. Extract text from every page
        extracted_pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            page_text = (
                page.extract_text() or ""
            )

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
            detail=(
                "Could not read the "
                "uploaded PDF."
            ),
        ) from exc

    # 7. Validate extracted text
    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "No readable text was "
                "found in the PDF."
            ),
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

    # 9. Create the MySQL metadata record first so its
    # generated ID can scope both S3 and Chroma identities.
    resume = Resume(
        user_id=current_user.id,
        original_filename=(
            file.filename or "resume.pdf"
        ),
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
            detail=(
                "Could not create "
                "resume record."
            ),
        ) from exc

    object_key: str | None = None

    # 10. Store the original PDF privately.
    try:
        object_key = upload_resume_pdf(
            contents=contents,
            user_id=current_user.id,
            resume_id=resume.id,
        )

        resume.s3_object_key = object_key

        db.commit()
        db.refresh(resume)

    except ResumeStorageError as exc:
        db.rollback()

        _delete_stored_resume_safely(
            object_key=object_key
        )

        _mark_resume_failed(
            resume=resume,
            db=db,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Resume file storage "
                "is temporarily unavailable."
            ),
        ) from exc

    except Exception as exc:
        db.rollback()

        _delete_stored_resume_safely(
            object_key=object_key
        )

        _mark_resume_failed(
            resume=resume,
            db=db,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save resume "
                "storage metadata."
            ),
        ) from exc

    try:
        # 11. Create embeddings and persist vectors.
        #
        # resume_id is the Chroma collection identity.
        # thread_id is retained as upload metadata.
        save_resume_vector_store(
            thread_id=thread_id,
            chunks=chunks,
            user_id=str(current_user.id),
            resume_id=str(resume.id),
        )

        # 12. Mark processing as completed.
        resume.processing_status = "completed"

        resume.vector_collection_id = (
            f"resume_{resume.id}"
        )

        db.commit()
        db.refresh(resume)

    except Exception as exc:
        db.rollback()

        _delete_stored_resume_safely(
            object_key=object_key
        )

        try:
            resume.s3_object_key = None
            resume.vector_collection_id = None
            resume.processing_status = "failed"
            db.commit()

        except Exception:
            db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Resume indexing failed.",
        ) from exc

    return {
        "resume_id": resume.id,
        "user_id": current_user.id,
        "thread_id": thread_id,
        "filename": resume.original_filename,
        "pages": len(reader.pages),
        "characters": len(extracted_text),
        "chunks_count": len(chunks),
        "processing_status": (
            resume.processing_status
        ),
        "vector_collection_id": (
            resume.vector_collection_id
        ),
        "original_file_stored": bool(
            resume.s3_object_key
        ),
        "message": (
            "Resume securely stored, processed, "
            "and indexed successfully."
        ),
    }