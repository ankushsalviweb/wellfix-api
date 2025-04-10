"""
API endpoints for managing repair jobs.
"""

from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.core.dependencies import get_current_user, require_admin
from wellfix_api.core.status_validator import is_transition_allowed
from wellfix_api.core.notifications import notify_admin_new_job
from wellfix_api.models.user import User, UserRole
from wellfix_api.models.enums import JobStatus, PaymentStatus
from wellfix_api.schemas.job import (
    JobCreate, JobSummary, JobDetail, JobList,
    JobStatusUpdateCreate, JobStatusUpdateResponse,
    JobNoteCreate, JobQuoteUpdate, PaymentStatusUpdate, 
    JobCancellation, JobAssignment
)
from wellfix_api.crud import crud_job, crud_address, crud_service_area

router = APIRouter(tags=["Jobs"])


@router.post("", response_model=JobDetail, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new repair job.
    
    Only customers can create jobs. The job will be initialized with 
    PENDING_ASSIGNMENT status and needs to be assigned to an engineer by an admin.
    
    Validates:
    - The address belongs to the customer
    - The address's pincode is in a serviceable area
    """
    # Only customers can create jobs
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only customers can create repair jobs"
        )
    
    # Validate address ownership
    if job_data.address_id:
        address = crud_address.get_address(db, job_data.address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Address not found"
            )
        
        if address.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Address does not belong to the current user"
            )
        
        # Validate address is in serviceable area
        if not crud_service_area.is_pincode_serviceable(db, address.pincode):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail=f"Pincode {address.pincode} is not in a serviceable area"
            )
    
    # Create the job
    new_job = crud_job.create_job(
        db=db, 
        job_data=job_data.model_dump(), 
        customer_id=current_user.id
    )
    
    # Notify admins about the new job
    notify_admin_new_job(new_job)
    
    return new_job


@router.get("", response_model=JobList)
async def list_jobs(
    status_filter: Optional[JobStatus] = Query(None, description="Filter by job status"),
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of jobs to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    List repair jobs based on user role.
    
    - Customers see only their own jobs.
    - Engineers see only jobs assigned to them.
    - Admins see all jobs.
    """
    if current_user.role == UserRole.ADMIN:
        # Admins can see all jobs
        filter_params = {}
        if status_filter:
            filter_params["status"] = status_filter
            
        jobs, count = crud_job.list_jobs(
            db=db, 
            skip=skip, 
            limit=limit, 
            filter_params=filter_params
        )
    elif current_user.role == UserRole.ENGINEER:
        # Engineers see only their assigned jobs
        jobs, count = crud_job.list_jobs_by_engineer(
            db=db, 
            engineer_id=current_user.id, 
            skip=skip, 
            limit=limit,
            status=status_filter
        )
    else:  # CUSTOMER
        # Customers see only their own jobs
        jobs, count = crud_job.list_jobs_by_customer(
            db=db, 
            customer_id=current_user.id, 
            skip=skip, 
            limit=limit,
            status=status_filter
        )
    
    return {"count": count, "jobs": jobs}


@router.get("/{job_id}", response_model=JobDetail)
async def get_job_details(
    job_id: int = Path(..., description="The ID of the job to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get details for a specific job.
    
    - Customers can only access their own jobs.
    - Engineers can only access jobs assigned to them.
    - Admins can access any job.
    """
    job = crud_job.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Job not found"
        )
    
    # Check permissions based on role
    if current_user.role == UserRole.ADMIN:
        # Admins can access any job
        pass
    elif current_user.role == UserRole.ENGINEER:
        # Engineers can only access jobs assigned to them
        if job.engineer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Not authorized to access this job"
            )
    else:  # CUSTOMER
        # Customers can only access their own jobs
        if job.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Not authorized to access this job"
            )
    
    return job


@router.patch("/{job_id}/status", response_model=JobDetail)
async def update_job_status(
    status_update: JobStatusUpdateCreate,
    job_id: int = Path(..., description="The ID of the job to update"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a job's status.
    
    Engineers can update status for jobs assigned to them.
    Admins can update status for any job.
    Status transitions are validated to ensure they follow the allowed workflow.
    """
    # Only Engineers and Admins can update status
    if current_user.role not in [UserRole.ENGINEER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Engineers and Admins can update job status"
        )
    
    # Get the job
    job = crud_job.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.ENGINEER and job.engineer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Engineers can only update status for jobs assigned to them"
        )
    
    # Validate status transition
    if not is_transition_allowed(job.status, status_update.status, current_user.role):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status transition from {job.status} to {status_update.status} for {current_user.role}"
        )
    
    # Prepare extra updates (if needed for certain transitions)
    extra_updates = {}
    
    # If transitioning to lab-related statuses with consent flag provided
    if status_update.customer_consent_for_lab is not None:
        if status_update.status in [JobStatus.PENDING_PICKUP_FOR_LAB, JobStatus.ESCALATED_TO_LAB]:
            extra_updates["customer_consent_for_lab"] = status_update.customer_consent_for_lab
        else:
            # Ignore consent flag for non-lab-related transitions
            pass
    
    # If transitioning to certain statuses, customer_consent_for_lab must be True
    if status_update.status in [JobStatus.IN_TRANSIT_TO_LAB] and not job.customer_consent_for_lab:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Customer consent required for lab-related transitions"
        )
    
    # Update the job status
    updated_job = crud_job.update_job_status(
        db=db,
        job_id=job_id,
        new_status=status_update.status,
        user_id=current_user.id,
        notes=status_update.notes,
        extra_updates=extra_updates
    )
    
    return updated_job


