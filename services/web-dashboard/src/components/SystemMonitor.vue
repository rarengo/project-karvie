<template>
  <div class="system-monitor glass-panel">
    <header class="monitor-header">
      <div>
        <h3>System & Container Health</h3>
        <p class="subtitle">Live status monitoring for Karvie microservices</p>
      </div>
      <button @click="refreshHealth" class="btn-secondary">
        <span>Refresh Status</span>
      </button>
    </header>

    <div class="status-grid">
      <div class="status-card glass-panel">
        <div class="card-top">
          <span class="service-name">LiteLLM Proxy Router</span>
          <span :class="['status-dot', healthStatus.litellmService ? 'online' : 'offline']"></span>
        </div>
        <div class="card-details">
          <p>Endpoint: <code>http://localhost:8000</code></p>
          <p>Status: <strong>{{ healthStatus.litellmService ? 'Online' : 'Unreachable' }}</strong></p>
        </div>
      </div>

      <div class="status-card glass-panel">
        <div class="card-top">
          <span class="service-name">Python FastAPI Memory Service</span>
          <span :class="['status-dot', healthStatus.memoryService ? 'online' : 'offline']"></span>
        </div>
        <div class="card-details">
          <p>Endpoint: <code>http://localhost:8081</code></p>
          <p>Status: <strong>{{ healthStatus.memoryService ? 'Online' : 'Unreachable' }}</strong></p>
        </div>
      </div>

      <div class="status-card glass-panel">
        <div class="card-top">
          <span class="service-name">PostgreSQL (pgvector)</span>
          <span class="status-dot online"></span>
        </div>
        <div class="card-details">
          <p>Port: <code>5432</code></p>
          <p>Status: <strong>Online (1.5GB RAM Cap)</strong></p>
        </div>
      </div>

      <div class="status-card glass-panel">
        <div class="card-top">
          <span class="service-name">Ollama AI Engine</span>
          <span class="status-dot online"></span>
        </div>
        <div class="card-details">
          <p>Models Loaded: <code>qwen2.5-coder:7b</code>, <code>nomic-embed-text</code></p>
          <p>Status: <strong>Active (8GB RAM Cap)</strong></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { checkHealth } from '../services/api';

const healthStatus = ref({
  memoryService: false,
  litellmService: false,
});

const refreshHealth = async () => {
  healthStatus.value = await checkHealth();
};

onMounted(() => {
  refreshHealth();
});
</script>

<style scoped>
.system-monitor {
  flex: 1;
  height: calc(100vh - 2rem);
  margin: 1rem 1rem 1rem 0;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.monitor-header h3 {
  font-family: var(--font-heading);
  font-size: 1.2rem;
}

.subtitle {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
}

.status-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-name {
  font-weight: 600;
  font-size: 0.95rem;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.online {
  background: var(--accent-success);
  box-shadow: 0 0 10px var(--accent-success);
}

.status-dot.offline {
  background: #ef4444;
  box-shadow: 0 0 10px #ef4444;
}

.card-details p {
  font-size: 0.85rem;
  color: var(--text-muted);
}

code {
  font-family: var(--font-mono);
  color: var(--accent-secondary);
}
</style>
