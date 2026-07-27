import os
import re
from typing import List, Dict, Any


def chunk_file_content(file_path: str, content: str, max_chunk_size: int = 800) -> List[Dict[str, Any]]:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".vue":
        return parse_vue_sfc(file_path, content)
    
    return parse_generic_code(file_path, content, max_chunk_size)


def parse_vue_sfc(file_path: str, content: str) -> List[Dict[str, Any]]:
    chunks = []
    chunk_index = 0
    
    # Extract <script setup> or <script>
    script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if script_match:
        chunks.append({
            "filePath": file_path,
            "chunkIndex": chunk_index,
            "content": f"// Vue 3 Component Script\n{script_match.group(1).strip()}",
            "metadata": {"language": "typescript", "type": "component_script"}
        })
        chunk_index += 1

    # Extract <template>
    template_match = re.search(r'<template[^>]*>(.*?)</template>', content, re.DOTALL)
    if template_match:
        chunks.append({
            "filePath": file_path,
            "chunkIndex": chunk_index,
            "content": f"<!-- Vue 3 Template -->\n{template_match.group(1).strip()}",
            "metadata": {"language": "html", "type": "component_template"}
        })
        chunk_index += 1

    if not chunks:
        return parse_generic_code(file_path, content)
        
    return chunks


def parse_generic_code(file_path: str, content: str, max_chunk_size: int = 800) -> List[Dict[str, Any]]:
    lines = content.splitlines()
    chunks = []
    current_lines = []
    current_length = 0
    chunk_index = 0
    
    ext = os.path.splitext(file_path)[1].lower()
    lang_map = {
        ".ts": "typescript",
        ".js": "javascript",
        ".py": "python",
        ".json": "json",
        ".md": "markdown",
        ".sql": "sql"
    }
    language = lang_map.get(ext, "text")

    for line in lines:
        current_lines.append(line)
        current_length += len(line)
        
        if current_length >= max_chunk_size:
            chunks.append({
                "filePath": file_path,
                "chunkIndex": chunk_index,
                "content": "\n".join(current_lines),
                "metadata": {"language": language, "type": "generic_code"}
            })
            chunk_index += 1
            current_lines = []
            current_length = 0

    if current_lines:
        chunks.append({
            "filePath": file_path,
            "chunkIndex": chunk_index,
            "content": "\n".join(current_lines),
            "metadata": {"language": language, "type": "generic_code"}
        })

    return chunks
