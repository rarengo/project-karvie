# Project Karvie - Logging & Telemetry Guide

This document explains how logging is structured and configured across Project Karvie's microservices stack.

---

## 🪵 Log Format Standard

All microservices write structured logs to `stdout` in the following unified format:

```text
YYYY-MM-DD HH:MM:SS | LEVEL    | SERVICE_NAME | MESSAGE
```

### Log Levels
The logging level can be configured at runtime via the `LOG_LEVEL` environment variable for each container:

- `DEBUG`: Verbose internal operations (raw vector dimension stats, individual chunk processing).
- `INFO` *(Default)*: HTTP request/response metrics, agent state transitions, sandbox command execution, vault sync events.
- `WARNING`: Security approval gate triggers, missing directories, failed lookups.
- `ERROR`: Unhandled exceptions, failed sandbox commands, LiteLLM connectivity errors.

---

## ⚙️ Environment Configuration

In your `.env` file or `docker-compose.yml`, set the desired log level:

```env
LOG_LEVEL=INFO
```

---

## 🔍 How to View Microservice Logs

### 1. View All System Logs
```bash
docker compose logs -f
```

### 2. View Agent Orchestrator Logs
```bash
docker compose logs -f agent-orchestrator
```

### 3. View Memory & RAG Indexer Service Logs
```bash
docker compose logs -f memory-service
```

### 4. View LiteLLM Proxy Logs
```bash
docker compose logs -f litellm
```

---

## 📊 Example Log Streams

### Agent Orchestrator Workflow Log:
```text
2026-09-06 14:30:00 | INFO     | agent-orchestrator | Incoming HTTP request: POST /execute-task from 172.18.0.1
2026-09-06 14:30:00 | INFO     | agent-orchestrator.workflow | Starting agent workflow [Task ID: 9b1deb4d-3b7d-4b69-9b7e-908e3a2b1c4d]
2026-09-06 14:30:00 | INFO     | agent-orchestrator.workflow | [Task ID: 9b1deb4d-3b7d-4b69-9b7e-908e3a2b1c4d] Step 1/3: Running Planner Agent...
2026-09-06 14:30:02 | INFO     | agent-orchestrator.planner | Planner Agent completed in 1.85s with 4 steps.
2026-09-06 14:30:02 | INFO     | agent-orchestrator.workflow | [Task ID: 9b1deb4d-3b7d-4b69-9b7e-908e3a2b1c4d] Step 2/3: Running Coder Agent...
2026-09-06 14:30:08 | INFO     | agent-orchestrator.coder | Coder Agent completed in 5.42s (1420 chars generated).
2026-09-06 14:30:08 | INFO     | agent-orchestrator.workflow | [Task ID: 9b1deb4d-3b7d-4b69-9b7e-908e3a2b1c4d] Step 3/3: Running Reviewer Agent...
2026-09-06 14:30:10 | INFO     | agent-orchestrator.reviewer | Reviewer Agent completed in 1.92s (Approved: True)
2026-09-06 14:30:10 | INFO     | agent-orchestrator.workflow | [Task ID: 9b1deb4d-3b7d-4b69-9b7e-908e3a2b1c4d] Workflow finished with status: COMPLETED
2026-09-06 14:30:10 | INFO     | agent-orchestrator | HTTP Response: POST /execute-task - Status 200 (9210.4ms)
```

### Memory RAG Search Log:
```text
2026-09-06 14:31:05 | INFO     | memory-service | Incoming HTTP request: POST /search-context from 172.18.0.1
2026-09-06 14:31:05 | INFO     | memory-service | Searching code context for query: 'Vue 3 setup components' (limit=5, threshold=0.35)
2026-09-06 14:31:05 | INFO     | memory-service.db | pgvector query executed in 14.2ms (found 5 rows above threshold 0.35)
2026-09-06 14:31:05 | INFO     | memory-service | HTTP Response: POST /search-context - Status 200 (38.5ms)
```
