import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const LITELLM_URL = process.env.LITELLM_URL || 'http://litellm:8000';
const LITELLM_API_KEY = process.env.LITELLM_MASTER_KEY || 'sk-karvie-local-master-key';

export async function generateEmbedding(text: string): Promise<number[]> {
  try {
    const response = await axios.post(
      `${LITELLM_URL}/v1/embeddings`,
      {
        model: 'karvie-embedder',
        input: text,
      },
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${LITELLM_API_KEY}`,
        },
        timeout: 15000,
      }
    );

    if (response.data && response.data.data && response.data.data[0]) {
      return response.data.data[0].embedding;
    }

    throw new Error('Invalid embedding response format from LiteLLM proxy.');
  } catch (error: any) {
    console.error('Error generating embedding:', error.message || error);
    throw error;
  }
}
