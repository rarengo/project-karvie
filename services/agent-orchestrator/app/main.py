from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.graph.workflow import (
    run_agent_workflow,
    run_devops_with_approval,
    approve_pending_command,
    reject_pending_command,
    pending_approvals,
)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Karvie LangGraph Multi-Agent Orchestrator Service",
    description="Python multi-agent framework (Planner, Coder, Reviewer, DevOps) with Security Approval Gates",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentTaskRequest(BaseModel):
    prompt: str = Field(..., example="Create an Express.js TypeScript health check endpoint with unit tests.")
    context: Optional[str] = Field(default="", example="Existing project codebase structure")


class DevOpsCommandRequest(BaseModel):
    task_id: str = Field(..., example="task-12345")
    command: str = Field(..., example="git push origin main")


class ApprovalActionRequest(BaseModel):
    task_id: str = Field(..., example="task-12345")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "karvie-agent-orchestrator",
        "version": "2.0.0",
    }


@app.post("/execute-task", tags=["Multi-Agent Orchestrator"])
async def execute_task(request: AgentTaskRequest):
    try:
        result = await run_agent_workflow(request.prompt, request.context or "")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute-devops", tags=["DevOps Agent"])
async def execute_devops(request: DevOpsCommandRequest):
    try:
        result = await run_devops_with_approval(request.task_id, request.command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pending-approvals", tags=["Security Approval Gates"])
async def list_pending_approvals():
    return {
        "count": len(pending_approvals),
        "pending": list(pending_approvals.values()),
    }


@app.post("/approve-command", tags=["Security Approval Gates"])
async def approve_command(request: ApprovalActionRequest):
    result = approve_pending_command(request.task_id)
    if result["status"] == "NOT_FOUND":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@app.post("/reject-command", tags=["Security Approval Gates"])
async def reject_command(request: ApprovalActionRequest):
    result = reject_pending_command(request.task_id)
    if result["status"] == "NOT_FOUND":
        raise HTTPException(status_code=404, detail=result["message"])
    return result
