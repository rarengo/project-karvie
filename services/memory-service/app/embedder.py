import os
import httpx
from typing import List

LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")
LITELLM_API_KEY = os.getenv("LITELLM_MASTER_KEY", "sk-karvie-local-master-key")


async def generate_embedding(text: str) -> List[float]:
    url = f"{LITELLM_URL}/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LITELLM_API_KEY}",
    }
    payload = {
        "model": "karvie-embedder",
        "input": text,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["embedding"]
            
        raise ValueError(f"Unexpected embedding payload structure: {data}")
