'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Activity, Battery, Wifi } from 'lucide-react';

interface Sensor {
  id: string;
  sensor_id: string;
  location: string;
  temperature: number;
  humidity: number;
  battery: number;
  signal: number;
  status: 'online' | 'offline';
  timestamp: string;
}

interface Props {
  limit?: number;
}

export default function SensorTable({ limit }: Props) {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSensors = async () => {
      try {
        const response = await api.get('/api/sensors');
        let data = response.data || [];

        if (limit) {
          data = data.slice(0, limit);
        }

        setSensors(data);
      } catch (error) {
        console.error('Error fetching sensors:', error);
        // Set empty array on error
        setSensors([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSensors();
  }, [limit]);

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-gray-200 animate-pulse rounded" />
        ))}
      </div>
    );
  }

  if (sensors.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Activity className="h-12 w-12 mx-auto mb-4 text-gray-300" />
        <p>No sensor data available</p>
        <p className="text-sm mt-1">Start by adding some sensors to your platform</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Sensor
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Location
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Temperature
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sensors.map((sensor) => (
            <tr key={sensor.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 whitespace-nowrap">
                <div className="flex items-center">
                  <Activity className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm font-medium text-gray-900">{sensor.sensor_id}</span>
                </div>
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {sensor.location}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                <div className="flex items-center">
                  <span className="font-medium">{sensor.temperature.toFixed(1)}°C</span>
                  <span className="text-gray-400 ml-2">{sensor.humidity.toFixed(0)}%</span>
                </div>
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                <div className="flex items-center space-x-2">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      sensor.status === 'online'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {sensor.status}
                  </span>
                  <div className="flex items-center text-gray-400">
                    <Battery className="h-4 w-4 mr-1" />
                    <span className="text-xs">{sensor.battery}%</span>
                  </div>
                  <div className="flex items-center text-gray-400">
                    <Wifi className="h-4 w-4 mr-1" />
                    <span className="text-xs">{sensor.signal}%</span>
                  </div>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
