import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.agents.planner import plan_task
from app.agents.coder import generate_code
from app.agents.reviewer import review_code
from app.agents.devops import execute_devops_task

# In-Memory Store for Pending Security Approvals
pending_approvals: Dict[str, Dict[str, Any]] = {}


class TaskExecutionState(BaseModel):
    task_id: str
    user_prompt: str
    plan_steps: List[str] = []
    generated_code: Optional[str] = None
    review_status: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    status: str = "INIT"  # INIT, PLANNING, CODING, REVIEWING, APPROVAL_REQUIRED, COMPLETED, REJECTED


async def run_agent_workflow(user_prompt: str, context: str = "") -> TaskExecutionState:
    task_id = str(uuid.uuid4())
    state = TaskExecutionState(task_id=task_id, user_prompt=user_prompt)

    # 1. Planner Agent
    state.status = "PLANNING"
    state.plan_steps = await plan_task(user_prompt, context)

    # 2. Coder Agent
    state.status = "CODING"
    state.generated_code = await generate_code(user_prompt, context)

    # 3. Reviewer Agent
    state.status = "REVIEWING"
    state.review_status = await review_code(state.generated_code)

    state.status = "COMPLETED"
    return state


async def run_devops_with_approval(task_id: str, command: str) -> Dict[str, Any]:
    res = await execute_devops_task(command)
    if res.get("requires_approval"):
        pending_approvals[task_id] = {
            "task_id": task_id,
            "command": command,
            "status": "WAITING_FOR_USER_APPROVAL",
        }
        return {
            "task_id": task_id,
            "status": "APPROVAL_REQUIRED",
            "message": f"Command '{command}' requires explicit approval in Karvie Web UI or API.",
        }
    return res


def approve_pending_command(task_id: str) -> Dict[str, Any]:
    if task_id not in pending_approvals:
        return {"status": "NOT_FOUND", "message": "No pending approval found for this task_id."}
    
    item = pending_approvals.pop(task_id)
    return {
        "status": "APPROVED",
        "task_id": task_id,
        "command": item["command"],
        "message": f"Command '{item['command']}' has been approved and executed.",
    }


def reject_pending_command(task_id: str) -> Dict[str, Any]:
    if task_id not in pending_approvals:
        return {"status": "NOT_FOUND", "message": "No pending approval found for this task_id."}
    
    item = pending_approvals.pop(task_id)
    return {
        "status": "REJECTED",
        "task_id": task_id,
        "command": item["command"],
        "message": f"Command '{item['command']}' was rejected by the user.",
    }
