/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_USE_MOCK: string
  // Optional: resolved in src/lib/api-config.ts. Required for production
  // builds (fail-fast), optional in development (localhost fallback).
  readonly VITE_API_BASE_URL?: string
  readonly VITE_DEBUG: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
