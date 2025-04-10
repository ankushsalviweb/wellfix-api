import logging
from fastapi import FastAPI

# Import settings early to catch config errors on startup
from wellfix_api.core.config import settings

# Import the API router
from wellfix_api.api.v1 import api_router

# Import exception handlers
from wellfix_api.core.exceptions import setup_exception_handlers

# Import middleware setup
from wellfix_api.core.middlewares import setup_middlewares

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create FastAPI app
app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# Setup exception handlers
setup_exception_handlers(app)

# Setup middlewares
setup_middlewares(app)

@app.get("/health", tags=["Health"])
def health_check():
    """Check if the API is running."""
    return {"status": "ok"}

# Include the API router
app.include_router(api_router, prefix=settings.API_V1_STR) 