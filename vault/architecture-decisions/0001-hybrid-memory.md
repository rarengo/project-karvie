# ADR 0001: Hybrid Memory Architecture

## Context
Project Karvie requires both deterministic structured data access (project schemas, AWS topology, user preferences) and high-speed semantic search over codebase ASTs and documentation.

## Decision
We adopt a **Hybrid Memory Strategy**:
1. **PostgreSQL 16 + pgvector**: Primary relational and vector embedding store.
2. **Obsidian Vault (Git-tracked Markdown)**: Human-editable knowledge base synced directly with the AI vector pipeline.
3. **Redis 7**: High-speed short-term task cache and agent step PubSub.

## Status
Accepted.
