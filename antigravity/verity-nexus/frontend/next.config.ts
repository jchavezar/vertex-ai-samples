import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8001/api/:path*',
      },
      {
        source: '/mcp/:path*',
        destination: 'https://mcp-ledger-toolbox-oyntfgdwsq-uc.a.run.app/mcp/:path*',
      },
    ];
  },
};

export default nextConfig;
