"""
FastAPI routes for AI SME Evaluation Platform
"""

import asyncio
import logging
import time
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse

from src.models import EvaluationRequest, EvaluationResponse
from src.orchestrator_factory import get_orchestrator
from src.config import get_settings
from src.logging_utils import (
    LoggingContext,
    log_evaluation_progress,
    log_performance_metric,
    timing_decorator,
    create_logger_with_context,
)

logger = create_logger_with_context(__name__)
settings = get_settings()

# Create API router
evaluation_router = APIRouter(
    prefix="/evaluation",
    tags=["evaluation"],
    responses={404: {"description": "Not found"}},
)

# Global orchestrator instance
orchestrator = get_orchestrator()


@evaluation_router.post(
    "/evaluate",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate AI Response",
    description="Evaluate an AI response using multi-agent system for selected metrics: Accuracy, Hallucination, Authoritativeness, and/or Usefulness",
)
@timing_decorator("api_evaluate_response")
async def evaluate_response(request: EvaluationRequest) -> EvaluationResponse:
    """
    Evaluate an AI response across selected quality metrics using specialized agents.

    This endpoint orchestrates multiple AI agents to evaluate the provided response
    on selected metrics from:
    - **Accuracy**: Factual correctness and absence of errors
    - **Hallucination**: Detection of fabricated or made-up information
    - **Authoritativeness**: Quality and relevance of citations and sources
    - **Usefulness**: Overall quality, responsiveness, and practical value

    Args:
        request: Evaluation request containing the user query, AI response, context chunks, and selected metrics

    Returns:
        Evaluation response with scores for selected metrics and overall assessment

    Raises:
        HTTPException: If evaluation fails or times out
    """
    request_start_time = time.time()

    # Create logging context with correlation ID
    with LoggingContext() as correlation_id:
        try:
            log_evaluation_progress(
                logger,
                "api_request_received",
                correlation_id,
                {
                    "endpoint": "/evaluate",
                    "selected_metrics": request.eval_metrices,
                    "query_length": len(request.user_query),
                    "response_length": len(request.ai_response),
                    "context_chunks_provided": len(
                        [
                            chunk
                            for chunk in [
                                request.chunk_1,
                                request.chunk_2,
                                request.chunk_3,
                                request.chunk_4,
                                request.chunk_5,
                            ]
                            if chunk.strip()
                        ]
                    ),
                    "file_uploaded": request.uploaded_file is not None,
                    "file_name": (
                        request.uploaded_file.name if request.uploaded_file else None
                    ),
                    "file_type": (
                        request.uploaded_file.type if request.uploaded_file else None
                    ),
                    "file_size": (
                        request.uploaded_file.size if request.uploaded_file else None
                    ),
                },
            )

            # Check if we're at capacity
            active_count = orchestrator.get_active_evaluations_count()
            if active_count >= settings.max_concurrent_evaluations:
                log_evaluation_progress(
                    logger,
                    "api_request_rejected_capacity",
                    correlation_id,
                    {
                        "active_evaluations": active_count,
                        "max_concurrent": settings.max_concurrent_evaluations,
                    },
                )

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Maximum concurrent evaluations ({settings.max_concurrent_evaluations}) reached. Please try again later.",
                )

            log_evaluation_progress(
                logger,
                "api_request_validation_start",
                correlation_id,
                {
                    "active_evaluations": active_count,
                    "capacity_available": settings.max_concurrent_evaluations
                    - active_count,
                },
            )

            logger.info(
                f"Starting evaluation for query: {request.user_query[:100]}... with metrics: {request.eval_metrices}"
            )

            # Log file upload information if present
            if request.uploaded_file:
                logger.info(
                    f"File uploaded for evaluation: {request.uploaded_file.name} "
                    f"({request.uploaded_file.type}, {request.uploaded_file.size} bytes)"
                )

            # Validate request
            if not request.user_query.strip():
                log_evaluation_progress(
                    logger,
                    "api_request_validation_failed",
                    correlation_id,
                    {"validation_error": "empty_user_query"},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User query cannot be empty",
                )

            if not request.ai_response.strip():
                log_evaluation_progress(
                    logger,
                    "api_request_validation_failed",
                    correlation_id,
                    {"validation_error": "empty_ai_response"},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="AI response cannot be empty",
                )

            # Validate eval_metrices
            if not request.eval_metrices:
                log_evaluation_progress(
                    logger,
                    "api_request_validation_failed",
                    correlation_id,
                    {"validation_error": "no_metrics_selected"},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one evaluation metric must be selected",
                )

            valid_metrics = {
                "Accuracy",
                "Hallucination",
                "Authoritativeness",
                "Usefulness",
            }
            invalid_metrics = set(request.eval_metrices) - valid_metrics
            if invalid_metrics:
                log_evaluation_progress(
                    logger,
                    "api_request_validation_failed",
                    correlation_id,
                    {
                        "validation_error": "invalid_metrics",
                        "invalid_metrics": list(invalid_metrics),
                        "valid_metrics": list(valid_metrics),
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid metrics: {list(invalid_metrics)}. Valid metrics are: {list(valid_metrics)}",
                )

            # Remove duplicates while preserving order
            original_metrics = request.eval_metrices.copy()
            request.eval_metrices = list(dict.fromkeys(request.eval_metrices))

            if len(original_metrics) != len(request.eval_metrices):
                log_evaluation_progress(
                    logger,
                    "api_request_metrics_deduplicated",
                    correlation_id,
                    {
                        "original_metrics": original_metrics,
                        "deduplicated_metrics": request.eval_metrices,
                    },
                )

            log_evaluation_progress(
                logger,
                "api_request_validation_complete",
                correlation_id,
                {
                    "validation_passed": True,
                    "final_metrics": request.eval_metrices,
                    "validation_time": time.time() - request_start_time,
                },
            )

            # Perform evaluation
            evaluation_start_time = time.time()
            result = await orchestrator.evaluate(request)
            evaluation_time = time.time() - evaluation_start_time

            total_request_time = time.time() - request_start_time

            log_performance_metric(
                logger,
                "api_evaluation_time",
                evaluation_time,
                context={
                    "correlation_id": correlation_id,
                    "evaluation_id": result.evaluation_id,
                    "selected_metrics": request.eval_metrices,
                    "metrics_count": len(request.eval_metrices),
                },
            )

            log_evaluation_progress(
                logger,
                "api_request_complete",
                correlation_id,
                {
                    "evaluation_id": result.evaluation_id,
                    "overall_rating": result.overall.overall_rating,
                    "overall_score": result.overall.overall_score,
                    "selected_metrics": request.eval_metrices,
                    "total_request_time": total_request_time,
                    "evaluation_time": evaluation_time,
                    "processing_time": result.processing_time,
                },
            )

            logger.info(
                f"Evaluation completed: {result.evaluation_id} - Overall: {result.overall.overall_rating} - Metrics: {request.eval_metrices}"
            )

            return result

        except HTTPException as http_exc:
            total_request_time = time.time() - request_start_time

            log_evaluation_progress(
                logger,
                "api_request_failed_http",
                correlation_id,
                {
                    "status_code": http_exc.status_code,
                    "detail": http_exc.detail,
                    "total_request_time": total_request_time,
                },
            )

            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            total_request_time = time.time() - request_start_time

            log_evaluation_progress(
                logger,
                "api_request_failed_internal",
                correlation_id,
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "total_request_time": total_request_time,
                },
            )

            logger.error(f"Evaluation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Evaluation failed: {str(e)}",
            )


