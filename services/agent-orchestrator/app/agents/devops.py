from typing import Dict, Any
from app.tools.sandbox_runner import execute_in_sandbox, is_high_risk_command


async def execute_devops_task(command: str) -> Dict[str, Any]:
    """DevOps Agent: Manages Docker builds, Serverless deployments, and git pushes."""
    if is_high_risk_command(command):
        return {
            "status": "APPROVAL_REQUIRED",
            "command": command,
            "requires_approval": True,
            "message": f"High-risk command '{command}' paused for user approval.",
        }

    return await execute_in_sandbox(command)
