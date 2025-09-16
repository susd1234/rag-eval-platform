"""
AutoGen Core v0.7.4 based evaluation agents for SME platform
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod

from autogen_core import RoutedAgent, MessageContext, message_handler
import json

from src.models import EvaluationContext, MetricEvaluation
from src.proxy_client import llm_client
from src.config import get_settings
from src.agent_config_loader import get_agent_config, AgentConfig
from src.logging_utils import (
    log_agent_communication,
    log_evaluation_progress,
    log_performance_metric,
    timing_decorator,
    create_logger_with_context,
)

logger = create_logger_with_context(__name__)
settings = get_settings()


class EvaluationCriteria:
    """Centralized evaluation criteria definitions"""

    ACCURACY = {
        "definition": "Response contains information that is true and correct. It doesn't have any hallucination (information that is completely invented by the AI that does not exist) but some aspects of the response is incorrect in some way.",
        "3": "Great - Response is accurate and contains no factual errors or hallucinations",
        "2": "Good - Response is mostly accurate with minor factual issues",
        "1": "Fair - Response has some accuracy but contains notable factual errors",
        "0": "Poor - Response contains significant factual errors or does not provide expected results",
    }

    HALLUCINATION = {
        "definition": "Response should not contain information that is completely 'made up' (i.e., citations or references to information that does not exist and cannot be verified).",
        "3": "Great - No fabricated information, all references are verifiable",
        "2": "Good - Minimal risk of fabrication, references are mostly verifiable",
        "1": "Fair - Some potentially fabricated elements or unverifiable references",
        "0": "Poor - Contains made up law, citations, or completely fabricated information",
    }

    AUTHORITATIVENESS = {
        "definition": "Citations should be included as instructed for each task. Where included citations should be individually checked as indicated by your Lead. Citations should be valid and support the legal statements in the response.",
        "3": "Great - Citations are relevant, support the response, represent good law, and are authoritative/citable",
        "2": "Good - Citations are relevant and support the response but may lack recency or be from lower courts",
        "1": "Fair - Citations support the response but are not relevant to query or not good law or not authoritative",
        "0": "Poor - Citations do not support any part of the AI-generated response",
    }

    USEFULNESS = {
        "definition": "Overall assessment of response quality considering accuracy, hallucination avoidance, responsiveness, completeness, authoritativeness and appropriateness.",
        "3": "Great - Excellent response that is accurate, non-hallucinatory, responsive, complete, authoritative and appropriate",
        "2": "Good - OK response without accuracy issues but may have minor issues in other dimensions",
        "1": "Fair - Deficient response related to prompt but has major issues making it insufficient for users",
        "0": "Poor - Bad response unrelated to prompt or has major issues making it embarrassing to display",
    }


class AgentEvaluationRequest:
    """Message type for evaluation requests - Simple string-based for AutoGen compatibility"""

    @staticmethod
    def create_message(context: EvaluationContext, request_id: str) -> str:
        """Create a JSON string message from EvaluationContext"""
        message_data = {
            "user_query": context.user_query,
            "ai_response": context.ai_response,
            "context_chunks": context.context_chunks,
            "model": context.model,
            "request_id": request_id,
            "message_type": "evaluation_request",
        }
        return json.dumps(message_data)

    @staticmethod
    def parse_message(message: str) -> EvaluationContext:
        """Parse JSON string message to EvaluationContext"""
        data = json.loads(message)
        return EvaluationContext(
            user_query=data["user_query"],
            ai_response=data["ai_response"],
            context_chunks=data["context_chunks"],
            evaluation_criteria={},
            target_metric="",
            model=data.get("model", "gpt-4o-mini"),
        )

    @staticmethod
    def get_request_id(message: str) -> str:
        """Extract request ID from message"""
        data = json.loads(message)
        return data["request_id"]


class AgentEvaluationResult:
    """Message type for evaluation results - Simple string-based for AutoGen compatibility"""

    @staticmethod
    def create_message(
        evaluation: MetricEvaluation, request_id: str, agent_id: str
    ) -> str:
        """Create a JSON string message from MetricEvaluation"""
        message_data = {
            "metric": evaluation.metric,
            "rating": evaluation.rating,
            "score": evaluation.score,
            "badge": evaluation.badge,
            "reasoning": evaluation.reasoning,
            "request_id": request_id,
            "agent_id": agent_id,
            "message_type": "evaluation_result",
        }
        return json.dumps(message_data)

    @staticmethod
    def parse_message(message: str) -> tuple[MetricEvaluation, str, str]:
        """Parse JSON string message to MetricEvaluation, request_id, agent_id"""
        data = json.loads(message)
        evaluation = MetricEvaluation(
            metric=data["metric"],
            rating=data["rating"],
            score=data["score"],
            badge=data["badge"],
            reasoning=data["reasoning"],
        )
        return evaluation, data["request_id"], data["agent_id"]


class BaseEvaluationAgent(RoutedAgent):
    """Base class for evaluation agents using AutoGen Core v0.7.4"""

    def __init__(self, name: str, metric: str):
        super().__init__(name)
        self.metric = metric
        self.agent_name = name  # Store the name for later use

        # Load configuration from YAML
        self.config = get_agent_config(metric.lower())
        if self.config:
            logger.info(f"Loaded YAML configuration for {metric} agent")
        else:
            logger.warning(
                f"No YAML configuration found for {metric} agent, using fallback"
            )
            # Fallback to hardcoded criteria if YAML config not available
            self.criteria = getattr(EvaluationCriteria, metric.upper())

    @message_handler
    @timing_decorator("agent_message_handling")
    async def handle_evaluation_request(self, message: str, ctx: MessageContext) -> str:
        """Handle evaluation request for this agent's metric"""
        request_start_time = time.time()

        try:
            # Parse the JSON message
            context = AgentEvaluationRequest.parse_message(message)
            request_id = AgentEvaluationRequest.get_request_id(message)

            log_agent_communication(
                logger,
                "message_received",
                self.agent_name,
                self.metric,
                request_id,
                {
                    "context_chunks_count": len(context.context_chunks),
                    "query_length": len(context.user_query),
                    "response_length": len(context.ai_response),
                    "agent_metric": self.metric,
                },
            )

            logger.info(
                f"{self.metric} agent processing evaluation request {request_id}"
            )

            # Perform the evaluation
            evaluation_start_time = time.time()
            evaluation_result = await self._evaluate_metric(context)
            evaluation_time = time.time() - evaluation_start_time

            log_performance_metric(
                logger,
                f"{self.metric}_evaluation_time",
                evaluation_time,
                context={
                    "agent_name": self.agent_name,
                    "request_id": request_id,
                    "metric": self.metric,
                },
            )

            log_agent_communication(
                logger,
                "evaluation_completed",
                self.agent_name,
                self.metric,
                request_id,
                {
                    "rating": evaluation_result["rating"],
                    "score": evaluation_result["score"],
                    "badge": evaluation_result["badge"],
                    "reasoning_length": len(evaluation_result["reasoning"]),
                    "evaluation_time": evaluation_time,
                },
            )

            logger.info(
                f"{self.metric} agent completed evaluation: {evaluation_result['rating']}"
            )

            metric_eval = MetricEvaluation(**evaluation_result)

            total_processing_time = time.time() - request_start_time

            log_agent_communication(
                logger,
                "message_response_ready",
                self.agent_name,
                self.metric,
                request_id,
                {
                    "total_processing_time": total_processing_time,
                    "evaluation_successful": True,
                    "final_rating": evaluation_result["rating"],
                    "final_score": evaluation_result["score"],
                },
            )

            # Create and return JSON message
            return AgentEvaluationResult.create_message(
                metric_eval,
                request_id,
                self.agent_name,
            )

        except Exception as e:
            total_processing_time = time.time() - request_start_time

            # Try to get request_id for error logging
            try:
                request_id = AgentEvaluationRequest.get_request_id(message)
            except:
                request_id = "unknown"

            log_agent_communication(
                logger,
                "evaluation_failed",
                self.agent_name,
                self.metric,
                request_id,
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "total_processing_time": total_processing_time,
                    "evaluation_successful": False,
                },
            )

            logger.error(f"Error in {self.metric} agent: {str(e)}")
            error_eval = MetricEvaluation(
                metric=self.metric,
                rating="Poor",
                score=0,
                badge="Bronze",
                reasoning=f"Evaluation failed: {str(e)}",
            )

            return AgentEvaluationResult.create_message(
                error_eval,
                request_id,
                self.agent_name,
            )

    @abstractmethod
    async def _evaluate_metric(self, context: EvaluationContext) -> Dict[str, Any]:
        """Evaluate the specific metric - to be implemented by subclasses"""
        pass

    def _create_specialized_prompt(self, context: EvaluationContext) -> str:
        """Create a specialized prompt for this metric"""
        context_text = "\n\n".join(
            [chunk for chunk in context.context_chunks if chunk.strip()]
        )

        # Use YAML configuration if available, otherwise fallback to hardcoded
        if self.config:
            definition = self.config.definition
            rating_scale = self._build_rating_scale_from_config()
            specific_instructions = self._get_specific_instructions_from_config()
        else:
            definition = self.criteria["definition"]
            rating_scale = f"""- 3 (Great): {self.criteria['3']}
- 2 (Good): {self.criteria['2']}
- 1 (Fair): {self.criteria['1']}
- 0 (Poor): {self.criteria['0']}"""
            specific_instructions = self._get_specific_instructions()

        prompt = f"""
You are a specialized {self.metric} evaluation expert for AI responses in professional/legal contexts.

EVALUATION TASK: Assess the {self.metric} of the AI response below.

USER QUERY:
{context.user_query}

AI RESPONSE TO EVALUATE:
{context.ai_response}

CONTEXT CHUNKS PROVIDED:
{context_text}

{self.metric.upper()} EVALUATION CRITERIA:
{definition}

RATING SCALE:
{rating_scale}

{specific_instructions}

REASONING REQUIREMENTS:
Your reasoning must be comprehensive and include:
1. SPECIFIC EVIDENCE: Quote specific parts of the AI response that support your evaluation
2. CONTEXT ANALYSIS: Explain how the provided context chunks relate to your assessment
3. DETAILED JUSTIFICATION: Provide clear explanations for why you assigned this particular rating
4. COMPARATIVE ANALYSIS: Reference the rating criteria and explain how the response meets or fails to meet each level
5. CONCRETE EXAMPLES: Identify specific instances that demonstrate the quality level you've assigned

Provide your evaluation in this exact format:
RATING: [Great/Good/Fair/Poor]
SCORE: [3/2/1/0]
REASONING: [Comprehensive reasoning that includes specific evidence from the response, analysis of context chunks, detailed justification for the rating, comparative analysis against criteria, and concrete examples. This should be at least 3-4 sentences with specific quotes and references.]
"""
        return prompt.strip()

    def _build_rating_scale_from_config(self) -> str:
        """Build rating scale from YAML configuration"""
        if not self.config:
            return ""

        rating_lines = []
        for rating in [3, 2, 1, 0]:
            label = self.config.get_rating_label(rating)
            description = self.config.get_rating_description(rating)
            rating_lines.append(f"- {rating} ({label}): {description}")

        return "\n".join(rating_lines)

    def _get_specific_instructions_from_config(self) -> str:
        """Get specific instructions from YAML configuration"""
        if not self.config:
            return self._get_specific_instructions()

        instructions = []

        # Add focus areas
        if self.config.focus_areas:
            instructions.append(f"{self.metric.upper()} FOCUS AREAS:")
            for i, area in enumerate(self.config.focus_areas, 1):
                instructions.append(f"{i}. {area}")
            instructions.append("")

        # Add detailed reasoning guidelines
        instructions.append(f"DETAILED REASONING GUIDELINES FOR {self.metric.upper()}:")

        # Add agent-specific instructions based on metric
        if (
            self.metric.lower() == "authoritativeness"
            and self.config.authority_hierarchy
        ):
            instructions.append(
                "- List each citation mentioned in the AI response and evaluate its authority level"
            )
            instructions.append(
                "- Explain how each cited source directly supports or relates to the user's query"
            )
            instructions.append(
                "- Assess the hierarchical quality of sources (statutes, court cases, regulations vs. secondary sources)"
            )
            instructions.append(
                "- Note the jurisdictional relevance (e.g., California law for California questions)"
            )
            instructions.append(
                "- Comment on the recency and current validity of cited legal authorities"
            )
            instructions.append(
                "- Quote specific parts of the response that are supported by authoritative sources"
            )
            instructions.append(
                "- Identify any statements that lack proper authoritative support"
            )
            instructions.append(
                "- Explain whether the citations collectively provide strong legal foundation for the response"
            )
            instructions.append(
                "- Note the balance between primary and secondary sources if both are used"
            )
            instructions.append("")
            instructions.append(
                "Assess whether citations properly support the legal statements made in the response."
            )

        elif self.metric.lower() == "hallucination" and self.config.detection_methods:
            instructions.append(
                "- Identify all specific citations, case names, and legal references in the AI response"
            )
            instructions.append(
                "- Cross-reference each citation against the provided context chunks"
            )
            instructions.append(
                "- Quote any suspicious or unverifiable claims and explain why they appear fabricated"
            )
            instructions.append(
                "- Explain the difference between general legal concepts (acceptable) vs. specific false claims (hallucination)"
            )
            instructions.append(
                "- Note any overly specific details that lack proper source attribution"
            )
            instructions.append(
                '- Identify patterns that suggest information was "made up" rather than recalled from valid sources'
            )
            instructions.append(
                "- If no hallucinations found, specify which elements you verified and why they appear legitimate"
            )
            instructions.append(
                "- Provide specific examples of verifiable vs. potentially fabricated content"
            )
            instructions.append("")
            instructions.append(
                "Verify that all specific legal references, case names, and statutory citations can be validated."
            )

        elif self.metric.lower() == "usefulness" and self.config.quality_dimensions:
            instructions.append(
                "- Analyze how directly the response addresses the specific user query"
            )
            instructions.append(
                "- Evaluate the completeness by identifying what questions are answered vs. what might be missing"
            )
            instructions.append(
                "- Comment on the practical value and actionability of the information provided"
            )
            instructions.append(
                "- Assess the clarity and organization of the response structure"
            )
            instructions.append(
                "- Note the appropriateness of legal complexity for the intended audience"
            )
            instructions.append(
                "- Quote specific examples that demonstrate high utility or identify gaps in usefulness"
            )
            instructions.append(
                "- Explain how well the response balances thoroughness with accessibility"
            )
            instructions.append(
                "- Consider whether the response provides sufficient context for practical application"
            )
            instructions.append(
                "- Assess if the response would help a professional make informed decisions"
            )
            instructions.append(
                "- Note any areas where the response could be more useful or complete"
            )
            instructions.append("")
            instructions.append(
                "Consider whether a professional would find this response valuable and actionable."
            )

        else:  # Default for accuracy and others
            instructions.append(
                "- Quote specific statements from the AI response and verify them against context chunks"
            )
            instructions.append(
                "- Identify any factual errors or misrepresentations with specific examples"
            )
            instructions.append(
                "- Explain how well the response aligns with the provided legal sources"
            )
            instructions.append(
                "- Note any logical inconsistencies or contradictions within the response"
            )
            instructions.append(
                "- Reference specific legal principles or facts that support or contradict the response"
            )
            instructions.append(
                "- Provide examples of accurate information and explain why it's correct"
            )
            instructions.append(
                "- If errors exist, specify what they are and how they deviate from established facts"
            )
            instructions.append("")
            instructions.append(
                "Check each factual claim against the provided context chunks and general knowledge."
            )

        return "\n".join(instructions)

    @abstractmethod
    def _get_specific_instructions(self) -> str:
        """Get metric-specific evaluation instructions (fallback method)"""
        pass

    def _extract_evaluation_components(
        self, response: str, metric: str
    ) -> Dict[str, Any]:
        """Extract rating, score, and reasoning from LLM response"""
        try:
            lines = response.strip().split("\n")
            rating = "Poor"
            score = 0
            reasoning = "No reasoning provided"
            reasoning_lines = []
            in_reasoning_section = False

            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("RATING:"):
                    rating = line.split(":", 1)[1].strip()
                elif line.startswith("SCORE:"):
                    try:
                        score = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        score = 0
                elif line.startswith("REASONING:"):
                    # Extract the initial reasoning content after the colon
                    initial_reasoning = line.split(":", 1)[1].strip()
                    if initial_reasoning:
                        reasoning_lines.append(initial_reasoning)
                    in_reasoning_section = True
                elif in_reasoning_section and line:
                    # Continue collecting reasoning lines until we hit another section or end
                    if not (
                        line.startswith("RATING:")
                        or line.startswith("SCORE:")
                        or line.startswith("REASONING:")
                    ):
                        reasoning_lines.append(line)

            # Join all reasoning lines into a comprehensive reasoning text
            if reasoning_lines:
                reasoning = " ".join(reasoning_lines).strip()

            # Ensure minimum reasoning quality
            if not reasoning or len(reasoning) < 20:
                reasoning = f"Limited reasoning provided for {metric} evaluation. Rating: {rating}, Score: {score}"

            # Validate and normalize rating
            valid_ratings = ["Great", "Good", "Fair", "Poor"]
            if rating not in valid_ratings:
                rating = "Poor"
                score = 0

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
            logger.error(f"Error parsing {metric} evaluation response: {str(e)}")
            return {
                "metric": metric,
                "rating": "Poor",
                "score": 0,
                "badge": "Bronze",
                "reasoning": f"Failed to parse evaluation: {str(e)}",
            }


