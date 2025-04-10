"""
Notification utilities for the WellFix API.

This module contains functions to handle notifications for various events in the system.
Initially, these functions will just log messages, but they can be extended to send
actual notifications (emails, SMS, etc.) in the future.
"""

import logging
from typing import Any, Dict, Optional

from wellfix_api.models.job import RepairJob

logger = logging.getLogger(__name__)


def notify_admin_new_job(job: RepairJob) -> None:
    """
    Send a notification to admins about a new job.
    
    Args:
        job: The new job that was created
    """
    logger.info(
        f"[ADMIN NOTIFICATION] New job created - ID: {job.id}, "
        f"Customer: {job.customer_id}, "
        f"Type: {job.repair_type_requested}, "
        f"Status: {job.status}"
    )
    # In the future, this could send an email, SMS, or push notification 