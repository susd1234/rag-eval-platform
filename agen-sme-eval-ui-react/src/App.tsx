import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import EvaluationForm from './components/EvaluationForm';
import ResultsDisplay from './components/ResultsDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import SystemStatus from './components/SystemStatus';
import { EvaluationRequest, EvaluationResponse } from './types/evaluation';
import { evaluationAPI } from './services/api';

function App() {
  const [results, setResults] = useState<EvaluationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEvaluationSubmit = async (request: EvaluationRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      setResults(null);

      const response = await evaluationAPI.evaluate(request);
      setResults(response);
    } catch (err: any) {
      console.error('Evaluation failed:', err);
      setError(err.response?.data?.detail || err.message || 'Evaluation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewEvaluation = () => {
    setResults(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-dark-primary">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AnimatePresence mode="wait">
          {!results && !isLoading && (
            <motion.div
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="space-y-8"
            >
              {/* Hero Section */}
              <div className="text-center mb-12">
                <motion.h1
                  className="text-4xl md:text-6xl font-bold text-gray-100 mb-6"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8 }}
                >
                  AI Assisted SME Evaluation
                  <span className="block text-gradient">Application</span>
                </motion.h1>
                <motion.p
                  className="text-xl text-gray-400 max-w-3xl mx-auto leading-relaxed"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8, delay: 0.2 }}
                >
                  Advanced multi-agent system for evaluating AI responses across accuracy, 
                  hallucination detection, authoritativeness, and usefulness metrics.
                </motion.p>
              </div>

              {/* System Status */}
              <SystemStatus />

              {/* Error Display */}
              {error && (
                <motion.div
                  className="card border-red-500/50 bg-red-500/5"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-5 h-5 border-2 border-red-400 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-red-400 font-medium">Error: {error}</span>
                  </div>
                </motion.div>
              )}

              {/* Evaluation Form */}
              <EvaluationForm onSubmit={handleEvaluationSubmit} isLoading={isLoading} />
            </motion.div>
          )}

          {isLoading && (
            <motion.div
              key="loading"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              <LoadingSpinner />
            </motion.div>
          )}

          {results && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="space-y-8"
            >
              {/* Back Button */}
              <div className="flex justify-start">
                <motion.button
                  onClick={handleNewEvaluation}
                  className="btn-secondary flex items-center space-x-2"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                  <span>New Evaluation</span>
                </motion.button>
              </div>

              {/* Results */}
              <ResultsDisplay results={results} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="bg-dark-secondary border-t border-gray-800 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-gray-400">
              AI SME Evaluation Platform - Powered by Multi-Agent Architecture
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Built with React, TypeScript, and Tailwind CSS
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
