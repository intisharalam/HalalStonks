// next.config.js

module.exports = {
  async rewrites() {
    const rewriteConfig = [
      {
        source: '/',
        destination: '/home', // Example destination for your Next.js routes
      },
    ];

    return rewriteConfig;
  },
};
