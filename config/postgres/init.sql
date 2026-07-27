-- Project Karvie DB Initialization Script
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Project Metadata Table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    repo_url VARCHAR(512),
    tech_stack JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Code & Documentation Vector Embeddings Table
CREATE TABLE IF NOT EXISTS project_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    file_path VARCHAR(1024) NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(768), -- Embedding dim for nomic-embed-text
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS project_embeddings_vector_idx 
ON project_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Agent Execution History & Long-Term Memory Table
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    task_prompt TEXT NOT NULL,
    execution_plan JSONB,
    result_summary TEXT,
    status VARCHAR(50) DEFAULT 'completed',
    embedding vector(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed Default Project Karvie
INSERT INTO projects (name, description, tech_stack)
VALUES (
    'Karvie',
    'Self-hosted AI software engineer and automation platform',
    '["Vue.js", "TypeScript", "Node.js", "Express", "PostgreSQL", "Docker", "vLLM", "LangGraph", "AWS"]'
) ON CONFLICT (name) DO NOTHING;
