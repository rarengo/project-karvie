# Vue 3 & TypeScript Coding Standards - Project Karvie

## 1. Component Rules
- Always use `<script setup lang="ts">` pattern.
- Use explicit Type definitions for all Props & Emits.
- Keep components small (<200 lines). Extract sub-components when complex.
- Do NOT use inline style tags; use external/scoped CSS tokens.

## 2. API & Service Rules
- Use `Axios` or `fetch` wrapped in strongly typed API services.
- Always implement explicit error try/catch blocks with log reporting.
- Use Pinia for state management when data is shared across multiple views.

## 3. Node.js & Express API Rules
- Always validate input schemas using `zod` or `joi`.
- Controllers must be decoupled from Business Logic services.
- All async handlers must pass unhandled errors to the global error middleware.