class AccuracyAgent(BaseEvaluationAgent):
    """Agent specialized in evaluating response accuracy"""

    def __init__(self):
        super().__init__("AccuracyAgent", "Accuracy")

    async def _evaluate_metric(self, context: EvaluationContext) -> Dict[str, Any]:
        """Evaluate accuracy of the response"""
        prompt = self._create_specialized_prompt(context)

        # Use system prompt from YAML config if available
        system_prompt = "You are an expert fact-checker and accuracy evaluator for professional AI responses."
        if self.config and self.config.system_prompt:
            system_prompt = self.config.system_prompt

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]

        # Use explicit timeout to prevent hanging
        response = await llm_client.chat_completion(
            messages, model=context.model, timeout=settings.llm_request_timeout
        )
        return self._extract_evaluation_components(response, "Accuracy")

    def _get_specific_instructions(self) -> str:
        return """
ACCURACY FOCUS AREAS:
1. Factual correctness of all statements
2. Absence of hallucinated information
3. Proper representation of cited sources
4. Logical consistency throughout the response
5. Alignment with established legal principles

DETAILED REASONING GUIDELINES FOR ACCURACY:
- Quote specific statements from the AI response and verify them against context chunks
- Identify any factual errors or misrepresentations with specific examples
- Explain how well the response aligns with the provided legal sources
- Note any logical inconsistencies or contradictions within the response
- Reference specific legal principles or facts that support or contradict the response
- Provide examples of accurate information and explain why it's correct
- If errors exist, specify what they are and how they deviate from established facts

Check each factual claim against the provided context chunks and general knowledge.
"""


