from typing import Dict, Any
from app.tools.sandbox_runner import execute_in_sandbox


async def git_clone_repo(repo_url: str, target_dir: str) -> Dict[str, Any]:
    cmd = f"git clone {repo_url} {target_dir}"
    return await execute_in_sandbox(cmd)


async def git_status(repo_dir: str) -> Dict[str, Any]:
    cmd = f"git status -s"
    return await execute_in_sandbox(cmd, cwd=repo_dir)


async def git_create_branch(repo_dir: str, branch_name: str) -> Dict[str, Any]:
    cmd = f"git checkout -b {branch_name}"
    return await execute_in_sandbox(cmd, cwd=repo_dir)


async def git_commit_changes(repo_dir: str, commit_message: str) -> Dict[str, Any]:
    cmd = f"git add . && git commit -m '{commit_message}'"
    return await execute_in_sandbox(cmd, cwd=repo_dir)


async def git_push_branch(repo_dir: str, branch_name: str) -> Dict[str, Any]:
    cmd = f"git push origin {branch_name}"
    return await execute_in_sandbox(cmd, cwd=repo_dir)
