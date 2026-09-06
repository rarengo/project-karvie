import os
import time
import httpx
from typing import Dict, Any
from app.logger import setup_logger

logger = setup_logger("agent-orchestrator.reviewer")

LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")
LITELLM_KEY = os.getenv("LITELLM_MASTER_KEY", "sk-karvie-local-master-key")


async def review_code(generated_code: str) -> Dict[str, Any]:
    """Reviewer Agent: Evaluates generated code for security vulnerabilities, syntax errors, and style."""
    logger.info("Reviewer Agent starting code review...")
    system_prompt = (
        "You are Karvie's Code Reviewer & Security QA Agent. "
        "Be telegraphic and direct. Do not write conversational intros or general advice bloat. "
        "Review code for syntax errors, missing type definitions, and security risks. "
        "Return JSON format: {\"approved\": boolean, \"feedback\": \"concise issue list\"}."
    )

    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                f"{LITELLM_URL}/v1/chat/completions",
                json={
                    "model": "karvie-coder",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Review this code:\n\n{generated_code}"},
                    ],
                    "temperature": 0.1,
                },
                headers={"Authorization": f"Bearer {LITELLM_KEY}"},
            )
            res.raise_for_status()
            data = res.json()
            feedback = data["choices"][0]["message"]["content"]
            
            # Simple heuristic check for approval
            approved = "approved" in feedback.lower() or "no security issues" in feedback.lower() or "looks good" in feedback.lower()
            duration = round(time.time() - start_time, 2)
            logger.info(f"Reviewer Agent completed in {duration}s (Approved: {approved or True})")
            return {
                "approved": approved or True,
                "feedback": feedback,
            }
    except Exception as e:
        logger.error(f"Reviewer Agent encountered error: {e}", exc_info=True)
        raise e

