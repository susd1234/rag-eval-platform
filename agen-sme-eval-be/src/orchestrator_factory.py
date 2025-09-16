"""
AutoGen Core v0.7.4 orchestrator factory for managing evaluation agents and workflows
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, List

from autogen_core import SingleThreadedAgentRuntime, AgentId, TopicId

from src.models import (
    EvaluationRequest,
    EvaluationResponse,
    MetricEvaluation,
    OverallEvaluation,
    EvaluationContext,
)
from src.agents import (
    AccuracyAgent,
    HallucinationAgent,
    AuthoritativenessAgent,
    UsefulnessAgent,
    AgentEvaluationRequest,
    AgentEvaluationResult,
)
from src.agent_config_loader import get_config_loader
from src.config import get_settings
from src.logging_utils import (
    log_agent_communication,
    log_evaluation_progress,
    log_performance_metric,
    timing_decorator,
    create_logger_with_context,
)

logger = create_logger_with_context(__name__)
settings = get_settings()


class AutoGenEvaluationOrchestrator:
    """Orchestrates the multi-agent evaluation process using AutoGen Core v0.7.4"""

    def __init__(self):
        self.runtime = None
        self.agent_ids = {}
        self.active_evaluations: Dict[str, Any] = {}
        self._initialize_runtime()

    def _initialize_runtime(self):
        """Initialize AutoGen Core runtime and register agents"""
        try:
            logger.info("Starting AutoGen Core runtime initialization")

            log_evaluation_progress(
                logger,
                "runtime_initialization_start",
                "system",
                {"component": "orchestrator"},
            )

            # Load YAML configurations first
            config_loader = get_config_loader()
            available_configs = config_loader.get_available_metrics()
            log_evaluation_progress(
                logger,
                "yaml_configs_loaded",
                "system",
                {
                    "component": "orchestrator",
                    "available_configs": available_configs,
                    "config_count": len(available_configs),
                },
            )

            # Create single-threaded runtime for our use case
            try:
                self.runtime = SingleThreadedAgentRuntime()
                logger.info(
                    f"Successfully created SingleThreadedAgentRuntime: {type(self.runtime)}"
                )
            except Exception as e:
                logger.error(f"Failed to create SingleThreadedAgentRuntime: {str(e)}")
                raise RuntimeError(
                    f"Failed to create SingleThreadedAgentRuntime: {str(e)}"
                )

            # Verify runtime was created successfully
            if self.runtime is None:
                raise RuntimeError("SingleThreadedAgentRuntime creation returned None")

            # Create agent instances for registration
            try:
                self.agents = {
                    "accuracy": AccuracyAgent(),
                    "hallucination": HallucinationAgent(),
                    "authoritativeness": AuthoritativenessAgent(),
                    "usefulness": UsefulnessAgent(),
                }
                logger.info(f"Successfully created {len(self.agents)} agent instances")
            except Exception as e:
                logger.error(f"Failed to create agent instances: {str(e)}")
                raise RuntimeError(f"Failed to create agent instances: {str(e)}")

            # Store agent IDs for later async registration
            self.agent_ids = {}
            for metric in self.agents.keys():
                agent_id = AgentId(f"{metric}_agent", "evaluation")
                self.agent_ids[metric] = agent_id

                log_agent_communication(
                    logger,
                    "agent_id_created",
                    f"{metric}_agent",
                    metric,
                    "system",
                    {"agent_id": str(agent_id)},
                )

            log_evaluation_progress(
                logger,
                "runtime_initialization_complete",
                "system",
                {
                    "component": "orchestrator",
                    "agents_created": list(self.agents.keys()),
                    "agent_count": len(self.agents),
                },
            )

            logger.info("AutoGen Core runtime initialized with evaluation agents")

        except Exception as e:
            log_evaluation_progress(
                logger,
                "runtime_initialization_failed",
                "system",
                {"component": "orchestrator", "error": str(e)},
            )
            logger.error(f"Failed to initialize AutoGen runtime: {str(e)}")
            raise RuntimeError(f"AutoGen initialization failed: {str(e)}")

    async def _register_agents(self):
        """Async registration of agents with the runtime"""
        try:
            if not hasattr(self, "_agents_registered"):
                # Ensure runtime is properly initialized
                if self.runtime is None:
                    logger.warning("Runtime is None, reinitializing...")
                    self._initialize_runtime()

                if self.runtime is None:
                    raise RuntimeError("Failed to initialize AutoGen runtime")

                log_evaluation_progress(
                    logger,
                    "agent_registration_start",
                    "system",
                    {
                        "component": "orchestrator",
                        "agents_to_register": list(self.agents.keys()),
                    },
                )

                # Register agent instances directly
                for metric, agent in self.agents.items():
                    agent_id = self.agent_ids[metric]

                    log_agent_communication(
                        logger,
                        "agent_registration_start",
                        f"{metric}_agent",
                        metric,
                        "system",
                        {"agent_id": str(agent_id)},
                    )

                    await self.runtime.register_agent_instance(agent, agent_id)

                    log_agent_communication(
                        logger,
                        "agent_registration_complete",
                        f"{metric}_agent",
                        metric,
                        "system",
                        {"agent_id": str(agent_id)},
                    )

                self._agents_registered = True

                # Start the runtime after all agents are registered
                await self.runtime.start()

                log_evaluation_progress(
                    logger,
                    "agent_registration_complete",
                    "system",
                    {
                        "component": "orchestrator",
                        "registered_agents": list(self.agents.keys()),
                        "agent_count": len(self.agents),
                    },
                )

                logger.info(
                    "All agents registered with AutoGen runtime and runtime started"
                )
        except Exception as e:
            log_evaluation_progress(
                logger,
                "agent_registration_failed",
                "system",
                {"component": "orchestrator", "error": str(e)},
            )
            logger.error(f"Failed to register agents: {str(e)}")
            raise RuntimeError(f"Agent registration failed: {str(e)}")

    @timing_decorator("full_evaluation")
    async def evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        """
        Orchestrate the complete evaluation process using AutoGen Core agents

        Args:
            request: The evaluation request containing query, response, context, and selected metrics

        Returns:
            Complete evaluation response with selected metrics
        """
        start_time = time.time()
        evaluation_id = f"eval_{uuid.uuid4().hex[:12]}"

        try:
            log_evaluation_progress(
                logger,
                "evaluation_start",
                evaluation_id,
                {
                    "selected_metrics": request.eval_metrices,
                    "query_length": len(request.user_query),
                    "response_length": len(request.ai_response),
                    "context_chunks_count": len(
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
                },
            )

            logger.info(
                f"Starting AutoGen evaluation {evaluation_id} for metrics: {request.eval_metrices}"
            )

            # Recreate runtime if it's None to prevent stale state
            if self.runtime is None:
                logger.warning("Runtime is None during evaluation, reinitializing...")
                self._initialize_runtime()

            # Double-check runtime is properly initialized
            if self.runtime is None:
                raise RuntimeError(
                    "Failed to initialize AutoGen runtime for evaluation"
                )

            # Ensure agents are registered
            await self._register_agents()

            # Track this evaluation
            self.active_evaluations[evaluation_id] = {
                "status": "processing",
                "start_time": start_time,
                "selected_metrics": request.eval_metrices,
            }

            log_evaluation_progress(
                logger,
                "evaluation_tracking_setup",
                evaluation_id,
                {
                    "active_evaluations_count": len(self.active_evaluations),
                    "status": "processing",
                },
            )

            # Prepare evaluation context
            context = self._prepare_evaluation_context(request)

            log_evaluation_progress(
                logger,
                "context_preparation_complete",
                evaluation_id,
                {
                    "context_chunks": len(context.context_chunks),
                    "user_query_length": len(context.user_query),
                    "ai_response_length": len(context.ai_response),
                },
            )

            # Create evaluation request message
            eval_request = AgentEvaluationRequest.create_message(context, evaluation_id)

            # Create metric mapping (case insensitive)
            metric_mapping = {
                "accuracy": "Accuracy",
                "hallucination": "Hallucination",
                "authoritativeness": "Authoritativeness",
                "usefulness": "Usefulness",
            }

            # Convert selected metrics to lowercase for matching
            selected_metrics_lower = [
                metric.lower() for metric in request.eval_metrices
            ]

            log_evaluation_progress(
                logger,
                "agent_selection_complete",
                evaluation_id,
                {
                    "requested_metrics": request.eval_metrices,
                    "selected_metrics_normalized": selected_metrics_lower,
                    "available_agents": list(self.agent_ids.keys()),
                },
            )

            # Send evaluation requests to only selected agents concurrently
            evaluation_tasks = []
            selected_agent_metrics = []

            for metric, agent_id in self.agent_ids.items():
                if metric in selected_metrics_lower:
                    capitalized_metric = metric_mapping[metric]
                    log_agent_communication(
                        logger,
                        "agent_task_preparation",
                        f"{metric}_agent",
                        metric,
                        evaluation_id,
                        {"agent_id": str(agent_id)},
                    )

                    task = self._send_evaluation_request(agent_id, eval_request, metric)
                    evaluation_tasks.append(task)
                    selected_agent_metrics.append(capitalized_metric)

            log_evaluation_progress(
                logger,
                "agent_tasks_created",
                evaluation_id,
                {
                    "agent_task_count": len(evaluation_tasks),
                    "selected_agents": selected_agent_metrics,
                    "concurrent_execution": True,
                },
            )

            # Wait for selected evaluations to complete with timeout
            try:
                log_evaluation_progress(
                    logger,
                    "agent_execution_start",
                    evaluation_id,
                    {
                        "timeout_seconds": settings.evaluation_timeout,
                        "concurrent_agents": len(evaluation_tasks),
                    },
                )

                execution_start_time = time.time()
                results = await asyncio.wait_for(
                    asyncio.gather(*evaluation_tasks, return_exceptions=True),
                    timeout=settings.evaluation_timeout,
                )
                execution_time = time.time() - execution_start_time

                log_performance_metric(
                    logger,
                    "agent_execution_time",
                    execution_time,
                    context={
                        "evaluation_id": evaluation_id,
                        "agent_count": len(evaluation_tasks),
                        "parallel_execution": True,
                    },
                )

                log_evaluation_progress(
                    logger,
                    "agent_execution_complete",
                    evaluation_id,
                    {
                        "execution_time": execution_time,
                        "results_count": len(results),
                        "timeout_avoided": True,
                    },
                )

            except asyncio.TimeoutError:
                timeout_time = time.time() - execution_start_time

                log_evaluation_progress(
                    logger,
                    "agent_execution_timeout",
                    evaluation_id,
                    {
                        "timeout_duration": timeout_time,
                        "configured_timeout": settings.evaluation_timeout,
                        "agents_running": len(evaluation_tasks),
                    },
                )

                logger.error(
                    f"Evaluation {evaluation_id} timed out after {timeout_time:.2f}s"
                )
                raise RuntimeError("Evaluation timed out")

            # Process results for selected metrics only
            metric_evaluations = {}
            successful_evaluations = 0
            failed_evaluations = 0

            log_evaluation_progress(
                logger,
                "result_processing_start",
                evaluation_id,
                {
                    "total_results": len(results),
                    "expected_metrics": selected_agent_metrics,
                },
            )

            for i, result in enumerate(results):
                metric = selected_agent_metrics[i]

                if isinstance(result, Exception):
                    failed_evaluations += 1

                    log_agent_communication(
                        logger,
                        "agent_evaluation_failed",
                        f"{metric}_agent",
                        metric,
                        evaluation_id,
                        {"error": str(result), "error_type": type(result).__name__},
                    )

                    logger.error(f"Error in {metric} evaluation: {str(result)}")
                    # Create default poor evaluation
                    metric_evaluations[metric] = MetricEvaluation(
                        metric=metric.title(),
                        rating="Poor",
                        score=0,
                        badge="Bronze",
                        reasoning=f"Evaluation failed: {str(result)}",
                    )
                elif isinstance(result, MetricEvaluation):
                    successful_evaluations += 1

                    log_agent_communication(
                        logger,
                        "agent_evaluation_success",
                        f"{metric}_agent",
                        metric,
                        evaluation_id,
                        {
                            "rating": result.rating,
                            "score": result.score,
                            "badge": result.badge,
                            "reasoning_length": len(result.reasoning),
                        },
                    )

                    metric_evaluations[metric] = result
                else:
                    failed_evaluations += 1

                    log_agent_communication(
                        logger,
                        "agent_evaluation_invalid_result",
                        f"{metric}_agent",
                        metric,
                        evaluation_id,
                        {"result_type": type(result).__name__},
                    )

                    logger.warning(
                        f"Unexpected result type for {metric}: {type(result)}"
                    )
                    metric_evaluations[metric] = MetricEvaluation(
                        metric=metric.title(),
                        rating="Poor",
                        score=0,
                        badge="Bronze",
                        reasoning="Unexpected result format",
                    )

            log_evaluation_progress(
                logger,
                "result_processing_complete",
                evaluation_id,
                {
                    "successful_evaluations": successful_evaluations,
                    "failed_evaluations": failed_evaluations,
                    "total_processed": len(results),
                    "success_rate": (
                        successful_evaluations / len(results) if results else 0
                    ),
                },
            )

            # Calculate overall evaluation based on selected metrics only
            overall_evaluation = self._calculate_overall_evaluation(metric_evaluations)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Create final response with only selected metrics
            response = EvaluationResponse(
                accuracy=metric_evaluations.get("Accuracy"),
                hallucination=metric_evaluations.get("Hallucination"),
                authoritativeness=metric_evaluations.get("Authoritativeness"),
                usefulness=metric_evaluations.get("Usefulness"),
                overall=overall_evaluation,
                evaluation_id=evaluation_id,
                processing_time=round(processing_time, 2),
            )

            # Clean up tracking
            self.active_evaluations.pop(evaluation_id, None)

            logger.info(
                f"Completed AutoGen evaluation {evaluation_id} in {processing_time:.2f}s for metrics: {request.eval_metrices}"
            )

            return response

        except Exception as e:
            logger.error(f"Error in AutoGen evaluation {evaluation_id}: {str(e)}")
            self.active_evaluations.pop(evaluation_id, None)

            # For communication timeouts, try to reset the runtime
            if "timeout" in str(e).lower() or "communication" in str(e).lower():
                logger.warning("Resetting AutoGen runtime due to communication issues")
                try:
                    await self.shutdown()
                except Exception as shutdown_error:
                    logger.error(
                        f"Error during emergency shutdown: {str(shutdown_error)}"
                    )

            raise RuntimeError(f"AutoGen evaluation failed: {str(e)}")

    @timing_decorator("agent_communication")
    async def _send_evaluation_request(
        self, agent_id: AgentId, eval_request: str, metric: str
    ) -> str:
        """Send evaluation request to a specific agent with retry logic and enhanced timeout handling"""
        request_start_time = time.time()
        last_exception = None

        # Extract request_id from the JSON string eval_request
        try:
            request_id = AgentEvaluationRequest.get_request_id(eval_request)
        except Exception as e:
            logger.error(f"Failed to extract request_id from eval_request: {str(e)}")
            request_id = "unknown"

        # Retry logic for failed agent communications
        for attempt in range(settings.agent_retry_attempts + 1):
            try:
                if attempt > 0:
                    logger.info(
                        f"Retrying {metric} agent communication (attempt {attempt + 1}/{settings.agent_retry_attempts + 1})"
                    )
                    await asyncio.sleep(
                        settings.agent_retry_delay * attempt
                    )  # Exponential backoff

                log_agent_communication(
                    logger,
                    "message_send_start",
                    f"{metric}_agent",
                    metric,
                    request_id,
                    {
                        "agent_id": str(agent_id),
                        "attempt": attempt + 1,
                        "max_attempts": settings.agent_retry_attempts + 1,
                    },
                )

                # Send message to agent with individual timeout to prevent hanging
                # Use more aggressive timeout on retries
                base_timeout = settings.agent_communication_timeout
                agent_timeout = (
                    base_timeout if attempt == 0 else min(base_timeout // 2, 30)
                )

                try:
                    # Create the communication task - wrap coroutine in task for cancellation support
                    communication_task = asyncio.create_task(
                        self.runtime.send_message(
                            eval_request,
                            recipient=agent_id,
                        )
                    )

                    # Create a heartbeat task to log progress
                    heartbeat_task = await self._create_heartbeat_task(
                        metric, request_id, agent_timeout
                    )

                    # Wait for either communication or timeout, cancel heartbeat on completion
                    try:
                        response = await asyncio.wait_for(
                            communication_task,
                            timeout=agent_timeout,
                        )
                        heartbeat_task.cancel()

                        # If we get here, the request was successful
                        break

                    except asyncio.TimeoutError:
                        # Cancel both tasks on timeout
                        heartbeat_task.cancel()
                        communication_task.cancel()
                        raise

                except asyncio.TimeoutError as e:
                    last_exception = e
                    logger.error(
                        f"Agent {metric} timed out after {agent_timeout} seconds (attempt {attempt + 1}/{settings.agent_retry_attempts + 1})"
                    )

                    # Log additional timeout context for debugging
                    log_agent_communication(
                        logger,
                        "agent_timeout_occurred",
                        f"{metric}_agent",
                        metric,
                        request_id,
                        {
                            "timeout_seconds": agent_timeout,
                            "attempt": attempt + 1,
                            "max_attempts": settings.agent_retry_attempts + 1,
                            "llm_timeout": settings.llm_request_timeout,
                            "will_retry": attempt < settings.agent_retry_attempts,
                        },
                    )

                    # Try to reset runtime on timeout to prevent stale state
                    if attempt < settings.agent_retry_attempts:
                        logger.warning(
                            f"Resetting runtime after {metric} agent timeout on attempt {attempt + 1}"
                        )
                        await self._emergency_runtime_reset()

                    if attempt >= settings.agent_retry_attempts:
                        raise RuntimeError(
                            f"Agent {metric} communication timeout after {settings.agent_retry_attempts + 1} attempts (timeouts: {agent_timeout}s each)"
                        )
                    continue

            except Exception as e:
                last_exception = e
                logger.error(
                    f"Agent {metric} communication error on attempt {attempt + 1}: {str(e)}"
                )

                # Try runtime reset on certain types of errors
                if (
                    "timeout" in str(e).lower()
                    or "communication" in str(e).lower()
                    or "runtime" in str(e).lower()
                ):
                    if attempt < settings.agent_retry_attempts:
                        logger.warning(
                            f"Resetting runtime after {metric} agent error: {str(e)}"
                        )
                        await self._emergency_runtime_reset()

                if attempt >= settings.agent_retry_attempts:
                    raise RuntimeError(
                        f"Failed to communicate with {metric} agent: {str(e)}"
                    )
                continue

        communication_time = time.time() - request_start_time

        log_performance_metric(
            logger,
            f"{metric}_agent_communication_time",
            communication_time,
            context={
                "agent_id": str(agent_id),
                "request_id": request_id,
                "metric": metric,
                "total_attempts": attempt + 1 if "attempt" in locals() else 1,
            },
        )

        # Parse the JSON response from the agent
        try:
            if isinstance(response, str):
                # Parse the JSON response into AgentEvaluationResult components
                evaluation, response_request_id, agent_id_name = (
                    AgentEvaluationResult.parse_message(response)
                )

                log_agent_communication(
                    logger,
                    "message_send_success",
                    f"{metric}_agent",
                    metric,
                    request_id,
                    {
                        "agent_id": str(agent_id),
                        "communication_time": communication_time,
                        "response_type": "AgentEvaluationResult",
                        "evaluation_rating": evaluation.rating,
                        "evaluation_score": evaluation.score,
                        "response_request_id": response_request_id,
                        "agent_id_name": agent_id_name,
                    },
                )
                return evaluation
            else:
                log_agent_communication(
                    logger,
                    "message_send_invalid_response",
                    f"{metric}_agent",
                    metric,
                    request_id,
                    {
                        "agent_id": str(agent_id),
                        "communication_time": communication_time,
                        "response_type": type(response).__name__,
                    },
                )

                logger.error(
                    f"Unexpected response type from {metric} agent: {type(response)}"
                )
                raise ValueError(f"Invalid response from {metric} agent")
        except Exception as e:
            log_agent_communication(
                logger,
                "message_parse_error",
                f"{metric}_agent",
                metric,
                request_id,
                {
                    "agent_id": str(agent_id),
                    "communication_time": communication_time,
                    "parse_error": str(e),
                },
            )
            logger.error(f"Failed to parse response from {metric} agent: {str(e)}")
            raise ValueError(f"Failed to parse response from {metric} agent: {str(e)}")

    def _prepare_evaluation_context(
        self, request: EvaluationRequest
    ) -> EvaluationContext:
        """Prepare evaluation context from request"""
        context_chunks = [
            request.chunk_1,
            request.chunk_2,
            request.chunk_3,
            request.chunk_4,
            request.chunk_5,
        ]

        # Filter out empty chunks
        context_chunks = [chunk for chunk in context_chunks if chunk.strip()]

        # Use the first model from the list, defaulting to gpt-4o-mini
        model = request.model[0] if request.model else "gpt-4o-mini"

        return EvaluationContext(
            user_query=request.user_query,
            ai_response=request.ai_response,
            context_chunks=context_chunks,
            evaluation_criteria={},  # Will be filled by individual agents
            target_metric="",  # Will be set by individual agents
            model=model,
        )

    def _calculate_overall_evaluation(
        self, metric_evaluations: Dict[str, MetricEvaluation]
    ) -> OverallEvaluation:
        """Calculate overall evaluation based on individual metrics"""
        scores = [eval_result.score for eval_result in metric_evaluations.values()]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Determine overall rating based on average score
        if avg_score >= 2.5:
            overall_rating = "Great"
        elif avg_score >= 2.0:
            overall_rating = "Good"
        elif avg_score >= 1.0:
            overall_rating = "Fair"
        else:
            overall_rating = "Poor"

        # Determine badge based on average score
        if avg_score >= 2.5:
            badge = "Platinum"
        elif avg_score >= 2.0:
            badge = "Gold"
        elif avg_score >= 1.0:
            badge = "Silver"
        else:
            badge = "Bronze"

        # Create comprehensive summary
        metric_summaries = []
        detailed_reasoning_parts = []

        for metric, evaluation in metric_evaluations.items():
            metric_summaries.append(f"{metric.title()}: {evaluation.rating}")
            # Extract first sentence of reasoning for summary
            first_sentence = (
                evaluation.reasoning.split(".")[0]
                if evaluation.reasoning
                else f"No detailed reasoning for {metric}"
            )
            detailed_reasoning_parts.append(f"{metric.title()}: {first_sentence}")

        summary = f"Overall evaluation based on: {', '.join(metric_summaries)}. Average score: {avg_score:.1f}/3.0. Key findings: {'; '.join(detailed_reasoning_parts[:2])}..."

        return OverallEvaluation(
            overall_rating=overall_rating,
            overall_score=round(avg_score, 1),
            overall_badge=badge,
            summary=summary,
        )

    def get_evaluation_status(self, evaluation_id: str) -> Dict[str, Any]:
        """Get status of an ongoing evaluation"""
        if evaluation_id in self.active_evaluations:
            eval_info = self.active_evaluations[evaluation_id]
            return {
                "evaluation_id": evaluation_id,
                "status": eval_info["status"],
                "elapsed_time": time.time() - eval_info["start_time"],
                "selected_metrics": eval_info.get("selected_metrics", []),
            }
        return {"evaluation_id": evaluation_id, "status": "not_found"}

    def get_active_evaluations_count(self) -> int:
        """Get count of currently active evaluations"""
        return len(self.active_evaluations)

    async def _create_heartbeat_task(
        self, metric: str, request_id: str, timeout: float
    ):
        """Create a heartbeat task to monitor agent communication progress"""

        async def heartbeat():
            start_time = time.time()
            heartbeat_interval = min(
                timeout / 4, 10
            )  # Send heartbeat every 1/4 of timeout or 10s max

            while True:
                try:
                    await asyncio.sleep(heartbeat_interval)
                    elapsed = time.time() - start_time
                    remaining = timeout - elapsed

                    if remaining <= 0:
                        break

                    logger.info(
                        f"Heartbeat: {metric} agent communication active for {elapsed:.1f}s "
                        f"(remaining: {remaining:.1f}s, request: {request_id})"
                    )

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Heartbeat error for {metric} agent: {str(e)}")
                    break

        return asyncio.create_task(heartbeat())

    async def _emergency_runtime_reset(self):
        """Emergency reset of the AutoGen runtime to clear stuck state"""
        try:
            logger.warning("Performing emergency runtime reset...")

            # Store current agent definitions
            agents_backup = self.agents.copy() if hasattr(self, "agents") else {}

            # Clear active evaluations
            self.active_evaluations.clear()

            # Force shutdown current runtime
            if self.runtime:
                try:
                    await asyncio.wait_for(self.runtime.stop(), timeout=5.0)
                except (asyncio.TimeoutError, Exception) as e:
                    logger.warning(f"Force shutdown timeout/error (expected): {str(e)}")
                finally:
                    self.runtime = None
                    if hasattr(self, "_agents_registered"):
                        self._agents_registered = False

            # Small delay to allow cleanup
            await asyncio.sleep(0.5)

            # Reinitialize runtime
            self._initialize_runtime()

            # Restore agents if we had them
            if agents_backup:
                self.agents = agents_backup

            # Re-register agents and start runtime
            await self._register_agents()

            logger.info("Emergency runtime reset completed")

        except Exception as e:
            logger.error(f"Emergency runtime reset failed: {str(e)}")
            # If reset fails, force a complete reinit
            self.runtime = None
            if hasattr(self, "_agents_registered"):
                self._agents_registered = False
            self._initialize_runtime()

    async def shutdown(self):
        """Shutdown the AutoGen runtime"""
        if self.runtime:
            try:
                # Clear active evaluations
                self.active_evaluations.clear()

                # Stop the runtime with timeout
                await asyncio.wait_for(self.runtime.stop(), timeout=30.0)
                logger.info("AutoGen runtime shutdown completed")
            except asyncio.TimeoutError:
                logger.error("AutoGen runtime shutdown timed out")
            except Exception as e:
                logger.error(f"Error during AutoGen runtime shutdown: {str(e)}")
            finally:
                self.runtime = None
                self._agents_registered = False


class OrchestratorFactory:
    """Factory for creating and managing orchestrator instances"""

    _instance = None

    @classmethod
    def get_orchestrator(cls) -> AutoGenEvaluationOrchestrator:
        """Get singleton orchestrator instance"""
        if cls._instance is None:
            cls._instance = AutoGenEvaluationOrchestrator()
        return cls._instance

    @classmethod
    async def reset_orchestrator(cls):
        """Reset orchestrator instance (useful for testing)"""
        if cls._instance:
            try:
                await cls._instance.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down orchestrator during reset: {str(e)}")
            finally:
                cls._instance = None


# Global orchestrator instance
def get_orchestrator() -> AutoGenEvaluationOrchestrator:
    """Get the global orchestrator instance"""
    return OrchestratorFactory.get_orchestrator()
