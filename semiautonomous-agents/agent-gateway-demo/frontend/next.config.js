/** @type {import('next').NextConfig} */
module.exports = {
  reactStrictMode: true,
  experimental: { serverActions: { allowedOrigins: ["*"] } },
  // Cloud Run sets PORT; Next reads from process.env at start
};
