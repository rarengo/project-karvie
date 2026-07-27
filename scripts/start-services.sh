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
docker compose up -d

echo "Waiting for services to become healthy..."
sleep 5

docker compose ps

echo ""
echo "=========================================="
echo " Karvie Infrastructure Services Started!"
echo " - LiteLLM Router Proxy: http://localhost:8000"
echo " - PostgreSQL (pgvector): localhost:5432"
echo " - Redis Cache: localhost:6379"
echo " - Ollama API: http://localhost:11434"
echo "=========================================="
