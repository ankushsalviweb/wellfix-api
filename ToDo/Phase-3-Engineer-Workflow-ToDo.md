# WellFix - Phase 3 ToDo: Engineer Workflow & Status Updates

**Goal:** Implement Engineer job views, detailed/validated status updates, note logging, quoting, payment updates, lab escalation.

**Reference Plan:** `Plan/03-phase-engineer-workflow.md`

**Instructions:** Follow Check -> Code -> Test -> Iterate. Ensure adherence to `/rules` and alignment with `/docs`.

---

### 1. Engineer Job Listing & Details Access

*   [x] **Task 1.1:** Modify `GET /jobs` logic: If user role is Engineer, call `crud_job.list_jobs_by_engineer(engineer_id=current_user.id)`.
*   [x] **Task 1.2:** Modify `GET /jobs/{job_id}` authorization: Add check `current_user.role == 'ENGINEER' AND job.engineer_id == current_user.id`.
*   [x] **Task 1.3:** Write/update integration tests (`tests/api/v1/test_jobs_engineer.py`) for Engineer listing assigned jobs and accessing details (success/fail).

### 2. Job Status State Machine & Validation Logic

*   [x] **Task 2.1:** Define allowed status transitions visually (e.g., simple diagram or table) based on `docs/data-models.md` statuses and `docs/functional-requirements.md` workflows.
*   [x] **Task 2.2:** Implement status validation logic (e.g., `core/status_validator.py` function `is_transition_allowed(current_status, next_status, role)`).
*   [x] **Task 2.3:** Write unit tests (`tests/core/test_status_validator.py`) covering numerous valid/invalid transitions for different roles.

### 3. Update Job Status API (/jobs/{job_id}/status - PATCH)

*   [x] **Task 3.1:** Implement `PATCH /jobs/{job_id}/status` endpoint (`api/v1/endpoints/jobs.py`) accessible by Engineer & Admin.
*   [x] **Task 3.2:** Add authorization: Must be Admin OR assigned Engineer for the job.
*   [x] **Task 3.3:** Call status validator (`is_transition_allowed`) before updating. Return 422 if invalid.
*   [x] **Task 3.4:** If notes provided, append to `engineer_notes` or `admin_notes` based on `current_user.role`.
*   [x] **Task 3.5:** Handle specific field updates needed for certain transitions (e.g., `customer_consent_for_lab`).
*   [x] **Task 3.6:** Use `crud_job.update_job` to save status and other changes.
*   [x] **Task 3.7:** Write integration tests (`tests/api/v1/test_jobs_status.py`) testing valid/invalid transitions by Engineer/Admin, authorization, note appending, consent flag update.

### 4. Add Job Notes API (/jobs/{job_id}/notes - POST)

*   [x] **Task 4.1:** Implement `POST /jobs/{job_id}/notes` endpoint (`api/v1/endpoints/jobs.py`) for Engineer/Admin.
*   [x] **Task 4.2:** Add authorization: Must be Admin OR assigned Engineer.
*   [x] **Task 4.3:** Get job, append notes to relevant field (`engineer_notes`/`admin_notes`), save using `crud_job.update_job` (or dedicated CRUD function).
*   [x] **Task 4.4:** Write integration tests (`tests/api/v1/test_jobs_notes.py`) for adding notes as Engineer/Admin.

### 5. Lab Escalation & Consent Capture

*   [x] **Task 5.1:** Ensure `PATCH /jobs/{job_id}/status` correctly handles setting `customer_consent_for_lab=True` when request data includes it during the appropriate status transition (e.g., to `PENDING_PICKUP_FOR_LAB`).
*   [x] **Task 5.2:** Update integration tests for status updates (Task 3.7) to specifically verify consent flag handling.

### 6. Update Job Quote API (/jobs/{job_id}/quote - PATCH)

*   [x] **Task 6.1:** Implement `PATCH /jobs/{job_id}/quote` endpoint (`api/v1/endpoints/jobs.py`) for Admin/Engineer.
*   [x] **Task 6.2:** Add authorization: Must be Admin OR assigned Engineer.
*   [x] **Task 6.3:** Implement logic to update `estimated_cost`/`final_cost` using `crud_job.update_job`.
*   [x] **Task 6.4:** Add validation based on job status (e.g., require `LAB_DIAGNOSIS` before setting `estimated_cost`).
*   [x] **Task 6.5:** Append optional notes.
*   [x] **Task 6.6:** Write integration tests (`tests/api/v1/test_jobs_quote.py`) for updating costs (Admin/Engineer access, status validation).

### 7. Update Payment Status API (/jobs/{job_id}/payment - PATCH)

*   [x] **Task 7.1:** Implement `PATCH /jobs/{job_id}/payment` endpoint (`api/v1/endpoints/jobs.py`) for Admin/Engineer.
*   [x] **Task 7.2:** Add authorization: Must be Admin OR assigned Engineer.
*   [x] **Task 7.3:** Implement logic to update `payment_status` using `crud_job.update_job`. Validate input enum.
*   [x] **Task 7.4:** Add validation based on job status (e.g., require `COMPLETED` or `PENDING_PAYMENT`).
*   [x] **Task 7.5:** Write integration tests (`tests/api/v1/test_jobs_payment.py`) for updating payment status. 