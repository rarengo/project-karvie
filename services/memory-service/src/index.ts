import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import * as fs from 'fs';
import * as path from 'path';
import { generateEmbedding } from './embedder';
import { searchCodeContext, storeEmbeddingChunk, clearProjectEmbeddings } from './db';
import { parseFileToChunks } from './indexer';
import { syncVaultDirectory } from './vault-syncer';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8081;

app.use(express.json());

// Health Check
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'healthy', service: 'karvie-memory-service' });
});

// Search Context Endpoint
app.post('/search-context', async (req: Request, res: Response) => {
  try {
    const { query, limit = 5, threshold = 0.4 } = req.body;

    if (!query) {
      return res.status(400).json({ error: 'Query string is required.' });
    }

    const queryVector = await generateEmbedding(query);
    const results = await searchCodeContext(queryVector, limit, threshold);

    return res.json({
      query,
      resultsCount: results.length,
      results,
    });
  } catch (error: any) {
    console.error('Error in /search-context:', error.message || error);
    return res.status(500).json({ error: error.message || 'Internal server error' });
  }
});

// Index Obsidian Vault Endpoint
app.post('/index-vault', async (req: Request, res: Response) => {
  try {
    const vaultPath = req.body.vaultPath || path.join(__dirname, '../../vault');
    console.log(`Starting Obsidian Vault indexing from: ${vaultPath}`);

    const result = await syncVaultDirectory(vaultPath);
    return res.json({
      message: 'Vault indexing completed successfully.',
      ...result,
    });
  } catch (error: any) {
    console.error('Error in /index-vault:', error.message || error);
    return res.status(500).json({ error: error.message || 'Internal server error' });
  }
});

// Index Local Target Repository Endpoint
app.post('/index-project', async (req: Request, res: Response) => {
  try {
    const { projectPath, projectId } = req.body;

    if (!projectPath || !fs.existsSync(projectPath)) {
      return res.status(400).json({ error: 'Valid projectPath directory is required.' });
    }

    let indexedFiles = 0;
    let indexedChunks = 0;

    async function walkAndIndex(dir: string) {
      const entries = fs.readdirSync(dir, { withFileTypes: true });

      for (const entry of entries) {
        if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === 'dist') {
          continue;
        }

        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory()) {
          await walkAndIndex(fullPath);
        } else if (entry.isFile()) {
          const content = fs.readFileSync(fullPath, 'utf-8');
          const relPath = path.relative(projectPath, fullPath);
          const chunks = parseFileToChunks(relPath, content);

          for (const chunk of chunks) {
            try {
              const embedding = await generateEmbedding(chunk.content);
              await storeEmbeddingChunk({
                projectId,
                filePath: chunk.filePath,
                chunkIndex: chunk.chunkIndex,
                content: chunk.content,
                metadata: chunk.metadata,
                embedding,
              });
              indexedChunks++;
            } catch (err: any) {
              console.error(`Failed to store chunk for ${chunk.filePath}:`, err.message);
            }
          }
          indexedFiles++;
        }
      }
    }

    await walkAndIndex(projectPath);

    return res.json({
      message: 'Project indexing completed.',
      indexedFiles,
      indexedChunks,
    });
  } catch (error: any) {
    console.error('Error in /index-project:', error.message || error);
    return res.status(500).json({ error: error.message || 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`==========================================`);
  console.log(` Karvie Memory & RAG Service listening on port ${PORT}`);
  console.log(`==========================================`);
});
