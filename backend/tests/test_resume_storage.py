from io import BytesIO

import pytest
from botocore.exceptions import ClientError

from app.services.resume_storage import (
    ResumeStorageError,
    build_resume_object_key,
    delete_resume_pdf,
    download_resume_pdf,
    resume_pdf_exists,
    upload_resume_pdf,
)


TEST_BUCKET = "careerpilot-test-resumes"


class FakeS3Client:
    def __init__(self) -> None:
        self.objects: dict[
            tuple[str, str],
            bytes,
        ] = {}

        self.last_put_request = None
        self.last_delete_request = None

    def put_object(
        self,
        **kwargs,
    ):
        self.last_put_request = kwargs

        self.objects[
            (
                kwargs["Bucket"],
                kwargs["Key"],
            )
        ] = kwargs["Body"]

        return {
            "ETag": "test-etag",
        }

    def get_object(
        self,
        **kwargs,
    ):
        key = (
            kwargs["Bucket"],
            kwargs["Key"],
        )

        if key not in self.objects:
            raise _missing_object_error(
                "GetObject"
            )

        return {
            "Body": BytesIO(
                self.objects[key]
            ),
        }

    def delete_object(
        self,
        **kwargs,
    ):
        self.last_delete_request = kwargs

        self.objects.pop(
            (
                kwargs["Bucket"],
                kwargs["Key"],
            ),
            None,
        )

        return {}

    def head_object(
        self,
        **kwargs,
    ):
        key = (
            kwargs["Bucket"],
            kwargs["Key"],
        )

        if key not in self.objects:
            raise _missing_object_error(
                "HeadObject"
            )

        return {
            "ContentLength": len(
                self.objects[key]
            ),
        }


class FailingS3Client:
    def put_object(
        self,
        **_kwargs,
    ):
        raise ClientError(
            {
                "Error": {
                    "Code": "AccessDenied",
                    "Message": "Access denied",
                },
            },
            "PutObject",
        )


def _missing_object_error(
    operation_name: str,
) -> ClientError:
    return ClientError(
        {
            "Error": {
                "Code": "404",
                "Message": "Not found",
            },
        },
        operation_name,
    )


@pytest.fixture(autouse=True)
def configure_test_bucket(
    monkeypatch,
):
    monkeypatch.setenv(
        "S3_RESUME_BUCKET",
        TEST_BUCKET,
    )


def test_build_resume_object_key():
    assert build_resume_object_key(
        user_id=12,
        resume_id=34,
    ) == (
        "users/12/"
        "resumes/34/"
        "original.pdf"
    )


@pytest.mark.parametrize(
    (
        "user_id",
        "resume_id",
    ),
    [
        (0, 1),
        (-1, 1),
        (1, 0),
        (1, -1),
    ],
)
def test_object_key_rejects_invalid_ids(
    user_id,
    resume_id,
):
    with pytest.raises(ValueError):
        build_resume_object_key(
            user_id=user_id,
            resume_id=resume_id,
        )


def test_uploads_private_resume_pdf():
    client = FakeS3Client()

    contents = (
        b"%PDF-1.4 CareerPilot test"
    )

    object_key = upload_resume_pdf(
        contents=contents,
        user_id=7,
        resume_id=19,
        client=client,
    )

    assert object_key == (
        "users/7/"
        "resumes/19/"
        "original.pdf"
    )

    assert client.last_put_request == {
        "Bucket": TEST_BUCKET,
        "Key": object_key,
        "Body": contents,
        "ContentType": "application/pdf",
        "Metadata": {
            "user-id": "7",
            "resume-id": "19",
        },
    }


def test_upload_rejects_empty_content():
    with pytest.raises(
        ValueError,
        match=(
            "Resume PDF contents "
            "cannot be empty."
        ),
    ):
        upload_resume_pdf(
            contents=b"",
            user_id=1,
            resume_id=1,
            client=FakeS3Client(),
        )


def test_downloads_uploaded_resume():
    client = FakeS3Client()

    contents = (
        b"%PDF-1.4 private resume"
    )

    object_key = upload_resume_pdf(
        contents=contents,
        user_id=4,
        resume_id=9,
        client=client,
    )

    downloaded = download_resume_pdf(
        object_key=object_key,
        client=client,
    )

    assert downloaded == contents


def test_deletes_uploaded_resume():
    client = FakeS3Client()

    object_key = upload_resume_pdf(
        contents=b"%PDF-1.4 delete test",
        user_id=3,
        resume_id=8,
        client=client,
    )

    assert resume_pdf_exists(
        object_key=object_key,
        client=client,
    )

    delete_resume_pdf(
        object_key=object_key,
        client=client,
    )

    assert not resume_pdf_exists(
        object_key=object_key,
        client=client,
    )


def test_missing_resume_does_not_exist():
    assert not resume_pdf_exists(
        object_key=(
            "users/1/"
            "resumes/999/"
            "original.pdf"
        ),
        client=FakeS3Client(),
    )


def test_storage_failure_is_normalized():
    with pytest.raises(
        ResumeStorageError,
        match=(
            "Could not store "
            "the resume PDF."
        ),
    ):
        upload_resume_pdf(
            contents=b"%PDF-1.4 failure",
            user_id=1,
            resume_id=2,
            client=FailingS3Client(),
        )


def test_missing_bucket_configuration(
    monkeypatch,
):
    monkeypatch.delenv(
        "S3_RESUME_BUCKET",
        raising=False,
    )

    with pytest.raises(
        ResumeStorageError,
        match=(
            "S3_RESUME_BUCKET "
            "is not configured."
        ),
    ):
        upload_resume_pdf(
            contents=b"%PDF-1.4 test",
            user_id=1,
            resume_id=2,
            client=FakeS3Client(),
        )