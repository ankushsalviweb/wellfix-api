# WellFix - Plan: Phase 2 - Core Job Workflow (Customer/Admin)

**Phase Goal:** Implement the ability for customers to create repair jobs and for admins/customers to view job details and lists. Implement basic admin assignment and customer address management.

**Depends On:** Phase 1 Completion

**Related Documentation:**
*   `docs/data-models.md` (RepairJob, Address, ServiceableArea models)
*   `docs/api-design.md` (Sections 4, 5.1, 5.2, 6.1, 6.2, 6.3, 6.6)
*   `docs/functional-requirements.md` (Sections 4.2, 4.3.1, 4.3.4 [partially], 4.4.1, 4.4.2 [partially])
*   `docs/non-functional-requirements.mdc` (Reliability, Security, Maintainability)
*   Relevant `/rules/*.mdc` files

---

## Tasks Breakdown (Check -> Code -> Test -> Iterate)

**1. RepairJob Model & Migrations**
    *   [ ] **Check:** Review `docs/data-models.md` for the `RepairJob` entity and its relationships (User, Address).
    *   [ ] **Code:** Define SQLAlchemy model for `RepairJob` (`models/job.py`). Include necessary enums for status, repair type, etc. Establish relationships with `User` and `Address`.
    *   [ ] **Code:** Create Alembic migration script for the `RepairJob` table.
    *   [ ] **Test:** Run migrations. Basic tests to create/retrieve `RepairJob` via session, verifying relationships.
    *   [ ] **Iterate:** Refine model and migration based on testing.

**2. ServiceableArea Model & Admin Management**
    *   [ ] **Check:** Review `docs/data-models.md` (ServiceableArea) and `docs/api-design.md` (Section 5).
    *   [ ] **Code:** Define SQLAlchemy model for `ServiceableArea` (`models/service_area.py`).
    *   [ ] **Code:** Create Alembic migration for `ServiceableArea` table.
    *   [ ] **Code:** Define Pydantic schemas for `ServiceableArea` (`schemas/service_area.py`).
    *   [ ] **Code:** Implement CRUD functions for `ServiceableArea` (`crud/crud_service_area.py`).
    *   [ ] **Code:** Implement Admin API endpoints:
        *   `GET /admin/serviceable-areas` (List areas).
        *   `POST /admin/serviceable-areas` (Add area).
        *   `PATCH /admin/serviceable-areas/{pincode}` (Update status).
    *   [ ] **Test:** Run migrations. Unit tests for CRUD. Integration tests for API endpoints, including Admin role checks.
    *   [ ] **Iterate:** Refine model, schemas, CRUD, and API logic.

**3. Customer Address Management (/addresses)**
    *   [ ] **Check:** Review `docs/api-design.md` (Section 4) and `docs/functional-requirements.md` (4.2.1).
    *   [ ] **Code:** Implement API endpoints for Customers:
        *   `GET /addresses` (List own addresses).
        *   `POST /addresses` (Create address, *including validation against active ServiceableArea*).
        *   `GET /addresses/{address_id}` (Get own address details).
        *   `PATCH /addresses/{address_id}` (Update own address, *including pincode validation*).
        *   `DELETE /addresses/{address_id}` (Delete own address).
    *   [ ] **Test:** Integration tests for all address endpoints, covering CRUD operations, ownership checks, and pincode validation against `ServiceableArea`.
    *   [ ] **Iterate:** Refine address logic, validation, and error handling.

**4. RepairJob Schemas & CRUD**
    *   [ ] **Check:** Review `docs/data-models.md` (RepairJob) and map to API schemas in `docs/api-design.md`.
    *   [ ] **Code:** Define Pydantic schemas for `RepairJob` (Create, Update, Base, InDB, potentially different schemas for List vs Detail views) (`schemas/job.py`).
    *   [ ] **Code:** Implement basic CRUD functions for `RepairJob` (`crud/crud_job.py`), including filtering logic needed for listing.
    *   [ ] **Test:** Unit tests for `RepairJob` CRUD functions.
    *   [ ] **Iterate:** Adjust schemas and CRUD based on requirements and testing.

