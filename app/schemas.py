from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models import JobStatus, JobType


class SkillSpec(BaseModel):
    name: str
    label: str
    job_type: JobType
    description: str
    default_provider: str = "mock"


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class ProjectResponse(BaseModel):
    id: int
    name: str
    created_at: datetime


class CreateJobRequest(BaseModel):
    project_id: int
    skill_name: str
    prompt: str = Field(min_length=1, max_length=5000)
    negative_prompt: Optional[str] = None
    provider_name: Optional[str] = None


class CreateVariantRequest(BaseModel):
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    provider_name: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    project_id: int
    skill_name: str
    job_type: JobType
    status: JobStatus
    prompt: str
    negative_prompt: Optional[str]
    provider_name: str
    provider_task_id: Optional[str]
    parent_job_id: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime


class AssetResponse(BaseModel):
    id: int
    job_id: int
    project_id: int
    kind: JobType
    url: str
    metadata_json: str
    created_at: datetime


class JobDetailResponse(BaseModel):
    job: JobResponse
    assets: list[AssetResponse]


class GenericMessage(BaseModel):
    message: str
    data: Optional[dict[str, Any]] = None
