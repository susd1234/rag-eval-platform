# Enhanced Logging for Inter-Agent Communications

This document describes the comprehensive logging system that has been implemented to track inter-agent communications and request progress throughout the SME evaluation platform.

## Overview

The enhanced logging system provides:
- **Structured JSON logging** with correlation IDs
- **Request lifecycle tracking** from API to final response
- **Inter-agent communication monitoring** with detailed timing
- **Performance metrics** for optimization
- **LLM interaction logging** for debugging model behavior
- **Error tracking** with context and timing information

## Key Features

### 1. Correlation IDs
Every request is assigned a unique correlation ID that tracks all related operations:
```json
{
  "timestamp": "15JAN24_103045",
  "level": "INFO",
  "logger": "src.api",
  "correlation_id": "req_a1b2c3d4e5f6",
  "message": "API request received",
  "evaluation_step": "api_request_received"
}
```

### 2. Request Lifecycle Tracking
Complete visibility into request flow:
- API request received
- Validation steps
- Agent registration
- Context preparation
- Agent task creation
- Concurrent execution
- Result processing
- Response generation

### 3. Inter-Agent Communication Logging
Detailed tracking of agent interactions:
```json
{
  "timestamp": "15JAN24_103047",
  "level": "INFO",
  "logger": "src.orchestrator_factory",
  "correlation_id": "req_a1b2c3d4e5f6",
  "agent_name": "accuracy_agent",
  "metric": "accuracy",
  "request_id": "eval_xyz789",
  "evaluation_step": "message_send_start",
  "message": "Agent Communication - message_send_start: accuracy_agent (accuracy) - Request: eval_xyz789"
}
```

### 4. Performance Metrics
Timing information for optimization:
```json
{
  "timestamp": "15JAN24_103048",
  "level": "INFO",
  "logger": "src.agents",
  "correlation_id": "req_a1b2c3d4e5f6",
  "processing_time": 1.234,
  "evaluation_step": "performance_accuracy_evaluation_time",
  "message": "Performance Metric - accuracy_evaluation_time: 1.234 seconds"
}
```

### 5. LLM Interaction Logging
Model request/response tracking:
```json
{
  "timestamp": "15JAN24_103049",
  "level": "INFO",
  "logger": "src.proxy_client",
  "correlation_id": "req_a1b2c3d4e5f6",
  "model_name": "gpt-4",
  "processing_time": 2.567,
  "response_length": 1024,
  "evaluation_step": "llm_request_success",
  "message": "LLM Interaction - request_success: gpt-4"
}
```

## Log Structure

### Standard Fields
All log entries include:
- `timestamp`: Custom formatted timestamp (DDMMMYY_HHMMSS format, e.g., "15JAN24_103045")
- `level`: Log level (INFO, WARNING, ERROR)
- `logger`: Source module name
- `correlation_id`: Unique request identifier
- `message`: Human-readable message

### Context-Specific Fields
Additional fields based on operation type:
- `agent_name`: Name of the agent involved
- `metric`: Evaluation metric being processed
- `request_id`: Evaluation request identifier
- `evaluation_step`: Current step in the process
- `processing_time`: Operation duration in seconds
- `model_name`: LLM model being used
- `response_length`: Response size in characters

## Evaluation Steps Tracked

### API Layer Steps
- `api_request_received`
- `api_request_validation_start`
- `api_request_validation_complete`
- `api_request_validation_failed`
- `api_request_complete`
- `api_request_failed_http`
- `api_request_failed_internal`

### Orchestrator Steps
- `runtime_initialization_start`
- `runtime_initialization_complete`
- `evaluation_start`
- `context_preparation_complete`
- `agent_selection_complete`
- `agent_tasks_created`
- `agent_execution_start`
- `agent_execution_complete`
- `result_processing_start`
- `result_processing_complete`

### Agent Communication Steps
- `agent_id_created`
- `agent_registration_start`
- `agent_registration_complete`
- `message_send_start`
- `message_send_success`
- `message_send_failed`
- `message_received`
- `evaluation_completed`
- `evaluation_failed`

### LLM Interaction Steps
- `llm_request_start`
- `llm_request_success`
- `llm_request_failed`

## Usage Examples

### Viewing Request Flow
To follow a complete request, filter logs by correlation ID:
```bash
# Filter logs for a specific request
grep "req_a1b2c3d4e5f6" application.log

# View agent communications only
grep "Agent Communication" application.log | jq .

# View performance metrics
grep "Performance Metric" application.log | jq .
```

### Monitoring Agent Performance
```bash
# View all agent evaluation times
grep "evaluation_time" application.log | jq '.processing_time'

# Monitor LLM response times
grep "llm_response_time" application.log | jq '.processing_time'
```

### Debugging Failed Requests
```bash
# Find failed evaluations
grep "evaluation_failed" application.log | jq .

# View error details
grep "ERROR" application.log | jq '.message, .error'
```

## Configuration

The logging system is automatically configured in `app.py`:
```python
from src.logging_utils import setup_enhanced_logging
setup_enhanced_logging()
```

### Log Levels
- **INFO**: Normal operations, request flow, performance metrics
- **WARNING**: Non-critical issues, timeouts, retries
- **ERROR**: Failures, exceptions, critical issues

### Correlation Context
Use the `LoggingContext` manager for operations that need correlation tracking:
```python
from src.logging_utils import LoggingContext

with LoggingContext() as correlation_id:
    # All logging within this context will include the correlation_id
    logger.info("Operation started")
```

## Benefits

1. **Request Traceability**: Follow any request from API entry to completion
2. **Performance Monitoring**: Identify bottlenecks and optimization opportunities
3. **Agent Communication Visibility**: Debug inter-agent message flow
4. **Error Diagnosis**: Detailed context for troubleshooting failures
5. **System Monitoring**: Track system health and capacity utilization
6. **Audit Trail**: Complete record of all operations for compliance

## Best Practices

1. **Always use correlation IDs** for request-scoped operations
2. **Log at appropriate levels** to avoid noise while maintaining visibility
3. **Include timing information** for performance-critical operations
4. **Provide context** in error messages to aid debugging
5. **Use structured data** to enable log analysis and alerting

## Integration with Monitoring Tools

The structured JSON format enables integration with:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana** for visualization
- **Prometheus** for metrics collection
- **CloudWatch** for AWS deployments
- **Splunk** for enterprise monitoring

Example Grafana dashboard queries:
```promql
# Average request processing time
avg(processing_time{evaluation_step="api_evaluation_time"})

# Agent communication failures
count(evaluation_step{evaluation_step="message_send_failed"})

# LLM response times by model
avg(processing_time{evaluation_step="llm_response_time"}) by (model_name)
```
