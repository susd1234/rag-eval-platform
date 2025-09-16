# RAG Evaluation Platform (Powered by Agentic AI)

A comprehensive **full-stack RAG Evaluation Platform** that employs a sophisticated multi-agent AI system to evaluate AI responses across critical quality metrics. This platform combines a modern React frontend with a robust FastAPI backend to provide real-time evaluation capabilities for RAG (Retrieval-Augmented Generation) applications.

## 🎯 Overview

The AI Assisted SME Evaluation Platform is designed to assess the quality of AI-generated responses using specialized AI agents. It evaluates responses across four key dimensions:

- **🎯 Accuracy** - Factual correctness and absence of errors
- **🔍 Hallucination** - Detection of fabricated or made-up information  
- **📚 Authoritativeness** - Quality and relevance of citations and sources
- **💡 Usefulness** - Overall quality, responsiveness, and practical value

### Key Features

- **Multi-Agent Architecture**: Specialized AI agents for each evaluation metric
- **Real-time Evaluation**: Fast, concurrent processing of evaluation requests
- **Modern UI**: Beautiful, responsive React frontend with animations
- **Comprehensive API**: RESTful API with detailed documentation
- **Flexible Configuration**: Support for multiple LLM providers (GPT, Claude)
- **File Upload Support**: Evaluate responses with context from uploaded documents
- **Selective Evaluation**: Choose specific metrics to evaluate
- **Performance Monitoring**: Built-in health checks and performance metrics

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **React 19** with TypeScript for type safety
- **Tailwind CSS** for modern, responsive styling
- **Framer Motion** for smooth animations and transitions
- **Axios** for API communication
- **Lucide React** for consistent iconography

### Backend (FastAPI + Python)
- **FastAPI** for high-performance API development
- **AutoGen Core v0.7.4** for multi-agent orchestration
- **LiteLLM** for universal LLM interface
- **Pydantic** for data validation and serialization
- **Uvicorn** for ASGI server deployment

### Multi-Agent System
- **AccuracyAgent** - Specialized in fact-checking and accuracy evaluation
- **HallucinationAgent** - Expert in detecting fabricated information
- **AuthoritativenessAgent** - Evaluates citation quality and source authority
- **UsefulnessAgent** - Assesses overall response quality and utility

## 🚀 Quick Start

### Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.11+
- **OpenAI API key** (for GPT models) OR **Anthropic API key** (for Claude models)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sme-eval-platform
   ```

2. **Set up the backend:**
   ```bash
   cd agen-sme-eval-be
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend:**
   ```bash
   cd ../agen-sme-eval-ui-react
   npm install
   ```

4. **Configure environment variables:**
   ```bash
   cd ../agen-sme-eval-be
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

### Running the Application

#### Option 1: Full Stack Launch (Recommended)
```bash
# From the root directory
./launch-full-stack.sh
```

#### Option 2: Manual Launch
```bash
# Terminal 1 - Backend
cd agen-sme-eval-be
source venv/bin/activate
python app.py

# Terminal 2 - Frontend  
cd agen-sme-eval-ui-react
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:9777
- **API Documentation**: http://localhost:9777/docs

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `agen-sme-eval-be` directory:

```env
# Application Settings
PORT=9777
ENVIRONMENT=development

# Model Configuration  
MODEL_PROVIDER=gpt  # Options: gpt, claude
GPT_MODEL=gpt-4o-mini
CLAUDE_MODEL=claude-3-sonnet-20240229

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: LiteLLM Proxy
LITELLM_PROXY_URL=  # URL to LiteLLM proxy endpoint

# Performance Settings
MAX_CONCURRENT_EVALUATIONS=5
EVALUATION_TIMEOUT=300  # seconds
```

### Model Selection

The platform supports multiple LLM providers:
- **GPT**: Uses OpenAI's models (default: gpt-4o-mini)
- **Claude**: Uses Anthropic's models (default: claude-3-sonnet-20240229)

Set `MODEL_PROVIDER=gpt` or `MODEL_PROVIDER=claude` in your `.env` file.

## 📡 API Reference

### Base URL
```
http://localhost:9777/api/v1
```

### Core Endpoints

#### 1. Evaluate Response
**POST** `/evaluation/evaluate`

Evaluate an AI response across selected quality metrics.

**Request Body:**
```json
{
  "model": ["gpt-4o-mini"],
  "eval_metrices": ["Accuracy", "Hallucination", "Authoritativeness", "Usefulness"],
  "user_query": "Is a verbal employment contract enforceable in California?",
  "ai_response": "Yes, verbal employment contracts are generally enforceable...",
  "chunk_1": "California Employment Contract Law\nSource: Labor Code Section 2922...",
  "chunk_2": "Verbal Contract Enforceability Standards\nSource: Foley v. Interactive Data Corp...",
  "chunk_3": "Evidence Requirements for Oral Agreements\nSource: Guz v. Bechtel National, Inc...",
  "chunk_4": "",
  "chunk_5": "",
  "uploaded_file": {
    "name": "legal_document.pdf",
    "content": "Document content as text...",
    "type": "application/pdf",
    "size": 1024
  }
}
```

