import os
import time
import httpx
from typing import Dict, Any
from app.logger import setup_logger

logger = setup_logger("agent-orchestrator.coder")

LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")
LITELLM_KEY = os.getenv("LITELLM_MASTER_KEY", "sk-karvie-local-master-key")


async def generate_code(step_prompt: str, context: str = "") -> str:
    """Coder Agent: Generates clean, strongly typed Vue 3, TypeScript, or Express code."""
    logger.info(f"Coder Agent starting for step prompt: '{step_prompt[:60]}...'")
    system_prompt = (
        "You are Karvie's Senior Coding Agent specialized in Vue 3 (<script setup>), TypeScript, Node.js, and Express. "
        "Output code immediately without introductions, preambles, or conversational wrap-ups. "
        "Keep code syntax 100% complete and fully typed—never omit code or use placeholders."
    )
    
    user_content = f"Task Step: {step_prompt}\n\nExisting Codebase Context:\n{context}"

    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(
                f"{LITELLM_URL}/v1/chat/completions",
                json={
                    "model": "karvie-coder",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    "temperature": 0.2,
                },
                headers={"Authorization": f"Bearer {LITELLM_KEY}"},
            )
            res.raise_for_status()
            data = res.json()
            generated_code = data["choices"][0]["message"]["content"]
            duration = round(time.time() - start_time, 2)
            logger.info(f"Coder Agent completed in {duration}s ({len(generated_code)} chars generated).")
            return generated_code
    except Exception as e:
        logger.error(f"Coder Agent encountered error: {e}", exc_info=True)
        raise e

