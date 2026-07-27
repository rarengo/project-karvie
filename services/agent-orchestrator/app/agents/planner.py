import os
import httpx
from typing import Dict, Any, List

LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")
LITELLM_KEY = os.getenv("LITELLM_MASTER_KEY", "sk-karvie-local-master-key")


async def plan_task(prompt: str, context: str = "") -> List[str]:
    """Planner Agent: Decomposes a user engineering goal into sub-task steps."""
    system_prompt = (
        "You are Karvie's Lead Systems Architect and Planner Agent. "
        "Break down the user request into a clean, numbered list of 3-5 sub-tasks."
    )
    
    user_content = f"User Request: {prompt}\n\nRelevant Code Context:\n{context}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(
            f"{LITELLM_URL}/v1/chat/completions",
            json={
                "model": "karvie-coder",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.1,
            },
            headers={"Authorization": f"Bearer {LITELLM_KEY}"},
        )
        data = res.json()
        content = data["choices"][0]["message"]["content"]
        
        # Parse numbered lines into plan steps
        steps = [line.strip() for line in content.splitlines() if line.strip()]
        return steps
