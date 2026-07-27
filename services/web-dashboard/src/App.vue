<template>
  <div class="app-layout">
    <Sidebar :activeTab="activeTab" @select-tab="tab => activeTab = tab" />

    <main class="content-area">
      <ChatStudio v-if="activeTab === 'chat'" />
      <MemoryWorkbench v-else-if="activeTab === 'memory'" />
      <SystemMonitor v-else-if="activeTab === 'system'" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Sidebar from './components/Sidebar.vue';
import ChatStudio from './components/ChatStudio.vue';
import MemoryWorkbench from './components/MemoryWorkbench.vue';
import SystemMonitor from './components/SystemMonitor.vue';

const activeTab = ref('chat');
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  width: 100vw;
  background-color: var(--bg-primary);
}

.content-area {
  flex: 1;
  display: flex;
}
</style>
