import axios from 'axios';

// Get current host IP dynamically so it works seamlessly over Tailscale or Localhost
const currentHost = window.location.hostname;

export const LITELLM_API_BASE = `http://${currentHost}:8000`;
export const MEMORY_API_BASE = `http://${currentHost}:8081`;
export const MASTER_KEY = 'sk-karvie-local-master-key';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export async function sendChatMessage(messages: ChatMessage[], model: string = 'karvie-coder') {
  const response = await axios.post(
    `${LITELLM_API_BASE}/v1/chat/completions`,
    {
      model,
      messages,
      temperature: 0.2,
    },
    {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${MASTER_KEY}`,
      },
    }
  );

  return response.data;
}

export async function searchContext(query: string, limit: number = 5) {
  const response = await axios.post(
    `${MEMORY_API_BASE}/search-context`,
    {
      query,
      limit,
    },
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  return response.data;
}

export async function triggerVaultIndex() {
  const response = await axios.post(
    `${MEMORY_API_BASE}/index-vault`,
    {},
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  return response.data;
}

export async function checkHealth() {
  try {
    const memoryRes = await axios.get(`${MEMORY_API_BASE}/health`, { timeout: 3000 });
    const litellmRes = await axios.get(`${LITELLM_API_BASE}/health/readiness`, { timeout: 3000 });

    return {
      memoryService: memoryRes.data.status === 'healthy',
      litellmService: litellmRes.status === 200,
    };
  } catch (e) {
    return {
      memoryService: false,
      litellmService: false,
    };
  }
}
