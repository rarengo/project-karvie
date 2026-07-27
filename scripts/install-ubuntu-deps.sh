#!/usr/bin/env bash
# ==============================================================================
# Project Karvie - Phase 1 Setup Script for Ubuntu Server 24.04 LTS
# ==============================================================================
# Description: Installs Docker, NVIDIA Container Toolkit, CUDA drivers, Python 3.12,
# Node.js 20 LTS, and configures basic system security (UFW, Sysctl limits).
# ==============================================================================

set -euo pipefail

echo "=========================================="
echo " Starting Project Karvie System Setup"
echo "=========================================="

# 1. System Update & Essential Packages
echo "[1/6] Updating APT repositories & installing base tools..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    htop \
    ufw \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    build-essential

# 2. Configure Firewall (UFW)
echo "[2/6] Configuring UFW Firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 8000/tcp comment 'LiteLLM Proxy'
sudo ufw allow 8080/tcp comment 'Karvie API Gateway'
sudo ufw allow 3000/tcp comment 'Karvie Web Dashboard'
# Uncomment below if enabling ufw now:
# sudo ufw --force enable

# 3. Install Docker Engine & Docker Compose
echo "[3/6] Installing Docker Engine..."
if ! command -v docker &> /dev/null; then
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker "$USER"
    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi

# 4. Install NVIDIA Container Toolkit (for GPU Acceleration if NVIDIA GPU is present)
echo "[4/6] Checking for NVIDIA GPU & setup Container Toolkit..."
if lspci | grep -i nvidia &> /dev/null; then
    echo "NVIDIA GPU detected. Installing NVIDIA Container Toolkit..."
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

    sudo apt-get update
    sudo apt-get install -y nvidia-container-toolkit
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker
    echo "NVIDIA Container Toolkit installed."
else
    echo "No NVIDIA GPU detected by lspci (or running in VM/Mac environment). Skipping NVIDIA Toolkit."
fi

# 5. Install Node.js 20 LTS
echo "[5/6] Installing Node.js 20 LTS..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "Node.js is already installed: $(node -v)"
fi

# 6. Increase System Virtual Memory & File Handles for Vector DB / vLLM
echo "[6/6] Applying Kernel Tuning for high performance..."
sudo sysctl -w vm.max_map_count=262144
sudo sysctl -w fs.file-max=65536
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.d/99-karvie.conf
echo "fs.file-max=65536" | sudo tee -a /etc/sysctl.d/99-karvie.conf

echo "=========================================="
echo " Project Karvie Setup Completed!"
echo " Note: Re-login or run 'newgrp docker' to apply docker group permissions."
echo "=========================================="