class HallucinationAgent(BaseEvaluationAgent):
    """Agent specialized in detecting hallucinations"""

    def __init__(self):
        super().__init__("HallucinationAgent", "Hallucination")

    async def _evaluate_metric(self, context: EvaluationContext) -> Dict[str, Any]:
        """Evaluate for hallucinations in the response"""
        prompt = self._create_specialized_prompt(context)

        # Use system prompt from YAML config if available
        system_prompt = "You are an expert in detecting AI hallucinations and fabricated information in professional responses."
        if self.config and self.config.system_prompt:
            system_prompt = self.config.system_prompt

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]

        # Use explicit timeout to prevent hanging
        response = await llm_client.chat_completion(
            messages, model=context.model, timeout=settings.llm_request_timeout
        )
        return self._extract_evaluation_components(response, "Hallucination")

    def _get_specific_instructions(self) -> str:
        return """
HALLUCINATION DETECTION FOCUS:
1. Fabricated case citations or legal references
2. Made-up statutes, regulations, or legal principles
3. Non-existent court decisions or legal precedents
4. Invented legal terminology or concepts
5. False claims about legal procedures or requirements

DETAILED REASONING GUIDELINES FOR HALLUCINATION:
- Identify all specific citations, case names, and legal references in the AI response
- Cross-reference each citation against the provided context chunks
- Quote any suspicious or unverifiable claims and explain why they appear fabricated
- Explain the difference between general legal concepts (acceptable) vs. specific false claims (hallucination)
- Note any overly specific details that lack proper source attribution
- Identify patterns that suggest information was "made up" rather than recalled from valid sources
- If no hallucinations found, specify which elements you verified and why they appear legitimate
- Provide specific examples of verifiable vs. potentially fabricated content

Verify that all specific legal references, case names, and statutory citations can be validated.
"""


