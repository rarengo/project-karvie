import os
import time
import asyncio
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from app.db import get_db_pool, close_db_pool, search_code_context, store_embedding_chunk
from app.embedder import generate_embedding
from app.vault_syncer import sync_vault, start_vault_watcher
from app.ast_indexer import chunk_file_content
from app.logger import setup_logger

logger = setup_logger("memory-service")
vault_observer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global vault_observer
    logger.info("Initializing Memory Service lifespan...")
    # Startup: Initialize DB Pool
    await get_db_pool()

    # Start Real-Time Watchdog Observer for Obsidian Vault
    vault_dir = os.getenv("VAULT_DIR", os.path.join(os.path.dirname(__file__), "../../vault"))
    if os.path.exists(vault_dir):
        loop = asyncio.get_running_loop()
        vault_observer = start_vault_watcher(vault_dir, loop)
    else:
        logger.warning(f"Vault directory not found at: {vault_dir}")

    yield

    # Shutdown: Stop Watchdog & Close DB Pool
    logger.info("Shutting down Memory Service...")
    if vault_observer:
        vault_observer.stop()
        vault_observer.join()
        logger.info("Watchdog observer stopped.")
    await close_db_pool()


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Karvie RAG Memory & AST Indexer Service",
    description="Python FastAPI service providing vector search, YAML frontmatter parsing, and real-time Obsidian vault watching",
    version="2.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    client_host = request.client.host if request.client else "unknown"

    logger.info(f"Incoming HTTP request: {method} {path} from {client_host}")

    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"HTTP Response: {method} {path} - Status {response.status_code} ({duration_ms}ms)")
        return response
    except Exception as exc:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"HTTP Error: {method} {path} failed after {duration_ms}ms: {exc}", exc_info=True)
        raise exc


class SearchRequest(BaseModel):
    query: str = Field(..., example="How to write Vue 3 script setup components?")
    limit: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.35, ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    query: str
    results_count: int
    results: List[Dict[str, Any]]


class IndexVaultRequest(BaseModel):
    vault_path: Optional[str] = Field(default=None, example="/app/vault")


class IndexProjectRequest(BaseModel):
    project_path: str = Field(..., example="/app/target_repo")
    project_id: Optional[str] = Field(default=None)


@app.get("/health", tags=["Health"])
async def health_check():
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "service": "karvie-memory-service-python",
        "version": "2.1.0",
        "realtime_watcher": vault_observer is not None and vault_observer.is_alive(),
    }


@app.post("/search-context", response_model=SearchResponse, tags=["Search"])
async def search_context(request: SearchRequest):
    logger.info(f"Searching code context for query: '{request.query}' (limit={request.limit}, threshold={request.similarity_threshold})")
    try:
        query_vector = await generate_embedding(request.query)
        results = await search_code_context(
            query_embedding=query_vector,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold,
        )
        logger.info(f"Search context query returned {len(results)} matching results.")
        return SearchResponse(
            query=request.query,
            results_count=len(results),
            results=results,
        )
    except Exception as e:
        logger.error(f"Error during search-context: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index-vault", tags=["Indexing"])
async def index_vault(request: IndexVaultRequest):
    vault_dir = request.vault_path or os.path.join(os.path.dirname(__file__), "../../vault")
    logger.info(f"Indexing vault directory: '{vault_dir}'")
    try:
        result = await sync_vault(vault_dir)
        logger.info(f"Vault indexing complete. Total files: {result.get('total_files')}, status: {result.get('status')}")
        return result
    except Exception as e:
        logger.error(f"Error during index-vault: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index-project", tags=["Indexing"])
async def index_project(request: IndexProjectRequest):
    logger.info(f"Indexing project directory: '{request.project_path}' (project_id: {request.project_id})")
    if not os.path.exists(request.project_path):
        logger.warning(f"Project indexing failed - path '{request.project_path}' does not exist.")
        raise HTTPException(status_code=400, detail=f"Path '{request.project_path}' does not exist.")

    indexed_files = 0
    indexed_chunks = 0

    try:
        for root, dirs, files in os.walk(request.project_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "dist", "build", "__pycache__")]
            
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, request.project_path)
                
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        
                    chunks = chunk_file_content(rel_path, content)
                    for chunk in chunks:
                        embedding = await generate_embedding(chunk["content"])
                        await store_embedding_chunk(
                            file_path=chunk["filePath"],
                            chunk_index=chunk["chunkIndex"],
                            content=chunk["content"],
                            metadata=chunk["metadata"],
                            embedding=embedding,
                            project_id=request.project_id
                        )
                        indexed_chunks += 1
                    indexed_files += 1
                except Exception as file_err:
                    logger.error(f"Error processing project file {rel_path}: {file_err}")

        logger.info(f"Project indexing completed successfully: {indexed_files} files, {indexed_chunks} chunks indexed.")
        return {
            "message": "Project code indexing completed.",
            "indexed_files": indexed_files,
            "indexed_chunks": indexed_chunks,
        }
    except Exception as e:
        logger.error(f"Error during index-project execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

