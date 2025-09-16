import React from 'react';
import { motion } from 'framer-motion';
import { 
  Trophy, 
  Target, 
  Shield, 
  BookOpen, 
  Star, 
  Clock, 
  Hash,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  XCircle,
  Info
} from 'lucide-react';
import { EvaluationResponse } from '../types/evaluation';

interface ResultsDisplayProps {
  results: EvaluationResponse;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  const getMetricIcon = (metric: string) => {
    switch (metric) {
      case 'Accuracy': return <Target className="w-5 h-5" />;
      case 'Hallucination': return <Shield className="w-5 h-5" />;
      case 'Authoritativeness': return <BookOpen className="w-5 h-5" />;
      case 'Usefulness': return <Star className="w-5 h-5" />;
      default: return <Info className="w-5 h-5" />;
    }
  };

  const getBadgeClass = (badge: string) => {
    switch (badge) {
      case 'Platinum': return 'metric-platinum';
      case 'Gold': return 'metric-gold';
      case 'Silver': return 'metric-silver';
      case 'Bronze': return 'metric-bronze';
      default: return 'metric-badge bg-gray-600 text-gray-100';
    }
  };

  const getRatingIcon = (rating: string) => {
    switch (rating) {
      case 'Great': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'Good': return <CheckCircle className="w-4 h-4 text-yellow-400" />;
      case 'Fair': return <AlertCircle className="w-4 h-4 text-orange-400" />;
      case 'Poor': return <XCircle className="w-4 h-4 text-red-400" />;
      default: return <Info className="w-4 h-4 text-gray-400" />;
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const metrics = [
    { key: 'accuracy', data: results.accuracy },
    { key: 'hallucination', data: results.hallucination },
    { key: 'authoritativeness', data: results.authoritativeness },
    { key: 'usefulness', data: results.usefulness },
  ].filter(metric => metric.data);

  return (
    <motion.div
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Overall Results */}
      <motion.div variants={itemVariants} className="card">
        <div className="flex items-center space-x-3 mb-4">
          <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-nvidia-green to-nvidia-green-dark rounded-lg">
            <Trophy className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-100">Overall Evaluation</h2>
            <p className="text-gray-400">Comprehensive assessment results</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-4xl font-bold text-gradient mb-2">
              {results.overall.overall_score.toFixed(1)}
            </div>
            <div className="text-gray-400">Overall Score</div>
          </div>
          <div className="text-center">
            <div className={`metric-badge ${getBadgeClass(results.overall.overall_badge)} text-lg px-4 py-2 mb-2`}>
              {results.overall.overall_badge}
            </div>
            <div className="text-gray-400">Badge</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 text-xl font-semibold text-gray-100 mb-2">
              {getRatingIcon(results.overall.overall_rating)}
              <span>{results.overall.overall_rating}</span>
            </div>
            <div className="text-gray-400">Rating</div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-dark-tertiary rounded-lg">
          <h3 className="font-semibold text-gray-100 mb-2">Summary</h3>
          <p className="text-gray-300 leading-relaxed">{results.overall.summary}</p>
        </div>
      </motion.div>

      {/* Individual Metrics */}
      <motion.div variants={itemVariants} className="card">
        <h3 className="text-xl font-bold text-gray-100 mb-6">Individual Metrics</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {metrics.map((metric) => (
            <motion.div
              key={metric.key}
              className="p-6 bg-dark-tertiary rounded-lg border border-gray-700"
              variants={itemVariants}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="flex items-center justify-center w-10 h-10 bg-nvidia-green/20 rounded-lg">
                  {getMetricIcon(metric.data!.metric)}
                </div>
                <div>
                  <h4 className="font-semibold text-gray-100">{metric.data!.metric}</h4>
                  <div className="flex items-center space-x-2">
                    <span className={`metric-badge ${getBadgeClass(metric.data!.badge)}`}>
                      {metric.data!.badge}
                    </span>
                    <span className="text-sm text-gray-400">
                      Score: {metric.data!.score}/3
                    </span>
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <div className="flex items-center space-x-2 mb-2">
                  {getRatingIcon(metric.data!.rating)}
                  <span className="font-medium text-gray-100">{metric.data!.rating}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-nvidia-green to-nvidia-green-light h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${(metric.data!.score / 3) * 100}%` }}
                  ></div>
                </div>
              </div>

              <div className="text-sm text-gray-300 leading-relaxed">
                {metric.data!.reasoning}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Evaluation Details */}
      <motion.div variants={itemVariants} className="card">
        <h3 className="text-xl font-bold text-gray-100 mb-4">Evaluation Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3 p-4 bg-dark-tertiary rounded-lg">
            <Hash className="w-5 h-5 text-nvidia-green" />
            <div>
              <div className="text-sm text-gray-400">Evaluation ID</div>
              <div className="font-mono text-sm text-gray-100">{results.evaluation_id}</div>
            </div>
          </div>
          <div className="flex items-center space-x-3 p-4 bg-dark-tertiary rounded-lg">
            <Clock className="w-5 h-5 text-nvidia-green" />
            <div>
              <div className="text-sm text-gray-400">Processing Time</div>
              <div className="font-semibold text-gray-100">{results.processing_time.toFixed(2)}s</div>
            </div>
          </div>
          <div className="flex items-center space-x-3 p-4 bg-dark-tertiary rounded-lg">
            <TrendingUp className="w-5 h-5 text-nvidia-green" />
            <div>
              <div className="text-sm text-gray-400">Metrics Evaluated</div>
              <div className="font-semibold text-gray-100">{metrics.length}</div>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ResultsDisplay;
