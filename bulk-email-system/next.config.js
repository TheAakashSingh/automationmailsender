/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  // Server Actions are enabled by default in Next.js 14
  webpack: (config, { isServer }) => {
    // Ensure @ alias resolves correctly
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
    }
    
    // Ensure proper module resolution
    config.resolve.modules = [
      path.resolve(__dirname, 'node_modules'),
      'node_modules',
    ]
    
    return config
  },
  // Ensure TypeScript paths are resolved
  typescript: {
    ignoreBuildErrors: false,
  },
  // Ensure ESLint doesn't block builds
  eslint: {
    ignoreDuringBuilds: false,
  },
}

module.exports = nextConfig

