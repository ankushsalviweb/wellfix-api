"""
API endpoints for managing ratings.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import get_current_user, require_admin
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.enums import JobStatus
from wellfix_api.schemas.rating import RatingCreate, RatingResponse, RatingListResponse
from wellfix_api.crud import crud_rating, crud_job

router = APIRouter(tags=["Ratings"])


@router.post("/jobs/{job_id}/ratings", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_rating(
    rating_data: RatingCreate,
    job_id: int = Path(..., description="The ID of the job to rate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Submit a rating for a job.
    
    Only customers can submit ratings, and only for their own completed jobs.
    A job can only be rated once.
    """
    # Only customers can submit ratings
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can submit ratings"
        )
    
    # Check if the job exists and belongs to the customer
    job = crud_job.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only rate your own jobs"
        )
    
    # Check if the job is completed
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only completed jobs can be rated"
        )
    
    # Check if the job already has a rating
    existing_rating = crud_rating.get_job_rating(db, job_id)
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This job has already been rated"
        )
    
    # Create the rating
    rating = crud_rating.create_rating(
        db=db,
        job_id=job_id,
        customer_id=current_user.id,
        score=rating_data.score,
        comment=rating_data.comment
    )
    
    return rating


@router.get("/jobs/{job_id}/ratings", response_model=RatingResponse)
async def get_job_rating(
    job_id: int = Path(..., description="The ID of the job"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get the rating for a specific job.
    
    Accessible by:
    - The customer who owns the job
    - The engineer assigned to the job
    - Any admin
    """
    # Get the job
    job = crud_job.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check authorization
    if (current_user.role == UserRole.CUSTOMER and job.customer_id != current_user.id) or \
       (current_user.role == UserRole.ENGINEER and job.engineer_id != current_user.id and current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this rating"
        )
    
    # Get the rating
    rating = crud_rating.get_job_rating(db, job_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rating found for this job"
        )
    
    return rating


@router.get("/admin/ratings", response_model=RatingListResponse)
async def list_ratings(
    engineer_id: str = Query(None, description="Filter by engineer ID"),
    min_score: int = Query(None, description="Filter by minimum score", ge=1, le=5),
    max_score: int = Query(None, description="Filter by maximum score", ge=1, le=5),
    skip: int = Query(0, description="Number of records to skip", ge=0),
    limit: int = Query(100, description="Maximum number of records to return", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    List all ratings with optional filtering.
    
    Returns a paginated list of ratings with:
    - ratings: List of rating objects
    - count: Total number of ratings matching the filter
    - page: Current page number
    - size: Number of items in the current page
    
    Admin only endpoint.
    """
    return crud_rating.list_ratings(
        db=db,
        engineer_id=engineer_id,
        min_score=min_score,
        max_score=max_score,
        skip=skip,
        limit=limit
    ) 