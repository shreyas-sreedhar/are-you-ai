"""FastAPI application main entry point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Video Fakeness Detector API",
    description="Backend API for detecting AI-generated fake videos using NVIDIA NIM",
    version="1.0.0"
)

# Configure CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",
        "http://localhost:*",
        "http://127.0.0.1:*",
        "*"  # Allow all origins for development (restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Video Fakeness Detector API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/v1/health",
            "analyze_frame": "/api/v1/analyze-frame",
            "analyze_batch": "/api/v1/analyze-batch"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("Starting AI Video Fakeness Detector API")
    logger.info(f"Host: {settings.host}")
    logger.info(f"Port: {settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"NIM API Endpoint: {settings.nim_api_endpoint}")
    logger.info(f"NIM Model: {settings.nim_model_name}")
    logger.info("API ready to accept requests")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

