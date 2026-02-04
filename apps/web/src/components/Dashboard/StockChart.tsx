'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface StockData {
  date: string;
  price: number;
  volume: number;
}

export default function StockChart() {
  const [data, setData] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Generate sample data
    const generateData = () => {
      const result = [];
      const today = new Date();

      for (let i = 30; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);

        result.push({
          date: date.toISOString().split('T')[0],
          price: Math.random() * 50 + 100,
          volume: Math.random() * 1000000 + 500000,
        });
      }

      return result;
    };

    setData(generateData());
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="h-64 bg-gray-200 animate-pulse rounded" />;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
        />
        <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
        <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
        <Tooltip
          labelFormatter={(value) => new Date(value).toLocaleDateString()}
          formatter={(value: number, name: string) => [
            name === 'price' ? `$${value.toFixed(2)}` : value.toLocaleString(),
            name === 'price' ? 'Price' : 'Volume'
          ]}
        />
        <Legend />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="price"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
          name="Price"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
