"""
CRUD operations for the Rating model.
"""

from typing import Optional, List, Dict, Any, Union

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from wellfix_api.models.job import Rating, RepairJob
from wellfix_api.models.user import User
from wellfix_api.schemas.rating import RatingListResponse


def create_rating(
    db: Session,
    job_id: int,
    customer_id: str,
    score: int,
    comment: Optional[str] = None
) -> Optional[Rating]:
    """
    Create a new rating for a job.
    
    Args:
        db: Database session
        job_id: ID of the job being rated
        customer_id: ID of the customer submitting the rating
        score: Rating score (1-5)
        comment: Optional comment for the rating
        
    Returns:
        The created rating if successful, None otherwise
    """
    # Get the job to retrieve the engineer_id
    job = db.query(RepairJob).filter(RepairJob.id == job_id).first()
    if not job:
        return None
    
    # Create the rating
    rating = Rating(
        job_id=job_id,
        customer_id=customer_id,
        engineer_id=job.engineer_id,  # Associate with the engineer who worked on the job
        score=score,
        comment=comment
    )
    
    db.add(rating)
    db.commit()
    db.refresh(rating)
    
    return rating


def get_job_rating(db: Session, job_id: int) -> Optional[Rating]:
    """
    Get the rating for a specific job.
    
    Args:
        db: Database session
        job_id: ID of the job
        
    Returns:
        The rating if found, None otherwise
    """
    return db.query(Rating).filter(Rating.job_id == job_id).first()


def list_ratings(
    db: Session,
    engineer_id: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    """
    List ratings with filtering options.
    
    Args:
        db: Database session
        engineer_id: Optional filter by engineer ID
        min_score: Optional filter by minimum score
        max_score: Optional filter by maximum score
        skip: Items to skip (pagination)
        limit: Maximum items to return (pagination)
        
    Returns:
        Dictionary with ratings list, count, page and size
    """
    # Build filters
    filters = []
    
    if engineer_id is not None:
        filters.append(Rating.engineer_id == engineer_id)
    
    if min_score is not None:
        filters.append(Rating.score >= min_score)
    
    if max_score is not None:
        filters.append(Rating.score <= max_score)
    
    # Apply filters if any
    query = db.query(Rating)
    if filters:
        query = query.filter(and_(*filters))
    
    # Get total count
    total_count = query.count()
    
    # Get paginated results
    ratings = query.order_by(Rating.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "ratings": ratings,
        "count": total_count,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": min(limit, len(ratings))
    }


def get_average_rating_for_engineer(db: Session, engineer_id: str) -> Optional[float]:
    """
    Calculate the average rating for an engineer.
    
    Args:
        db: Database session
        engineer_id: ID of the engineer
        
    Returns:
        Average rating as a float, or None if no ratings
    """
    result = db.query(func.avg(Rating.score)).filter(Rating.engineer_id == engineer_id).scalar()
    return float(result) if result is not None else None 