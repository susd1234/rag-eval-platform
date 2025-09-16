import axios from 'axios';
import { EvaluationRequest, EvaluationResponse, SystemHealth, MetricsInfo } from '../types/evaluation';

const API_BASE_URL = 'http://localhost:9777';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds timeout for evaluation requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const evaluationAPI = {
  // Submit evaluation request
  evaluate: async (request: EvaluationRequest): Promise<EvaluationResponse> => {
    const response = await api.post('/api/v1/evaluation/evaluate', request);
    return response.data;
  },

  // Get evaluation status
  getStatus: async (evaluationId: string) => {
    const response = await api.get(`/api/v1/evaluation/status/${evaluationId}`);
    return response.data;
  },

  // Get system health
  getHealth: async (): Promise<SystemHealth> => {
    const response = await api.get('/api/v1/evaluation/system/health');
    return response.data;
  },

  // Get metrics information
  getMetrics: async (): Promise<MetricsInfo> => {
    const response = await api.get('/api/v1/evaluation/metrics');
    return response.data;
  },

  // Test evaluation with sample data
  testEvaluation: async (): Promise<EvaluationResponse> => {
    const response = await api.post('/api/v1/evaluation/test');
    return response.data;
  },

  // Test single metric evaluation
  testSingleMetric: async (): Promise<EvaluationResponse> => {
    const response = await api.post('/api/v1/evaluation/test/single-metric');
    return response.data;
  },
};

export default api;
