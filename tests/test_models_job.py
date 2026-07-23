from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.job import Job, JobCreate, JobStatus


def test_job_status_enum_values() -> None:
    assert JobStatus.PENDING == "pending"  # type: ignore[comparison-overlap]
    assert JobStatus.RUNNING == "running"  # type: ignore[comparison-overlap]
    assert JobStatus.SUCCEEDED == "succeeded"  # type: ignore[comparison-overlap]
    assert JobStatus.FAILED == "failed"  # type: ignore[comparison-overlap]


def test_job_status_is_string_enum() -> None:
    # Confirms it can be compared/serialized as a plain string
    assert JobStatus.PENDING.value == "pending"
    assert isinstance(JobStatus.PENDING, str)


def test_job_create_defaults_payload_to_empty_dict() -> None:
    jc = JobCreate(name="my-job")
    assert jc.name == "my-job"
    assert jc.payload == {}


def test_job_create_with_payload() -> None:
    jc = JobCreate(name="my-job", payload={"key": "value"})
    assert jc.payload == {"key": "value"}


def test_job_create_payload_default_is_not_shared_between_instances() -> None:
    jc1 = JobCreate(name="a")
    jc2 = JobCreate(name="b")
    jc1.payload["mutated"] = True
    assert "mutated" not in jc2.payload


def test_job_create_requires_name() -> None:
    with pytest.raises(ValidationError):
        JobCreate()  # type: ignore[call-arg]


def test_job_full_construction() -> None:
    now = datetime.now(UTC)
    job_id = uuid4()
    job = Job(
        id=job_id,
        name="test-job",
        payload={"a": 1},
        status=JobStatus.PENDING,
        created_at=now,
        updated_at=now,
    )
    assert job.id == job_id
    assert job.status == JobStatus.PENDING
    assert job.attempts == 0  # default


def test_job_attempts_defaults_to_zero() -> None:
    now = datetime.now(UTC)
    job = Job(
        id=uuid4(),
        name="test-job",
        payload={},
        status=JobStatus.PENDING,
        created_at=now,
        updated_at=now,
    )
    assert job.attempts == 0


def test_job_rejects_invalid_status() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        Job(
            id=uuid4(),
            name="test-job",
            payload={},
            status="not-a-real-status",  # type: ignore[arg-type]
            created_at=now,
            updated_at=now,
        )


def test_job_rejects_invalid_uuid() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        Job(
            id="not-a-uuid",  # type: ignore[arg-type]
            name="test-job",
            payload={},
            status=JobStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
