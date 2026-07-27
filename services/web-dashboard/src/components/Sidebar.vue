<template>
  <aside class="sidebar glass-panel">
    <div class="brand">
      <div class="logo">
        <span class="logo-icon">⚡</span>
      </div>
      <div class="brand-text">
        <h2>KARVIE</h2>
        <span class="version">v2.0.0 • AI Engineer</span>
      </div>
    </div>

    <nav class="nav-menu">
      <button 
        :class="['nav-item', { active: activeTab === 'chat' }]" 
        @click="$emit('select-tab', 'chat')"
      >
        <span class="icon">💬</span>
        <span>Chat Studio</span>
      </button>

      <button 
        :class="['nav-item', { active: activeTab === 'memory' }]" 
        @click="$emit('select-tab', 'memory')"
      >
        <span class="icon">🧠</span>
        <span>RAG Memory</span>
      </button>

      <button 
        :class="['nav-item', { active: activeTab === 'system' }]" 
        @click="$emit('select-tab', 'system')"
      >
        <span class="icon">🖥️</span>
        <span>System Health</span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <div class="hardware-badge">
        <span class="badge-title">Host Server</span>
        <span class="badge-desc">ASUS VivoBook • 16GB RAM</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
defineProps<{
  activeTab: string;
}>();

defineEmits(['select-tab']);
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: calc(100vh - 2rem);
  margin: 1rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.logo {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: 0 4px 14px var(--accent-glow);
}

.brand-text h2 {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  letter-spacing: 0.05em;
  color: #fff;
}

.version {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  color: var(--text-muted);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-main);
}

.nav-item.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--border-active);
  color: #fff;
  box-shadow: 0 0 16px var(--accent-glow);
}

.hardware-badge {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
}

.badge-title {
  font-size: 0.75rem;
  color: var(--accent-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-desc {
  font-size: 0.8rem;
  color: var(--text-muted);
}
</style>
