# ADR 0002: Primary Local LLM Selection (Qwen2.5-Coder:1.5b)

## Context
Project Karvie is deployed on local host hardware (e.g. 16GB RAM laptop / edge server). Running `Qwen2.5-Coder:7b` alongside PostgreSQL, Redis, Memory Service, Agent Orchestrator, and LiteLLM consumed ~4.5GB of RAM for Ollama alone, resulting in higher memory contention on constrained hosts.

## Decision
We select **`Qwen2.5-Coder:1.5b`** as the primary local coding model (`karvie-coder`) for LiteLLM routing:
1. **Memory Efficiency**: ~1.5GB RAM footprint, reducing host memory pressure by over 60%.
2. **Speed & Latency**: Substantially faster token generation per second on CPU/integrated GPU hardware.
3. **Fallback Path**: Cloud heavy reasoning (`karvie-cloud-reasoner`, e.g. Claude 3.5 Sonnet) remains available for complex multi-file refactoring tasks.

## Status
Accepted.
