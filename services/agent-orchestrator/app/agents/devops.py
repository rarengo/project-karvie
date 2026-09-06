from typing import Dict, Any
from app.tools.sandbox_runner import execute_in_sandbox, is_high_risk_command
from app.logger import setup_logger

logger = setup_logger("agent-orchestrator.devops")


async def execute_devops_task(command: str) -> Dict[str, Any]:
    """DevOps Agent: Manages Docker builds, Serverless deployments, and git pushes."""
    logger.info(f"DevOps Agent evaluating command: '{command}'")
    if is_high_risk_command(command):
        logger.warning(f"DevOps Agent flagged high-risk command requiring approval: '{command}'")
        return {
            "status": "APPROVAL_REQUIRED",
            "command": command,
            "requires_approval": True,
            "message": f"High-risk command '{command}' paused for user approval.",
        }

    return await execute_in_sandbox(command)

