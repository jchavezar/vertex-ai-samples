import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8011/api/:path*',
        },
        {
          source: '/mcp/:path*',
          destination: 'http://localhost:8011/mcp/:path*',
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
