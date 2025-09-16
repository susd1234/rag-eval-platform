import React from 'react';
import { Brain, Zap, Activity } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-dark-secondary border-b border-gray-800 sticky top-0 z-50 backdrop-blur-sm bg-opacity-95">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-nvidia-green to-nvidia-green-dark rounded-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient">
                RAG Evaluation Platform
              </h1>
              <p className="text-sm text-gray-400">
                Multi-Agent RAG Assessment System
              </p>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-sm">
              <div className="flex items-center space-x-1">
                <Activity className="w-4 h-4 text-nvidia-green" />
                <span className="text-gray-300">System</span>
              </div>
              <div className="w-2 h-2 bg-nvidia-green rounded-full animate-pulse"></div>
              <span className="text-gray-400">Online</span>
            </div>
            
            <div className="flex items-center space-x-2 text-sm">
              <Zap className="w-4 h-4 text-nvidia-green" />
              <span className="text-gray-300">Agents</span>
              <span className="text-nvidia-green font-medium">4 Active</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