**5. Create Repair Job API (/jobs - POST)**
    *   [ ] **Check:** Review `docs/api-design.md` (6.1) and `docs/functional-requirements.md` (4.3.1).
    *   [ ] **Code:** Implement `POST /jobs` endpoint for Customers.
    *   [ ] **Code:** Include validation: Check `address_id` belongs to the customer, check address `pincode` is serviceable using `crud_service_area`.
    *   [ ] **Code:** Use `crud_job` to create the job with initial status.
    *   [ ] **Test:** Integration tests for job creation (success, address not owned, pincode not serviceable).
    *   [ ] **Iterate:** Refine creation logic, validation, and error responses.

**6. List Repair Jobs API (/jobs - GET)**
    *   [ ] **Check:** Review `docs/api-design.md` (6.2).
    *   [ ] **Code:** Implement `GET /jobs` endpoint.
    *   [ ] **Code:** Implement logic to filter results based on user role (Customer sees own, Admin sees all initially, Engineer logic deferred to Phase 3).
    *   [ ] **Code:** Implement filtering based on query parameters (status, pagination common; admin-specific filters).
    *   [ ] **Test:** Integration tests for listing jobs (as Customer, as Admin), testing filters and pagination.
    *   [ ] **Iterate:** Optimize query performance (if needed), refine filtering logic.

**7. Get Repair Job Details API (/jobs/{job_id} - GET)**
    *   [ ] **Check:** Review `docs/api-design.md` (6.3).
    *   [ ] **Code:** Implement `GET /jobs/{job_id}` endpoint.
    *   [ ] **Code:** Implement authorization logic: Customer can only access own jobs, Admin can access any. (Engineer access deferred).
    *   [ ] **Test:** Integration tests for getting job details (as Customer success/fail, as Admin success).
    *   [ ] **Iterate:** Refine response structure and authorization logic.

**8. Assign Engineer API (/jobs/{job_id}/assign - PATCH)**
    *   [ ] **Check:** Review `docs/api-design.md` (6.6).
    *   [ ] **Code:** Implement `PATCH /jobs/{job_id}/assign` endpoint for Admins.
    *   [ ] **Code:** Validate that the `engineer_id` corresponds to a user with the 'ENGINEER' role. Validate job status allows assignment.
    *   [ ] **Code:** Update `RepairJob.engineer_id` and potentially `RepairJob.status`.
    *   [ ] **Test:** Integration tests for assigning/unassigning engineers (Admin success, non-Admin fail, invalid engineer ID, job status validation).
    *   [ ] **Iterate:** Refine assignment logic and validation.

**9. Admin Job Notifications (Basic)**
    *   [ ] **Check:** Review `docs/functional-requirements.md` (4.4.1).
    *   [ ] **Code:** Implement a basic mechanism (e.g., simple logging or placeholder function call) triggered when a new job is created via `POST /jobs`.
    *   [ ] **Code:** (Optional) Implement basic email sending logic if feasible within phase scope.
    *   [ ] **Test:** Verify trigger mechanism works (check logs or mock function calls).
    *   [ ] **Iterate:** Plan for more robust notification system later.

---

**Phase 2 Definition of Done:**
*   `RepairJob` and `ServiceableArea` models and migrations are complete.
*   Admins can manage Serviceable Areas via API.
*   Customers can fully manage their Addresses via API, including pincode validation.
*   Customers can create new `RepairJob` requests via API, with validation.
*   Customers and Admins can list jobs via API with role-based filtering.
*   Customers and Admins can retrieve full job details via API with authorization.
*   Admins can assign/unassign Engineers to jobs via API.
*   Basic notification trigger for new jobs is implemented.
*   All new code has corresponding tests and passes.
*   Code adheres to rules (style, docs, etc.). 