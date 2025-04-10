"""
Middlewares for the WellFix API.
"""
import time
import logging
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all API requests with contextual information.
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate a unique request ID to correlate logs
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log the start of the request
        logger.info(
            f"Request started | ID: {request_id} | Method: {request.method} | "
            f"Path: {request.url.path} | Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Measure request duration
        start_time = time.time()
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response details
            logger.info(
                f"Request completed | ID: {request_id} | Method: {request.method} | "
                f"Path: {request.url.path} | Status: {response.status_code} | "
                f"Duration: {process_time:.4f}s"
            )
            
            # Add the request ID to the response headers for debugging
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log exceptions
            process_time = time.time() - start_time
            logger.error(
                f"Request failed | ID: {request_id} | Method: {request.method} | "
                f"Path: {request.url.path} | Error: {str(e)} | Duration: {process_time:.4f}s",
                exc_info=True
            )
            raise

def setup_middlewares(app: ASGIApp) -> None:
    """
    Setup all middlewares for the application.
    
    Args:
        app: The FastAPI application
    """
    # Add the request logging middleware
    app.add_middleware(RequestLoggingMiddleware) 