@router.post("/{job_id}/notes", response_model=JobDetail)
async def add_job_notes(
    note_data: JobNoteCreate,
    job_id: int = Path(..., description="The ID of the job to add notes to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Add notes to a job.
    
    Engineers can add notes to jobs assigned to them.
    Admins can add notes to any job.
    """
    # Only Engineers and Admins can add notes
    if current_user.role not in [UserRole.ENGINEER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Engineers and Admins can add notes to jobs"
        )
    
    # Get the job
    job = crud_job.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.ENGINEER and job.engineer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Engineers can only add notes to jobs assigned to them"
        )
    
    # Add notes to the job
    updated_job = crud_job.add_job_notes(
        db=db,
        job_id=job_id,
        user_id=current_user.id,
        notes=note_data.notes
    )
    
    return updated_job


@router.patch("/{job_id}/quote", response_model=JobDetail)
async def update_job_quote(
    quote_data: JobQuoteUpdate,
    job_id: int = Path(..., description="The ID of the job to update"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a job's cost quotes.
    
    Engineers can update quotes for jobs assigned to them.
    Admins can update quotes for any job.
    """
    # Only Engineers and Admins can update quotes
    if current_user.role not in [UserRole.ENGINEER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Engineers and Admins can update job quotes"
        )
    
    # Get the job
    job = crud_job.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.ENGINEER and job.engineer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Engineers can only update quotes for jobs assigned to them"
        )
    
    # Validate based on job status
    if quote_data.estimated_cost is not None:
        # Estimated cost can be set during diagnosis or later stages
        if job.status not in [
            JobStatus.LAB_DIAGNOSIS, 
            JobStatus.ON_SITE_DIAGNOSIS, 
            JobStatus.PENDING_QUOTE_APPROVAL,
            JobStatus.REPAIR_IN_PROGRESS_LAB,
            JobStatus.REPAIR_IN_PROGRESS_ON_SITE
        ]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Estimated cost can only be set during diagnosis or repair"
            )
    
    if quote_data.final_cost is not None:
        # Final cost should only be set near completion
        if job.status not in [
            JobStatus.COMPLETED,
            JobStatus.PENDING_PAYMENT,
            JobStatus.REPAIR_IN_PROGRESS_LAB,
            JobStatus.REPAIR_IN_PROGRESS_ON_SITE,
            JobStatus.PENDING_RETURN_DELIVERY,
            JobStatus.IN_TRANSIT_FROM_LAB
        ]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Final cost can only be set during final stages of repair"
            )
    
    # Update the job quote
    updated_job = crud_job.update_job_quote(
        db=db,
        job_id=job_id,
        user_id=current_user.id,
        estimated_cost=quote_data.estimated_cost,
        final_cost=quote_data.final_cost,
        notes=quote_data.notes
    )
    
    return updated_job


@router.patch("/{job_id}/payment", response_model=JobDetail)
async def update_payment_status(
    payment_data: PaymentStatusUpdate,
    job_id: int = Path(..., description="The ID of the job to update"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a job's payment status.
    
    Engineers can update payment status for jobs assigned to them.
    Admins can update payment status for any job.
    """
    # Only Engineers and Admins can update payment status
    if current_user.role not in [UserRole.ENGINEER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Engineers and Admins can update payment status"
        )
    
    # Get the job
    job = crud_job.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.ENGINEER and job.engineer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Engineers can only update payment status for jobs assigned to them"
        )
    
    # Validate based on job status
    if job.status not in [JobStatus.PENDING_PAYMENT, JobStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payment status can only be updated when job is in PENDING_PAYMENT or COMPLETED state"
        )
    
    # Update the payment status
    updated_job = crud_job.update_payment_status(
        db=db,
        job_id=job_id,
        payment_status=payment_data.payment_status,
        user_id=current_user.id,
        notes=payment_data.notes
    )
    
    return updated_job


@router.post("/{job_id}/cancel", response_model=JobDetail)
async def cancel_job(
    cancellation_data: JobCancellation,
    job_id: int = Path(..., description="The ID of the job to cancel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Cancel a job.
    
    Customers can cancel their own jobs.
    Admins can cancel any job.
    Jobs cannot be cancelled if they're already in COMPLETED or CANCELLED status.
    """
    # Get the job
    job = crud_job.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.CUSTOMER and job.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customers can only cancel their own jobs"
        )
    elif current_user.role == UserRole.ENGINEER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Engineers cannot cancel jobs"
        )
    
    # Check if job can be cancelled
    if job.status in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot cancel job in {job.status} status"
        )
    
    # Cancel the job
    cancelled_job = crud_job.cancel_job(
        db=db,
        job_id=job_id,
        user_id=current_user.id,
        reason=cancellation_data.reason
    )
    
    return cancelled_job


@router.patch("/{job_id}/assign", response_model=JobDetail)
async def assign_engineer_to_job(
    assignment_data: JobAssignment,
    job_id: int = Path(..., description="The ID of the job to assign"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    Assign or unassign an engineer to a job.
    
    Admin only endpoint.
    If engineer_id is null, the job is unassigned.
    """
    # Get the job
    job = crud_job.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if job can be assigned/unassigned
    if job.status in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot modify assignment for job in {job.status} status"
        )
    
    # If assigning an engineer, verify they exist and have ENGINEER role
    engineer_id = assignment_data.engineer_id
    if engineer_id:
        engineer = db.query(User).filter(User.id == engineer_id).first()
        if not engineer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Engineer not found"
            )
        if engineer.role != UserRole.ENGINEER:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User must have ENGINEER role to be assigned to jobs"
            )
    
    # Update the assignment
    updated_job = crud_job.assign_engineer(
        db=db,
        job_id=job_id,
        engineer_id=engineer_id,
        admin_id=current_user.id
    )
    
    return updated_job 