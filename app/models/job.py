# app/models/job
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobCreate(BaseModel):
    name: str
    payload: dict[str, Any] = Field(default_factory=dict)


class Job(BaseModel):
    id: UUID
    name: str
    payload: dict[str, Any]
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    attempts: int = 0
