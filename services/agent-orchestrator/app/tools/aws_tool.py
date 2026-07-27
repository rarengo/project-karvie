import os
from typing import Dict, Any
from app.tools.sandbox_runner import execute_in_sandbox


async def aws_list_lambdas() -> Dict[str, Any]:
    cmd = "aws lambda list-functions --query 'Functions[*].FunctionName' --output json"
    return await execute_in_sandbox(cmd)


async def aws_get_cloudwatch_logs(log_group_name: str, limit: int = 20) -> Dict[str, Any]:
    cmd = f"aws logs filter-log-events --log-group-name '{log_group_name}' --limit {limit} --output json"
    return await execute_in_sandbox(cmd)


async def serverless_deploy(project_dir: str) -> Dict[str, Any]:
    cmd = "serverless deploy"
    return await execute_in_sandbox(cmd, cwd=project_dir)
