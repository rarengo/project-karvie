# Project Karvie - Autonomous AI Software Engineering Platform

Project Karvie is a self-hosted, multi-agent AI software engineer and automation platform designed specifically for Vue.js, TypeScript, Node.js, Express, AWS, and Docker/Kubernetes workflows.

---

## 🏗️ Architecture Stack

- **Local Inference Engine**: Ollama (Primary `Qwen2.5-Coder:7b` + `nomic-embed-text` embeddings)
- **Model Router Proxy**: LiteLLM Proxy (OpenAI API standard routing with local/cloud fallback)
- **Agent Orchestration**: LangGraph state machine with Planner, Coder, Reviewer, and DevOps agents
- **Hybrid Memory**: PostgreSQL 16 (`pgvector`) + Redis 7 + Obsidian Markdown Vault
- **Tool Protocol**: Anthropic Model Context Protocol (MCP) for Git, AWS, Docker, and terminal sandbox

---

## 🚀 Quick Start Instructions (ASUS VivoBook / Ubuntu Server 24.04 LTS)

### 1. Host Infrastructure Setup
Run the automated installation script to configure Docker, NVIDIA Toolkit, and system parameters:

```bash
chmod +x scripts/install-ubuntu-deps.sh
./scripts/install-ubuntu-deps.sh
```

### 2. Start Core Infrastructure Services
Launch PostgreSQL (with `pgvector`), Redis, Ollama, and LiteLLM Router:

```bash
./scripts/start-services.sh
```

### 3. Pull Initial Utility & Embedding Models in Ollama
```bash
docker exec -it karvie-ollama ollama pull nomic-embed-text
docker exec -it karvie-ollama ollama pull qwen2.5-coder:7b
```

---

## 📂 Project Directory Structure

```
/opt/karvie/ (or ~/Project-karvie)
├── docker-compose.yml           # Core local infrastructure definition
├── .env.example                 # Environment variable templates
├── config/
│   ├── litellm-config.yaml      # Model router proxy configuration
│   └── postgres/init.sql        # Database & pgvector schema init
├── scripts/
│   ├── install-ubuntu-deps.sh   # Ubuntu Server installation script
│   └── start-services.sh        # Service startup script
└── vault/                       # Obsidian Markdown knowledge base
    ├── architecture-decisions/
    ├── coding-standards/
    └── aws-infrastructure/
```
