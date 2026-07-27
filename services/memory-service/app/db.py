import os
import json
import asyncpg
from typing import List, Dict, Any, Optional

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "karvie_admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "karvie_secure_password_change_me!")
POSTGRES_DB = os.getenv("POSTGRES_DB", "karvie_db")

db_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB,
            min_size=1,
            max_size=10,
        )
    return db_pool


async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None


async def store_embedding_chunk(
    file_path: str,
    chunk_index: int,
    content: str,
    metadata: Dict[str, Any],
    embedding: List[float],
    project_id: Optional[str] = None,
) -> str:
    pool = await get_db_pool()
    vector_str = f"[{','.join(map(str, embedding))}]"
    
    query = """
        INSERT INTO project_embeddings (project_id, file_path, chunk_index, content, metadata, embedding)
        VALUES ($1, $2, $3, $4, $5::jsonb, $6::vector)
        RETURNING id;
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            query,
            project_id,
            file_path,
            chunk_index,
            content,
            json.dumps(metadata),
            vector_str,
        )
        return str(row["id"])


async def search_code_context(
    query_embedding: List[float],
    limit: int = 5,
    similarity_threshold: float = 0.4,
) -> List[Dict[str, Any]]:
    pool = await get_db_pool()
    vector_str = f"[{','.join(map(str, query_embedding))}]"
    
    query = """
        SELECT 
          id,
          file_path,
          chunk_index,
          content,
          metadata,
          1 - (embedding <=> $1::vector) as similarity
        FROM project_embeddings
        WHERE 1 - (embedding <=> $1::vector) >= $2
        ORDER BY similarity DESC
        LIMIT $3;
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, vector_str, similarity_threshold, limit)
        results = []
        for r in rows:
            results.append({
                "id": str(r["id"]),
                "file_path": r["file_path"],
                "chunk_index": r["chunk_index"],
                "content": r["content"],
                "metadata": json.loads(r["metadata"]) if isinstance(r["metadata"], str) else r["metadata"],
                "similarity": float(r["similarity"]),
            })
        return results


async def clear_embeddings(prefix: Optional[str] = None):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        if prefix:
            await conn.execute("DELETE FROM project_embeddings WHERE file_path LIKE $1", f"{prefix}%")
        else:
            await conn.execute("DELETE FROM project_embeddings")
