/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: '/',
          destination: '/home',
        },
      ],
      afterFiles: [
        {
          source: '/:path*',
          destination: '/home',
        },
      ],
    };
  },
};

module.exports = nextConfig;
