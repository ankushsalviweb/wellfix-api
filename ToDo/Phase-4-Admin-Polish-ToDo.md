# WellFix - Phase 4 ToDo: Admin Tools, Ratings & Polish

**Goal:** Implement Admin pricing config, Customer ratings, basic reporting, job cancellation, and polish existing features.

**Reference Plan:** `Plan/04-phase-admin-polish.md`

**Instructions:** Follow Check -> Code -> Test -> Iterate. Ensure adherence to `/rules` and alignment with `/docs`.

---

### 1. PricingConfig Model & Admin Management

*   [x] **Task 1.1:** Define `PricingConfig` model (`models/pricing.py`).
*   [x] **Task 1.2:** Generate Alembic migration (`... -m "Add PricingConfig model"`). Review/edit.
*   [x] **Task 1.3:** Run migration.
*   [x] **Task 1.4:** Define `PricingConfig` Pydantic schemas (`schemas/pricing.py`).
*   [x] **Task 1.5:** Implement `PricingConfig` CRUD functions (`crud/crud_pricing.py`).
*   [x] **Task 1.6:** Implement Admin API endpoint `GET /admin/pricing` (`api/v1/endpoints/admin_pricing.py`).
*   [x] **Task 1.7:** Implement Admin API endpoint `POST /admin/pricing`.
*   [x] **Task 1.8:** Implement Admin API endpoint `PATCH /admin/pricing/{config_id}`.
*   [x] **Task 1.9:** Write unit tests (`tests/crud/test_crud_pricing.py`).
*   [x] **Task 1.10:** Write integration tests (`tests/api/v1/test_admin_pricing.py`) (Admin access required).

### 2. Rating Model & Migrations

*   [x] **Task 2.1:** Define `Rating` model (`models/job.py`) with fields and relationships (User, Job).
*   [x] **Task 2.2:** Generate Alembic migration (`... -m "Add Rating model"`). Review/edit.
*   [x] **Task 2.3:** Run migration.
*   [x] **Task 2.4:** Write basic model tests (`tests/models/test_rating.py`).

### 3. Rating Schemas & CRUD

*   [x] **Task 3.1:** Define `Rating` Pydantic schemas (`schemas/rating.py`).
*   [x] **Task 3.2:** Implement `Rating` CRUD functions (`crud/crud_rating.py`: `create_rating`, `get_job_rating`, `list_ratings`).
*   [x] **Task 3.3:** Write unit tests (`tests/crud/test_crud_rating.py`).

### 4. Submit Rating API (/jobs/{job_id}/ratings - POST)

*   [x] **Task 4.1:** Implement `POST /jobs/{job_id}/ratings` endpoint (`api/v1/endpoints/ratings.py` or add to `jobs.py`) for Customers.
*   [x] **Task 4.2:** Add validation: Job exists, belongs to customer, status is `COMPLETED`, rating doesn't already exist (use `crud_rating.get_job_rating`).
*   [x] **Task 4.3:** Use `crud_rating.create_rating` linking correct `customer_id` and `engineer_id`.
*   [x] **Task 4.4:** Write integration tests (`tests/api/v1/test_ratings.py`) for submission (success, fail conditions).

### 5. Get/List Ratings APIs

*   [x] **Task 5.1:** Implement `GET /jobs/{job_id}/ratings` endpoint. Add authorization (Customer owner, assigned Engineer, Admin).
*   [x] **Task 5.2:** Implement `GET /admin/ratings` endpoint (`api/v1/endpoints/admin_ratings.py`) using `require_admin` and `crud_rating.list_ratings` (with filtering).
*   [x] **Task 5.3:** Write integration tests for getting specific rating and listing ratings (Admin access, filters).

### 6. Cancel Job API (/jobs/{job_id}/cancel - POST)

*   [x] **Task 6.1:** Implement `POST /jobs/{job_id}/cancel` endpoint (`api/v1/endpoints/jobs.py`).
*   [x] **Task 6.2:** Add authorization: Must be Admin OR Customer owner of the job.
*   [x] **Task 6.3:** Define cancellable statuses (e.g., `PENDING_ASSIGNMENT`, `ASSIGNED_TO_ENGINEER`) and implement validation.
*   [x] **Task 6.4:** Use `crud_job.update_job` to set status to `CANCELLED` and save `cancellation_reason`.
*   [x] **Task 6.5:** Write integration tests (`tests/api/v1/test_jobs_cancel.py`) for cancellation (Customer/Admin success, authorization fail, status validation fail).

### 7. Basic Reporting Endpoints (/admin/reports)

*   [x] **Task 7.1:** Implement `GET /admin/reports/dashboard` endpoint (`api/v1/endpoints/admin_reports.py`) using `require_admin`.
*   [x] **Task 7.2:** Implement `GET /admin/reports/engineer-productivity` endpoint using `require_admin`.
*   [x] **Task 7.3:** Write aggregation queries using SQLAlchemy within dedicated service/CRUD functions (e.g., `services/reporting.py`).
*   [x] **Task 7.4:** Write integration tests (`tests/api/v1/test_admin_reports.py`) checking Admin access and basic response structure.

### 8. Workflow Polish & Refinement - IN PROGRESS

*   [x] **Task 8.1:** Review existing API endpoints for potential bugs or usability improvements based on testing/feedback. Fixed authentication in tests to improve reliability.
*   [x] **Task 8.2:** Enhance logging messages where needed for better traceability.
*   [x] **Task 8.3:** Improve clarity/consistency of error messages.
*   [x] **Task 8.4:** Refactor any complex code sections for better readability/maintainability. Refactored authentication dependencies for better separation of concerns.
*   [x] **Task 8.5:** Ensure all previous tests still pass after refinements. Fixed test fixtures to use dependency overrides, fixed API router paths. 