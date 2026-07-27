import { Pool } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'postgres',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  user: process.env.POSTGRES_USER || 'karvie_admin',
  password: process.env.POSTGRES_PASSWORD || 'karvie_secure_password_change_me!',
  database: process.env.POSTGRES_DB || 'karvie_db',
});

export interface EmbeddingChunk {
  projectId?: string;
  filePath: string;
  chunkIndex: number;
  content: string;
  metadata: Record<string, any>;
  embedding: number[];
}

export async function storeEmbeddingChunk(chunk: EmbeddingChunk): Promise<string> {
  const query = `
    INSERT INTO project_embeddings (project_id, file_path, chunk_index, content, metadata, embedding)
    VALUES (
      $1,
      $2,
      $3,
      $4,
      $5,
      $6::vector
    )
    RETURNING id;
  `;

  // Format array into pgvector literal format: '[0.1, 0.2, ...]'
  const vectorStr = `[${chunk.embedding.join(',')}]`;
  const result = await pool.query(query, [
    chunk.projectId || null,
    chunk.filePath,
    chunk.chunkIndex,
    chunk.content,
    JSON.stringify(chunk.metadata),
    vectorStr,
  ]);

  return result.rows[0].id;
}

export async function searchCodeContext(
  queryEmbedding: number[],
  limit: number = 5,
  similarityThreshold: number = 0.5
) {
  const vectorStr = `[${queryEmbedding.join(',')}]`;
  const query = `
    SELECT 
      id,
      file_path,
      chunk_index,
      content,
      metadata,
      1 - (embedding <=> $1::vector) as similarity
    FROM project_embeddings
    WHERE 1 - (embedding <=> $1::vector) >= $2
    ORDER BY similarity DESC
    LIMIT $3;
  `;

  const result = await pool.query(query, [vectorStr, similarityThreshold, limit]);
  return result.rows;
}

export async function clearProjectEmbeddings(filePathPrefix?: string) {
  if (filePathPrefix) {
    await pool.query('DELETE FROM project_embeddings WHERE file_path LIKE $1', [`${filePathPrefix}%`]);
  } else {
    await pool.query('DELETE FROM project_embeddings');
  }
}

export default pool;
