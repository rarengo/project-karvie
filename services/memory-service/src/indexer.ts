import * as fs from 'fs';
import * as path from 'path';
import { parse as parseVueSFC } from '@vue/compiler-sfc';

export interface CodeChunk {
  filePath: string;
  chunkIndex: number;
  content: string;
  metadata: {
    language: string;
    type: 'function' | 'component' | 'interface' | 'general';
    startLine?: number;
    endLine?: number;
  };
}

export function parseFileToChunks(filePath: string, fileContent: string): CodeChunk[] {
  const ext = path.extname(filePath).toLowerCase();
  const chunks: CodeChunk[] = [];

  if (ext === '.vue') {
    return parseVueComponent(filePath, fileContent);
  }

  if (ext === '.ts' || ext === '.js' || ext === '.json') {
    return parseTypeScriptCode(filePath, fileContent);
  }

  // Fallback chunking for generic text / markdown files
  return parseGenericText(filePath, fileContent);
}

function parseVueComponent(filePath: string, content: string): CodeChunk[] {
  const chunks: CodeChunk[] = [];
  try {
    const sfc = parseVueSFC(content);
    let index = 0;

    if (sfc.descriptor.scriptSetup) {
      chunks.push({
        filePath,
        chunkIndex: index++,
        content: `// Vue 3 <script setup>\n${sfc.descriptor.scriptSetup.content}`,
        metadata: { language: 'typescript', type: 'component' },
      });
    }

    if (sfc.descriptor.template) {
      chunks.push({
        filePath,
        chunkIndex: index++,
        content: `<!-- Vue 3 Template -->\n${sfc.descriptor.template.content}`,
        metadata: { language: 'html', type: 'component' },
      });
    }

    if (chunks.length === 0) {
      return parseGenericText(filePath, content);
    }
  } catch (err) {
    return parseGenericText(filePath, content);
  }

  return chunks;
}

function parseTypeScriptCode(filePath: string, content: string, maxChunkSize: number = 800): CodeChunk[] {
  const lines = content.split('\n');
  const chunks: CodeChunk[] = [];
  let currentChunk: string[] = [];
  let currentLength = 0;
  let chunkIndex = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    currentChunk.push(line);
    currentLength += line.length;

    if (currentLength >= maxChunkSize || i === lines.length - 1) {
      chunks.push({
        filePath,
        chunkIndex: chunkIndex++,
        content: currentChunk.join('\n'),
        metadata: { language: 'typescript', type: 'general' },
      });
      currentChunk = [];
      currentLength = 0;
    }
  }

  return chunks;
}

function parseGenericText(filePath: string, content: string, maxChunkSize: number = 1000): CodeChunk[] {
  const lines = content.split('\n');
  const chunks: CodeChunk[] = [];
  let currentChunk: string[] = [];
  let currentLength = 0;
  let chunkIndex = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    currentChunk.push(line);
    currentLength += line.length;

    if (currentLength >= maxChunkSize || i === lines.length - 1) {
      chunks.push({
        filePath,
        chunkIndex: chunkIndex++,
        content: currentChunk.join('\n'),
        metadata: { language: 'text', type: 'general' },
      });
      currentChunk = [];
      currentLength = 0;
    }
  }

  return chunks;
}
