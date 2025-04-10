"""
Utility functions for creating and authenticating test users.
"""

import uuid
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from wellfix_api.models.user import User, UserRole
from wellfix_api.core.security import get_password_hash


def create_admin_user(db: Session) -> User:
    """Create an admin user for testing if it doesn't already exist."""
    # Check if admin exists
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if admin:
        return admin
    
    # Create a new admin
    admin = User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword"),
        first_name="Admin",
        last_name="User",
        phone_number="1234567890",
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def create_customer_user(db: Session) -> User:
    """Create a customer user for testing if it doesn't already exist."""
    # Check if customer exists
    customer = db.query(User).filter(User.email == "customer@example.com").first()
    if customer:
        return customer
    
    # Create a new customer
    customer = User(
        id=str(uuid.uuid4()),
        email="customer@example.com",
        password_hash=get_password_hash("customerpassword"),
        first_name="Customer",
        last_name="User",
        phone_number="1234567891",
        role=UserRole.CUSTOMER,
        is_active=True
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def create_engineer_user(db: Session) -> User:
    """Create an engineer user for testing if it doesn't already exist."""
    # Check if engineer exists
    engineer = db.query(User).filter(User.email == "engineer@example.com").first()
    if engineer:
        return engineer
    
    # Create a new engineer
    engineer = User(
        id=str(uuid.uuid4()),
        email="engineer@example.com",
        password_hash=get_password_hash("engineerpassword"),
        first_name="Engineer",
        last_name="User",
        phone_number="1234567892",
        role=UserRole.ENGINEER,
        is_active=True
    )
    db.add(engineer)
    db.commit()
    db.refresh(engineer)
    return engineer


def get_token_for_user(client: TestClient, email: str) -> str:
    """Get an authentication token for a test user."""
    login_data = {
        "username": email,
        "password": f"{email.split('@')[0]}password"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    
    # If login fails, try the default user credentials
    if response.status_code != 200:
        response = client.post("/api/v1/auth/login", data={
            "username": email,
            "password": "password"
        })
    
    # Extract and return the token
    return response.json().get("access_token", "") 