import os
import time
import httpx
from typing import List
from app.logger import setup_logger

logger = setup_logger("memory-service.embedder")

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

    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                embedding_dim = len(data["data"][0]["embedding"])
                logger.debug(f"Generated embedding vector (dim: {embedding_dim}) in {duration_ms}ms")
                return data["data"][0]["embedding"]
                
            logger.error(f"Unexpected embedding payload structure received from LiteLLM: {data}")
            raise ValueError(f"Unexpected embedding payload structure: {data}")
    except Exception as e:
        logger.error(f"Failed to generate embedding via LiteLLM: {e}", exc_info=True)
        raise e

