import Link from 'next/link';
import { ArrowRight, Book, Code, Database, Globe } from 'lucide-react';

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-br from-primary-600 to-blue-700 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">Documentation</h1>
          <p className="text-xl md:text-2xl mb-8 text-blue-100">
            Complete guide to building with HDCP Platform
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-16">
        {/* Quick Start */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Quick Start</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Link href="/docs/setup" className="card-hover group">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-primary-50 rounded-lg group-hover:bg-primary-100 transition-colors">
                  <Book className="h-8 w-8 text-primary-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Setup Guide</h3>
                  <p className="text-gray-600">
                    Get up and running in minutes with our step-by-step installation guide
                  </p>
                </div>
              </div>
            </Link>

            <Link href="/docs/deployment" className="card-hover group">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-green-50 rounded-lg group-hover:bg-green-100 transition-colors">
                  <Database className="h-8 w-8 text-green-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Deployment</h3>
                  <p className="text-gray-600">
                    Deploy to production with Docker and our cloud-ready configuration
                  </p>
                </div>
              </div>
            </Link>
          </div>
        </section>

        {/* API Documentation */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">API Reference</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Link href="/docs/api/stocks" className="card-hover group">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                  <Code className="h-8 w-8 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Stock Prices</h3>
                  <p className="text-gray-600">REST API endpoints for stock price data</p>
                </div>
              </div>
            </Link>

            <Link href="/docs/api/sensors" className="card-hover group">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-green-50 rounded-lg group-hover:bg-green-100 transition-colors">
                  <Code className="h-8 w-8 text-green-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">IoT Sensors</h3>
                  <p className="text-gray-600">API for sensor readings and metrics</p>
                </div>
              </div>
            </Link>

            <Link href="/docs/api/products" className="card-hover group">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-purple-50 rounded-lg group-hover:bg-purple-100 transition-colors">
                  <Code className="h-8 w-8 text-purple-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Products</h3>
                  <p className="text-gray-600">Product price tracking API</p>
                </div>
              </div>
            </Link>

            <Link href="/docs/api/carbon-credits" className="card-hover group">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-emerald-50 rounded-lg group-hover:bg-emerald-100 transition-colors">
                  <Code className="h-8 w-8 text-emerald-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Carbon Credits</h3>
                  <p className="text-gray-600">ESG and carbon credit tracking</p>
                </div>
              </div>
            </Link>

            <Link href="/docs/graphql" className="card-hover group">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-yellow-50 rounded-lg group-hover:bg-yellow-100 transition-colors">
                  <Code className="h-8 w-8 text-yellow-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">GraphQL</h3>
                  <p className="text-gray-600">Unified GraphQL API schema</p>
                </div>
              </div>
            </Link>
          </div>
        </section>

        {/* Scenarios */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Scenarios</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Pre-configured Scenarios</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <ArrowRight className="h-5 w-5 text-primary-600 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">Stock Price Monitoring</p>
                    <p className="text-sm text-gray-600">Real-time stock prices with technical indicators</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <ArrowRight className="h-5 w-5 text-primary-600 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">IoT Sensor Data</p>
                    <p className="text-sm text-gray-600">Device metrics with alerts and battery tracking</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <ArrowRight className="h-5 w-5 text-primary-600 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">E-commerce Price Tracking</p>
                    <p className="text-sm text-gray-600">Multi-platform price comparisons</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <ArrowRight className="h-5 w-5 text-primary-600 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">Carbon Credit Tracking</p>
                    <p className="text-sm text-gray-600">ESG compliance and environmental impact</p>
                  </div>
                </li>
              </ul>
            </div>

            <div className="card">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Features</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <Globe className="h-5 w-5 text-primary-600 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">Multi-language Support</p>
                    <p className="text-sm text-gray-600">8 languages with RTL support</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <Database className="h-5 w-5 text-primary-600 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">Flexible Configuration</p>
                    <p className="text-sm text-gray-600">Enable/disable scenarios easily</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <Code className="h-5 w-5 text-primary-600 mt-1" />
                  <div>
                    <p className="font-medium text-gray-900">Production Ready</p>
                    <p className="text-sm text-gray-600">Docker, monitoring, and caching</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Tech Stack */}
        <section>
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Tech Stack</h2>
          <div className="card">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Backend</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>• FastAPI (Python)</li>
                  <li>• PostgreSQL 15</li>
                  <li>• SQLAlchemy 2.0</li>
                  <li>• Redis 7</li>
                  <li>• GraphQL</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Frontend</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>• Next.js 14</li>
                  <li>• TypeScript 5</li>
                  <li>• Tailwind CSS</li>
                  <li>• React Query</li>
                  <li>• Recharts</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">CMS</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>• Strapi 4</li>
                  <li>• GraphQL API</li>
                  <li>• i18n Plugin</li>
                  <li>• User Permissions</li>
                  <li>• Content Management</li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
