import os
import yaml
import asyncio
from typing import Dict, Any, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.ast_indexer import chunk_file_content
from app.embedder import generate_embedding
from app.db import store_embedding_chunk, clear_embeddings
from app.logger import setup_logger

logger = setup_logger("memory-service.vault_syncer")


def extract_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Extracts YAML frontmatter headers from markdown files."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
                return metadata, body
            except Exception as e:
                logger.error(f"Error parsing YAML frontmatter: {e}")
    return {}, content.strip()


async def process_single_file(full_path: str, vault_dir: str):
    """Processes and embeds a single markdown file into pgvector."""
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_content = f.read()

        frontmatter_meta, body = extract_frontmatter(raw_content)
        rel_path = os.path.relpath(full_path, vault_dir)
        
        chunks = chunk_file_content(f"vault/{rel_path}", body)
        for chunk in chunks:
            embedding = await generate_embedding(chunk["content"])
            combined_metadata = {
                **chunk["metadata"],
                **frontmatter_meta,
                "category": "vault",
                "file": rel_path,
            }
            await store_embedding_chunk(
                file_path=chunk["filePath"],
                chunk_index=chunk["chunkIndex"],
                content=chunk["content"],
                metadata=combined_metadata,
                embedding=embedding,
            )
        logger.debug(f"Processed vault note '{rel_path}' into {len(chunks)} chunks.")
    except Exception as e:
        logger.error(f"Failed to process single file {full_path}: {e}")


async def sync_vault(vault_dir: str) -> Dict[str, Any]:
    if not os.path.exists(vault_dir):
        logger.warning(f"Vault sync failed - directory does not exist: {vault_dir}")
        return {"total_files": 0, "total_chunks": 0, "status": "Directory does not exist"}

    total_files = 0
    logger.info(f"Starting full sync of Obsidian vault: '{vault_dir}'")
    await clear_embeddings("vault/")

    for root, _, files in os.walk(vault_dir):
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                await process_single_file(full_path, vault_dir)
                total_files += 1

    logger.info(f"Full vault sync completed successfully. Total .md notes synced: {total_files}")
    return {"total_files": total_files, "status": "success"}


class VaultWatchHandler(FileSystemEventHandler):
    """Watchdog file handler for real-time vault indexing."""

    def __init__(self, vault_dir: str, loop: asyncio.AbstractEventLoop):
        self.vault_dir = vault_dir
        self.loop = loop

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            logger.info(f"[Watchdog] Vault note modified: {event.src_path}")
            asyncio.run_coroutine_threadsafe(
                process_single_file(event.src_path, self.vault_dir), self.loop
            )

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            logger.info(f"[Watchdog] New vault note created: {event.src_path}")
            asyncio.run_coroutine_threadsafe(
                process_single_file(event.src_path, self.vault_dir), self.loop
            )


def start_vault_watcher(vault_dir: str, loop: asyncio.AbstractEventLoop) -> Observer:
    """Starts background real-time file watcher on vault directory."""
    handler = VaultWatchHandler(vault_dir, loop)
    observer = Observer()
    observer.schedule(handler, path=vault_dir, recursive=True)
    observer.start()
    logger.info(f"[Watchdog] Real-time Obsidian Vault watcher active on: {vault_dir}")
    return observer

