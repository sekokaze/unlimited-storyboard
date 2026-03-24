from app.models import JobType
from app.schemas import SkillSpec

SKILLS: dict[str, SkillSpec] = {
    "image.concept_v1": SkillSpec(
        name="image.concept_v1",
        label="Image Concept",
        job_type=JobType.image,
        description="文本生成图片（概念草图）",
    ),
    "video.story_v1": SkillSpec(
        name="video.story_v1",
        label="Video Story",
        job_type=JobType.video,
        description="文本生成短视频（MVP）",
    ),
}


def list_skills() -> list[SkillSpec]:
    return list(SKILLS.values())


def get_skill(skill_name: str) -> SkillSpec | None:
    return SKILLS.get(skill_name)
