import type { NextConfig } from "next";

// Stamp the build time so the client can detect stale bundles without relying
// solely on the SW update cycle. Exposed as NEXT_PUBLIC_BUILD_HASH.
process.env.NEXT_PUBLIC_BUILD_HASH = String(Date.now());

const nextConfig: NextConfig = {
  output: "standalone",
  // Raise the proxy body buffer ceiling so multipart uploads from modern
  // phone cameras (often 5-10MB) are not silently truncated. The
  // per-route /api/profile/photo/upload still enforces its own MAX_BYTES.
  experimental: {
    proxyClientMaxBodySize: "15mb",
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "flagcdn.com" },
      { protocol: "https", hostname: "r2.thesportsdb.com" },
      { protocol: "https", hostname: "a.espncdn.com" },
    ],
  },
  async headers() {
    return [
      {
        source: "/sw.js",
        headers: [
          { key: "Content-Type", value: "application/javascript; charset=utf-8" },
          { key: "Cache-Control", value: "no-cache, no-store, must-revalidate" },
        ],
      },
    ];
  },
};

export default nextConfig;
