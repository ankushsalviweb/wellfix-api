# WellFix - Phase 2 ToDo: Core Job Workflow (Customer/Admin)

**Goal:** Implement RepairJob model, Customer job creation/viewing, Admin job viewing/assignment, ServiceableArea & Address management.

**Reference Plan:** `Plan/02-phase-core-workflow.md`

**Instructions:** Follow Check -> Code -> Test -> Iterate. Ensure adherence to `/rules` and alignment with `/docs`.

---

### 1. RepairJob Model & Migrations

*   [x] **Task 1.1:** Define `RepairJob` SQLAlchemy model (`models/job.py`) with all fields and relationships (to User, Address) as per `docs/data-models.md`.
*   [x] **Task 1.2:** Define necessary Enums (JobStatus, RepairType, PaymentStatus) within `models/job.py` or `models/enums.py`.
*   [x] **Task 1.3:** Generate Alembic migration (`alembic revision --autogenerate -m "Add RepairJob model"`). Review and edit.
*   [x] **Task 1.4:** Run migration (`alembic upgrade head`).
*   [x] **Task 1.5:** Write basic model tests (`tests/models/test_job.py`) for creation and relationships.

### 2. ServiceableArea Model & Admin Management

*   [x] **Task 2.1:** Define `ServiceableArea` model (`models/service_area.py`).
*   [x] **Task 2.2:** Generate Alembic migration (`... -m "Add ServiceableArea model"`). Review/edit.
*   [x] **Task 2.3:** Run migration.
*   [x] **Task 2.4:** Define `ServiceableArea` Pydantic schemas (`schemas/service_area.py`).
*   [x] **Task 2.5:** Implement `ServiceableArea` CRUD functions (`crud/crud_service_area.py`: `get_area`, `list_areas`, `create_area`, `update_area_status`). Include logic to check if a pincode is active.
*   [x] **Task 2.6:** Implement Admin API endpoint `GET /admin/serviceable-areas` (`api/v1/endpoints/admin_service_areas.py`).
*   [x] **Task 2.7:** Implement Admin API endpoint `POST /admin/serviceable-areas`.
*   [x] **Task 2.8:** Implement Admin API endpoint `PATCH /admin/serviceable-areas/{pincode}`.
*   [x] **Task 2.9:** Write unit tests (`tests/crud/test_crud_service_area.py`) for CRUD functions.
*   [x] **Task 2.10:** Write integration tests (`tests/api/v1/test_admin_service_areas.py`) for API endpoints (Admin access required).

### 3. Customer Address Management (/addresses)

*   [x] **Task 3.1:** Implement `GET /addresses` endpoint (`api/v1/endpoints/addresses.py`) for Customers to list their addresses.
*   [x] **Task 3.2:** Implement `POST /addresses` endpoint. **Crucially:** Add validation using `crud_service_area` to ensure the `pincode` is active before creating.
*   [x] **Task 3.3:** Implement `GET /addresses/{address_id}` endpoint with ownership check.
*   [x] **Task 3.4:** Implement `PATCH /addresses/{address_id}` endpoint. **Crucially:** Add validation using `crud_service_area` if the `pincode` is being updated.
*   [x] **Task 3.5:** Implement `DELETE /addresses/{address_id}` endpoint.
*   [x] **Task 3.6:** Write/update integration tests (`tests/api/v1/test_addresses.py`) covering all endpoints, ownership, and pincode validation during create/update.

### 4. RepairJob Schemas & CRUD

*   [x] **Task 4.1:** Define `RepairJob` Pydantic schemas (`schemas/job.py`: `JobBase`, `JobCreate` [customer input], `JobUpdate` [internal use], `Job` [API response], `JobList` [summary for lists]). Include nested schemas for user/address details where appropriate in responses.
*   [x] **Task 4.2:** Implement `RepairJob` CRUD functions (`crud/crud_job.py`: `create_job`, `get_job`, `list_jobs_by_customer`, `list_jobs_by_engineer` [placeholder], `list_all_jobs` [admin], `update_job`). Include filtering/pagination logic in list functions.
*   [x] **Task 4.3:** Write unit tests (`tests/crud/test_crud_job.py`) for CRUD functions.

### 5. Create Repair Job API (/jobs - POST)

*   [x] **Task 5.1:** Implement `POST /jobs` endpoint (`api/v1/endpoints/jobs.py`) for Customers.
*   [x] **Task 5.2:** Add validation: Check ownership of `address_id` using `crud_address`.
*   [x] **Task 5.3:** Add validation: Check address pincode is serviceable using `crud_service_area`.
*   [x] **Task 5.4:** Use `crud_job.create_job` to save the job with `status='PENDING_ASSIGNMENT'` (or similar initial state).
*   [x] **Task 5.5:** Write integration tests (`tests/api/v1/test_jobs_customer.py`) for job creation (success, address validation fail, pincode validation fail).

### 6. List Repair Jobs API (/jobs - GET)

*   [x] **Task 6.1:** Implement `GET /jobs` endpoint (`api/v1/endpoints/jobs.py`).
*   [x] **Task 6.2:** Use `get_current_user` dependency. Check user role.
*   [x] **Task 6.3:** If Customer, call `crud_job.list_jobs_by_customer`.
*   [x] **Task 6.4:** If Admin, call `crud_job.list_all_jobs`.
*   [x] **Task 6.5:** (Engineer logic deferred). Handle query parameters (status, pagination) within CRUD or service layer.
*   [x] **Task 6.6:** Write integration tests (`tests/api/v1/test_jobs_customer.py`, `tests/api/v1/test_jobs_admin.py`) for listing jobs as Customer and Admin, testing filters.

### 7. Get Repair Job Details API (/jobs/{job_id} - GET)

*   [x] **Task 7.1:** Implement `GET /jobs/{job_id}` endpoint (`api/v1/endpoints/jobs.py`).
*   [x] **Task 7.2:** Use `crud_job.get_job` to retrieve the job.
*   [x] **Task 7.3:** Implement authorization: Check if `current_user.role == 'ADMIN'` OR (`current_user.role == 'CUSTOMER'` AND `job.customer_id == current_user.id`). Raise 403/404 otherwise.
*   [x] **Task 7.4:** Write integration tests for getting details (Customer success/fail, Admin success).

### 8. Assign Engineer API (/jobs/{job_id}/assign - PATCH)

*   [x] **Task 8.1:** Implement `PATCH /jobs/{job_id}/assign` endpoint (`api/v1/endpoints/jobs.py`) using `require_admin` dependency.
*   [x] **Task 8.2:** Get engineer user using `crud_user.get_user`. Validate user exists and `role == 'ENGINEER'`.
*   [x] **Task 8.3:** Get job using `crud_job.get_job`. Validate job exists and status is appropriate for assignment (e.g., `PENDING_ASSIGNMENT`).
*   [x] **Task 8.4:** Use `crud_job.update_job` to set `engineer_id` and update `status` to `ASSIGNED_TO_ENGINEER`.
*   [x] **Task 8.5:** Write integration tests (`tests/api/v1/test_jobs_admin.py`) for assigning/unassigning (Admin success, validation failures).

### 9. Admin Job Notifications (Basic)

*   [x] **Task 9.1:** In `POST /jobs` endpoint logic (Task 5.4), add a call to a placeholder notification function (e.g., `notifications.notify_admin_new_job(job)`).
*   [x] **Task 9.2:** Implement the placeholder function in `core/notifications.py` (initially just logs a message).
*   [x] **Task 9.3:** Write test to ensure the notification function is called on successful job creation (can use `mocker`). 