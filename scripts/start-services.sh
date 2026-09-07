#!/usr/bin/env bash
# ==============================================================================
# Project Karvie - Start Local Stack
# ==============================================================================

set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Starting Docker Compose services for Project Karvie..."
docker compose up -d --build

echo "Waiting for services to become healthy..."
sleep 5

docker compose ps

echo "Checking / pulling required Ollama AI models..."
docker exec karvie-ollama ollama pull nomic-embed-text || true
docker exec karvie-ollama ollama pull qwen2.5-coder:1.5b || true

echo ""
echo "=============================================================================="
echo " Project Karvie Infrastructure & Services Started!"
echo " - Web Dashboard UI:              http://localhost:3000"
echo " - Agent Orchestrator API:        http://localhost:8082 (Docs: http://localhost:8082/docs)"
echo " - Memory Service RAG API:        http://localhost:8081 (Docs: http://localhost:8081/docs)"
echo " - LiteLLM Router Proxy Gateway:  http://localhost:8000 (V1: http://localhost:8000/v1/chat/completions)"
echo " - PostgreSQL (pgvector):         localhost:5432"
echo " - Redis State & Cache:           localhost:6379"
echo " - Ollama AI Engine API:          http://localhost:11434"
echo "=============================================================================="
