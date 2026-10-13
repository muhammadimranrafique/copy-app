/**
 * Central API base-URL resolution.
 *
 * Rules:
 * - Development: falls back to http://127.0.0.1:8080/api/v1 so the Vite dev
 *   server works out of the box.
 * - Production: VITE_API_BASE_URL MUST be provided (Vercel project env var,
 *   build-time). If it is missing the app fails fast with a clear error
 *   instead of silently calling localhost or a stale host.
 *
 * The value is baked in at build time by Vite. It is NOT a secret and must
 * never contain credentials.
 */
const envBase = import.meta.env.VITE_API_BASE_URL?.trim();

if (import.meta.env.PROD && !envBase) {
  throw new Error(
    'VITE_API_BASE_URL is not configured for this production build. ' +
      'Set it in the Vercel project settings (Settings -> Environment Variables), ' +
      'e.g. VITE_API_BASE_URL=https://api.example.com/api/v1, then redeploy. ' +
      'The app refuses to run with an undefined production API endpoint.'
  );
}

export const API_BASE = envBase || 'http://127.0.0.1:8080/api/v1';
