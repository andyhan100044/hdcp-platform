'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Leaf, Globe } from 'lucide-react';

interface CarbonCredit {
  id: string;
  project_id: string;
  project_name: string;
  standard: string;
  location: string;
  project_type: string;
  total_credits: number;
  co2_offset: number;
  forest_area?: number;
  communities?: number;
}

export default function CarbonCard() {
  const [credits, setCredits] = useState<CarbonCredit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCredits = async () => {
      try {
        const response = await api.get('/api/carbon-credits');
        setCredits(response.data?.slice(0, 3) || []);
      } catch (error) {
        console.error('Error fetching carbon credits:', error);
        setCredits([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCredits();
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-200 animate-pulse rounded" />
        ))}
      </div>
    );
  }

  if (credits.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Leaf className="h-12 w-12 mx-auto mb-4 text-gray-300" />
        <p>No carbon credit projects</p>
        <p className="text-sm mt-1">Track environmental impact with ESG data</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {credits.map((credit) => (
        <div
          key={credit.id}
          className="border border-gray-200 rounded-lg p-4 hover:border-emerald-300 transition-colors"
        >
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <h3 className="font-medium text-gray-900">{credit.project_name}</h3>
              <p className="text-sm text-gray-500 mt-1">{credit.location}</p>
            </div>
            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-emerald-100 text-emerald-800">
              {credit.standard}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 mt-3">
            <div className="flex items-center">
              <Globe className="h-4 w-4 text-emerald-600 mr-2" />
              <div>
                <p className="text-xs text-gray-500">Total Credits</p>
                <p className="text-lg font-semibold text-gray-900">
                  {credit.total_credits.toLocaleString()}
                </p>
              </div>
            </div>

            <div className="flex items-center">
              <Leaf className="h-4 w-4 text-emerald-600 mr-2" />
              <div>
                <p className="text-xs text-gray-500">CO₂ Offset</p>
                <p className="text-lg font-semibold text-gray-900">
                  {credit.co2_offset.toLocaleString()}t
                </p>
              </div>
            </div>
          </div>

          {credit.forest_area && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <p className="text-xs text-gray-500">
                Forest Area: <span className="font-medium text-gray-700">{credit.forest_area} ha</span>
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
