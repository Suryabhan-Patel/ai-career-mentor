"""
FastAPI application entry point.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.routes import resume_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Career Mentor API",
    description="Resume analysis and career path recommendation system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume_routes.router)


@app.get("/")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON with API status
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "AI Career Mentor API",
            "version": "1.0.0"
        },
        status_code=200
    )


@app.get("/info")
async def api_info():
    """
    Get API information and available endpoints.
    
    Returns:
        JSON with API info and endpoints
    """
    return JSONResponse(
        content={
            "name": "AI Career Mentor API",
            "description": "Resume analysis and career path recommendation system",
            "version": "1.0.0",
            "features": [
                "Resume PDF upload and text extraction",
                "Skill extraction using NLP",
                "Career role matching",
                "Skill gap analysis",
                "Embedding-based similarity matching"
            ],
            "endpoints": {
                "GET /": "Health check",
                "GET /info": "API information",
                "POST /api/upload-resume": "Upload and analyze PDF resume",
                "POST /api/analyze-text": "Analyze raw resume text",
                "GET /api/job-roles": "Get all available job roles"
            }
        },
        status_code=200
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    logger.error(f"HTTP Error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Custom general exception handler."""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "Internal server error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
