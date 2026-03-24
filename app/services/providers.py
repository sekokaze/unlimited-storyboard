from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from typing import Any

from app.models import JobType


@dataclass
class ProviderResult:
    provider_task_id: str
    output_url: str
    raw: dict[str, Any]


class MockProviderClient:
    async def generate(self, *, job_type: JobType, prompt: str, negative_prompt: str | None = None) -> ProviderResult:
        await asyncio.sleep(1.2 if job_type == JobType.image else 2.2)
        task_id = f"mock_{uuid.uuid4().hex[:12]}"
        suffix = "png" if job_type == JobType.image else "mp4"
        url = f"https://example-cdn.local/{task_id}.{suffix}"
        return ProviderResult(
            provider_task_id=task_id,
            output_url=url,
            raw={"prompt": prompt, "negative_prompt": negative_prompt, "job_type": job_type.value},
        )


class ProviderGateway:
    def __init__(self):
        self._mock = MockProviderClient()

    async def generate(self, provider_name: str, *, job_type: JobType, prompt: str, negative_prompt: str | None) -> ProviderResult:
        # MVP: 所有 provider_name 都先走 mock，后续可在这里接入真实第三方
        return await self._mock.generate(job_type=job_type, prompt=prompt, negative_prompt=negative_prompt)
