import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    ssr: 'scripts/site_worker_entry.ts',
    outDir: 'dist/server',
    emptyOutDir: false,
    rollupOptions: { output: { entryFileNames: 'index.js', format: 'es' } },
  },
})

