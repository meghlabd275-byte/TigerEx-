/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker multi-stage builds
  output: 'standalone',
  // trailingSlash: true,
  images: {
    domains: [
      'localhost',
      'tigerex.com',
      'unsplash.com',
      'images.unsplash.com',
      'pexels.com',
      'pixabay.com',
      'giphy.com',
      'wikimedia.org',
      'placeholder.com',
    ],
  },
  // Enable image optimization
  experimental: {
    optimizePackageFonts: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:3001/api/:path*',
      },
    ];
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname, 'src'),
    };
    return config;
  },
};

module.exports = nextConfig;