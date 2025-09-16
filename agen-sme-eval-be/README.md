# AI Assisted SME Evaluation Platform

A sophisticated **Agentic AI** backend service for evaluating RAG (Retrieval-Augmented Generation) applications using **FastAPI** and **AutoGen Core v0.4.0**. This platform employs specialized AI agents to assess responses across four critical quality metrics.

## 🎯 Overview

This platform evaluates AI responses (particularly for ASK, DRAFT, and SUMMARIZATION use cases) using a multi-agent architecture that provides comprehensive quality assessment across:

- **Accuracy** - Factual correctness and absence of errors
- **Hallucination** - Detection of fabricated or made-up information  
- **Authoritativeness** - Quality and relevance of citations and sources
- **Usefulness** - Overall quality, responsiveness, and practical value

## 🏗️ Architecture

### Multi-Agent System (AutoGen Core v0.7.4)
- **AccuracyAgent** - Specialized in fact-checking and accuracy evaluation
- **HallucinationAgent** - Expert in detecting fabricated information
- **AuthoritativenessAgent** - Evaluates citation quality and source authority
- **UsefulnessAgent** - Assesses overall response quality and utility

All agents are built using AutoGen Core v0.7.4 framework with proper message passing and async communication patterns.

### Technology Stack
- **FastAPI** - Modern, fast web framework for building APIs
- **AutoGen Core v0.7.4** - Multi-agent conversation framework
- **LiteLLM** - Universal LLM interface supporting GPT and Claude models
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server for production deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for GPT models) OR Anthropic API key (for Claude models)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd agen-sme-eval-be
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Start the server:**
   ```bash
   python app.py
   ```

The service will be available at `http://localhost:9777`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

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

The platform supports switching between model providers:
- **GPT**: Uses OpenAI's models (default: gpt-4o-mini)
- **Claude**: Uses Anthropic's models (default: claude-3-sonnet-20240229)

Set `MODEL_PROVIDER=gpt` or `MODEL_PROVIDER=claude` in your `.env` file.

## 📡 API Reference

### Base URL
```
http://localhost:9777/api/v1
```

### Endpoints

#### 1. Evaluate Response
**POST** `/evaluation/evaluate`

Evaluate an AI response across all quality metrics.

**Request Body:**
```json
{
  "user_query": "Is a verbal employment contract enforceable in California?",
  "ai_response": "Yes, verbal employment contracts are generally enforceable...",
  "chunk_1": "California Employment Contract Law\\nSource: Labor Code Section 2922...",
  "chunk_2": "Verbal Contract Enforceability Standards\\nSource: Foley v. Interactive Data Corp...",
  "chunk_3": "Evidence Requirements for Oral Agreements\\nSource: Guz v. Bechtel National, Inc...",
  "chunk_4": "",
  "chunk_5": ""
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

## 🧪 Testing

### Run Sample Evaluation
```bash
curl -X POST "http://localhost:9777/api/v1/evaluation/test" \
     -H "Content-Type: application/json"
```

### Check System Health
```bash
curl "http://localhost:9777/api/v1/evaluation/system/health"
```

## 🔧 Development

### Project Structure
```
agen-sme-eval-be/
├── app.py                    # Main FastAPI application
├── src/
│   ├── __init__.py
│   ├── agents.py            # AutoGen Core evaluation agents
│   ├── api.py               # FastAPI routes and endpoints
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic data models
│   ├── orchestrator_factory.py  # Agent orchestration
│   └── proxy_client.py      # LiteLLM client interface
├── agents_config/           # Agent configuration files
│   ├── accuracy_agent.yaml
│   ├── hallucination_agent.yaml
│   ├── authoritativeness_agent.yaml
│   └── usefulness_agent.yaml
├── requirements.txt         # Python dependencies
├── env.example             # Environment configuration template
└── README.md               # This file
```

### Adding New Agents
1. Create agent class in `src/agents.py`
2. Add configuration in `agents_config/`
3. Register agent in `src/orchestrator_factory.py`
4. Update API models if needed

## 📈 Performance

### Concurrent Evaluations
- Supports up to 5 concurrent evaluations by default
- Configurable via `MAX_CONCURRENT_EVALUATIONS`
- Automatic request queuing when at capacity

### Timeouts
- Default evaluation timeout: 300 seconds
- Configurable via `EVALUATION_TIMEOUT`
- Graceful handling of timeouts

## 🚀 Deployment

### Production Considerations
1. **Security**: Set strong API keys and configure CORS appropriately
2. **Scaling**: Consider load balancing for high-traffic scenarios  
3. **Monitoring**: Implement logging and health checks
4. **Environment**: Set `ENVIRONMENT=production` in production

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 9777
CMD ["python", "app.py"]
```

## 📝 License

This project is part of the SME Evaluation Platform and is intended for evaluation and educational purposes.

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all agents follow the base evaluation pattern

## 📞 Support

For questions or issues:
1. Check the API documentation at `http://localhost:9777/docs`
2. Review the health check endpoint for system status
3. Examine logs for detailed error information

---

**Built with ❤️ using FastAPI and AutoGen Core**
