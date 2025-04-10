# WellFix - Plan: Phase 1 - Foundation & Authentication

**Phase Goal:** Establish the project structure, database connection, core data models, and implement robust authentication and basic user management features.

**Related Documentation:**
*   `docs/architecture-overview.md` (Project Structure, Modularity, Tech Stack)
*   `docs/data-models.md` (User, Address models primarily)
*   `docs/api-design.md` (Sections 1, 2, 3)
*   `docs/functional-requirements.md` (Section 4.1)
*   `docs/non-functional-requirements.mdc` (Security, Maintainability, Reliability)
*   Relevant `/rules/*.mdc` files (Structure, Style, Dependencies, Config, Error Handling, Docs)

---

## Tasks Breakdown (Check -> Code -> Test -> Iterate)

**1. Project Setup & Structure**
    *   [ ] **Check:** Review `rules/python-project-structure-rule.mdc` and `docs/architecture-overview.md` for the modular structure.
    *   [ ] **Code:** Initialize the project repository (e.g., `git init`).
    *   [ ] **Code:** Create the main application directory structure (e.g., `wellfix_api/`, `tests/`, `scripts/`, `config/`).
    *   [ ] **Code:** Set up chosen web framework (FastAPI preferred) with basic application entry point (`main.py`).
    *   [ ] **Code:** Implement core module structure within `wellfix_api/` (e.g., `auth/`, `users/`, `core/`, `models/`, `schemas/`, `crud/`).
    *   [ ] **Test:** N/A (Structure setup).
    *   [ ] **Iterate:** Refine structure based on initial setup.

**2. Dependency & Configuration Management**
    *   [ ] **Check:** Review `rules/python-dependency-management-rule.mdc` and `rules/python-configuration-management-rule.mdc`.
    *   [ ] **Code:** Initialize dependency management (e.g., `poetry init` or create `requirements.txt`). Add initial dependencies (Python, FastAPI/Uvicorn, Pydantic, Passlib, python-jose, SQLAlchemy/psycopg2, Alembic).
    *   [ ] **Code:** Set up configuration loading (e.g., using Pydantic Settings, `.env` file) for database URL, JWT secrets, etc.
    *   [ ] **Test:** Basic test to ensure configuration loads correctly.
    *   [ ] **Iterate:** Adjust configuration approach if needed.

**3. Database Setup & Core Models**
    *   [ ] **Check:** Review `docs/data-models.md` (User, Address models) and database choice (PostgreSQL) from `docs/architecture-overview.md`.
    *   [ ] **Code:** Implement basic database connection logic (`core/db.py`).
    *   [ ] **Code:** Define SQLAlchemy models for `User` and `Address` based on `docs/data-models.md` (`models/user.py`, `models/address.py`).
    *   [ ] **Code:** Set up Alembic for database migrations (`alembic/`).
    *   [ ] **Code:** Create initial Alembic migration script for User and Address tables.
    *   [ ] **Test:** Run migrations against a test database. Basic tests to create/retrieve User/Address via SQLAlchemy session.
    *   [ ] **Iterate:** Refine models and migrations based on testing.

**4. Core Schemas & CRUD Utilities**
    *   [ ] **Check:** Review Pydantic usage, map models to API schemas in `docs/api-design.md`.
    *   [ ] **Code:** Define Pydantic schemas for User (Create, Update, Base, InDB) and Address (`schemas/user.py`, `schemas/address.py`).
    *   [ ] **Code:** Implement basic CRUD (Create, Read, Update, Delete) utility functions for User and Address models (`crud/crud_user.py`, `crud/crud_address.py`).
    *   [ ] **Test:** Unit tests for CRUD functions using a test database session.
    *   [ ] **Iterate:** Adjust schemas and CRUD functions based on tests.

**5. Authentication Implementation (/auth)**
    *   [ ] **Check:** Review `docs/api-design.md` (Section 1) and `docs/functional-requirements.md` (4.1.1, 4.1.2, 4.1.3).
    *   [ ] **Code:** Implement password hashing utilities (`core/security.py`).
    *   [ ] **Code:** Implement JWT token creation and decoding utilities (`core/security.py`).
    *   [ ] **Code:** Implement API endpoints for:
        *   `POST /auth/register` (Customer registration, using `crud_user`).
        *   `POST /auth/login` (User login, checking hash, returning JWT).
        *   `GET /auth/me` (Dependency to get current user from token).
    *   [ ] **Test:** Integration tests for register, login (success/failure cases), get current user. Unit tests for security utilities.
    *   [ ] **Iterate:** Refine auth logic, token handling, and error responses.

**6. User Profile Management (/users/me)**
    *   [ ] **Check:** Review `docs/api-design.md` (Section 2) and `docs/functional-requirements.md` (4.1.5).
    *   [ ] **Code:** Implement API endpoints for:
        *   `GET /users/me` (Can reuse dependency from /auth/me).
        *   `PATCH /users/me` (Update user's own profile, using `crud_user`).
    *   [ ] **Test:** Integration tests for getting and updating the current user's profile.
    *   [ ] **Iterate:** Adjust update logic and response formats.

**7. Admin User Management (/admin/users)**
    *   [ ] **Check:** Review `docs/api-design.md` (Section 3) and `docs/functional-requirements.md` (4.1.6).
    *   [ ] **Code:** Implement dependency for requiring Admin role.
    *   [ ] **Code:** Implement API endpoints for:
        *   `GET /admin/users` (List users with filtering/pagination, using `crud_user`).
        *   `POST /admin/users` (Create Engineer/Admin, using `crud_user`).
        *   `GET /admin/users/{user_id}` (Get specific user details, using `crud_user`).
        *   `PATCH /admin/users/{user_id}` (Update specific user details, using `crud_user`).
    *   [ ] **Test:** Integration tests for all admin user management endpoints, including role checks (Admin access, non-Admin rejection) and functionality (list, create, get, update).
    *   [ ] **Iterate:** Refine admin logic, permissions, and responses.

**8. Initial Logging & Error Handling Setup**
    *   [ ] **Check:** Review `rules/python-error-handling-and-logging-rule.mdc`.
    *   [ ] **Code:** Configure basic logging (e.g., log to console/file).
    *   [ ] **Code:** Implement basic exception handlers in FastAPI to return standard error responses (e.g., for 404, 422, 500).
    *   [ ] **Test:** Manually trigger errors or write tests to check error response format.
    *   [ ] **Iterate:** Improve logging format and error handling detail.

---

**Phase 1 Definition of Done:**
*   Project structure is established and follows rules.
*   Dependencies and configuration are managed correctly.
*   Database connection works; User and Address models/migrations are implemented.
*   User registration and login (all roles) are functional and secure (JWT).
*   Users can view/update their own profiles.
*   Admins can list, create, view, and update users.
*   Basic logging and standardized error handling are in place.
*   All implemented code has corresponding tests (unit/integration) and passes.
*   Code adheres to style guides and includes basic documentation. 