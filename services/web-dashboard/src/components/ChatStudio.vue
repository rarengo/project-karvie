<template>
  <div class="chat-studio glass-panel">
    <header class="chat-header">
      <div class="header-info">
        <h3>AI Coding Studio</h3>
        <span class="active-model">Model: {{ selectedModel }}</span>
      </div>
      <div class="model-selector">
        <select v-model="selectedModel" class="select-input">
          <option value="karvie-coder">karvie-coder (Qwen2.5 7B Local)</option>
          <option value="karvie-utility">karvie-utility (Fast 1.5B Local)</option>
          <option value="karvie-cloud-reasoner">karvie-cloud-reasoner (Cloud Fallback)</option>
        </select>
      </div>
    </header>

    <div class="message-feed" ref="feedRef">
      <div 
        v-for="(msg, i) in messages" 
        :key="i" 
        :class="['chat-bubble', msg.role]"
      >
        <div class="avatar">{{ msg.role === 'user' ? '👤' : '⚡' }}</div>
        <div class="bubble-content">
          <div class="sender-name">{{ msg.role === 'user' ? 'You' : 'Karvie AI' }}</div>
          <pre class="formatted-text">{{ msg.content }}</pre>
        </div>
      </div>

      <div v-if="loading" class="chat-bubble assistant loading">
        <div class="avatar">⚡</div>
        <div class="bubble-content">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <footer class="input-bar">
      <textarea 
        v-model="userPrompt" 
        @keydown.enter.prevent="handleSend" 
        placeholder="Ask Karvie to write code, refactor components, or debug errors..." 
        rows="2"
      ></textarea>
      <button @click="handleSend" :disabled="loading || !userPrompt.trim()" class="btn-primary">
        <span>Send</span>
        <span class="icon">➔</span>
      </button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { sendChatMessage, type ChatMessage } from '../services/api';

const selectedModel = ref('karvie-coder');
const userPrompt = ref('');
const loading = ref(false);
const feedRef = ref<HTMLDivElement | null>(null);

const messages = ref<ChatMessage[]>([
  {
    role: 'assistant',
    content: 'Hello! I am Karvie, your autonomous AI software engineer. How can I help you code today?',
  },
]);

const scrollToBottom = async () => {
  await nextTick();
  if (feedRef.value) {
    feedRef.value.scrollTop = feedRef.value.scrollHeight;
  }
};

const handleSend = async () => {
  if (!userPrompt.value.trim() || loading.value) return;

  const promptText = userPrompt.value.trim();
  userPrompt.value = '';

  messages.value.push({ role: 'user', content: promptText });
  loading.value = true;
  await scrollToBottom();

  try {
    const payloadMessages: ChatMessage[] = [
      { role: 'system', content: 'You are Karvie, an expert AI software engineer specialized in Vue 3, TypeScript, Express, AWS, and Docker.' },
      ...messages.value,
    ];

    const response = await sendChatMessage(payloadMessages, selectedModel.value);
    const replyText = response.choices[0].message.content;

    messages.value.push({ role: 'assistant', content: replyText });
  } catch (err: any) {
    const errorMsg =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      err.message ||
      'Failed to reach Karvie AI backend.';
    messages.value.push({
      role: 'assistant',
      content: `❌ Error: ${errorMsg}`,
    });
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
};
</script>

<style scoped>
.chat-studio {
  flex: 1;
  height: calc(100vh - 2rem);
  margin: 1rem 1rem 1rem 0;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info h3 {
  font-family: var(--font-heading);
  font-size: 1.1rem;
}

.active-model {
  font-size: 0.8rem;
  color: var(--accent-secondary);
}

.select-input {
  background: rgba(0, 0, 0, 0.4);
  color: var(--text-main);
  border: 1px solid var(--border-color);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  outline: none;
  font-size: 0.85rem;
}

.message-feed {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.chat-bubble {
  display: flex;
  gap: 1rem;
  max-width: 85%;
}

.chat-bubble.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bubble-content {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  padding: 1rem;
  border-radius: 12px;
}

.chat-bubble.user .bubble-content {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--border-active);
}

.sender-name {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.35rem;
}

.formatted-text {
  white-space: pre-wrap;
  font-family: var(--font-sans);
  font-size: 0.95rem;
}

.input-bar {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

textarea {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-main);
  padding: 0.75rem;
  font-family: var(--font-sans);
  font-size: 0.95rem;
  outline: none;
  resize: none;
}

textarea:focus {
  border-color: var(--accent-primary);
}

/* Typing Indicator Animation */
.typing-indicator span {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: var(--accent-primary);
  border-radius: 50%;
  margin-right: 4px;
  animation: bounce 1.2s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}
</style>