class AuthoritativenessAgent(BaseEvaluationAgent):
    """Agent specialized in evaluating authoritativeness of citations"""

    def __init__(self):
        super().__init__("AuthoritativenessAgent", "Authoritativeness")

    async def _evaluate_metric(self, context: EvaluationContext) -> Dict[str, Any]:
        """Evaluate authoritativeness of citations and sources"""
        prompt = self._create_specialized_prompt(context)

        # Use system prompt from YAML config if available
        system_prompt = "You are an expert in legal authority and citation evaluation for professional legal responses."
        if self.config and self.config.system_prompt:
            system_prompt = self.config.system_prompt

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]

        # Use explicit timeout to prevent hanging
        response = await llm_client.chat_completion(
            messages, model=context.model, timeout=settings.llm_request_timeout
        )
        return self._extract_evaluation_components(response, "Authoritativeness")

    def _get_specific_instructions(self) -> str:
        return """
AUTHORITATIVENESS EVALUATION FOCUS:
1. Relevance of citations to the specific query
2. Quality and reliability of cited sources
3. Recency and current validity of legal authorities
4. Hierarchical appropriateness (primary vs secondary sources)
5. Jurisdictional relevance of cited authorities

DETAILED REASONING GUIDELINES FOR AUTHORITATIVENESS:
- List each citation mentioned in the AI response and evaluate its authority level
- Explain how each cited source directly supports or relates to the user's query
- Assess the hierarchical quality of sources (statutes, court cases, regulations vs. secondary sources)
- Note the jurisdictional relevance (e.g., California law for California questions)
- Comment on the recency and current validity of cited legal authorities
- Quote specific parts of the response that are supported by authoritative sources
- Identify any statements that lack proper authoritative support
- Explain whether the citations collectively provide strong legal foundation for the response
- Note the balance between primary and secondary sources if both are used

Assess whether citations properly support the legal statements made in the response.
"""


