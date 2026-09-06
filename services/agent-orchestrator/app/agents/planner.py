import os
import time
import httpx
from typing import Dict, Any, List
from app.logger import setup_logger

logger = setup_logger("agent-orchestrator.planner")

LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")
LITELLM_KEY = os.getenv("LITELLM_MASTER_KEY", "sk-karvie-local-master-key")


async def plan_task(prompt: str, context: str = "") -> List[str]:
    """Planner Agent: Decomposes a user engineering goal into sub-task steps."""
    logger.info(f"Planner Agent starting for prompt: '{prompt[:60]}...'")
    system_prompt = (
        "You are Karvie's Lead Systems Architect and Planner Agent. "
        "Be telegraphic and extremely direct. No greetings, preambles, or conversational filler. "
        "Output ONLY a clean, numbered list of 3-5 sub-tasks."
    )
    
    user_content = f"User Request: {prompt}\n\nRelevant Code Context:\n{context}"

    start_time = time.time()
    try:
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
            res.raise_for_status()
            data = res.json()
            content = data["choices"][0]["message"]["content"]
            
            # Parse numbered lines into plan steps
            steps = [line.strip() for line in content.splitlines() if line.strip()]
            duration = round(time.time() - start_time, 2)
            logger.info(f"Planner Agent completed in {duration}s with {len(steps)} steps.")
            return steps
    except Exception as e:
        logger.error(f"Planner Agent encountered error: {e}", exc_info=True)
        raise e

