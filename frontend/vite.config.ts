import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Fail safe: a production build must have an explicit API base URL.
  // Vercel provides VITE_API_BASE_URL as a build-time environment variable;
  // local production builds read it from .env / .env.production.
  const env = loadEnv(mode, process.cwd(), '')
  if (mode === 'production' && !env.VITE_API_BASE_URL) {
    throw new Error(
      'VITE_API_BASE_URL is required for production builds. ' +
        'Set it in the Vercel project settings (Settings -> Environment Variables), ' +
        'e.g. VITE_API_BASE_URL=https://api.example.com/api/v1, then redeploy.'
    )
  }

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    build: {
      target: 'esnext',
      cssCodeSplit: true,
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor-react': ['react', 'react-dom', 'react-router-dom'],
            'vendor-ui': ['@radix-ui/react-dialog', '@radix-ui/react-select', 'lucide-react', 'sonner'],
            'vendor-utils': ['@tanstack/react-query', 'date-fns', 'clsx', 'tailwind-merge'],
          },
        },
      },
      chunkSizeWarningLimit: 1000,
    },
  }
})
