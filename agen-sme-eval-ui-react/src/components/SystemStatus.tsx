import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Server, Users, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { evaluationAPI } from '../services/api';
import { SystemHealth } from '../types/evaluation';

const SystemStatus: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        setIsLoading(true);
        const healthData = await evaluationAPI.getHealth();
        setHealth(healthData);
        setError(null);
      } catch (err) {
        setError('Failed to fetch system status');
        console.error('Health check failed:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center space-x-3">
          <div className="w-4 h-4 border-2 border-nvidia-green border-t-transparent rounded-full animate-spin"></div>
          <span className="text-gray-300">Checking system status...</span>
        </div>
      </div>
    );
  }

  if (error || !health) {
    return (
      <div className="card border-red-500/50 bg-red-500/5">
        <div className="flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span className="text-red-400">System status unavailable</span>
        </div>
      </div>
    );
  }

  const statusItems = [
    {
      icon: Server,
      label: 'System Status',
      value: health.status === 'healthy' ? 'Online' : 'Offline',
      color: health.status === 'healthy' ? 'text-green-400' : 'text-red-400',
      bgColor: health.status === 'healthy' ? 'bg-green-400/20' : 'bg-red-400/20',
    },
    {
      icon: Users,
      label: 'Active Evaluations',
      value: `${health.active_evaluations}/${health.max_concurrent_evaluations}`,
      color: 'text-nvidia-green',
      bgColor: 'bg-nvidia-green/20',
    },
    {
      icon: Activity,
      label: 'Model Provider',
      value: health.model_provider.toUpperCase(),
      color: 'text-blue-400',
      bgColor: 'bg-blue-400/20',
    },
    {
      icon: Clock,
      label: 'Timeout',
      value: `${health.evaluation_timeout}s`,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-400/20',
    },
  ];

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center space-x-3 mb-4">
        <div className="flex items-center justify-center w-8 h-8 bg-nvidia-green/20 rounded-lg">
          <Activity className="w-4 h-4 text-nvidia-green" />
        </div>
        <h3 className="text-lg font-semibold text-gray-100">System Status</h3>
        <div className="flex items-center space-x-1 ml-auto">
          {health.status === 'healthy' ? (
            <CheckCircle className="w-4 h-4 text-green-400" />
          ) : (
            <AlertCircle className="w-4 h-4 text-red-400" />
          )}
          <span className={`text-sm font-medium ${
            health.status === 'healthy' ? 'text-green-400' : 'text-red-400'
          }`}>
            {health.status === 'healthy' ? 'Healthy' : 'Unhealthy'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statusItems.map((item, index) => (
          <motion.div
            key={item.label}
            className={`p-4 rounded-lg ${item.bgColor} border border-gray-700`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <div className="flex items-center space-x-2 mb-2">
              <item.icon className={`w-4 h-4 ${item.color}`} />
              <span className="text-sm text-gray-400">{item.label}</span>
            </div>
            <div className={`text-lg font-semibold ${item.color}`}>
              {item.value}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Available Agents:</span>
          <div className="flex space-x-2">
            {health.agents.map((agent, index) => (
              <span
                key={agent}
                className="px-2 py-1 bg-nvidia-green/20 text-nvidia-green rounded text-xs font-medium"
              >
                {agent}
              </span>
            ))}
          </div>
        </div>
        <div className="flex items-center justify-between text-sm mt-2">
          <span className="text-gray-400">Version:</span>
          <span className="text-gray-300 font-mono">{health.version}</span>
        </div>
      </div>
    </motion.div>
  );
};

export default SystemStatus;
