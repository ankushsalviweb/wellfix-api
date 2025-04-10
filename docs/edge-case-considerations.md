# WellFix - Edge Case & Implementation Considerations

**Version:** 1.0
**Date:** 2023-10-27

This document lists potential edge cases, concurrency issues, and other implementation details that developers should consider when building the features outlined in the functional requirements and API design. It complements the main ToDo lists.

---

## 1. Authentication & Authorization

*   **Account Lockout:** Consider implementing account lockout or rate limiting on login (`POST /auth/login`) to prevent brute-force attacks.
*   **Token Expiration/Refresh:** The current design uses a single access token. For longer sessions, consider implementing refresh tokens.
*   **RBAC Granularity:** Ensure Role-Based Access Control is strictly enforced on *all* relevant API endpoints, especially PATCH/POST/DELETE operations. Test cases should explicitly verify forbidden access attempts.
*   **Admin Self-Management:** Can an admin deactivate or change the role of their own account? Define and enforce rules around this.

## 2. Address & Serviceable Area Management

*   **Address Deletion Constraint:** The API design mentions preventing deletion of an address linked to active jobs (`DELETE /addresses/{address_id}`). Define "active" clearly (e.g., any status before `COMPLETED` or `CANCELLED`) and implement this check.
*   **Pincode Validation Timing:** Validation occurs on address creation/update and job creation. What happens if an admin deactivates a pincode *after* a job is created but *before* it's assigned/started? The current design allows this; consider if workflows need adjustment or warnings.
*   **Case Sensitivity:** Ensure pincode comparisons (e.g., in `ServiceableArea` checks) are consistent (e.g., always store/compare uppercase).

## 3. Job Workflow & Status Updates

*   **Concurrency:** What happens if two users (e.g., Admin and Engineer) try to update the status or assign the same job simultaneously? Use database transaction isolation levels appropriately. Consider using optimistic locking (e.g., passing expected current status/version) for critical updates if needed.
*   **Status Transition Side Effects:** Ensure actions triggered by status changes (like notifications) are handled reliably (e.g., use background tasks for sending emails to avoid blocking the API response).
*   **Orphaned Jobs:** What happens if an assigned engineer's account is deactivated? Ensure jobs can still be reassigned by an Admin.
*   **Lab Consent Flow:** The V1 consent is a simple boolean. Consider the exact UI flow and how/when this flag should be *unset* if the customer changes their mind before pickup.
*   **Cancellation Rules:** Define the exact statuses where cancellation is allowed/disallowed for both Customers and Admins. Ensure the `POST /jobs/{job_id}/cancel` endpoint strictly enforces this.
*   **Data Consistency:** Ensure related data (e.g., `final_cost`, `payment_status`) is only set/updated when the job is in an appropriate state.

## 4. Ratings

*   **Timing:** Ensure ratings can *only* be submitted after a job reaches the `COMPLETED` status.
*   **Uniqueness:** Enforce that only one rating can be submitted per job (database constraint or application logic).
*   **Engineer Deactivation:** What happens to ratings if the rated engineer's account is deactivated? Decide if ratings should be kept/anonymized/deleted.

## 5. Reporting & Analytics

*   **Performance:** Aggregation queries for reports (`GET /admin/reports/*`) can be slow on large datasets. Ensure proper database indexing on relevant columns (status, timestamps, engineer_id, customer_id, etc.). Consider caching results for frequently accessed reports.
*   **Time Zones:** Ensure all timestamps (`created_at`, `updated_at`, `scheduled_datetime`) are handled consistently, preferably stored in UTC in the database and converted to local timezones only for display purposes if needed.

## 6. General

*   **Input Validation:** Beyond basic type checks, validate string lengths, numerical ranges (e.g., rating score), and potentially use regular expressions for formats like phone numbers where appropriate.
*   **Idempotency:** Consider idempotency for critical POST/PATCH operations where feasible, especially if network issues could cause retries.
*   **Error Logging:** Ensure sufficient context (e.g., user ID, job ID, request details) is logged with errors to aid debugging.

---

Developers should actively think about these points during implementation and testing, bringing up any ambiguities or concerns for discussion. 