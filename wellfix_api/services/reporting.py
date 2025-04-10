"""
Reporting service functions.

These functions aggregate data from the database to generate reports for the admin dashboard.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract, cast, Float, Integer
from sqlalchemy.sql import label

from wellfix_api.models.job import RepairJob, Rating, JobStatusUpdate
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.enums import JobStatus

# Set up logging
logger = logging.getLogger(__name__)


def get_dashboard_metrics(db: Session) -> Dict[str, Any]:
    """
    Get dashboard metrics for the admin dashboard.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with dashboard metrics:
        - counts of jobs in various statuses
        - average rating score
        - pending assignments count
        - jobs in lab count
        - completed jobs count (last 30 days)
        - total customer count
        - total engineer count
    """
    try:
        # Get current datetime for time-based queries
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # Count jobs in various statuses
        job_status_counts = (
            db.query(
                RepairJob.status,
                func.count(RepairJob.id).label("count")
            )
            .group_by(RepairJob.status)
            .all()
        )
        
        # Convert to dictionary for easier access
        status_counts = {status.name: 0 for status in JobStatus}
        for status, count in job_status_counts:
            status_counts[status.name] = count
        
        # Get average rating
        avg_rating = db.query(func.avg(Rating.score)).scalar()
        avg_rating = float(avg_rating) if avg_rating is not None else None
        
        # Count pending assignments
        pending_assignments = status_counts.get(JobStatus.PENDING_ASSIGNMENT.name, 0)
        
        # Count jobs in lab statuses
        lab_statuses = [
            JobStatus.ESCALATED_TO_LAB.name,
            JobStatus.PENDING_PICKUP_FOR_LAB.name,
            JobStatus.IN_TRANSIT_TO_LAB.name,
            JobStatus.LAB_DIAGNOSIS.name,
            JobStatus.REPAIR_IN_PROGRESS_LAB.name,
            JobStatus.IN_TRANSIT_FROM_LAB.name
        ]
        jobs_in_lab = sum(status_counts.get(status, 0) for status in lab_statuses)
        
        # Count completed jobs in last 30 days
        completed_last_30_days = (
            db.query(func.count(RepairJob.id))
            .filter(
                RepairJob.status == JobStatus.COMPLETED,
                RepairJob.updated_at >= thirty_days_ago
            )
            .scalar()
        )
        
        # Count total customers and engineers
        customer_count = (
            db.query(func.count(User.id))
            .filter(User.role == UserRole.CUSTOMER)
            .scalar()
        )
        
        engineer_count = (
            db.query(func.count(User.id))
            .filter(User.role == UserRole.ENGINEER)
            .scalar()
        )
        
        return {
            "job_status_counts": status_counts,
            "average_rating": avg_rating,
            "pending_assignments": pending_assignments,
            "jobs_in_lab": jobs_in_lab,
            "completed_last_30_days": completed_last_30_days,
            "total_customers": customer_count,
            "total_engineers": engineer_count
        }
    except Exception as e:
        logger.error(f"Error generating dashboard metrics: {str(e)}")
        return {
            "error": "Failed to generate dashboard metrics",
            "details": str(e)
        }


def get_engineer_productivity(db: Session, days: int = 30) -> Dict[str, Any]:
    """
    Get engineer productivity metrics.
    
    Args:
        db: Database session
        days: Number of days to look back for metrics (default: 30)
        
    Returns:
        Dictionary with engineer productivity metrics:
        - engineers: list of engineers with metrics
          - id: engineer ID
          - name: engineer name
          - jobs_completed: number of jobs completed
          - avg_completion_time: average time to complete jobs (days)
          - avg_rating: average rating for engineer
    """
    try:
        # Get current datetime for time-based queries
        now = datetime.now()
        start_date = now - timedelta(days=days)
        
        # Get all engineers with job counts and average ratings
        engineers_query = (
            db.query(
                User.id,
                User.first_name,
                User.last_name,
                func.count(RepairJob.id).label("jobs_completed"),
                func.avg(Rating.score).label("avg_rating")
            )
            .outerjoin(RepairJob, User.id == RepairJob.engineer_id)
            .outerjoin(Rating, RepairJob.id == Rating.job_id)
            .filter(
                User.role == UserRole.ENGINEER,
                RepairJob.status == JobStatus.COMPLETED,
                RepairJob.updated_at >= start_date
            )
            .group_by(User.id)
            .all()
        )
        
        # Format the results
        engineers = []
        for engineer_id, first_name, last_name, jobs_completed, avg_rating in engineers_query:
            # Calculate average completion time for this engineer
            avg_completion_time = calculate_avg_completion_time(db, engineer_id, start_date)
            
            engineers.append({
                "id": engineer_id,
                "name": f"{first_name} {last_name}",
                "jobs_completed": jobs_completed,
                "avg_completion_time": avg_completion_time,
                "avg_rating": float(avg_rating) if avg_rating is not None else None
            })
        
        return {
            "time_period": f"Last {days} days",
            "engineers": engineers
        }
    except Exception as e:
        logger.error(f"Error generating engineer productivity: {str(e)}")
        return {
            "error": "Failed to generate engineer productivity metrics",
            "details": str(e)
        }


def calculate_avg_completion_time(db: Session, engineer_id: int, start_date: datetime) -> float:
    """
    Calculate the average time from assignment to completion for an engineer.
    
    Args:
        db: Database session
        engineer_id: ID of the engineer
        start_date: Start date for the calculation
        
    Returns:
        Average completion time in days or None if no completed jobs
    """
    # Get all status updates for assignment and completion
    assignments = (
        db.query(JobStatusUpdate)
        .join(RepairJob, JobStatusUpdate.job_id == RepairJob.id)
        .filter(
            RepairJob.engineer_id == engineer_id,
            RepairJob.status == JobStatus.COMPLETED,
            JobStatusUpdate.new_status == JobStatus.ASSIGNED,
            JobStatusUpdate.timestamp >= start_date
        )
        .all()
    )
    
    completions = (
        db.query(JobStatusUpdate)
        .join(RepairJob, JobStatusUpdate.job_id == RepairJob.id)
        .filter(
            RepairJob.engineer_id == engineer_id,
            RepairJob.status == JobStatus.COMPLETED,
            JobStatusUpdate.new_status == JobStatus.COMPLETED,
            JobStatusUpdate.timestamp >= start_date
        )
        .all()
    )
    
    # Create mapping of job_id to timestamps
    assignment_times = {update.job_id: update.timestamp for update in assignments}
    completion_times = {update.job_id: update.timestamp for update in completions}
    
    # Calculate time differences for jobs that have both assignment and completion
    time_diffs = []
    for job_id, assigned_time in assignment_times.items():
        if job_id in completion_times:
            completed_time = completion_times[job_id]
            diff_days = (completed_time - assigned_time).total_seconds() / (60 * 60 * 24)  # Convert to days
            time_diffs.append(diff_days)
    
    # Calculate average
    if time_diffs:
        return sum(time_diffs) / len(time_diffs)
    else:
        return None 