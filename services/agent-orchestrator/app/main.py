import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.graph.workflow import (
    run_agent_workflow,
    run_devops_with_approval,
    approve_pending_command,
    reject_pending_command,
    pending_approvals,
)
from app.logger import setup_logger
from fastapi.middleware.cors import CORSMiddleware

logger = setup_logger("agent-orchestrator")

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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    client_host = request.client.host if request.client else "unknown"

    logger.info(f"Incoming HTTP request: {method} {path} from {client_host}")

    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"HTTP Response: {method} {path} - Status {response.status_code} ({duration_ms}ms)")
        return response
    except Exception as exc:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"HTTP Error: {method} {path} failed after {duration_ms}ms: {exc}", exc_info=True)
        raise exc


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
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "service": "karvie-agent-orchestrator",
        "version": "2.0.0",
    }


@app.post("/execute-task", tags=["Multi-Agent Orchestrator"])
async def execute_task(request: AgentTaskRequest):
    logger.info(f"Executing multi-agent task prompt: '{request.prompt[:80]}...'")
    try:
        result = await run_agent_workflow(request.prompt, request.context or "")
        logger.info(f"Multi-agent task completed successfully (task_id: {result.task_id}, status: {result.status})")
        return result
    except Exception as e:
        logger.error(f"Error executing agent task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute-devops", tags=["DevOps Agent"])
async def execute_devops(request: DevOpsCommandRequest):
    logger.info(f"Executing DevOps command request (task_id: {request.task_id}, command: '{request.command}')")
    try:
        result = await run_devops_with_approval(request.task_id, request.command)
        logger.info(f"DevOps execution result status: {result.get('status')} for task_id: {request.task_id}")
        return result
    except Exception as e:
        logger.error(f"Error executing DevOps task (task_id: {request.task_id}): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pending-approvals", tags=["Security Approval Gates"])
async def list_pending_approvals():
    count = len(pending_approvals)
    logger.info(f"Listing pending approval security gates (count: {count})")
    return {
        "count": count,
        "pending": list(pending_approvals.values()),
    }


@app.post("/approve-command", tags=["Security Approval Gates"])
async def approve_command(request: ApprovalActionRequest):
    logger.info(f"User command approval requested for task_id: {request.task_id}")
    result = approve_pending_command(request.task_id)
    if result["status"] == "NOT_FOUND":
        logger.warning(f"Approve request failed - task_id not found: {request.task_id}")
        raise HTTPException(status_code=404, detail=result["message"])
    logger.info(f"Successfully approved command for task_id: {request.task_id}")
    return result


@app.post("/reject-command", tags=["Security Approval Gates"])
async def reject_command(request: ApprovalActionRequest):
    logger.info(f"User command rejection requested for task_id: {request.task_id}")
    result = reject_pending_command(request.task_id)
    if result["status"] == "NOT_FOUND":
        logger.warning(f"Reject request failed - task_id not found: {request.task_id}")
        raise HTTPException(status_code=404, detail=result["message"])
    logger.info(f"Successfully rejected command for task_id: {request.task_id}")
    return result

