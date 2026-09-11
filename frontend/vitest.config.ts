import path from 'node:path'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

const frontendDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(frontendDir, '..')

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    root: repoRoot,
    include: ['tests/frontend/**/*.{test,spec}.{ts,tsx}'],
  },
  server: {
    fs: {
      allow: [repoRoot],
    },
  },
})
