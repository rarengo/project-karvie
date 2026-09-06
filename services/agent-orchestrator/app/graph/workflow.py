import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.agents.planner import plan_task
from app.agents.coder import generate_code
from app.agents.reviewer import review_code
from app.agents.devops import execute_devops_task
from app.logger import setup_logger

logger = setup_logger("agent-orchestrator.workflow")

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
    logger.info(f"Starting agent workflow [Task ID: {task_id}]")

    # 1. Planner Agent
    state.status = "PLANNING"
    logger.info(f"[Task ID: {task_id}] Step 1/3: Running Planner Agent...")
    state.plan_steps = await plan_task(user_prompt, context)
    logger.info(f"[Task ID: {task_id}] Planner completed. Generated {len(state.plan_steps)} steps.")

    # 2. Coder Agent
    state.status = "CODING"
    logger.info(f"[Task ID: {task_id}] Step 2/3: Running Coder Agent...")
    state.generated_code = await generate_code(user_prompt, context)
    logger.info(f"[Task ID: {task_id}] Coder completed code generation ({len(state.generated_code)} chars).")

    # 3. Reviewer Agent
    state.status = "REVIEWING"
    logger.info(f"[Task ID: {task_id}] Step 3/3: Running Reviewer Agent...")
    state.review_status = await review_code(state.generated_code)
    logger.info(f"[Task ID: {task_id}] Reviewer completed. Approved: {state.review_status.get('approved')}")

    state.status = "COMPLETED"
    logger.info(f"[Task ID: {task_id}] Workflow finished with status: COMPLETED")
    return state


async def run_devops_with_approval(task_id: str, command: str) -> Dict[str, Any]:
    logger.info(f"Executing DevOps command check for task '{task_id}': '{command}'")
    res = await execute_devops_task(command)
    if res.get("requires_approval"):
        logger.warning(f"SECURITY GATE: Command '{command}' for task '{task_id}' requires explicit approval!")
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
    logger.info(f"DevOps command completed without requiring approval (task_id: '{task_id}')")
    return res


def approve_pending_command(task_id: str) -> Dict[str, Any]:
    if task_id not in pending_approvals:
        logger.warning(f"Attempted to approve task_id '{task_id}' but it was not found in pending store")
        return {"status": "NOT_FOUND", "message": "No pending approval found for this task_id."}
    
    item = pending_approvals.pop(task_id)
    logger.info(f"Approved command '{item['command']}' for task_id '{task_id}'")
    return {
        "status": "APPROVED",
        "task_id": task_id,
        "command": item["command"],
        "message": f"Command '{item['command']}' has been approved and executed.",
    }


def reject_pending_command(task_id: str) -> Dict[str, Any]:
    if task_id not in pending_approvals:
        logger.warning(f"Attempted to reject task_id '{task_id}' but it was not found in pending store")
        return {"status": "NOT_FOUND", "message": "No pending approval found for this task_id."}
    
    item = pending_approvals.pop(task_id)
    logger.info(f"Rejected command '{item['command']}' for task_id '{task_id}'")
    return {
        "status": "REJECTED",
        "task_id": task_id,
        "command": item["command"],
        "message": f"Command '{item['command']}' was rejected by the user.",
    }

