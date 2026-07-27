import os
import httpx
from typing import Dict, Any

LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")
LITELLM_KEY = os.getenv("LITELLM_MASTER_KEY", "sk-karvie-local-master-key")


async def generate_code(step_prompt: str, context: str = "") -> str:
    """Coder Agent: Generates clean, strongly typed Vue 3, TypeScript, or Express code."""
    system_prompt = (
        "You are Karvie's Senior Coding Agent specialized in Vue 3 (<script setup>), TypeScript, Node.js, and Express. "
        "Write clean, production-grade code adhering to strict coding standards."
    )
    
    user_content = f"Task Step: {step_prompt}\n\nExisting Codebase Context:\n{context}"

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
        data = res.json()
        return data["choices"][0]["message"]["content"]
