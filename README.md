# Unlimited Storyboard MVP (No-GPU)

一个可直接跑起来的 MVP：
- 通过 `skill` 创建异步作图/视频任务
- 后端通过统一 provider 网关调用第三方 AI（MVP 用 mock provider 模拟）
- 支持任务历史、状态查询、基于历史任务重新生成
- 附带一个超简前端页面用于快速试跑

## 1) 快速启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

打开：
- API 文档: http://127.0.0.1:8000/docs
- MVP 页面: http://127.0.0.1:8000/

## 2) 关键接口

- `GET /api/skills` 查看可用 skills
- `POST /api/projects` 创建项目
- `POST /api/jobs` 创建任务
- `GET /api/jobs/{job_id}` 查询任务
- `GET /api/projects/{project_id}/jobs` 获取项目任务历史
- `POST /api/jobs/{job_id}/variant` 基于旧任务变体生成

## 3) Skill 与 Provider 设计

- Skill：定义输入 schema、任务类型、默认 provider 路由。
- Provider Gateway：统一调用第三方服务（图片/视频），便于后续接入真实厂商 SDK/REST API。
- Orchestrator：把 job 从 `queued -> running -> succeeded/failed`，并将结果写入 `asset`。

你可以把 `MockProviderClient` 替换为真实厂商调用（OpenAI、Runway、Pika、Replicate 等）。

## 4) MVP 数据库

默认使用 `sqlite:///./mvp.db`，包含：
- `project`
- `job`
- `asset`

如果要改 Postgres，只需修改 `app/database.py` 的连接串。
