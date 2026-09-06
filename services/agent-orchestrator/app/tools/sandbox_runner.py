import asyncio
import re
import time
from typing import Dict, Any
from app.logger import setup_logger

logger = setup_logger("agent-orchestrator.sandbox")

# High-risk command patterns requiring human approval
HIGH_RISK_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\bdrop\s+database\b",
    r"\bdrop\s+table\b",
    r"\bgit\s+push\s+--force\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\baws\s+deploy\b",
    r"\bserverless\s+deploy\b",
    r"\bdocker\s+run\s+.*--privileged\b",
    r"\bkubectl\s+delete\b",
]


def is_high_risk_command(command: str) -> bool:
    """Checks if a bash command matches dangerous high-risk execution patterns."""
    for pattern in HIGH_RISK_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


async def execute_in_sandbox(command: str, cwd: str = "/tmp") -> Dict[str, Any]:
    """Executes a command safely inside an isolated subprocess runner."""
    logger.info(f"Sandbox runner requested command execution: '{command}' (cwd: {cwd})")
    if is_high_risk_command(command):
        logger.warning(f"Sandbox runner blocked high-risk command: '{command}'")
        return {
            "status": "APPROVAL_REQUIRED",
            "high_risk": True,
            "command": command,
            "message": "Command detected as high-risk. Requires human approval before execution.",
        }

    start_time = time.time()
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
        duration = round(time.time() - start_time, 2)

        logger.info(f"Sandbox command executed in {duration}s (exit_code: {process.returncode}): '{command}'")

        return {
            "status": "COMPLETED",
            "exit_code": process.returncode,
            "stdout": stdout.decode("utf-8", errors="ignore"),
            "stderr": stderr.decode("utf-8", errors="ignore"),
            "command": command,
        }
    except asyncio.TimeoutError:
        duration = round(time.time() - start_time, 2)
        logger.error(f"Sandbox command timed out after {duration}s: '{command}'")
        return {
            "status": "TIMEOUT",
            "exit_code": -1,
            "error": "Command execution timed out after 30 seconds.",
            "command": command,
        }
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        logger.error(f"Sandbox command execution failed after {duration}s: {e}", exc_info=True)
        return {
            "status": "ERROR",
            "exit_code": -1,
            "error": str(e),
            "command": command,
        }

