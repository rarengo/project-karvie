# Project Karvie - Self-Hosted AI Software Engineer & Automation Platform

**Project Karvie** is a self-hosted, multi-agent AI software engineering platform built on a 100% Python backend, Vue 3 Web Dashboard, and local LLM inference engines (`Qwen2.5-Coder:7b` + `nomic-embed-text` via Ollama).

---

## 🏗️ System Architecture & Services Stack

| Container Service | Technology Stack | Port | Purpose |
| :--- | :--- | :--- | :--- |
| **`karvie-web-dashboard`** | Vue 3 + Vite + NGINX | `3000` | Glassmorphic Web Dashboard UI for Chat & Memory Workbench |
| **`karvie-memory-service`** | Python 3.12 + FastAPI + Asyncpg | `8081` | RAG Memory Pipeline, AST Code Parsing & Obsidian Vault Indexer |
| **`karvie-litellm`** | LiteLLM Router Proxy | `8000` | OpenAI-compatible API gateway with local & cloud failover |
| **`karvie-postgres`** | PostgreSQL 16 + `pgvector` | `5432` | Relational project state and vector embedding database |
| **`karvie-redis`** | Redis 7 Alpine | `6379` | High-speed short-term task cache & agent PubSub |
| **`karvie-ollama`** | Ollama Engine | `11434` | Memory-optimized local LLM & embedding model server |

---

## 📋 Target Hardware Profile (ASUS VivoBook / Ubuntu Server 24.04 LTS)

- **Host OS**: Ubuntu Server 24.04 LTS
- **CPU & RAM**: Intel Core i7, 16 GB RAM
- **Network**: Tailscale Private Mesh VPN (`100.x.y.z`)
- **Memory Allocations**:
  - Ollama AI Engine: 8.0 GB RAM max
  - PostgreSQL (`pgvector`): 1.5 GB RAM
  - Python Memory Service: 1.0 GB RAM
  - LiteLLM Router: 512 MB RAM
  - Web UI Dashboard: 256 MB RAM
  - Reserved for Ubuntu Host OS: ~4.7 GB RAM

---

## 🚀 Complete Step-by-Step Installation Guide

### Step 1: Clone / Copy Codebase to Your Ubuntu Server
Connect to your server via SSH (over Tailscale or local IP) and set up the directory:

```bash
mkdir -p ~/Project-karvie
cd ~/Project-karvie
```

---

### Step 2: Run Automated System Dependencies Setup
Execute the automated setup script to install Docker, Node.js 20 LTS, configure UFW firewall rules, and apply 16GB RAM kernel tuning:

```bash
chmod +x scripts/install-ubuntu-deps.sh
./scripts/install-ubuntu-deps.sh
```

Apply Docker user permissions without rebooting:
```bash
newgrp docker
```

---

### Step 3: Build & Start All Karvie Docker Containers
Launch all 6 Karvie microservices:

```bash
chmod +x scripts/start-services.sh
./scripts/start-services.sh
```

To build all custom containers (Python FastAPI + Vue 3 NGINX Web Dashboard):
```bash
docker compose up -d --build
```

Verify all containers are up and healthy:
```bash
docker compose ps
```

---

### Step 4: Download Local AI Models into Ollama
Pull the memory-optimized 7B coding model and vector embedding model into your server:

```bash
# 1. Download Vector Embedding Model (~270 MB)
docker exec -it karvie-ollama ollama pull nomic-embed-text

# 2. Download Primary 7B Coding Model (~4.5 GB)
docker exec -it karvie-ollama ollama pull qwen2.5-coder:7b
```

---

### Step 5: Index Obsidian Knowledge Vault
Populate `pgvector` memory with your initial coding standards and architecture decisions:

```bash
curl -X POST http://localhost:8081/index-vault
```

---

## 🌐 Accessing Karvie Interfaces

### 1. Web Dashboard UI (Browser)
Open your browser and navigate to:
```
http://<TAILSCALE_IP>:3000
```
- **Chat Studio**: Interactive prompt and code generation with `karvie-coder`.
- **RAG Memory**: Perform real-time vector searches against `pgvector`.
- **System Health**: View status of all server containers.

### 2. Interactive Python FastAPI OpenAPI Docs
View and test memory service endpoints directly in your browser:
```
http://<TAILSCALE_IP>:8081/docs
```

### 3. Postman / API Client Endpoint
Send OpenAI-compatible requests over Tailscale:
- **URL**: `POST http://<TAILSCALE_IP>:8000/v1/chat/completions`
- **Headers**:
  - `Content-Type`: `application/json`
  - `Authorization`: `Bearer sk-karvie-local-master-key`
- **Payload**:
  ```json
  {
    "model": "karvie-coder",
    "messages": [
      {"role": "user", "content": "Write an Express.js TypeScript route for user login."}
    ]
  }
  ```

---

## 🛠️ Operational & Maintenance Commands

- **View Live Microservice Logs**:
  ```bash
  docker compose logs -f
  ```
- **Restart Specific Service**:
  ```bash
  docker compose restart memory-service
  ```
- **Stop All Containers**:
  ```bash
  docker compose down
  ```
