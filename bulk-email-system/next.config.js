/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  webpack: (config, { isServer, webpack }) => {
    // Use __dirname for more reliable path resolution in webpack
    const rootPath = path.resolve(__dirname)
    
    // CRITICAL: Set @ alias BEFORE any other resolution
    // This must be done first to ensure Vercel resolves paths correctly
    if (!config.resolve) {
      config.resolve = {}
    }
    
    if (!config.resolve.alias) {
      config.resolve.alias = {}
    }
    
    // Explicitly override @ alias - this is critical for Vercel
    config.resolve.alias['@'] = rootPath
    
    // Also set as object property (some webpack versions need this)
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': rootPath,
    }
    
    // Ensure extensions include TypeScript
    if (!config.resolve.extensions) {
      config.resolve.extensions = []
    }
    const extensions = new Set([
      ...config.resolve.extensions,
      '.ts',
      '.tsx',
      '.js',
      '.jsx',
    ])
    config.resolve.extensions = Array.from(extensions)
    
    return config
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
}

module.exports = nextConfig

