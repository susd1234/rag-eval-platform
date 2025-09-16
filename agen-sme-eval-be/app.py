#!/usr/bin/env python3
"""
Main FastAPI application for AI Assisted SME Evaluation Platform of RAG Application
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.api import evaluation_router
from src.config import get_settings
from src.logging_utils import setup_enhanced_logging, create_logger_with_context

# Setup enhanced logging first
setup_enhanced_logging()

logger = create_logger_with_context(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting AI Assisted SME Evaluation Platform...")
    logger.info(f"Running on port {settings.port}")
    logger.info(f"Using model provider: {settings.model_provider}")
    yield
    logger.info("Shutting down AI Assisted SME Evaluation Platform...")


# Create FastAPI application
app = FastAPI(
    title="AI Assisted SME Evaluation Platform",
    description="Agentic AI service for evaluating RAG applications on Accuracy, Hallucination, Authoritativeness, and Usefulness",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(evaluation_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "AI Assisted SME Evaluation Platform",
        "version": "1.0.0",
        "description": "Evaluates RAG applications using multi-agent AI system",
        "metrics": ["Accuracy", "Hallucination", "Authoritativeness", "Usefulness"],
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "sme-eval-platform"}


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True if settings.environment == "development" else False,
        log_level="info",
    )
