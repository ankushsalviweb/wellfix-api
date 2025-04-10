# WellFix - Phase 1 ToDo: Foundation & Authentication

**Goal:** Establish project structure, DB, core models (User, Address), auth, and basic user management APIs.

**Reference Plan:** `Plan/01-phase-foundation.md`

**Instructions:** Follow Check -> Code -> Test -> Iterate for each task. Ensure adherence to `/rules` and alignment with `/docs`.

---

### 1. Project Setup & Structure

*   [ ] **Task 1.1:** Initialize Git repository.
*   [ ] **Task 1.2:** Create root directories (`wellfix_api`, `tests`, `scripts`, `config`).
*   [ ] **Task 1.3:** Setup FastAPI `main.py` entry point.
*   [ ] **Task 1.4:** Create initial module directories within `wellfix_api` (`auth`, `users`, `core`, `models`, `schemas`, `crud`, `api/v1/endpoints`).
*   [ ] **Task 1.5:** Create `__init__.py` files as needed for package structure.

### 2. Dependency & Configuration Management

*   [ ] **Task 2.1:** Initialize `Poetry` (`poetry init`) or create `requirements.txt`.
*   [ ] **Task 2.2:** Add core dependencies: `python`, `fastapi`, `uvicorn[standard]`, `pydantic[email]`, `passlib[bcrypt]`, `python-jose[cryptography]`, `sqlalchemy`, `psycopg2-binary`, `alembic`, `python-dotenv` (or similar for config).
*   [ ] **Task 2.3:** Implement configuration loading (e.g., `core/config.py` using Pydantic Settings) for `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.
*   [ ] **Task 2.4:** Create `.env.example` file with placeholder config variables.
*   [ ] **Task 2.5:** Write basic test (`tests/core/test_config.py`) to ensure config loads.

### 3. Database Setup & Core Models

*   [ ] **Task 3.1:** Implement database session handling (`core/db.py` - `SessionLocal`, `get_db` dependency).
*   [ ] **Task 3.2:** Define `User` model (`models/user.py`) with fields from `docs/data-models.md` (use SQLAlchemy).
*   [ ] **Task 3.3:** Define `Address` model (`models/address.py`) with fields and relationship to `User`.
*   [ ] **Task 3.4:** Set up Alembic (`alembic init alembic`). Configure `alembic.ini` and `env.py` to use database URL from config and target models.
*   [ ] **Task 3.5:** Generate initial Alembic migration (`alembic revision --autogenerate -m "Initial User and Address models"`). Review and edit migration script.
*   [ ] **Task 3.6:** Write basic model tests (`tests/models/test_user.py`, `tests/models/test_address.py`) ensuring model creation and relationship work via test DB session.
*   [ ] **Task 3.7:** Run migrations (`alembic upgrade head`) on test/dev database.

### 4. Core Schemas & CRUD Utilities

*   [ ] **Task 4.1:** Define `User` Pydantic schemas (`schemas/user.py`: `UserBase`, `UserCreate`, `UserUpdate`, `UserInDB`, `User`).
*   [ ] **Task 4.2:** Define `Address` Pydantic schemas (`schemas/address.py`: `AddressBase`, `AddressCreate`, `AddressUpdate`, `Address`).
*   [ ] **Task 4.3:** Implement `User` CRUD functions (`crud/crud_user.py`: `get_user`, `get_user_by_email`, `get_users`, `create_user`, `update_user`).
*   [ ] **Task 4.4:** Implement `Address` CRUD functions (`crud/crud_address.py`: `create_user_address`, `get_user_addresses`, `update_address`, `delete_address`).
*   [ ] **Task 4.5:** Define Token schemas (`schemas/token.py`: `Token`, `TokenData`).
*   [ ] **Task 4.6:** Write unit tests (`tests/crud/test_crud_user.py`, `tests/crud/test_crud_address.py`) for all CRUD functions using a test DB session.

### 5. Authentication Implementation (/auth)

*   [ ] **Task 5.1:** Implement password hashing (`core/security.py`: `verify_password`, `get_password_hash`).
*   [ ] **Task 5.2:** Implement JWT handling (`core/security.py`: `create_access_token`, potentially `decode_access_token` if needed outside dependency).
*   [ ] **Task 5.3:** Implement `get_current_user` dependency (`core/dependencies.py` or `auth/dependencies.py`) using token decoding and `crud_user.get_user`.
*   [ ] **Task 5.4:** Implement `POST /auth/register` endpoint (`api/v1/endpoints/auth.py`) using `crud_user.create_user` and `create_access_token`.
*   [ ] **Task 5.5:** Implement `POST /auth/login` endpoint (`api/v1/endpoints/auth.py`) using `crud_user.get_user_by_email`, `verify_password`, and `create_access_token`.
*   [ ] **Task 5.6:** Implement `GET /auth/me` endpoint (`api/v1/endpoints/auth.py`) using the `get_current_user` dependency.
*   [ ] **Task 5.7:** Write integration tests (`tests/api/v1/test_auth.py`) for register, login (success/fail), get /me (auth required).
*   [ ] **Task 5.8:** Write unit tests (`tests/core/test_security.py`) for password/JWT functions.

### 6. User Profile Management (/users/me)

*   [ ] **Task 6.1:** Implement `GET /users/me` endpoint (`api/v1/endpoints/users.py`) using `get_current_user` dependency.
*   [ ] **Task 6.2:** Implement `PATCH /users/me` endpoint (`api/v1/endpoints/users.py`) using `get_current_user` and `crud_user.update_user`.
*   [ ] **Task 6.3:** Write integration tests (`tests/api/v1/test_users.py`) for `GET /users/me` and `PATCH /users/me` (auth required, update specific fields).

### 7. Admin User Management (/admin/users)

*   [ ] **Task 7.1:** Implement `require_admin` dependency (`core/dependencies.py` or `admin/dependencies.py`) checking `current_user.role == 'ADMIN'`.
*   [ ] **Task 7.2:** Implement `GET /admin/users` endpoint (`api/v1/endpoints/admin_users.py`) using `crud_user.get_users` and `require_admin` dependency. Implement pagination/filtering.
*   [ ] **Task 7.3:** Implement `POST /admin/users` endpoint using `crud_user.create_user` (ensure role is Engineer/Admin) and `require_admin`.
*   [ ] **Task 7.4:** Implement `GET /admin/users/{user_id}` endpoint using `crud_user.get_user` and `require_admin`.
*   [ ] **Task 7.5:** Implement `PATCH /admin/users/{user_id}` endpoint using `crud_user.update_user` and `require_admin`.
*   [ ] **Task 7.6:** Write integration tests (`tests/api/v1/test_admin_users.py`) for all admin endpoints: Test Admin access, test non-Admin rejection (403), test functionality (list+filter, create, get, update).

### 8. Initial Logging & Error Handling Setup

*   [ ] **Task 8.1:** Configure basic logging in FastAPI startup (e.g., using `logging.basicConfig` or `loguru`).
*   [ ] **Task 8.2:** Implement basic FastAPI exception handlers for `HTTPException`, 404 Not Found (e.g., `NoResultFound` from SQLAlchemy), 422 Unprocessable Entity (e.g., DB `IntegrityError` on unique constraints), and a generic 500 handler.
*   [ ] **Task 8.3:** Ensure handlers log the error and return JSON responses matching format in `docs/api-design.md`.
*   [ ] **Task 8.4:** Manually test/write tests to verify error responses for common scenarios (invalid input, resource not found, duplicate email). 