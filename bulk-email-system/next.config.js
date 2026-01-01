/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  // Server Actions are enabled by default in Next.js 14
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
    }
    return config
  },
}

module.exports = nextConfig

