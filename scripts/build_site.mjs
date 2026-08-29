import { build } from 'vite'
import { readFile, readdir, writeFile } from 'node:fs/promises'
import { join, relative } from 'node:path'

await build()
const assetFiles = []
const collect = async (directory) => {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) await collect(path)
    else {
      const relativePath = relative('dist', path).replaceAll('\\', '/')
      if (!relativePath.startsWith('server/') && relativePath !== 'site-assets.mjs') assetFiles.push(path)
    }
  }
}
await collect('dist')
const encoded = {}
for (const path of assetFiles) {
  const bytes = await readFile(path)
  const urlPath = `/${relative('dist', path).replaceAll('\\', '/')}`
  encoded[urlPath === '/index.html' ? '/' : urlPath] = { data: bytes.toString('base64'), contentType: urlPath.endsWith('.html') ? 'text/html; charset=utf-8' : urlPath.endsWith('.css') ? 'text/css; charset=utf-8' : urlPath.endsWith('.js') ? 'text/javascript; charset=utf-8' : urlPath.endsWith('.svg') ? 'image/svg+xml' : urlPath.endsWith('.woff2') ? 'font/woff2' : 'application/octet-stream' }
}
await writeFile('dist/site-assets.mjs', `export const SITE_ASSETS = ${JSON.stringify(encoded)}\n`)
await build({ configFile: 'vite.config.site.ts' })
