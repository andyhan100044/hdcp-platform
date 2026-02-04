'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Plus, Search, Leaf, Globe } from 'lucide-react';

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
  additionality_score?: number;
  co_benefits_score?: number;
  timestamp: string;
}

export default function CarbonCreditsPage() {
  const [credits, setCredits] = useState<CarbonCredit[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchCredits = async () => {
      try {
        const response = await api.get('/api/carbon-credits');
        setCredits(response.data || []);
      } catch (error) {
        console.error('Error fetching carbon credits:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCredits();
  }, []);

  const filteredCredits = credits.filter(credit =>
    credit.project_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    credit.project_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    credit.standard.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Carbon Credits</h1>
              <p className="text-gray-600 mt-2">Monitor environmental impact and ESG compliance</p>
            </div>
            <button className="btn-primary inline-flex items-center gap-2">
              <Plus className="h-5 w-5" />
              Add Project
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Search and Filters */}
        <div className="card mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search projects..."
                className="input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <select className="input md:w-48">
              <option>All Standards</option>
              <option>VCS</option>
              <option>Gold Standard</option>
              <option>CDM</option>
              <option>ACR</option>
            </select>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Credits</p>
                <p className="text-3xl font-bold text-emerald-600 mt-2">
                  {credits.reduce((sum, c) => sum + c.total_credits, 0).toLocaleString()}
                </p>
              </div>
              <Globe className="h-12 w-12 text-emerald-600 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">CO₂ Offset</p>
                <p className="text-3xl font-bold text-emerald-600 mt-2">
                  {credits.reduce((sum, c) => sum + c.co2_offset, 0).toLocaleString()}t
                </p>
              </div>
              <Leaf className="h-12 w-12 text-emerald-600 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Projects</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{credits.length}</p>
              </div>
              <Globe className="h-12 w-12 text-blue-600 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Forest Area</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {credits.reduce((sum, c) => sum + (c.forest_area || 0), 0).toLocaleString()}ha
                </p>
              </div>
              <Leaf className="h-12 w-12 text-green-600 opacity-20" />
            </div>
          </div>
        </div>

        {/* Credits Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="card">
                <div className="h-64 bg-gray-200 animate-pulse rounded" />
              </div>
            ))}
          </div>
        ) : filteredCredits.length === 0 ? (
          <div className="card text-center py-12">
            <Leaf className="h-16 w-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No carbon credit projects</h3>
            <p className="text-gray-500 mb-4">
              {searchTerm ? 'Try a different search term' : 'Get started by adding your first project'}
            </p>
            {!searchTerm && (
              <button className="btn-primary">Add Project</button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCredits.map((credit) => (
              <div key={credit.id} className="card-hover">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{credit.project_name}</h3>
                    <p className="text-sm text-gray-500 mt-1">{credit.location}</p>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                    {credit.standard}
                  </span>
                </div>

                <div className="mb-4">
                  <p className="text-xs text-gray-500">Project Type</p>
                  <p className="text-sm font-medium text-gray-900 mt-1">{credit.project_type}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-gray-500">Total Credits</p>
                    <p className="text-xl font-bold text-emerald-600 mt-1">
                      {credit.total_credits.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">CO₂ Offset</p>
                    <p className="text-xl font-bold text-emerald-600 mt-1">
                      {credit.co2_offset.toLocaleString()}t
                    </p>
                  </div>
                </div>

                {credit.forest_area && (
                  <div className="mb-4 pt-4 border-t border-gray-100">
                    <p className="text-xs text-gray-500">Forest Area</p>
                    <p className="text-lg font-semibold text-gray-900 mt-1">{credit.forest_area} ha</p>
                  </div>
                )}

                {credit.communities && (
                  <div className="pt-4 border-t border-gray-100">
                    <p className="text-xs text-gray-500">Communities Benefited</p>
                    <p className="text-lg font-semibold text-gray-900 mt-1">{credit.communities}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
