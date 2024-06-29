/** @type {import('next').NextConfig} */

const nextConfig = {
    rewrites: async () => {
      return [
        {
            source: '/',
            destination: '/home',
        },
      ];
    },
  };
  
  module.exports = nextConfig;