**Response:**
```json
{
  "accuracy": {
    "metric": "Accuracy",
    "rating": "Great",
    "score": 3,
    "badge": "Platinum",
    "reasoning": "Response contains accurate legal information..."
  },
  "hallucination": {
    "metric": "Hallucination", 
    "rating": "Great",
    "score": 3,
    "badge": "Platinum",
    "reasoning": "No fabricated information detected..."
  },
  "authoritativeness": {
    "metric": "Authoritativeness",
    "rating": "Great", 
    "score": 3,
    "badge": "Platinum",
    "reasoning": "Citations are relevant and authoritative..."
  },
  "usefulness": {
    "metric": "Usefulness",
    "rating": "Great",
    "score": 3, 
    "badge": "Platinum",
    "reasoning": "Response is comprehensive and helpful..."
  },
  "overall": {
    "overall_rating": "Great",
    "overall_score": 3.0,
    "overall_badge": "Platinum", 
    "summary": "Excellent response across all evaluation criteria"
  },
  "evaluation_id": "eval_123456789",
  "processing_time": 15.23
}
```

#### 2. Get Evaluation Metrics
**GET** `/evaluation/metrics`

Get detailed information about evaluation metrics and rating scales.

#### 3. System Health Check
**GET** `/evaluation/system/health`

Check system health and configuration status.

#### 4. Test Evaluation
**POST** `/evaluation/test`

Test the evaluation system with a sample request.

#### 5. Test Single Metric
**POST** `/evaluation/test/single-metric`

Test evaluation with only the Accuracy metric.

## 📊 Rating System

### Score Scale
- **3 (Great)** - Excellent performance → **Platinum Badge**
- **2 (Good)** - Good performance with minor issues → **Gold Badge**  
- **1 (Fair)** - Fair performance with notable issues → **Silver Badge**
- **0 (Poor)** - Poor performance requiring improvement → **Bronze Badge**

### Overall Rating
The overall rating is calculated as the average of all individual metric scores, providing a comprehensive quality assessment.

## 🔍 Evaluation Metrics Details

### 1. Accuracy
Evaluates factual correctness and absence of errors in the response.
- Checks statements against provided context
- Verifies logical consistency
- Identifies potential factual errors

### 2. Hallucination
Detects fabricated or made-up information in the response.
- Identifies non-existent citations
- Flags invented legal concepts
- Verifies reference authenticity

### 3. Authoritativeness  
Assesses the quality and relevance of citations and sources.
- Evaluates source hierarchy (primary vs secondary)
- Checks jurisdictional relevance
- Assesses currency and validity

### 4. Usefulness
Evaluates overall response quality and practical value.
- Assesses responsiveness to query
- Evaluates completeness and organization
- Considers practical applicability

## 🎨 Frontend Features

### User Interface
- **Modern Design**: Clean, professional interface with dark theme
- **Responsive Layout**: Works seamlessly on desktop and mobile devices
- **Interactive Forms**: Intuitive evaluation form with file upload support
- **Real-time Feedback**: Live system status and loading indicators
- **Results Visualization**: Beautiful display of evaluation results with badges

### Components
- **Header**: Navigation and branding
- **EvaluationForm**: Main form for submitting evaluation requests
- **ResultsDisplay**: Comprehensive results visualization
- **SystemStatus**: Real-time system health monitoring
- **LoadingSpinner**: Animated loading states

## 🧪 Testing

### API Testing
```bash
# Test evaluation endpoint
curl -X POST "http://localhost:9777/api/v1/evaluation/test" \
     -H "Content-Type: application/json"

# Check system health
curl "http://localhost:9777/api/v1/evaluation/system/health"

# Test single metric
curl -X POST "http://localhost:9777/api/v1/evaluation/test/single-metric" \
     -H "Content-Type: application/json"
```

### Frontend Testing
```bash
cd agen-sme-eval-ui-react
npm test
```

## 📁 Project Structure

