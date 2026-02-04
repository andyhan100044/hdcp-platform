import { Suspense } from 'react';
import DashboardStats from '@/components/Dashboard/DashboardStats';
import StockChart from '@/components/Dashboard/StockChart';
import SensorTable from '@/components/Dashboard/SensorTable';
import ProductCard from '@/components/Dashboard/ProductCard';
import CarbonCard from '@/components/Dashboard/CarbonCard';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome to your data platform overview</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Grid */}
        <Suspense fallback={<div className="h-32 bg-gray-200 animate-pulse rounded-lg" />}>
          <DashboardStats />
        </Suspense>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
          <Link
            href="/dashboard/stocks"
            className="card-hover group bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-lg"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">Stock Prices</h3>
                <p className="text-blue-100 text-sm">Monitor market data</p>
              </div>
              <ArrowUpRight className="h-6 w-6 text-blue-200 group-hover:text-white transition-colors" />
            </div>
          </Link>

          <Link
            href="/dashboard/sensors"
            className="card-hover group bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-lg"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">IoT Sensors</h3>
                <p className="text-green-100 text-sm">Track device metrics</p>
              </div>
              <ArrowUpRight className="h-6 w-6 text-green-200 group-hover:text-white transition-colors" />
            </div>
          </Link>

          <Link
            href="/dashboard/products"
            className="card-hover group bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-lg"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">Product Prices</h3>
                <p className="text-purple-100 text-sm">Compare marketplace</p>
              </div>
              <ArrowUpRight className="h-6 w-6 text-purple-200 group-hover:text-white transition-colors" />
            </div>
          </Link>

          <Link
            href="/dashboard/carbon-credits"
            className="card-hover group bg-gradient-to-br from-emerald-500 to-emerald-600 text-white p-6 rounded-lg"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">Carbon Credits</h3>
                <p className="text-emerald-100 text-sm">ESG tracking</p>
              </div>
              <ArrowUpRight className="h-6 w-6 text-emerald-200 group-hover:text-white transition-colors" />
            </div>
          </Link>
        </div>

        {/* Charts and Tables Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
          {/* Stock Chart */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Stock Price Trend</h2>
              <Link href="/dashboard/stocks" className="text-sm text-primary-600 hover:text-primary-700">
                View All
              </Link>
            </div>
            <Suspense fallback={<div className="h-64 bg-gray-200 animate-pulse rounded" />}>
              <StockChart />
            </Suspense>
          </div>

          {/* Recent Sensor Readings */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Recent Sensors</h2>
              <Link href="/dashboard/sensors" className="text-sm text-primary-600 hover:text-primary-700">
                View All
              </Link>
            </div>
            <Suspense fallback={<div className="h-64 bg-gray-200 animate-pulse rounded" />}>
              <SensorTable limit={5} />
            </Suspense>
          </div>
        </div>

        {/* Products and Carbon Credits */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
          {/* Product Card */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Tracked Products</h2>
              <Link href="/dashboard/products" className="text-sm text-primary-600 hover:text-primary-700">
                View All
              </Link>
            </div>
            <Suspense fallback={<div className="h-48 bg-gray-200 animate-pulse rounded" />}>
              <ProductCard />
            </Suspense>
          </div>

          {/* Carbon Credit Card */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Carbon Credits</h2>
              <Link href="/dashboard/carbon-credits" className="text-sm text-primary-600 hover:text-primary-700">
                View All
              </Link>
            </div>
            <Suspense fallback={<div className="h-48 bg-gray-200 animate-pulse rounded" />}>
              <CarbonCard />
            </Suspense>
          </div>
        </div>
      </div>
    </div>
  );
}
