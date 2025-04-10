import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

logger = logging.getLogger(__name__)

class DatabaseValidationError(Exception):
    """Exception raised for database validation errors."""
    def __init__(self, detail: str):
        self.detail = detail

def setup_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers with the FastAPI application."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors from Pydantic models."""
        # Log the error
        logger.warning(f"Validation error: {exc}")
        
        # Extract error details
        error_details = []
        for error in exc.errors():
            error_details.append({
                "location": error.get("loc", []),
                "message": error.get("msg", ""),
                "type": error.get("type", "")
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Invalid input", "errors": error_details},
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors (e.g., unique constraint violations)."""
        # Log the error
        logger.warning(f"Database integrity error: {exc}")
        
        error_message = str(exc)
        detail = "Database constraint violated"
        
        # Customize message based on error
        if "unique constraint" in error_message.lower() and "email" in error_message.lower():
            detail = "Email already registered"
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": detail},
        )
    
    @app.exception_handler(NoResultFound)
    async def not_found_exception_handler(request: Request, exc: NoResultFound):
        """Handle SQLAlchemy no result found errors."""
        # Log the error
        logger.warning(f"Resource not found: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )
    
    @app.exception_handler(DatabaseValidationError)
    async def database_validation_exception_handler(request: Request, exc: DatabaseValidationError):
        """Handle custom database validation errors."""
        # Log the error
        logger.warning(f"Database validation error: {exc.detail}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle any uncaught exceptions."""
        # Log the error
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        ) 