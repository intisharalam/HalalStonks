/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'development' 
          ? 'http://localhost:8000/api/:path*' // Local development URL for Django
          : 'https://halal-stonks.vercel.app/api/:path*', // Replace with your actual Django backend URL on Vercel
      },
      {
        source: '/',
        destination: '/home', // Example destination for your Next.js routes
      },
    ];
  },
};

export default nextConfig;
