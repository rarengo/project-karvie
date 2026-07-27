# Project Karvie - Autonomous AI Software Engineer & Automation Platform

**Project Karvie** is a self-hosted, multi-agent AI software engineering platform built on a 100% Python backend, LangGraph agent orchestration framework, Vue 3 Web Dashboard, and local LLM inference engines (`Qwen2.5-Coder:7b` + `nomic-embed-text` via Ollama).

---

## 🏗️ System Architecture & Microservices Stack

| Container Service | Technology Stack | Port | Purpose |
| :--- | :--- | :--- | :--- |
| **`karvie-web-dashboard`** | Vue 3 + Vite + NGINX | `3000` | Glassmorphic Web Dashboard UI for Chat & Memory Workbench |
| **`karvie-agent-orchestrator`** | Python 3.12 + LangGraph + FastAPI | `8082` | Multi-Agent Network (Planner, Coder, Reviewer, DevOps) & Security Gates |
| **`karvie-memory-service`** | Python 3.12 + FastAPI + Asyncpg | `8081` | RAG Memory Pipeline, AST Code Parsing & Obsidian Vault Indexer |
| **`karvie-litellm`** | LiteLLM Router Proxy | `8000` | OpenAI-compatible API gateway with local & cloud failover |
| **`karvie-postgres`** | PostgreSQL 16 + `pgvector` | `5432` | Relational project state and vector embedding database |
| **`karvie-redis`** | Redis 7 Alpine | `6379` | High-speed short-term task cache & agent PubSub |
| **`karvie-ollama`** | Ollama Engine | `11434` | Memory-optimized local LLM & embedding model server |

---

## 🛡️ Security & Command Approval Architecture

1. **Subprocess Sandbox Runner**: Commands run safely with resource caps and execution timeouts.
2. **Interactive Security Approval Gates**: High-risk commands automatically pause agent execution and require explicit user approval:
   - 🛑 `rm -rf`, `drop table`, `drop database`
   - 🛑 `git push --force`, `git reset --hard`
   - 🛑 `aws deploy`, `serverless deploy`
3. **Pending Approval Endpoints**:
   - `GET http://<SERVER_IP>:8082/pending-approvals`
   - `POST http://<SERVER_IP>:8082/approve-command`
   - `POST http://<SERVER_IP>:8082/reject-command`

---

## 📋 Target Hardware Profile (ASUS VivoBook / Ubuntu Server 24.04 LTS)

- **Host OS**: Ubuntu Server 24.04 LTS
- **CPU & RAM**: Intel Core i7, 16 GB RAM
- **Network**: Tailscale Private Mesh VPN (`100.x.y.z`)

---

## 🚀 Complete Step-by-Step Installation Guide

### Step 1: Clone / Copy Codebase to Your Ubuntu Server
Connect to your server via SSH (over Tailscale or local IP) and set up the directory:

```bash
mkdir -p ~/Project-karvie
cd ~/Project-karvie
```

---

### Step 2: Build & Start All 7 Karvie Docker Containers
Launch all microservices:

```bash
docker compose up -d --build
```

Verify containers status:
```bash
docker compose ps
```

---

### Step 3: Pull Local AI Models in Ollama
```bash
docker exec -it karvie-ollama ollama pull nomic-embed-text
docker exec -it karvie-ollama ollama pull qwen2.5-coder:7b
docker exec -it karvie-ollama ollama pull qwen2.5-coder:1.5b
```

---

## 🌐 Accessing Karvie Services & APIs

- **Vue 3 Web Dashboard UI**: `http://<TAILSCALE_IP>:3000`
- **Agent Orchestrator API Docs**: `http://<TAILSCALE_IP>:8082/docs`
- **Python Memory RAG API Docs**: `http://<TAILSCALE_IP>:8081/docs`
- **LiteLLM OpenAI API Gateway**: `http://<TAILSCALE_IP>:8000/v1/chat/completions`
