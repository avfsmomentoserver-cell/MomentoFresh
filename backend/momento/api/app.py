"""
FastAPI Application for MomentoFresh

Main API server with all route modules.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..config import settings
from ..db import init_database
from ..hub import manager as ws_manager
from ..store import seed_initial_data

logger = logging.getLogger(__name__)

# Import route modules
from .routes import (
    core,
    rounds,
    analysis,
    pressure,
    backtest,
    linguistics,
    ingest,
    ws,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting MomentoFresh API server...")
    
    # Initialize database
    init_database()
    
    # Seed initial data
    seed_initial_data()
    
    logger.info("Database initialized and data seeded")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MomentoFresh API server...")
    logger.info("Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title="MomentoFresh API",
    description="Advanced Analytics & Forecasting Platform for Crash Games",
    version="4.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if not settings.cors_allow_all else ["*"],
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc),
        },
    )


# Include route modules
app.include_router(core.router, prefix="/api/v1", tags=["core"])
app.include_router(rounds.router, prefix="/api/v1", tags=["rounds"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(pressure.router, prefix="/api/v1", tags=["pressure"])
app.include_router(backtest.router, prefix="/api/v1", tags=["backtest"])
app.include_router(linguistics.router, prefix="/api/v1", tags=["linguistics"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
app.include_router(ws.router, prefix="/api/v1", tags=["websocket"])


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "version": "4.0.0"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "MomentoFresh API",
        "version": "4.0.0",
        "description": "Advanced Analytics & Forecasting Platform for Crash Games",
        "docs": "/docs",
        "health": "/health",
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: websockets.WebSocketServerProtocol):
    """Main WebSocket endpoint."""
    await ws_manager.connect(websocket)
    try:
        async for data in websocket:
            pass  # Messages handled by manager
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ws_manager.disconnect(websocket)


# For importing in run_api.py
import websockets
from ..hub import manager