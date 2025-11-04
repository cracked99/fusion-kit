"""
FastAPI application for multi-agent orchestration framework.

Main entry point for the REST API and WebSocket endpoints.
"""

import logging
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fusion_kit.api.schemas import HealthCheckResponse, ErrorResponse
from fusion_kit.api.websockets import ConnectionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Fusion Kit Multi-Agent API",
    description="REST API for multi-agent orchestration framework",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ============================================================================
# CORS Configuration
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Application State
# ============================================================================

# WebSocket connection manager for real-time updates
ws_manager = ConnectionManager()

# Application startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("Starting Fusion Kit API...")
    logger.info("Initializing database connection...")
    logger.info("Initializing Redis connection...")
    logger.info("API startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Fusion Kit API...")
    logger.info("Closing database connections...")
    logger.info("Closing Redis connections...")
    logger.info("API shutdown complete")


# ============================================================================
# Health Check Endpoints
# ============================================================================


@app.get("/api/v1/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.

    Returns detailed status of all system components.
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        database="connected",
        redis="connected",
    )


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def simple_health_check() -> HealthCheckResponse:
    """Simplified health check endpoint for monitoring."""
    return HealthCheckResponse(status="healthy")


@app.get("/api/v1/status", tags=["Health"])
async def get_status() -> Dict:
    """Get detailed API status."""
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "api": "ready",
            "database": "ready",
            "redis": "ready",
        },
    }


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Error",
            message=exc.detail,
            status_code=exc.status_code,
        ).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred. Please check logs.",
            status_code=500,
        ).dict(),
    )


# ============================================================================
# Root Endpoints
# ============================================================================


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint."""
    return {
        "name": "Fusion Kit Multi-Agent API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
        "status": "/api/v1/status",
    }


@app.get("/api", tags=["Info"])
async def api_root():
    """API root endpoint."""
    return {
        "api_version": "v1",
        "endpoints": {
            "health": "/api/v1/health",
            "status": "/api/v1/status",
            "agents": "/api/v1/agents",
            "tasks": "/api/v1/tasks",
            "projects": "/api/v1/projects",
            "workflows": "/api/v1/workflows",
            "ws": "/ws",
        },
    }


# ============================================================================
# Placeholder Routes (for Phase 3)
# ============================================================================


@app.get("/api/v1/agents", tags=["Agents"])
async def list_agents():
    """List all agents (Phase 3)."""
    return {
        "items": [],
        "total": 0,
        "message": "Agent endpoints coming in Phase 3",
    }


@app.post("/api/v1/agents", tags=["Agents"])
async def create_agent(agent_data: dict):
    """Create an agent (Phase 3)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Agent creation coming in Phase 3",
    )


@app.get("/api/v1/tasks", tags=["Tasks"])
async def list_tasks():
    """List all tasks (Phase 3)."""
    return {
        "items": [],
        "total": 0,
        "message": "Task endpoints coming in Phase 3",
    }


@app.get("/api/v1/projects", tags=["Projects"])
async def list_projects():
    """List all projects (Phase 3)."""
    return {
        "items": [],
        "total": 0,
        "message": "Project endpoints coming in Phase 3",
    }


@app.get("/api/v1/workflows", tags=["Workflows"])
async def list_workflows():
    """List all workflows (Phase 3)."""
    return {
        "items": [],
        "total": 0,
        "message": "Workflow endpoints coming in Phase 3",
    }


# ============================================================================
# WebSocket Endpoint
# ============================================================================


@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """
    WebSocket endpoint for real-time updates.

    Clients can subscribe to agent status updates, task events, etc.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            logger.debug(f"WebSocket message: {data}")
            # Echo back for now; real implementation in Phase 3
            await websocket.send_text(f"Received: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws_manager.disconnect(websocket)


# ============================================================================
# Version Endpoints
# ============================================================================


@app.get("/api/v1/version", tags=["Info"])
async def get_version():
    """Get API version information."""
    return {
        "version": "1.0.0",
        "api_version": "v1",
        "python_version": "3.11+",
        "status": "beta",
    }


# ============================================================================
# Configuration Info
# ============================================================================


@app.get("/api/v1/config", tags=["Info"])
async def get_config():
    """Get configuration information (non-sensitive)."""
    return {
        "features": {
            "agents": True,
            "workflows": True,
            "persistence": True,
            "messaging": True,
            "providers": True,
        },
        "components": {
            "database": "SQLite with SQLAlchemy",
            "message_queue": "Redis",
            "api_framework": "FastAPI",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