@evaluation_router.get(
    "/status/{evaluation_id}",
    summary="Get Evaluation Status",
    description="Get the status of an ongoing evaluation by its ID",
)
async def get_evaluation_status(evaluation_id: str) -> Dict[str, Any]:
    """
    Get the status of an ongoing evaluation.

    Args:
        evaluation_id: The unique identifier of the evaluation

    Returns:
        Status information including current state and elapsed time
    """
    try:
        status_info = orchestrator.get_evaluation_status(evaluation_id)

        if status_info["status"] == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation {evaluation_id} not found",
            )

        return status_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting evaluation status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get evaluation status: {str(e)}",
        )


@evaluation_router.get(
    "/metrics",
    summary="Get Evaluation Metrics",
    description="Get information about the evaluation metrics and their definitions",
)
async def get_evaluation_metrics() -> Dict[str, Any]:
    """
    Get detailed information about the evaluation metrics used by the platform.

    Returns:
        Dictionary containing metric definitions, rating scales, and examples
    """
    return {
        "metrics": {
            "accuracy": {
                "definition": "Response contains information that is true and correct. It doesn't have any hallucination (information that is completely invented by the AI that does not exist) but some aspects of the response is incorrect in some way.",
                "rating_scale": {
                    "3_great": "Response is accurate and contains no factual errors or hallucinations",
                    "2_good": "Response is mostly accurate with minor factual issues",
                    "1_fair": "Response has some accuracy but contains notable factual errors",
                    "0_poor": "Response contains significant factual errors or does not provide expected results",
                },
            },
            "hallucination": {
                "definition": "Response should not contain information that is completely 'made up' (i.e., citations or references to information that does not exist and cannot be verified).",
                "rating_scale": {
                    "3_great": "No fabricated information, all references are verifiable",
                    "2_good": "Minimal risk of fabrication, references are mostly verifiable",
                    "1_fair": "Some potentially fabricated elements or unverifiable references",
                    "0_poor": "Contains made up law, citations, or completely fabricated information",
                },
            },
            "authoritativeness": {
                "definition": "Citations should be included as instructed for each task. Where included citations should be individually checked as indicated by your Lead. Citations should be valid and support the legal statements in the response.",
                "rating_scale": {
                    "3_great": "Citations are relevant, support the response, represent good law, and are authoritative/citable",
                    "2_good": "Citations are relevant and support the response but may lack recency or be from lower courts",
                    "1_fair": "Citations support the response but are not relevant to query or not good law or not authoritative",
                    "0_poor": "Citations do not support any part of the AI-generated response",
                },
            },
            "usefulness": {
                "definition": "Overall assessment of response quality considering accuracy, hallucination avoidance, responsiveness, completeness, authoritativeness and appropriateness.",
                "rating_scale": {
                    "3_great": "Excellent response that is accurate, non-hallucinatory, responsive, complete, authoritative and appropriate",
                    "2_good": "OK response without accuracy issues but may have minor issues in other dimensions",
                    "1_fair": "Deficient response related to prompt but has major issues making it insufficient for users",
                    "0_poor": "Bad response unrelated to prompt or has major issues making it embarrassing to display",
                },
            },
        },
        "badges": {
            "platinum": "Score 3 - Excellent performance",
            "gold": "Score 2 - Good performance with minor issues",
            "silver": "Score 1 - Fair performance with notable issues",
            "bronze": "Score 0 - Poor performance requiring improvement",
        },
        "overall_calculation": "Overall rating is calculated as the average of all individual metric scores",
    }


