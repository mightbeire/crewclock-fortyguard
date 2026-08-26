import { build } from 'vite'

await build({
  configFile: false,
  build: {
    ssr: 'scripts/decision_runtime_entry.ts',
    outDir: 'build',
    emptyOutDir: false,
    rollupOptions: { output: { entryFileNames: 'decision-runtime.mjs' } },
  },
})
