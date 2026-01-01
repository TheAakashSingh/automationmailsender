/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  webpack: (config) => {
    // Explicitly resolve @ alias to project root
    const rootPath = path.resolve(process.cwd())
    
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      '@': rootPath,
    }
    
    // Ensure proper module resolution order
    config.resolve.modules = [
      ...(config.resolve.modules || []),
      path.resolve(rootPath, 'node_modules'),
      'node_modules',
    ]
    
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