@evaluation_router.get(
    "/system/health",
    summary="System Health Check",
    description="Check the health and status of the evaluation system",
)
async def system_health() -> Dict[str, Any]:
    """
    Get system health information including active evaluations and configuration.

    Returns:
        System health status and configuration information
    """
    try:
        active_evaluations = orchestrator.get_active_evaluations_count()

        return {
            "status": "healthy",
            "active_evaluations": active_evaluations,
            "max_concurrent_evaluations": settings.max_concurrent_evaluations,
            "model_provider": settings.model_provider,
            "current_model": (
                settings.gpt_model
                if settings.model_provider == "gpt"
                else settings.claude_model
            ),
            "evaluation_timeout": settings.evaluation_timeout,
            "agents": ["accuracy", "hallucination", "authoritativeness", "usefulness"],
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e), "active_evaluations": 0},
        )


@evaluation_router.post(
    "/test",
    summary="Test Evaluation",
    description="Test the evaluation system with a sample request for Accuracy and Usefulness metrics only",
)
async def test_evaluation() -> EvaluationResponse:
    """
    Test the evaluation system with a predefined sample request.

    This endpoint is useful for testing and demonstrating the selective evaluation capabilities.
    It evaluates only Accuracy and Usefulness metrics to demonstrate partial evaluation.

    Returns:
        Sample evaluation response with selected metrics
    """
    try:
        # Create a test request with selective metrics
        test_request = EvaluationRequest(
            eval_metrices=["Accuracy", "Usefulness"],  # Test with only 2 metrics
            user_query="Is a verbal employment contract enforceable in California?",
            ai_response="""Yes, verbal employment contracts are generally enforceable in California under specific circumstances, though written contracts provide stronger legal protection.

Legal Framework

California follows the at-will employment doctrine, but verbal agreements can create binding contractual obligations when they include essential terms: compensation, job duties, and duration. The key requirement is mutual agreement and consideration between employer and employee.

Enforceability Requirements

For a verbal employment contract to be enforceable, it must demonstrate clear terms and mutual assent. Courts examine whether both parties understood and agreed to specific conditions, including salary, responsibilities, and employment duration. Witness testimony or partial performance can provide evidence of the agreement's existence.

Statute of Limitations

Verbal employment contracts must be enforced within two years under California's statute of limitations for oral agreements, while written contracts have a four-year enforcement period.""",
            chunk_1="""California Employment Contract Law
Source: Labor Code Section 2922 - California At-Will Employment

Content: "An employment, having no specified term, may be terminated at the will of either party on notice to the other. Employment for a specified term means an employment for a period greater than one month. However, an oral contract of employment may be enforceable if it contains the essential elements of a contract: offer, acceptance, consideration, and mutual assent.\"""",
            chunk_2="""Verbal Contract Enforceability Standards
Source: Foley v. Interactive Data Corp., 47 Cal. 3d 654 (1988)

Content: "Oral employment contracts are subject to the same contract formation requirements as written agreements. The plaintiff must prove by clear and convincing evidence that the parties mutually agreed to specific terms regarding compensation, duration, and job responsibilities.\"""",
            chunk_3="""Evidence Requirements for Oral Agreements
Source: Guz v. Bechtel National, Inc., 24 Cal. 4th 317 (2000)

Content: "To establish an oral employment contract, the employee must present evidence of definite contractual terms, not merely expectations or understandings. Witness testimony, partial performance, or contemporaneous communications can support the existence of such agreements.\"""",
            chunk_4="",
            chunk_5="",
        )

        # Perform evaluation
        result = await orchestrator.evaluate(test_request)

        logger.info(
            f"Test evaluation completed: {result.evaluation_id} with metrics: {test_request.eval_metrices}"
        )

        return result

    except Exception as e:
        logger.error(f"Test evaluation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test evaluation failed: {str(e)}",
        )


@evaluation_router.post(
    "/test/single-metric",
    summary="Test Single Metric Evaluation",
    description="Test the evaluation system with only Accuracy metric",
)
async def test_single_metric_evaluation() -> EvaluationResponse:
    """
    Test the evaluation system with a predefined sample request for single metric.

    This endpoint demonstrates evaluating only the Accuracy metric.

    Returns:
        Sample evaluation response with only Accuracy metric
    """
    try:
        # Create a test request with single metric
        test_request = EvaluationRequest(
            eval_metrices=["Accuracy"],  # Test with only 1 metric
            user_query="What is the capital of France?",
            ai_response="The capital of France is Paris. Paris is located in the north-central part of France and serves as the country's political, economic, and cultural center.",
            chunk_1="France Geography: Paris is the capital and largest city of France, located in the north-central part of the country.",
            chunk_2="",
            chunk_3="",
            chunk_4="",
            chunk_5="",
        )

        # Perform evaluation
        result = await orchestrator.evaluate(test_request)

        logger.info(f"Single metric test evaluation completed: {result.evaluation_id}")

        return result

    except Exception as e:
        logger.error(f"Single metric test evaluation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Single metric test evaluation failed: {str(e)}",
        )
