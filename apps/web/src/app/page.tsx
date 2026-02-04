import Link from 'next/link';
import { ArrowRight, BarChart3, Cpu, ShoppingCart, Leaf } from 'lucide-react';

export default function Home() {
  const features = [
    {
      icon: <BarChart3 className="h-8 w-8 text-primary-600" />,
      title: 'Stock Price Monitoring',
      description: 'Real-time stock prices, historical data, and technical indicators for financial platforms.',
      link: '/stocks',
    },
    {
      icon: <Cpu className="h-8 w-8 text-primary-600" />,
      title: 'IoT Sensor Data',
      description: 'Monitor sensors with real-time alerts and battery tracking for smart buildings.',
      link: '/sensors',
    },
    {
      icon: <ShoppingCart className="h-8 w-8 text-primary-600" />,
      title: 'E-commerce Price Tracking',
      description: 'Track product prices across platforms with smart alerts and comparisons.',
      link: '/products',
    },
    {
      icon: <Leaf className="h-8 w-8 text-primary-600" />,
      title: 'Carbon Credit Tracking',
      description: 'Monitor environmental impact and carbon credits with ESG compliance.',
      link: '/carbon-credits',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 to-blue-700 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            HDCP Platform
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-blue-100">
            Universal Data Platform Template
          </p>
          <p className="text-lg mb-10 text-blue-50 max-w-3xl mx-auto">
            Build data-driven applications 10x faster with our production-ready template.
            Support for 8 languages, 4 scenarios, and modern tech stack.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/dashboard"
              className="bg-white text-primary-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-50 transition-colors inline-flex items-center justify-center gap-2"
            >
              View Dashboard
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="/docs"
              className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-primary-600 transition-colors inline-flex items-center justify-center"
            >
              Documentation
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Supported Scenarios
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Choose from pre-configured scenarios or combine multiple data types
              to build your perfect data platform.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <Link
                key={index}
                href={feature.link}
                className="card-hover group"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-primary-50 rounded-lg group-hover:bg-primary-100 transition-colors">
                    {feature.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600">
                      {feature.description}
                    </p>
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-primary-600 transition-colors mt-1" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Modern Tech Stack
            </h2>
            <p className="text-xl text-gray-600">
              Built with the latest and most reliable technologies
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 p-4 rounded-lg inline-block mb-4">
                <BarChart3 className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Backend</h3>
              <p className="text-gray-600 mb-2">FastAPI + PostgreSQL</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Async SQLAlchemy 2.0</li>
                <li>• Redis Caching</li>
                <li>• GraphQL API</li>
                <li>• Prometheus Metrics</li>
              </ul>
            </div>

            <div className="text-center">
              <div className="bg-green-100 p-4 rounded-lg inline-block mb-4">
                <Cpu className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Frontend</h3>
              <p className="text-gray-600 mb-2">Next.js + TypeScript</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• 8 Languages</li>
                <li>• Tailwind CSS</li>
                <li>• Server-side Rendering</li>
                <li>• SEO Optimized</li>
              </ul>
            </div>

            <div className="text-center">
              <div className="bg-purple-100 p-4 rounded-lg inline-block mb-4">
                <ShoppingCart className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">CMS</h3>
              <p className="text-gray-600 mb-2">Strapi + GraphQL</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Multi-language Content</li>
                <li>• User Permissions</li>
                <li>• GraphQL API</li>
                <li>• Headless CMS</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-600 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Build Your Data Platform?
          </h2>
          <p className="text-xl mb-8 text-blue-100 max-w-2xl mx-auto">
            Clone the template, configure your scenario, and deploy in minutes.
            Production-ready with Docker, monitoring, and SSL.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/dashboard"
              className="bg-white text-primary-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-50 transition-colors inline-flex items-center justify-center gap-2"
            >
              Get Started
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="/docs/setup"
              className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-primary-600 transition-colors"
            >
              Setup Guide
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
