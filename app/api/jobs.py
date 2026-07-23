from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from app.models.job import Job, JobCreate, JobStatus

router = APIRouter()


# --- In-memory store (swap for a real DB later) ---
_jobs: dict[UUID, Job] = {}


@router.post("", response_model=Job, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate) -> Job:
    now = datetime.now(UTC)
    job = Job(
        id=uuid4(),
        name=payload.name,
        payload=payload.payload,
        status=JobStatus.PENDING,
        created_at=now,
        updated_at=now,
    )
    _jobs[job.id] = job
    return job


@router.get("", response_model=list[Job])
def list_jobs(status_filter: JobStatus | None = None) -> list[Job]:
    jobs = list(_jobs.values())
    if status_filter:
        jobs = [j for j in jobs if j.status == status_filter]
    return jobs


@router.get("/{job_id}", response_model=Job)
def get_job(job_id: UUID) -> Job:
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/retry", response_model=Job)
def retry_job(job_id: UUID) -> Job:
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in (JobStatus.FAILED, JobStatus.SUCCEEDED):
        raise HTTPException(
            status_code=409,
            detail=f"Job in status '{job.status}' cannot be retried",
        )
    job.status = JobStatus.PENDING
    job.attempts += 1
    job.updated_at = datetime.now(UTC)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: UUID) -> None:
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    del _jobs[job_id]
