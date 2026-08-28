import os
from typing import Any, BinaryIO

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
)


PDF_CONTENT_TYPE = "application/pdf"


class ResumeStorageError(RuntimeError):
    """
    Raised when CareerPilot cannot complete an operation
    against private resume object storage.
    """


def _get_required_environment(
    name: str,
) -> str:
    value = os.getenv(name)

    if not value:
        raise ResumeStorageError(
            f"{name} is not configured."
        )

    return value


def get_resume_bucket() -> str:
    return _get_required_environment(
        "S3_RESUME_BUCKET"
    )


def create_s3_client() -> BaseClient:
    """
    Create an S3-compatible client.

    S3_ENDPOINT_URL is configured for local MinIO.
    In production it can be omitted so boto3 connects
    directly to Amazon S3 using the EC2 IAM role.
    """

    region = os.getenv(
        "AWS_REGION",
        "ap-south-1",
    )

    endpoint_url = (
        os.getenv("S3_ENDPOINT_URL")
        or None
    )

    return boto3.client(
        "s3",
        region_name=region,
        endpoint_url=endpoint_url,
        config=Config(
            signature_version="s3v4",
            s3={
                "addressing_style": "path",
            },
        ),
    )


def build_resume_object_key(
    *,
    user_id: int,
    resume_id: int,
) -> str:
    """
    Create an ownership-scoped object key.

    The original filename is intentionally excluded
    because it can contain unsafe characters or expose
    personal information.
    """

    if user_id <= 0:
        raise ValueError(
            "user_id must be positive."
        )

    if resume_id <= 0:
        raise ValueError(
            "resume_id must be positive."
        )

    return (
        f"users/{user_id}/"
        f"resumes/{resume_id}/"
        "original.pdf"
    )


def upload_resume_pdf(
    *,
    contents: bytes,
    user_id: int,
    resume_id: int,
    client: BaseClient | Any | None = None,
) -> str:
    """
    Upload the original PDF to private object storage
    and return its object key.
    """

    if not contents:
        raise ValueError(
            "Resume PDF contents cannot be empty."
        )

    bucket = get_resume_bucket()

    object_key = build_resume_object_key(
        user_id=user_id,
        resume_id=resume_id,
    )

    storage_client = (
        client or create_s3_client()
    )

    try:
        storage_client.put_object(
            Bucket=bucket,
            Key=object_key,
            Body=contents,
            ContentType=PDF_CONTENT_TYPE,
            Metadata={
                "user-id": str(user_id),
                "resume-id": str(resume_id),
            },
        )

    except (BotoCoreError, ClientError) as exc:
        raise ResumeStorageError(
            "Could not store the resume PDF."
        ) from exc

    return object_key


def download_resume_pdf(
    *,
    object_key: str,
    client: BaseClient | Any | None = None,
) -> bytes:
    """
    Download a private resume PDF.

    Authorization and ownership must be checked using
    the MySQL Resume record before calling this function.
    """

    if not object_key:
        raise ValueError(
            "object_key is required."
        )

    bucket = get_resume_bucket()

    storage_client = (
        client or create_s3_client()
    )

    try:
        response = storage_client.get_object(
            Bucket=bucket,
            Key=object_key,
        )

        body: BinaryIO = response["Body"]

        return body.read()

    except (BotoCoreError, ClientError) as exc:
        raise ResumeStorageError(
            "Could not retrieve the resume PDF."
        ) from exc


def delete_resume_pdf(
    *,
    object_key: str,
    client: BaseClient | Any | None = None,
) -> None:
    """
    Delete a resume from private object storage.
    """

    if not object_key:
        raise ValueError(
            "object_key is required."
        )

    bucket = get_resume_bucket()

    storage_client = (
        client or create_s3_client()
    )

    try:
        storage_client.delete_object(
            Bucket=bucket,
            Key=object_key,
        )

    except (BotoCoreError, ClientError) as exc:
        raise ResumeStorageError(
            "Could not delete the resume PDF."
        ) from exc


def resume_pdf_exists(
    *,
    object_key: str,
    client: BaseClient | Any | None = None,
) -> bool:
    """
    Check whether an object exists without downloading it.
    """

    if not object_key:
        return False

    bucket = get_resume_bucket()

    storage_client = (
        client or create_s3_client()
    )

    try:
        storage_client.head_object(
            Bucket=bucket,
            Key=object_key,
        )

        return True

    except ClientError as exc:
        error_code = str(
            exc.response.get(
                "Error",
                {},
            ).get(
                "Code",
                "",
            )
        )

        if error_code in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            return False

        raise ResumeStorageError(
            "Could not check the resume PDF."
        ) from exc

    except BotoCoreError as exc:
        raise ResumeStorageError(
            "Could not check the resume PDF."
        ) from exc