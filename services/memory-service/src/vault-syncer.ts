import * as fs from 'fs';
import * as path from 'path';
import { parseFileToChunks } from './indexer';
import { generateEmbedding } from './embedder';
import { storeEmbeddingChunk, clearProjectEmbeddings } from './db';

export async function syncVaultDirectory(vaultDir: string): Promise<{ totalFiles: number; totalChunks: number }> {
  if (!fs.existsSync(vaultDir)) {
    console.warn(`Vault directory does not exist: ${vaultDir}`);
    return { totalFiles: 0, totalChunks: 0 };
  }

  let totalFiles = 0;
  let totalChunks = 0;

  async function processDirectory(dir: string) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        await processDirectory(fullPath);
      } else if (entry.isFile() && entry.name.endsWith('.md')) {
        const content = fs.readFileSync(fullPath, 'utf-8');
        const relPath = path.relative(vaultDir, fullPath);
        const chunks = parseFileToChunks(`vault/${relPath}`, content);

        for (const chunk of chunks) {
          try {
            const embedding = await generateEmbedding(chunk.content);
            await storeEmbeddingChunk({
              filePath: chunk.filePath,
              chunkIndex: chunk.chunkIndex,
              content: chunk.content,
              metadata: { ...chunk.metadata, category: 'vault' },
              embedding,
            });
            totalChunks++;
          } catch (err: any) {
            console.error(`Failed to index vault chunk ${chunk.filePath}[${chunk.chunkIndex}]:`, err.message);
          }
        }

        totalFiles++;
      }
    }
  }

  // Clear existing vault embeddings first
  await clearProjectEmbeddings('vault/');
  await processDirectory(vaultDir);

  return { totalFiles, totalChunks };
}
