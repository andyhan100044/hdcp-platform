'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface Product {
  id: string;
  product_id: string;
  product_name: string;
  price: number;
  currency: string;
  availability: 'in_stock' | 'out_of_stock';
  source: string;
  timestamp: string;
}

export default function ProductCard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get('/api/products');
        setProducts(response.data?.slice(0, 3) || []);
      } catch (error) {
        console.error('Error fetching products:', error);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-20 bg-gray-200 animate-pulse rounded" />
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
        <p>No products tracked yet</p>
        <p className="text-sm mt-1">Start tracking prices to see insights</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {products.map((product) => (
        <div
          key={product.id}
          className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors"
        >
          <div className="flex items-start justify-between mb-2">
            <h3 className="font-medium text-gray-900 flex-1">{product.product_name}</h3>
            <span
              className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                product.availability === 'in_stock'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {product.availability === 'in_stock' ? 'In Stock' : 'Out of Stock'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {product.currency} {product.price.toFixed(2)}
              </p>
              <p className="text-sm text-gray-500 mt-1">{product.source}</p>
            </div>

            <div className="flex items-center text-green-600">
              <TrendingUp className="h-4 w-4 mr-1" />
              <span className="text-sm font-medium">+2.4%</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
