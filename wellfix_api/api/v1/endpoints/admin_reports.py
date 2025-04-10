"""
API endpoints for admin reporting.
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import require_admin
from wellfix_api.models.user import User
from wellfix_api.services import reporting

router = APIRouter(tags=["Admin: Reports"])


@router.get("/dashboard", status_code=status.HTTP_200_OK)
async def get_dashboard_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    Get dashboard metrics for the admin dashboard.
    
    Admin only endpoint.
    
    Returns:
        Dictionary with key metrics:
        - job status counts
        - average rating
        - pending assignments count
        - jobs in lab count
        - completed jobs in last 30 days
        - total customer count
        - total engineer count
    """
    return reporting.get_dashboard_metrics(db)


@router.get("/engineer-productivity", status_code=status.HTTP_200_OK)
async def get_engineer_productivity(
    days: int = Query(30, description="Number of days to look back", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    Get engineer productivity metrics.
    
    Admin only endpoint.
    
    Args:
        days: Number of days to look back for metrics (default: 30)
        
    Returns:
        Dictionary with:
        - engineers: list of engineers with metrics
          - id: engineer ID
          - name: engineer name
          - jobs_completed: number of jobs completed
          - avg_completion_time: average time to complete jobs (days)
          - avg_rating: average rating for engineer
    """
    return reporting.get_engineer_productivity(db, days=days) 