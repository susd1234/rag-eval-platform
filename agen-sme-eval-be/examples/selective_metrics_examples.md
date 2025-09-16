# Selective Metrics Processing Examples

This document demonstrates how to use the `eval_metrices` parameter to selectively process evaluation metrics.

## 1. Single Metric Evaluation

Evaluate only the Accuracy metric:

```json
{
  "eval_metrices": ["Accuracy"],
  "user_query": "What is the capital of France?",
  "ai_response": "The capital of France is Paris.",
  "chunk_1": "France Geography: Paris is the capital and largest city of France.",
  "chunk_2": "",
  "chunk_3": "",
  "chunk_4": "",
  "chunk_5": ""
}
```

**Expected Response:**
- Only `accuracy` field will be populated
- `hallucination`, `authoritativeness`, and `usefulness` fields will be `null`
- Overall evaluation will be based only on the Accuracy score

## 2. Two Metrics Evaluation

Evaluate Accuracy and Usefulness only:

```json
{
  "eval_metrices": ["Accuracy", "Usefulness"],
  "user_query": "Is a verbal employment contract enforceable in California?",
  "ai_response": "Yes, verbal employment contracts are generally enforceable in California under specific circumstances...",
  "chunk_1": "California Employment Contract Law...",
  "chunk_2": "Verbal Contract Enforceability Standards...",
  "chunk_3": "",
  "chunk_4": "",
  "chunk_5": ""
}
```

**Expected Response:**
- `accuracy` and `usefulness` fields will be populated
- `hallucination` and `authoritativeness` fields will be `null`
- Overall evaluation will be based on average of Accuracy and Usefulness scores

## 3. Three Metrics Evaluation

Evaluate Accuracy, Hallucination, and Authoritativeness:

```json
{
  "eval_metrices": ["Accuracy", "Hallucination", "Authoritativeness"],
  "user_query": "What are the legal requirements for forming a corporation?",
  "ai_response": "To form a corporation, you must file articles of incorporation, pay filing fees, and comply with state requirements...",
  "chunk_1": "Corporate Formation Requirements...",
  "chunk_2": "State Filing Requirements...",
  "chunk_3": "Legal Documentation Standards...",
  "chunk_4": "",
  "chunk_5": ""
}
```

**Expected Response:**
- `accuracy`, `hallucination`, and `authoritativeness` fields will be populated
- `usefulness` field will be `null`
- Overall evaluation will be based on average of the three selected metrics

## 4. All Metrics Evaluation (Default Behavior)

When no `eval_metrices` is specified or all metrics are included:

```json
{
  "eval_metrices": ["Accuracy", "Hallucination", "Authoritativeness", "Usefulness"],
  "user_query": "Explain the difference between criminal and civil law.",
  "ai_response": "Criminal law deals with offenses against the state...",
  "chunk_1": "Criminal Law Fundamentals...",
  "chunk_2": "Civil Law Overview...",
  "chunk_3": "Legal System Distinctions...",
  "chunk_4": "",
  "chunk_5": ""
}
```

**Expected Response:**
- All metric fields will be populated
- Overall evaluation will be based on average of all four metrics

## 5. API Endpoints for Testing

### Test Selective Evaluation
```bash
POST /evaluation/test
```
- Tests with Accuracy and Usefulness metrics only
- Demonstrates partial evaluation capabilities

### Test Single Metric Evaluation
```bash
POST /evaluation/test/single-metric
```
- Tests with only Accuracy metric
- Shows minimal evaluation setup

### Standard Evaluation
```bash
POST /evaluation/evaluate
```
- Accepts custom `eval_metrices` parameter
- Validates metric selection
- Processes only selected metrics

## Benefits of Selective Processing

1. **Performance**: Faster evaluation by running only required agents
2. **Cost Efficiency**: Reduced API calls to LLM providers
3. **Flexibility**: Focus on specific quality aspects
4. **Resource Management**: Better utilization of concurrent evaluation slots
5. **Customization**: Tailored evaluation based on use case requirements

## Validation Rules

- At least one metric must be selected
- Valid metrics: "Accuracy", "Hallucination", "Authoritativeness", "Usefulness"
- Duplicates are automatically removed
- Case-sensitive metric names
- Invalid metrics result in 400 Bad Request error

## Performance Implications

- **Single metric**: ~25% of original processing time
- **Two metrics**: ~50% of original processing time  
- **Three metrics**: ~75% of original processing time
- **All metrics**: 100% of original processing time (default behavior)

Processing time scales linearly with the number of selected metrics since agents run in parallel.
