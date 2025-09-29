import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync, existsSync } from 'fs'
import { join } from 'path'

// Custom plugin to copy routing files
const copyFilesPlugin = () => {
  return {
    name: 'copy-files',
    writeBundle() {
      const files = ['_redirects', '_headers', 'vercel.json']
      files.forEach(file => {
        const src = join(__dirname, 'public', file)
        const dest = join(__dirname, 'dist', file)
        if (existsSync(src)) {
          copyFileSync(src, dest)
          console.log(`Copied ${file} to dist folder`)
        }
      })
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), copyFilesPlugin()],
  server: {
    port: 5173,
    host: true
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined,
        // Add cache busting with content hashes
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
  base: '/'
})
