"""
LiteLLM proxy client for model interactions
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional

import litellm
from litellm import acompletion

from src.config import get_settings
from src.logging_utils import (
    log_llm_interaction,
    log_performance_metric,
    timing_decorator,
    create_logger_with_context,
)

logger = create_logger_with_context(__name__)
settings = get_settings()


class LLMProxyClient:
    """Client for interacting with LLM models via LiteLLM"""

    def __init__(self):
        self.settings = settings
        self._configure_litellm()

    def _configure_litellm(self):
        """Configure LiteLLM with API keys and settings"""
        # Set API keys
        if self.settings.openai_api_key:
            litellm.openai_key = self.settings.openai_api_key

        if self.settings.anthropic_api_key:
            litellm.anthropic_key = self.settings.anthropic_api_key

        # Configure proxy if provided
        if (
            self.settings.litellm_proxy_url
            and self.settings.litellm_proxy_url.strip()
            and not self.settings.litellm_proxy_url.strip().startswith("#")
            and "http" in self.settings.litellm_proxy_url.lower()
        ):
            litellm.api_base = self.settings.litellm_proxy_url.strip()

        # Set default temperature and max tokens
        litellm.temperature = self.settings.autogen_temperature
        litellm.max_tokens = self.settings.autogen_max_tokens

    def get_model_name(self) -> str:
        """Get the appropriate model name based on provider selection"""
        if self.settings.model_provider == "gpt":
            return self.settings.gpt_model
        elif self.settings.model_provider == "claude":
            return self.settings.claude_model
        else:
            return self.settings.gpt_model  # Default fallback

    @timing_decorator("llm_chat_completion")
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> str:
        """
        Generate chat completion using the specified or configured model

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Override model name (if not provided, uses configured model)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional parameters for the model

        Returns:
            Generated response content
        """
        request_start_time = time.time()
        model_name = model if model else self.get_model_name()

        try:
            # Use provided parameters or fall back to defaults
            temp = (
                temperature
                if temperature is not None
                else self.settings.autogen_temperature
            )
            max_tok = (
                max_tokens
                if max_tokens is not None
                else self.settings.autogen_max_tokens
            )

            # Calculate total input tokens/characters for logging
            total_input_chars = sum(len(msg.get("content", "")) for msg in messages)

            request_data = {
                "model": model_name,
                "message_count": len(messages),
                "total_input_chars": total_input_chars,
                "temperature": temp,
                "max_tokens": max_tok,
            }

            log_llm_interaction(
                logger, "request_start", model_name, request_data=request_data
            )

            logger.info(f"Making completion request to {model_name}")

            # Apply timeout to LLM call to prevent hanging
            llm_timeout = (
                timeout if timeout is not None else self.settings.llm_request_timeout
            )

            try:
                response = await asyncio.wait_for(
                    acompletion(
                        model=model_name,
                        messages=messages,
                        temperature=temp,
                        max_tokens=max_tok,
                        **kwargs,
                    ),
                    timeout=llm_timeout,
                )
            except asyncio.TimeoutError:
                timeout_context = {
                    "model": model_name,
                    "timeout_seconds": llm_timeout,
                    "input_chars": total_input_chars,
                    "message_count": len(messages),
                    "temperature": temp,
                    "max_tokens": max_tok,
                }

                log_llm_interaction(
                    logger,
                    "timeout_occurred",
                    model_name,
                    request_data=request_data,
                    response_data=timeout_context,
                )

                logger.error(
                    f"LLM request to {model_name} timed out after {llm_timeout}s "
                    f"(input: {total_input_chars} chars, messages: {len(messages)})"
                )
                raise RuntimeError(
                    f"LLM request timeout after {llm_timeout}s - model: {model_name}, "
                    f"input: {total_input_chars} chars"
                )

            request_time = time.time() - request_start_time
            content = response.choices[0].message.content

            response_data = {
                "content_length": len(content),
                "response_chars": len(content),
                "success": True,
            }

            log_llm_interaction(
                logger,
                "request_success",
                model_name,
                request_data=request_data,
                response_data=response_data,
                processing_time=request_time,
            )

            log_performance_metric(
                logger,
                "llm_response_time",
                request_time,
                context={
                    "model": model_name,
                    "input_chars": total_input_chars,
                    "output_chars": len(content),
                    "message_count": len(messages),
                },
            )

            logger.info(
                f"Received response from {model_name}: {len(content)} characters in {request_time:.3f}s"
            )

            return content

        except Exception as e:
            request_time = time.time() - request_start_time

            error_data = {
                "error": str(e),
                "error_type": type(e).__name__,
                "success": False,
            }

            log_llm_interaction(
                logger,
                "request_failed",
                model_name,
                request_data=(
                    request_data
                    if "request_data" in locals()
                    else {"model": model_name}
                ),
                response_data=error_data,
                processing_time=request_time,
            )

            logger.error(
                f"Error in chat completion after {request_time:.3f}s: {str(e)}"
            )
            raise RuntimeError(f"LLM completion failed: {str(e)}")

    async def evaluate_metric(
        self,
        metric: str,
        user_query: str,
        ai_response: str,
        context_chunks: List[str],
        evaluation_criteria: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate a specific metric using the LLM

        Args:
            metric: The metric to evaluate (Accuracy, Hallucination, etc.)
            user_query: Original user query
            ai_response: AI response to evaluate
            context_chunks: Context chunks used for the response
            evaluation_criteria: Criteria for the specific metric

        Returns:
            Evaluation result dictionary
        """
        try:
            # Prepare context
            context_text = "\n\n".join(
                [chunk for chunk in context_chunks if chunk.strip()]
            )

            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(
                metric, user_query, ai_response, context_text, evaluation_criteria
            )

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert evaluator for AI responses in legal/professional contexts.",
                },
                {"role": "user", "content": prompt},
            ]

            response = await self.chat_completion(messages)

            # Parse the response to extract evaluation details
            evaluation = self._parse_evaluation_response(response, metric)

            return evaluation

        except Exception as e:
            logger.error(f"Error evaluating {metric}: {str(e)}")
            # Return a default poor evaluation on error
            return {
                "metric": metric,
                "rating": "Poor",
                "score": 0,
                "badge": "Bronze",
                "reasoning": f"Evaluation failed due to error: {str(e)}",
            }

    def _create_evaluation_prompt(
        self,
        metric: str,
        user_query: str,
        ai_response: str,
        context_text: str,
        criteria: Dict[str, Any],
    ) -> str:
        """Create a detailed evaluation prompt for a specific metric"""

        base_prompt = f"""
Please evaluate the following AI response based on the {metric} metric.

USER QUERY:
{user_query}

AI RESPONSE:
{ai_response}

CONTEXT CHUNKS:
{context_text}

EVALUATION CRITERIA FOR {metric.upper()}:
{criteria.get(metric, '')}

RATING SCALE:
- 3 (Great): {criteria.get(f'{metric}_3', 'Excellent performance')}
- 2 (Good): {criteria.get(f'{metric}_2', 'Good performance with minor issues')}
- 1 (Fair): {criteria.get(f'{metric}_1', 'Deficient with major issues')}
- 0 (Poor): {criteria.get(f'{metric}_0', 'Bad performance, not usable')}

Please provide your evaluation in the following format:
RATING: [Great/Good/Fair/Poor]
SCORE: [3/2/1/0]
REASONING: [Detailed explanation of your evaluation, including specific examples from the response]

Focus specifically on {metric.lower()} aspects and provide concrete examples to support your rating.
"""

        return base_prompt.strip()

    def _parse_evaluation_response(self, response: str, metric: str) -> Dict[str, Any]:
        """Parse the LLM evaluation response into structured data"""
        try:
            lines = response.strip().split("\n")
            rating = "Poor"
            score = 0
            reasoning = "No reasoning provided"

            for line in lines:
                line = line.strip()
                if line.startswith("RATING:"):
                    rating = line.split(":", 1)[1].strip()
                elif line.startswith("SCORE:"):
                    try:
                        score = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        score = 0
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()

            # Map score to badge
            badge_mapping = {3: "Platinum", 2: "Gold", 1: "Silver", 0: "Bronze"}
            badge = badge_mapping.get(score, "Bronze")

            return {
                "metric": metric,
                "rating": rating,
                "score": score,
                "badge": badge,
                "reasoning": reasoning,
            }

        except Exception as e:
            logger.error(f"Error parsing evaluation response: {str(e)}")
            return {
                "metric": metric,
                "rating": "Poor",
                "score": 0,
                "badge": "Bronze",
                "reasoning": f"Failed to parse evaluation: {str(e)}",
            }


# Global client instance
llm_client = LLMProxyClient()
