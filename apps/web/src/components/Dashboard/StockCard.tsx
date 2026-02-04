'use client';

import { TrendingUp, TrendingDown } from 'lucide-react';
import { StockPrice } from '@/lib/api';
import { formatPrice, formatNumber } from '@/lib/api';

/**
 * Stock Card Component
 * Displays individual stock information
 */
interface StockCardProps {
  stock: StockPrice;
}

export default function StockCard({ stock }: StockCardProps) {
  const isPositive = (stock.price_change || 0) >= 0;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">{stock.symbol}</h3>
          <p className="text-sm text-gray-500 mt-1">
            {stock.source || 'Market Data'}
          </p>
        </div>
        <div className={`flex items-center gap-1 px-3 py-1 rounded-full ${
          isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
          <span className="text-sm font-medium">
            {isPositive ? '+' : ''}{stock.price_change_percent?.toFixed(2)}%
          </span>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-sm text-gray-600">Current Price</p>
          <p className="text-3xl font-bold text-gray-900">
            ${formatPrice(stock.price)}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
          <div>
            <p className="text-xs text-gray-500">Change</p>
            <p className={`text-sm font-semibold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? '+' : ''}${stock.price_change?.toFixed(2) || '0.00'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Volume</p>
            <p className="text-sm font-semibold text-gray-900">
              {formatNumber(stock.volume)}
            </p>
          </div>
        </div>

        <div className="pt-2">
          <p className="text-xs text-gray-400">
            Updated: {new Date(stock.timestamp).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
}
