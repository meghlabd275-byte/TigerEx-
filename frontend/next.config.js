/**
 * TigerEx Next.js Configuration
 */
const nextConfig = {
  output: 'export',
  unoptimized: true,
  trailingSlash: true,
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
  webpack: (config) => {
    config.resolve.alias = { ...config.resolve.alias, '@': require('path').resolve(__dirname, 'src') };
    return config;
  },
};
module.exports = nextConfig;
