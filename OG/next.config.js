// next.config.js

module.exports = {
  async rewrites() {
    const rewriteConfig = [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:8000/api/:path*' // Local development URL
          : 'https://halal-stonks.vercel.app/api/:path*', // Replace with your actual FastAPI backend URL on Vercel
      },
      {
        source: '/',
        destination: '/home', // Example destination for your Next.js routes
      },
    ];

    return rewriteConfig;
  },
};
