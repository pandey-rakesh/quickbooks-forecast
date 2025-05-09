"""
Main application module for the QuickBooks Sales Forecasting API.

This module initializes and configures the FastAPI application.
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from typing import Dict, Any

from app.config import API_TITLE, API_DESCRIPTION, API_VERSION
from app.api import router
from app.utils import setup_logger

# Set up logger
logger = setup_logger(__name__)


# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log request details and timing.
    """
    start_time = time.time()
    
    # Process the request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.4f}s"
        )
        
        return response
    
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request: {request.method} {request.url.path} "
            f"- Error: {str(e)} "
            f"- Time: {process_time:.4f}s"
        )
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )


# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


# Include API router
app.include_router(router)


# Add health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: Status information
    """
    return {
        "status": "ok",
        "api_version": API_VERSION,
        "api_title": API_TITLE
    }


# Add root endpoint that redirects to docs
@app.get("/")
async def root():
    """
    Root endpoint that redirects to API documentation.
    
    Returns:
        dict: Welcome message and links
    """
    return {
        "message": f"Welcome to {API_TITLE}",
        "version": API_VERSION,
        "documentation": "/docs",
        "redoc": "/redoc",
        "health_check": "/health"
    }


if __name__ == "__main__":
    """
    Run the application using Uvicorn when executed directly.
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )