from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any
from sqlalchemy.orm import Session

from wellfix_api.core.db import get_db
from wellfix_api.models.service_area import ServiceableArea
from wellfix_api.schemas.service_area import ServiceAreaStatus

router = APIRouter()

@router.get("/check/{pincode}", response_model=ServiceAreaStatus, status_code=status.HTTP_200_OK)
def check_serviceable_area(
    pincode: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Check if a pincode is serviceable.
    
    This endpoint is publicly accessible and allows checking if a given pincode
    is within the serviceable area of WellFix.
    """
    # Query the database for the pincode
    service_area = db.query(ServiceableArea).filter(
        ServiceableArea.pincode == pincode,
        ServiceableArea.is_active == True
    ).first()
    
    # Return the result (whether the pincode is serviceable)
    return {
        "pincode": pincode,
        "is_serviceable": service_area is not None
    } 