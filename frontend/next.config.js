// next.config.mjs

const { redirects } = require('next/dist/next-server/server/api-utils');
const nextConfig = {
  async redirects() {
    return [
      {
        source: '/',
        destination: '/home',
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