class UsefulnessAgent(BaseEvaluationAgent):
    """Agent specialized in evaluating overall usefulness"""

    def __init__(self):
        super().__init__("UsefulnessAgent", "Usefulness")

    async def _evaluate_metric(self, context: EvaluationContext) -> Dict[str, Any]:
        """Evaluate overall usefulness of the response"""
        prompt = self._create_specialized_prompt(context)

        # Use system prompt from YAML config if available
        system_prompt = "You are an expert in evaluating the overall usefulness and quality of professional AI responses."
        if self.config and self.config.system_prompt:
            system_prompt = self.config.system_prompt

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]

        # Use explicit timeout to prevent hanging
        response = await llm_client.chat_completion(
            messages, model=context.model, timeout=settings.llm_request_timeout
        )
        return self._extract_evaluation_components(response, "Usefulness")

    def _get_specific_instructions(self) -> str:
        return """
USEFULNESS EVALUATION FOCUS:
1. Responsiveness to the user's specific question
2. Completeness of the answer provided
3. Appropriateness for the intended audience
4. Practical applicability of the information
5. Overall coherence and organization
6. Balance of comprehensiveness vs clarity

DETAILED REASONING GUIDELINES FOR USEFULNESS:
- Analyze how directly the response addresses the specific user query
- Evaluate the completeness by identifying what questions are answered vs. what might be missing
- Comment on the practical value and actionability of the information provided
- Assess the clarity and organization of the response structure
- Note the appropriateness of legal complexity for the intended audience
- Quote specific examples that demonstrate high utility or identify gaps in usefulness
- Explain how well the response balances thoroughness with accessibility
- Consider whether the response provides sufficient context for practical application
- Assess if the response would help a professional make informed decisions
- Note any areas where the response could be more useful or complete

Consider whether a professional would find this response valuable and actionable.
"""


# Agent factory for creating agent instances
def create_evaluation_agents() -> Dict[str, BaseEvaluationAgent]:
    """Create all evaluation agents"""
    return {
        "accuracy": AccuracyAgent(),
        "hallucination": HallucinationAgent(),
        "authoritativeness": AuthoritativenessAgent(),
        "usefulness": UsefulnessAgent(),
    }