```
sme-eval-platform/
├── agen-sme-eval-be/              # Backend (FastAPI)
│   ├── app.py                     # Main FastAPI application
│   ├── main.py                    # Application entry point
│   ├── src/
│   │   ├── agents.py              # AutoGen Core evaluation agents
│   │   ├── api.py                 # FastAPI routes and endpoints
│   │   ├── config.py              # Configuration management
│   │   ├── models.py              # Pydantic data models
│   │   ├── orchestrator_factory.py # Agent orchestration
│   │   ├── proxy_client.py        # LiteLLM client interface
│   │   └── logging_utils.py       # Enhanced logging utilities
│   ├── agents_config/             # Agent configuration files
│   │   ├── accuracy_agent.yaml
│   │   ├── hallucination_agent.yaml
│   │   ├── authoritativeness_agent.yaml
│   │   └── usefulness_agent.yaml
│   ├── examples/                  # API usage examples
│   ├── requirements.txt           # Python dependencies
│   ├── pyproject.toml            # Project configuration
│   └── env.example               # Environment configuration template
├── agen-sme-eval-ui-react/        # Frontend (React)
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── Header.tsx
│   │   │   ├── EvaluationForm.tsx
│   │   │   ├── ResultsDisplay.tsx
│   │   │   ├── SystemStatus.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── services/              # API services
│   │   │   └── api.ts
│   │   ├── types/                 # TypeScript type definitions
│   │   │   └── evaluation.ts
│   │   ├── App.tsx                # Main application component
│   │   └── index.tsx              # Application entry point
│   ├── public/                    # Static assets
│   ├── package.json               # Node.js dependencies
│   └── tailwind.config.js         # Tailwind CSS configuration
├── launch-full-stack.sh           # Full stack launch script
├── launch-frontend.sh             # Frontend only launch script
├── launch.sh                      # Backend only launch script
└── README.md                      # This file
```

## 📈 Performance

### Concurrent Evaluations
- Supports up to 5 concurrent evaluations by default
- Configurable via `MAX_CONCURRENT_EVALUATIONS`
- Automatic request queuing when at capacity

### Timeouts
- Default evaluation timeout: 300 seconds
- Configurable via `EVALUATION_TIMEOUT`
- Graceful handling of timeouts

### Frontend Performance
- Optimized React components with proper memoization
- Lazy loading and code splitting
- Efficient state management
- Smooth animations with Framer Motion

## 🚀 Deployment

### Development
```bash
# Use the provided launch scripts
./launch-full-stack.sh
```

### Production Considerations

1. **Security**:
   - Set strong API keys
   - Configure CORS appropriately
   - Use HTTPS in production
   - Implement rate limiting

2. **Scaling**:
   - Consider load balancing for high-traffic scenarios
   - Use production-grade ASGI server (Gunicorn + Uvicorn)
   - Implement database for evaluation history

3. **Monitoring**:
   - Set up logging and health checks
   - Monitor API performance and error rates
   - Track evaluation metrics and trends

4. **Environment**:
   - Set `ENVIRONMENT=production`
   - Use production-grade LLM models
   - Configure proper error handling

### Docker Deployment (Optional)

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 9777
CMD ["python", "app.py"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🔧 Development

### Adding New Evaluation Metrics

1. **Create Agent Configuration**:
   ```yaml
   # agents_config/new_metric_agent.yaml
   name: NewMetricAgent
   description: "Agent for evaluating new metric"
   agent_type: evaluation
   metric: new_metric
   # ... configuration details
   ```

2. **Implement Agent Class**:
   ```python
   # src/agents.py
   class NewMetricAgent(BaseEvaluationAgent):
       def __init__(self, config: dict):
           super().__init__(config)
           # ... implementation
   ```

3. **Update Models**:
   ```python
   # src/models.py
   class EvaluationResponse(BaseModel):
       # ... existing fields
       new_metric: Optional[MetricEvaluation] = None
   ```

4. **Register in Orchestrator**:
   ```python
   # src/orchestrator_factory.py
   # Add new agent to the orchestrator
   ```

### Frontend Development

1. **Add New Components**:
   ```typescript
   // src/components/NewComponent.tsx
   import React from 'react';
   
   const NewComponent: React.FC = () => {
     // Component implementation
   };
   
   export default NewComponent;
   ```

2. **Update Types**:
   ```typescript
   // src/types/evaluation.ts
   export interface NewMetricEvaluation {
     // Type definition
   }
   ```

3. **Add API Services**:
   ```typescript
   // src/services/api.ts
   export const newMetricAPI = {
     // API methods
   };
   ```

## 📝 License

This project is part of the SME Evaluation Platform and is intended for evaluation and educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all agents follow the base evaluation pattern
5. Use TypeScript for frontend development
6. Follow PEP 8 for Python code

## 📞 Support

For questions or issues:

1. **Check the API documentation**: http://localhost:9777/docs
2. **Review the health check endpoint**: `/api/v1/evaluation/system/health`
3. **Examine logs** for detailed error information
4. **Check system status** in the frontend interface

### Common Issues

**Backend not starting:**
- Check if port 9777 is available
- Verify API keys are set correctly
- Ensure Python virtual environment is activated

**Frontend not connecting:**
- Verify backend is running on port 9777
- Check browser console for errors
- Ensure CORS is configured properly

**Evaluation timeouts:**
- Check API key limits and quotas
- Verify model provider configuration
- Review evaluation timeout settings

## 🎉 Getting Started

1. **Clone the repository**
2. **Set up your API keys** in the `.env` file
3. **Run the full stack application** using `./launch-full-stack.sh`
4. **Open your browser** to http://localhost:3000
5. **Start evaluating AI responses** with the intuitive interface

---

**Built with ❤️ using React, TypeScript, FastAPI, and AutoGen Core**

*Empowering AI evaluation through intelligent multi-agent systems*
