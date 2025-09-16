import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Zap, Target, Shield } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  message = "Evaluating your AI response..." 
}) => {
  const agents = [
    { icon: Target, name: "Accuracy Agent", color: "text-blue-400" },
    { icon: Shield, name: "Hallucination Agent", color: "text-red-400" },
    { icon: Brain, name: "Authoritativeness Agent", color: "text-purple-400" },
    { icon: Zap, name: "Usefulness Agent", color: "text-yellow-400" },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.6,
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const pulseVariants = {
    pulse: {
      scale: [1, 1.1, 1],
      opacity: [0.7, 1, 0.7],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut" as const,
      },
    },
  };

  return (
    <motion.div
      className="card max-w-2xl mx-auto text-center"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div
        className="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-nvidia-green to-nvidia-green-dark rounded-full mx-auto mb-6"
        variants={pulseVariants}
        animate="pulse"
      >
        <Brain className="w-10 h-10 text-white" />
      </motion.div>

      <motion.h2 
        className="text-2xl font-bold text-gray-100 mb-2"
        variants={itemVariants}
      >
        AI Agents at Work
      </motion.h2>
      
      <motion.p 
        className="text-gray-400 mb-8"
        variants={itemVariants}
      >
        {message}
      </motion.p>

      <div className="grid grid-cols-2 gap-4 mb-8">
        {agents.map((agent, index) => (
          <motion.div
            key={agent.name}
            className="flex items-center space-x-3 p-4 bg-dark-tertiary rounded-lg"
            variants={itemVariants}
            whileHover={{ scale: 1.05 }}
          >
            <div className="relative">
              <agent.icon className={`w-6 h-6 ${agent.color}`} />
              <motion.div
                className="absolute inset-0 w-6 h-6 border-2 border-nvidia-green rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              />
            </div>
            <div className="text-left">
              <div className="text-sm font-medium text-gray-100">{agent.name}</div>
              <div className="text-xs text-gray-400">Analyzing...</div>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="flex items-center justify-center space-x-2 text-nvidia-green"
        variants={itemVariants}
      >
        <div className="w-2 h-2 bg-nvidia-green rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-nvidia-green rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-2 h-2 bg-nvidia-green rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </motion.div>

      <motion.p 
        className="text-sm text-gray-500 mt-4"
        variants={itemVariants}
      >
        This may take 10-30 seconds depending on response complexity
      </motion.p>
    </motion.div>
  );
};

export default LoadingSpinner;
