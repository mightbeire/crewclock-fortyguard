import { build } from 'vite'

await build()
await build({ configFile: 'vite.config.site.ts' })

