"""
CRUD operations for RepairJob model.
"""

from typing import List, Optional, Tuple, Dict, Any, Union
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from wellfix_api.models.job import RepairJob, JobStatusUpdate
from wellfix_api.models.enums import JobStatus, PaymentStatus
from wellfix_api.models.user import User, UserRole


def get_job(db: Session, job_id: int) -> Optional[RepairJob]:
    """
    Get a specific job by ID.
    
    Args:
        db: Database session
        job_id: ID of the job to retrieve
        
    Returns:
        The job if found, None otherwise
    """
    return db.query(RepairJob).filter(RepairJob.id == job_id).first()


def list_jobs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    filter_params: Optional[Dict[str, Any]] = None
) -> Tuple[List[RepairJob], int]:
    """
    List all jobs with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        filter_params: Optional dictionary of filter parameters
            - status: Filter by specific status
            - customer_id: Filter by customer
            - engineer_id: Filter by assigned engineer
            - address_id: Filter by service address
        
    Returns:
        Tuple of (list of jobs, total count)
    """
    query = db.query(RepairJob)
    
    # Apply filters if provided
    if filter_params:
        if status := filter_params.get("status"):
            query = query.filter(RepairJob.status == status)
        
        if customer_id := filter_params.get("customer_id"):
            query = query.filter(RepairJob.customer_id == customer_id)
            
        if engineer_id := filter_params.get("engineer_id"):
            query = query.filter(RepairJob.engineer_id == engineer_id)
            
        if address_id := filter_params.get("address_id"):
            query = query.filter(RepairJob.address_id == address_id)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination and return results
    jobs = query.order_by(desc(RepairJob.updated_at)).offset(skip).limit(limit).all()
    
    return jobs, total


def list_jobs_by_customer(
    db: Session, 
    customer_id: Union[int, str], 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[JobStatus] = None
) -> Tuple[List[RepairJob], int]:
    """
    List jobs for a specific customer.
    
    Args:
        db: Database session
        customer_id: ID of the customer
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        status: Optional status filter
        
    Returns:
        Tuple of (list of jobs, total count)
    """
    query = db.query(RepairJob).filter(RepairJob.customer_id == customer_id)
    
    if status:
        query = query.filter(RepairJob.status == status)
    
    total = query.count()
    jobs = query.order_by(desc(RepairJob.updated_at)).offset(skip).limit(limit).all()
    
    return jobs, total


def list_jobs_by_engineer(
    db: Session, 
    engineer_id: Union[int, str], 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[JobStatus] = None
) -> Tuple[List[RepairJob], int]:
    """
    List jobs assigned to a specific engineer.
    
    Args:
        db: Database session
        engineer_id: ID of the engineer
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        status: Optional status filter
        
    Returns:
        Tuple of (list of jobs, total count)
    """
    query = db.query(RepairJob).filter(RepairJob.engineer_id == engineer_id)
    
    if status:
        query = query.filter(RepairJob.status == status)
    
    total = query.count()
    jobs = query.order_by(desc(RepairJob.updated_at)).offset(skip).limit(limit).all()
    
    return jobs, total


