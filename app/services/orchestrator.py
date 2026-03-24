from __future__ import annotations

import asyncio
from datetime import datetime

from sqlmodel import Session, select

from app.models import Asset, Job, JobStatus
from app.services.providers import ProviderGateway


class JobOrchestrator:
    def __init__(self):
        self.provider_gateway = ProviderGateway()
        self._stop = asyncio.Event()

    async def run_loop(self, engine):
        while not self._stop.is_set():
            try:
                await self._process_next_job(engine)
            except Exception:
                # MVP: 忽略异常继续轮询，生产版请接入日志与告警
                pass
            await asyncio.sleep(0.6)

    def stop(self):
        self._stop.set()

    async def _process_next_job(self, engine):
        with Session(engine) as session:
            job = session.exec(
                select(Job)
                .where(Job.status == JobStatus.queued)
                .order_by(Job.created_at.asc())
            ).first()

            if not job:
                return

            job.status = JobStatus.running
            job.updated_at = datetime.utcnow()
            session.add(job)
            session.commit()
            session.refresh(job)

        try:
            result = await self.provider_gateway.generate(
                job.provider_name,
                job_type=job.job_type,
                prompt=job.prompt,
                negative_prompt=job.negative_prompt,
            )

            with Session(engine) as session:
                db_job = session.get(Job, job.id)
                if not db_job:
                    return

                db_job.status = JobStatus.succeeded
                db_job.provider_task_id = result.provider_task_id
                db_job.updated_at = datetime.utcnow()

                asset = Asset(
                    job_id=db_job.id,
                    project_id=db_job.project_id,
                    kind=db_job.job_type,
                    url=result.output_url,
                    metadata_json=str(result.raw),
                )
                session.add(db_job)
                session.add(asset)
                session.commit()
        except Exception as exc:
            with Session(engine) as session:
                db_job = session.get(Job, job.id)
                if not db_job:
                    return
                db_job.status = JobStatus.failed
                db_job.error_message = str(exc)
                db_job.updated_at = datetime.utcnow()
                session.add(db_job)
                session.commit()
