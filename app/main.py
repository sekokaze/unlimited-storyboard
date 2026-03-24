from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from app.database import engine, get_session, init_db
from app.models import Asset, Job, Project
from app.schemas import (
    CreateJobRequest,
    CreateProjectRequest,
    CreateVariantRequest,
    JobDetailResponse,
    JobResponse,
    ProjectResponse,
    SkillSpec,
)
from app.services.orchestrator import JobOrchestrator
from app.services.skills import get_skill, list_skills

orchestrator = JobOrchestrator()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    task = asyncio.create_task(orchestrator.run_loop(engine))
    try:
        yield
    finally:
        orchestrator.stop()
        await task


app = FastAPI(title="Unlimited Storyboard MVP", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def index():
    return FileResponse("app/static/index.html")


@app.get("/api/skills", response_model=list[SkillSpec])
def api_list_skills():
    return list_skills()


@app.post("/api/projects", response_model=ProjectResponse)
def create_project(payload: CreateProjectRequest, session: Session = Depends(get_session)):
    project = Project(name=payload.name)
    session.add(project)
    session.commit()
    session.refresh(project)
    return ProjectResponse.model_validate(project)


@app.post("/api/jobs", response_model=JobResponse)
def create_job(payload: CreateJobRequest, session: Session = Depends(get_session)):
    skill = get_skill(payload.skill_name)
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

    project = session.get(Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")

    job = Job(
        project_id=payload.project_id,
        skill_name=skill.name,
        job_type=skill.job_type,
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
        provider_name=payload.provider_name or skill.default_provider,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return JobResponse.model_validate(job)


@app.get("/api/jobs/{job_id}", response_model=JobDetailResponse)
def get_job(job_id: int, session: Session = Depends(get_session)):
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    assets = session.exec(select(Asset).where(Asset.job_id == job_id)).all()
    return JobDetailResponse(
        job=JobResponse.model_validate(job),
        assets=[a.model_dump() for a in assets],
    )


@app.get("/api/projects/{project_id}/jobs", response_model=list[JobResponse])
def list_project_jobs(project_id: int, session: Session = Depends(get_session)):
    jobs = session.exec(
        select(Job)
        .where(Job.project_id == project_id)
        .order_by(Job.created_at.desc())
    ).all()
    return [JobResponse.model_validate(j) for j in jobs]


@app.post("/api/jobs/{job_id}/variant", response_model=JobResponse)
def create_variant(job_id: int, payload: CreateVariantRequest, session: Session = Depends(get_session)):
    parent = session.get(Job, job_id)
    if not parent:
        raise HTTPException(status_code=404, detail="job not found")

    job = Job(
        project_id=parent.project_id,
        skill_name=parent.skill_name,
        job_type=parent.job_type,
        prompt=payload.prompt or parent.prompt,
        negative_prompt=payload.negative_prompt or parent.negative_prompt,
        provider_name=payload.provider_name or parent.provider_name,
        parent_job_id=parent.id,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return JobResponse.model_validate(job)
