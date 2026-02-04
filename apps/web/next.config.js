/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  i18n: {
    locales: ['en', 'zh-CN', 'es', 'fr', 'de', 'ja', 'ko', 'ar'],
    defaultLocale: 'en',
    localeDetection: true
  },
  experimental: {
    serverActions: true
  },
  images: {
    domains: ['localhost'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_CMS_URL: process.env.NEXT_PUBLIC_CMS_URL,
  }
};

module.exports = nextConfig;
