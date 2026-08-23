from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class JobType(str, Enum):
    FIBONACCI = "fibonacci"
    PRIME_FACTORIZATION = "prime_factorization"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobCreate(BaseModel):
    type: JobType
    input: int = Field(..., ge=0, le=100_000)

    @model_validator(mode="after")
    def validate_task_input(self) -> "JobCreate":
        if self.type == JobType.PRIME_FACTORIZATION and self.input < 2:
            raise ValueError("prime_factorization input must be at least 2")
        return self


class Job(BaseModel):
    id: int
    type: JobType
    input: int
    status: JobStatus
    result: object | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class JobCreated(BaseModel):
    id: int
    status: JobStatus


class ResultResponse(BaseModel):
    id: int
    status: JobStatus
    result: object | None = None
    error: str | None = None