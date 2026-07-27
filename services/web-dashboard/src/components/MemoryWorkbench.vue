<template>
  <div class="memory-workbench glass-panel">
    <header class="workbench-header">
      <div>
        <h3>RAG Memory & AST Vector Search</h3>
        <p class="subtitle">Query Karvie's long-term memory & index markdown documentation</p>
      </div>
      <button @click="handleIndexVault" :disabled="indexing" class="btn-secondary">
        <span>{{ indexing ? 'Syncing Vault...' : '🔄 Sync Obsidian Vault' }}</span>
      </button>
    </header>

    <div class="search-box">
      <input 
        v-model="searchQuery" 
        @keyup.enter="handleSearch" 
        type="text" 
        placeholder="Enter natural language query to search pgvector memory (e.g. 'Vue 3 script setup rules')..." 
        class="search-input"
      />
      <button @click="handleSearch" :disabled="searching || !searchQuery.trim()" class="btn-primary">
        <span>Search Memory</span>
      </button>
    </div>

    <div class="results-container">
      <div v-if="searching" class="placeholder-box">
        <div class="spinner"></div>
        <p>Performing cosine similarity vector search in PostgreSQL (pgvector)...</p>
      </div>

      <div v-else-if="results.length > 0" class="results-list">
        <div v-for="(res, idx) in results" :key="idx" class="result-card">
          <div class="card-header">
            <span class="file-path">📄 {{ res.file_path }} (Chunk {{ res.chunk_index }})</span>
            <span class="similarity-badge">Score: {{ (res.similarity * 100).toFixed(1) }}%</span>
          </div>
          <pre class="card-code">{{ res.content }}</pre>
        </div>
      </div>

      <div v-else class="placeholder-box">
        <span class="icon">🔍</span>
        <p>No search results yet. Type a query above or click "Sync Obsidian Vault" to populate pgvector memory.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { searchContext, triggerVaultIndex } from '../services/api';

const searchQuery = ref('');
const searching = ref(false);
const indexing = ref(false);
const results = ref<any[]>([]);

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return;
  searching.value = true;
  try {
    const data = await searchContext(searchQuery.value.trim());
    results.value = data.results || [];
  } catch (err: any) {
    alert(`Failed to search memory: ${err.message}`);
  } finally {
    searching.value = false;
  }
};

const handleIndexVault = async () => {
  indexing.value = true;
  try {
    const res = await triggerVaultIndex();
    alert(`Obsidian Vault Indexed Successfully!\nFiles: ${res.total_files}\nChunks: ${res.total_chunks}`);
  } catch (err: any) {
    alert(`Failed to index vault: ${err.message}`);
  } finally {
    indexing.value = false;
  }
};
</script>

<style scoped>
.memory-workbench {
  flex: 1;
  height: calc(100vh - 2rem);
  margin: 1rem 1rem 1rem 0;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.workbench-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.workbench-header h3 {
  font-family: var(--font-heading);
  font-size: 1.2rem;
}

.subtitle {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.search-box {
  display: flex;
  gap: 0.75rem;
}

.search-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-main);
  padding: 0.75rem 1rem;
  outline: none;
  font-size: 0.95rem;
}

.search-input:focus {
  border-color: var(--accent-primary);
}

.results-container {
  flex: 1;
  overflow-y: auto;
}

.placeholder-box {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: var(--text-muted);
  text-align: center;
}

.placeholder-box .icon {
  font-size: 2.5rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.file-path {
  font-size: 0.85rem;
  color: var(--accent-secondary);
  font-weight: 500;
}

.similarity-badge {
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-success);
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-weight: 600;
}

.card-code {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.75rem;
  border-radius: 8px;
  white-space: pre-wrap;
}
</style>
