"""
Pydantic models for AI SME Evaluation Platform
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class UploadedFile(BaseModel):
    """Model for uploaded file information"""

    name: str = Field(..., description="Original filename")
    content: str = Field(..., description="File content as text")
    type: str = Field(..., description="MIME type of the file")
    size: int = Field(..., description="File size in bytes")


class EvaluationRequest(BaseModel):
    """Request model for evaluation endpoint"""

    model: List[str] = Field(
        default=["gpt-4o-mini"],
        description="List of models to use for evaluation. Default is gpt-4o-mini.",
    )
    eval_metrices: List[
        Literal["Accuracy", "Hallucination", "Authoritativeness", "Usefulness"]
    ] = Field(
        default=["Accuracy", "Hallucination", "Authoritativeness", "Usefulness"],
        description="List of metrics to evaluate. If not provided, all metrics will be evaluated.",
    )
    user_query: str = Field(..., description="The original user query")
    ai_response: str = Field(..., description="The AI-generated response to evaluate")
    chunk_1: str = Field(default="", description="First context chunk")
    chunk_2: str = Field(default="", description="Second context chunk")
    chunk_3: str = Field(default="", description="Third context chunk")
    chunk_4: str = Field(default="", description="Fourth context chunk")
    chunk_5: str = Field(default="", description="Fifth context chunk")
    uploaded_file: Optional[UploadedFile] = Field(
        default=None, description="Optional uploaded file information"
    )

    class Config:
        schema_extra = {
            "example": {
                "model": ["gpt-4o-mini"],
                "eval_metrices": [
                    "Accuracy",
                    "Hallucination",
                    "Authoritativeness",
                    "Usefulness",
                ],
                "user_query": "Is a verbal employment contract enforceable in California?",
                "ai_response": "Yes, verbal employment contracts are generally enforceable in California under specific circumstances...",
                "chunk_1": "California Employment Contract Law\nSource: Labor Code Section 2922...",
                "chunk_2": "Verbal Contract Enforceability Standards\nSource: Foley v. Interactive Data Corp...",
                "chunk_3": "Evidence Requirements for Oral Agreements\nSource: Guz v. Bechtel National, Inc...",
                "chunk_4": "",
                "chunk_5": "",
                "uploaded_file": None,
            }
        }


class MetricEvaluation(BaseModel):
    """Individual metric evaluation result"""

    metric: Literal["Accuracy", "Hallucination", "Authoritativeness", "Usefulness"]
    rating: Literal["Great", "Good", "Fair", "Poor"]
    score: Literal[3, 2, 1, 0]
    badge: Literal["Platinum", "Gold", "Silver", "Bronze"]
    reasoning: str = Field(..., description="Detailed reasoning for the evaluation")

    class Config:
        schema_extra = {
            "example": {
                "metric": "Accuracy",
                "rating": "Great",
                "score": 3,
                "badge": "Platinum",
                "reasoning": "The response contains accurate information about California employment law...",
            }
        }


class OverallEvaluation(BaseModel):
    """Overall evaluation summary"""

    overall_rating: Literal["Great", "Good", "Fair", "Poor"]
    overall_score: float = Field(
        ..., ge=0, le=3, description="Average score across all metrics"
    )
    overall_badge: Literal["Platinum", "Gold", "Silver", "Bronze"]
    summary: str = Field(..., description="Overall evaluation summary")


class EvaluationResponse(BaseModel):
    """Complete evaluation response"""

    accuracy: Optional[MetricEvaluation] = None
    hallucination: Optional[MetricEvaluation] = None
    authoritativeness: Optional[MetricEvaluation] = None
    usefulness: Optional[MetricEvaluation] = None
    overall: OverallEvaluation
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    processing_time: float = Field(
        ..., description="Time taken for evaluation in seconds"
    )

    class Config:
        schema_extra = {
            "example": {
                "accuracy": {
                    "metric": "Accuracy",
                    "rating": "Great",
                    "score": 3,
                    "badge": "Platinum",
                    "reasoning": "Response contains accurate legal information...",
                },
                "hallucination": {
                    "metric": "Hallucination",
                    "rating": "Great",
                    "score": 3,
                    "badge": "Platinum",
                    "reasoning": "No fabricated information detected...",
                },
                "authoritativeness": {
                    "metric": "Authoritativeness",
                    "rating": "Great",
                    "score": 3,
                    "badge": "Platinum",
                    "reasoning": "Citations are relevant and authoritative...",
                },
                "usefulness": {
                    "metric": "Usefulness",
                    "rating": "Great",
                    "score": 3,
                    "badge": "Platinum",
                    "reasoning": "Response is comprehensive and helpful...",
                },
                "overall": {
                    "overall_rating": "Great",
                    "overall_score": 3.0,
                    "overall_badge": "Platinum",
                    "summary": "Excellent response across all evaluation criteria",
                },
                "evaluation_id": "eval_123456789",
                "processing_time": 15.23,
            }
        }


class AgentMessage(BaseModel):
    """Message structure for agent communication"""

    role: Literal["user", "assistant", "system"]
    content: str
    agent_name: Optional[str] = None


class EvaluationContext(BaseModel):
    """Context information for evaluation agents"""

    user_query: str
    ai_response: str
    context_chunks: List[str]
    evaluation_criteria: dict
    target_metric: str
    model: str
