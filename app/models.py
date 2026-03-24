from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class JobType(str, Enum):
    image = "image"
    video = "video"


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(index=True)
    skill_name: str = Field(index=True)
    job_type: JobType
    status: JobStatus = Field(default=JobStatus.queued, index=True)

    prompt: str
    negative_prompt: Optional[str] = None
    provider_name: str = "mock"
    provider_task_id: Optional[str] = None

    parent_job_id: Optional[int] = Field(default=None, index=True)
    error_message: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Asset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(index=True)
    project_id: int = Field(index=True)
    kind: JobType
    url: str
    metadata_json: str = "{}"
    created_at: datetime = Field(default_factory=datetime.utcnow)
