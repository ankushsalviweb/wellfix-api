# WellFix - Plan: Phase 3 - Engineer Workflow & Status Updates

**Phase Goal:** Implement engineer-specific views (assigned jobs), detailed status update logic (including validation), note logging, quoting, payment status updates, and the lab escalation process.

**Depends On:** Phase 2 Completion

**Related Documentation:**
*   `docs/data-models.md` (RepairJob statuses, notes fields, costs)
*   `docs/api-design.md` (Sections 6.2, 6.3, 6.4, 6.5, 6.7, 6.8)
*   `docs/functional-requirements.md` (Sections 4.4.3 - 4.4.7, 4.5.2, 4.5.4, 4.9.1)
*   `docs/non-functional-requirements.mdc` (Reliability, Maintainability)
*   Relevant `/rules/*.mdc` files

---

## Tasks Breakdown (Check -> Code -> Test -> Iterate)

**1. Engineer Job Listing & Details Access**
    *   [ ] **Check:** Review `docs/api-design.md` (6.2, 6.3) for Engineer role access requirements.
    *   [ ] **Code:** Modify `GET /jobs` endpoint logic to correctly filter for jobs where `engineer_id` matches the authenticated Engineer.
    *   [ ] **Code:** Modify `GET /jobs/{job_id}` endpoint authorization to grant access if the authenticated user is the assigned Engineer.
    *   [ ] **Test:** Update/add integration tests for `GET /jobs` and `GET /jobs/{job_id}` specifically for the Engineer role (verify they see only assigned jobs, verify access granted/denied correctly).
    *   [ ] **Iterate:** Refine filtering and authorization logic.

**2. Job Status State Machine & Validation Logic**
    *   [ ] **Check:** Review the full list of `RepairJob` statuses in `docs/data-models.md`. Define the valid transitions between statuses (e.g., PENDING_ASSIGNMENT -> ASSIGNED_TO_ENGINEER, ON_SITE_DIAGNOSIS -> REPAIR_IN_PROGRESS_ON_SITE or ESCALATED_TO_LAB).
    *   [ ] **Code:** Design and implement a state validation mechanism. This could be a dedicated utility function, a state machine library, or logic within the relevant CRUD/API endpoint.
    *   [ ] **Code:** Define which roles (Engineer, Admin) can trigger which transitions.
    *   [ ] **Test:** Unit tests for the status transition validation logic covering allowed and disallowed transitions for different roles.
    *   [ ] **Iterate:** Refine the state machine logic for clarity and correctness.

**3. Update Job Status API (/jobs/{job_id}/status - PATCH)**
    *   [ ] **Check:** Review `docs/api-design.md` (6.4) and defined status transitions (Task 2 above).
    *   [ ] **Code:** Implement `PATCH /jobs/{job_id}/status` endpoint for Engineers and Admins.
    *   [ ] **Code:** Integrate the status transition validation logic (Task 2). Reject requests attempting invalid transitions with a `422 Unprocessable Entity` error.
    *   [ ] **Code:** Ensure the `notes` field in the request body is appended to the correct notes field (`engineer_notes` or `admin_notes`) based on the user's role.
    *   [ ] **Code:** Handle specific field updates required for certain transitions (e.g., setting `customer_consent_for_lab` when moving to `PENDING_PICKUP_FOR_LAB`).
    *   [ ] **Test:** Integration tests covering valid and invalid status updates by Engineers and Admins. Test role permissions. Test note appending. Test specific field updates during transitions.
    *   [ ] **Iterate:** Refine endpoint logic, validation, and error handling.

**4. Add Job Notes API (/jobs/{job_id}/notes - POST)**
    *   [ ] **Check:** Review `docs/api-design.md` (6.5).
    *   [ ] **Code:** Implement `POST /jobs/{job_id}/notes` endpoint for Engineers and Admins.
    *   [ ] **Code:** Append provided notes to the correct field (`engineer_notes` or `admin_notes`) based on user role.
    *   [ ] **Test:** Integration tests for adding notes as Engineer and Admin.
    *   [ ] **Iterate:** Refine note handling logic.

**5. Lab Escalation & Consent Capture**
    *   [ ] **Check:** Review functional requirements for lab escalation (4.4.5).
    *   [ ] **Code:** Ensure the status update endpoint (Task 3) correctly handles the transition to `ESCALATED_TO_LAB` and `PENDING_PICKUP_FOR_LAB`, including setting the `customer_consent_for_lab` flag based on request data.
    *   [ ] **Test:** Specific integration tests focusing on the lab escalation status transitions and consent flag update.
    *   [ ] **Iterate:** Clarify consent capture mechanism if needed (simple boolean for V1).

**6. Update Job Quote API (/jobs/{job_id}/quote - PATCH)**
    *   [ ] **Check:** Review `docs/api-design.md` (6.7) and functional requirements (4.5.2, 4.5.4).
    *   [ ] **Code:** Implement `PATCH /jobs/{job_id}/quote` endpoint for Admins/Engineers.
    *   [ ] **Code:** Allow updating `estimated_cost` and `final_cost`. Validate inputs.
    *   [ ] **Code:** Append optional notes to the user's note field.
    *   [ ] **Code:** Implement basic validation based on job status (e.g., maybe only allow setting `estimated_cost` after `LAB_DIAGNOSIS`).
    *   [ ] **Test:** Integration tests for updating quote/cost information as Admin/Engineer, including status validation.
    *   [ ] **Iterate:** Refine cost update logic and validation rules.

**7. Update Payment Status API (/jobs/{job_id}/payment - PATCH)**
    *   [ ] **Check:** Review `docs/api-design.md` (6.8) and functional requirements (4.9.1).
    *   [ ] **Code:** Implement `PATCH /jobs/{job_id}/payment` endpoint for Admins/Engineers.
    *   [ ] **Code:** Allow setting `payment_status` to `PAID` or `WAIVED`. Validate input.
    *   [ ] **Code:** Implement validation based on job status (e.g., job should likely be `COMPLETED` or `PENDING_PAYMENT`).
    *   [ ] **Test:** Integration tests for updating payment status, including status validation.
    *   [ ] **Iterate:** Refine payment status logic.

---

**Phase 3 Definition of Done:**
*   Engineers can list and view details of their assigned jobs.
*   Job status transitions are validated according to defined rules and roles.
*   Engineers and Admins can update job statuses and add notes via the API.
*   Lab escalation process, including basic consent capture, is supported via status updates.
*   Admins/Engineers can update job costs (quote/final) via API.
*   Admins/Engineers can update job payment status via API.
*   All new/modified code has corresponding tests and passes.
*   Code adheres to rules. 