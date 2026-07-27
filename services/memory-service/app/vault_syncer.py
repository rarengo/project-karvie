import os
from typing import Dict, Any
from app.ast_indexer import chunk_file_content
from app.embedder import generate_embedding
from app.db import store_embedding_chunk, clear_embeddings


async def sync_vault(vault_dir: str) -> Dict[str, Any]:
    if not os.path.exists(vault_dir):
        return {"total_files": 0, "total_chunks": 0, "status": "Directory does not exist"}

    total_files = 0
    total_chunks = 0

    await clear_embeddings("vault/")

    for root, _, files in os.walk(vault_dir):
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, vault_dir)
                
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                chunks = chunk_file_content(f"vault/{rel_path}", content)
                for chunk in chunks:
                    try:
                        embedding = await generate_embedding(chunk["content"])
                        await store_embedding_chunk(
                            file_path=chunk["filePath"],
                            chunk_index=chunk["chunkIndex"],
                            content=chunk["content"],
                            metadata={**chunk["metadata"], "category": "vault"},
                            embedding=embedding
                        )
                        total_chunks += 1
                    except Exception as e:
                        print(f"Error indexing chunk {chunk['filePath']}: {e}")
                
                total_files += 1

    return {"total_files": total_files, "total_chunks": total_chunks, "status": "success"}