def create_job(db: Session, job_data: Dict[str, Any], customer_id: Union[int, str]) -> RepairJob:
    """
    Create a new repair job.
    
    Args:
        db: Database session
        job_data: Dictionary containing job data
        customer_id: ID of the customer creating the job
        
    Returns:
        The newly created job
    """
    # Set initial status and timestamps
    job_data["status"] = JobStatus.PENDING_ASSIGNMENT
    job_data["customer_id"] = customer_id
    job_data["created_at"] = datetime.now(timezone.utc)
    job_data["updated_at"] = datetime.now(timezone.utc)
    job_data["payment_status"] = PaymentStatus.PENDING

    # Create the job
    db_job = RepairJob(**job_data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Create initial status update entry
    job_status_update = JobStatusUpdate(
        job_id=db_job.id,
        previous_status=None,
        new_status=JobStatus.PENDING_ASSIGNMENT,
        notes="Job created and pending assignment",
        user_id=customer_id,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(job_status_update)
    db.commit()

    return db_job


def assign_engineer(
    db: Session, 
    job_id: int, 
    engineer_id: Optional[Union[int, str]], 
    admin_id: Union[int, str]
) -> Optional[RepairJob]:
    """
    Assign or unassign an engineer to a job.
    
    Args:
        db: Database session
        job_id: ID of the job
        engineer_id: ID of the engineer to assign, or None to unassign
        admin_id: ID of the admin making the change
        
    Returns:
        The updated job if found, None otherwise
    """
    db_job = get_job(db, job_id)
    if not db_job:
        return None
    
    previous_status = db_job.status
    previous_engineer_id = db_job.engineer_id
    
    # Update the engineer assignment
    db_job.engineer_id = engineer_id
    
    # Update the job status if appropriate
    if engineer_id and db_job.status == JobStatus.PENDING_ASSIGNMENT:
        db_job.status = JobStatus.ASSIGNED
    elif not engineer_id and db_job.status == JobStatus.ASSIGNED:
        db_job.status = JobStatus.PENDING_ASSIGNMENT
    
    db.commit()
    db.refresh(db_job)
    
    # Record the status change if it happened
    if db_job.status != previous_status:
        record_status_update(
            db=db,
            job_id=job_id,
            previous_status=previous_status,
            new_status=db_job.status,
            user_id=admin_id,
            notes=f"{'Assigned to engineer' if engineer_id else 'Unassigned engineer'}"
        )
    
    return db_job


def update_job_status(
    db: Session, 
    job_id: int, 
    new_status: JobStatus, 
    user_id: Union[int, str],
    notes: Optional[str] = None,
    extra_updates: Optional[Dict[str, Any]] = None
) -> Optional[RepairJob]:
    """
    Update a job's status.
    
    Args:
        db: Database session
        job_id: ID of the job
        new_status: The new status to set
        user_id: ID of the user making the change (Engineer or Admin)
        notes: Optional notes about the status change
        extra_updates: Optional dictionary with additional fields to update
        
    Returns:
        The updated job if found, None otherwise
    """
    db_job = get_job(db, job_id)
    if not db_job:
        return None
    
    previous_status = db_job.status
    
    # Update the status
    db_job.status = new_status
    
    # Apply any extra updates
    if extra_updates:
        for key, value in extra_updates.items():
            if hasattr(db_job, key):
                setattr(db_job, key, value)
    
    # Add notes to the appropriate field based on user role
    user = db.query(User).filter(User.id == user_id).first()
    if notes:
        if user and user.role == UserRole.ENGINEER:
            if db_job.engineer_notes:
                db_job.engineer_notes += f"\n[{datetime.now(timezone.utc).isoformat()}] {notes}"
            else:
                db_job.engineer_notes = f"[{datetime.now(timezone.utc).isoformat()}] {notes}"
        else:  # Admin or otherwise
            if db_job.admin_notes:
                db_job.admin_notes += f"\n[{datetime.now(timezone.utc).isoformat()}] {notes}"
            else:
                db_job.admin_notes = f"[{datetime.now(timezone.utc).isoformat()}] {notes}"
    
    db.commit()
    db.refresh(db_job)
    
    # Record the status update
    record_status_update(
        db=db,
        job_id=job_id,
        previous_status=previous_status,
        new_status=new_status,
        user_id=user_id,
        notes=notes
    )
    
    return db_job


def add_job_notes(
    db: Session, 
    job_id: int, 
    user_id: Union[int, str], 
    notes: str
) -> Optional[RepairJob]:
    """
    Add notes to a job.
    
    Args:
        db: Database session
        job_id: ID of the job
        user_id: ID of the user adding notes
        notes: The notes to add
        
    Returns:
        The updated job if found, None otherwise
    """
    db_job = get_job(db, job_id)
    if not db_job or not notes:
        return None
    
    # Add notes to the appropriate field based on user role
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    if user.role == UserRole.ENGINEER:
        if db_job.engineer_notes:
            db_job.engineer_notes += f"\n[{timestamp}] {notes}"
        else:
            db_job.engineer_notes = f"[{timestamp}] {notes}"
    else:  # Admin or otherwise
        if db_job.admin_notes:
            db_job.admin_notes += f"\n[{timestamp}] {notes}"
        else:
            db_job.admin_notes = f"[{timestamp}] {notes}"
    
    db.commit()
    db.refresh(db_job)
    
    return db_job


def update_job_quote(
    db: Session, 
    job_id: int, 
    user_id: Union[int, str],
    estimated_cost: Optional[float] = None,
    final_cost: Optional[float] = None,
    notes: Optional[str] = None
) -> Optional[RepairJob]:
    """
    Update a job's cost quote.
    
    Args:
        db: Database session
        job_id: ID of the job
        user_id: ID of the user updating the quote
        estimated_cost: Optional estimated cost to set
        final_cost: Optional final cost to set
        notes: Optional notes about the quote
        
    Returns:
        The updated job if found, None otherwise
    """
    db_job = get_job(db, job_id)
    if not db_job:
        return None
    
    # Apply updates
    if estimated_cost is not None:
        db_job.estimated_cost = estimated_cost
    
    if final_cost is not None:
        db_job.final_cost = final_cost
    
    # Add notes if provided
    if notes:
        return add_job_notes(db, job_id, user_id, notes)
    else:
        db.commit()
        db.refresh(db_job)
        return db_job


def update_payment_status(
    db: Session, 
    job_id: int, 
    payment_status: PaymentStatus,
    user_id: Union[int, str],
    notes: Optional[str] = None
) -> Optional[RepairJob]:
    """
    Update a job's payment status.
    
    Args:
        db: Database session
        job_id: ID of the job
        payment_status: The new payment status
        user_id: ID of the user updating the payment status
        notes: Optional notes about the payment
        
    Returns:
        The updated job if found, None otherwise
    """
    db_job = get_job(db, job_id)
    if not db_job:
        return None
    
    db_job.payment_status = payment_status
    
    # Add notes if provided
    if notes:
        return add_job_notes(db, job_id, user_id, f"Payment status updated to {payment_status.value}: {notes}")
    else:
        db.commit()
        db.refresh(db_job)
        return db_job


def cancel_job(
    db: Session, 
    job_id: int, 
    user_id: Union[int, str],
    reason: str
) -> Optional[RepairJob]:
    """
    Cancel a job.
    
    Args:
        db: Database session
        job_id: ID of the job
        user_id: ID of the user cancelling the job
        reason: Reason for cancellation
        
    Returns:
        The updated job if found, None otherwise
    """
    db_job = get_job(db, job_id)
    if not db_job:
        return None
    
    previous_status = db_job.status
    db_job.status = JobStatus.CANCELLED
    db_job.cancellation_reason = reason
    
    db.commit()
    db.refresh(db_job)
    
    # Record the status update
    record_status_update(
        db=db,
        job_id=job_id,
        previous_status=previous_status,
        new_status=JobStatus.CANCELLED,
        user_id=user_id,
        notes=f"Job cancelled: {reason}"
    )
    
    return db_job


def record_status_update(
    db: Session, 
    job_id: int, 
    previous_status: Optional[JobStatus],
    new_status: JobStatus,
    user_id: Union[int, str],
    notes: Optional[str] = None
) -> JobStatusUpdate:
    """
    Record a job status update in the history.
    
    Args:
        db: Database session
        job_id: ID of the job
        previous_status: The previous status
        new_status: The new status
        user_id: ID of the user making the change
        notes: Optional notes about the status change
        
    Returns:
        The created status update record
    """
    # If it's the initial status, use the same status for previous
    if previous_status is None:
        previous_status = new_status
    
    status_update = JobStatusUpdate(
        job_id=job_id,
        user_id=user_id,
        previous_status=previous_status,
        new_status=new_status,
        notes=notes
    )
    
    db.add(status_update)
    db.commit()
    db.refresh(status_update)
    
    return status_update 