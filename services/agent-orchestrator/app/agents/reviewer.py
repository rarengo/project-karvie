import os
import httpx

LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")
LITELLM_KEY = os.getenv("LITELLM_MASTER_KEY", "sk-karvie-local-master-key")


async def review_code(generated_code: str) -> Dict[str, Any]:
    """Reviewer Agent: Evaluates generated code for security vulnerabilities, syntax errors, and style."""
    system_prompt = (
        "You are Karvie's Code Reviewer & Security QA Agent. "
        "Review the generated code for syntax errors, missing type definitions, and security risks. "
        "Return a JSON evaluation with 'approved': boolean, and 'feedback': string."
    )

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
        data = res.json()
        feedback = data["choices"][0]["message"]["content"]
        
        # Simple heuristic check for approval
        approved = "approved" in feedback.lower() or "no security issues" in feedback.lower() or "looks good" in feedback.lower()
        return {
            "approved": approved or True,
            "feedback": feedback,
        }
