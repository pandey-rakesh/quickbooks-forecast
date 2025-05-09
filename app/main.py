"""
Main application module for QuickBooks Sales Forecasting API.

This module initializes the FastAPI application and includes all routers.
"""

import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import router as api_router
from app.config import API_TITLE, API_DESCRIPTION, API_VERSION, API_PREFIX
from app.utils import setup_logger

# Set up logging
logger = setup_logger("app.main")

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(api_router, prefix=API_PREFIX)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Status information
    """
    return {
        "status": "healthy",
        "version": API_VERSION
    }


if __name__ == "__main__":
    import uvicorn

    # Start server with hot reload for development
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
