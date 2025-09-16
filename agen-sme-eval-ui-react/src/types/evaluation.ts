export interface MetricEvaluation {
  metric: 'Accuracy' | 'Hallucination' | 'Authoritativeness' | 'Usefulness';
  rating: 'Great' | 'Good' | 'Fair' | 'Poor';
  score: 3 | 2 | 1 | 0;
  badge: 'Platinum' | 'Gold' | 'Silver' | 'Bronze';
  reasoning: string;
}

export interface OverallEvaluation {
  overall_rating: 'Great' | 'Good' | 'Fair' | 'Poor';
  overall_score: number;
  overall_badge: 'Platinum' | 'Gold' | 'Silver' | 'Bronze';
  summary: string;
}

export interface EvaluationResponse {
  accuracy?: MetricEvaluation;
  hallucination?: MetricEvaluation;
  authoritativeness?: MetricEvaluation;
  usefulness?: MetricEvaluation;
  overall: OverallEvaluation;
  evaluation_id: string;
  processing_time: number;
}

export interface EvaluationRequest {
  model: string[];
  eval_metrices: ('Accuracy' | 'Hallucination' | 'Authoritativeness' | 'Usefulness')[];
  user_query: string;
  ai_response: string;
  chunk_1: string;
  chunk_2: string;
  chunk_3: string;
  chunk_4: string;
  chunk_5: string;
  uploaded_file?: {
    name: string;
    content: string;
    type: string;
    size: number;
  };
}

export interface SystemHealth {
  status: string;
  active_evaluations: number;
  max_concurrent_evaluations: number;
  model_provider: string;
  current_model: string;
  evaluation_timeout: number;
  agents: string[];
  version: string;
}

export interface MetricsInfo {
  metrics: {
    [key: string]: {
      definition: string;
      rating_scale: {
        [key: string]: string;
      };
    };
  };
  badges: {
    [key: string]: string;
  };
  overall_calculation: string;
}
