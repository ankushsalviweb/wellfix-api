# WellFix - Detailed Functional Requirements

**Version:** 1.0
**Date:** 2023-10-27

This document elaborates on the key features outlined in the PRD (Section 4), providing more specific functional details for the software development team. It references the conceptual data models (`docs/data-models.md`) and architecture (`docs/architecture-overview.md`).

---

## 4. Key Features & Functional Requirements (Detailed)

**4.1. Authentication & User Management**

*   **4.1.1 Customer Registration:**
    *   Input: First Name, Last Name, Email, Phone Number, Password, Confirm Password.
    *   Process: Validate inputs (required fields, email format, password complexity, match passwords). Check if email already exists. Hash password securely. Create `User` record with `role`='CUSTOMER'.
    *   Output: Logged-in session for the new customer.
*   **4.1.2 Customer Login:**
    *   Input: Email, Password.
    *   Process: Validate inputs. Find `User` by email. Verify password against stored hash. Check if `is_active`. Create logged-in session.
    *   Output: Logged-in session or error message.
*   **4.1.3 Engineer/Admin Login:**
    *   Input: Email, Password.
    *   Process: Same as Customer Login, but for users with `role`='ENGINEER' or 'ADMIN'. Accounts are pre-created by Admins.
    *   Output: Logged-in session or error message.
*   **4.1.4 Role-Based Access Control (RBAC):**
    *   Process: Backend API endpoints and frontend UI components must check the logged-in user's `role` before granting access to specific features or data (e.g., only Admins access user management, only Engineers update job notes).
*   **4.1.5 Customer Profile Management:**
    *   Input: View/Edit First Name, Last Name, Phone Number. Manage `Address`es (see 4.2).
    *   Process: Allow logged-in Customers to update their own profile details in the `User` record.
*   **4.1.6 Admin User Management:**
    *   Interface: Admin-only section.
    *   Process: List all users (Customers, Engineers, Admins). Filter by role. Create new Engineer/Admin users (set email, temporary password, role). Activate/Deactivate any user account (`is_active` flag in `User`).

**4.2. Address & Service Area Management**

*   **4.2.1 Customer Address Management:**
    *   Process: Logged-in Customers can Add, View, Edit, Delete their `Address` records. One address can be marked as `is_default`.
    *   Input (Add/Edit): Street Address, City, State, Pincode.
    *   Validation: All fields required. Pincode must exist and be active in `ServiceableArea` table.
*   **4.2.2 Pincode Validation during Scheduling:**
    *   Process: When a Customer selects an address for a new `RepairJob`, the system must re-verify that the `pincode` of the selected `Address` is currently active in the `ServiceableArea` table.
    *   Output: Prevent scheduling if pincode is not serviceable.
*   **4.3.3 Admin Serviceable Area Management:**
    *   Interface: Admin-only section.
    *   Process: List all pincodes in `ServiceableArea`. Add new pincode (Input: Pincode string). Activate/Deactivate existing pincodes (`is_active` flag).

**4.3. Repair Scheduling & Management**

*   **4.3.1 Initiate Repair Request (Customer):**
    *   Interface: Customer-facing form.
    *   Input: Select existing `Address` or add new (triggering validation 4.2.1), Laptop Manufacturer, Laptop Model, Laptop Serial Number (optional), Reported Symptoms (text area), select `repair_type_requested` (Enum: ON_SITE_PART, LAB_DIAGNOSIS, LAB_CHIP_LEVEL).
    *   Process: Create new `RepairJob` record with status `PENDING_APPROVAL` or `PENDING_ASSIGNMENT`. Link to Customer `user_id` and selected `Address`.
*   **4.3.2 Display Estimated Price & ETA:**
    *   Process: When the repair type is selected (and potentially based on symptoms/model), display an *estimated* cost based on `PricingConfig` (for flat rates) and a *preliminary Estimated Time of Arrival (ETA)* or turnaround time based on business rules (e.g., On-site: 2-4 hours, Lab: 3-5 days). This ETA should dynamically update based on the job's current `status` when viewed later.
*   **4.3.3 (Optional V1.1) Calendar Integration:**
    *   Process: Display a calendar/time slot picker. Availability could be based on generic business hours initially, or simplified engineer availability.
*   **4.3.4 Reschedule/Cancel Job:**
    *   Process (Customer): View upcoming jobs. Option to Reschedule (if status allows, e.g., before `ASSIGNED_TO_ENGINEER`) or Cancel (if status allows). Cancellation requires selecting a reason (stored in `cancellation_reason` field of `RepairJob`).
    *   Process (Admin): Admins can reschedule or cancel any job, providing a reason.
    *   Rules: Define which statuses allow rescheduling/cancellation (e.g., cannot cancel once repair is in progress).

**4.4. Job Assignment & Workflow**

*   **4.4.1 Admin Job Notifications:**
    *   Trigger: New `RepairJob` created (status `PENDING_APPROVAL` / `PENDING_ASSIGNMENT`).
    *   Mechanism: In-app notification badge/list for Admins. Email notification to a designated admin email address.
*   **4.4.2 Admin Job Dashboard & Assignment:**
    *   Interface: Admin view listing jobs.
    *   Features: Filter jobs by `status`, `pincode`. View job details. Assign pending jobs (`PENDING_ASSIGNMENT` status) to an available `User` (Engineer).
    *   Process (Assign): Select Engineer from a list. System changes `RepairJob` status to `ASSIGNED_TO_ENGINEER`, sets `engineer_id`. Notify assigned engineer (4.4.3).
*   **4.4.3 Engineer Job View:**
    *   Interface: Engineer-specific dashboard/list.
    *   Features: View jobs assigned to them (`engineer_id` matches logged-in user). See Customer details (`first_name`, `phone_number`), `Address` (with map link if possible), `RepairJob` details (laptop info, symptoms).
*   **4.4.4 On-Site Workflow (Engineer):**
    *   Process: Engineer updates `RepairJob` `status`:
        *   `EN_ROUTE` -> `ON_SITE_DIAGNOSIS` -> `REPAIR_IN_PROGRESS_ON_SITE` (if parts available) -> `PENDING_PAYMENT` -> `COMPLETED`.
    *   Logging: Engineer adds notes to `engineer_notes` at various stages.
    *   Parts: Simple text logging of parts used in `engineer_notes` initially.
*   **4.4.5 Lab Escalation Workflow (Engineer):**
    *   Trigger: On-site diagnosis determines lab repair is needed.
    *   Process:
        1.  Engineer discusses with Customer.
        2.  Engineer updates status to `ESCALATED_TO_LAB`.
        3.  Engineer captures customer consent digitally (e.g., checkbox, signature capture - V2?) setting `customer_consent_for_lab` = True in `RepairJob`.
        4.  Engineer updates status to `PENDING_PICKUP_FOR_LAB`.
*   **4.4.6 Lab Pickup/Delivery Workflow:**
    *   Process: Status updates track physical movement:
        *   `PENDING_PICKUP_FOR_LAB` -> `IN_TRANSIT_TO_LAB` -> `LAB_DIAGNOSIS` -> (Quote/Approval ->) `REPAIR_IN_PROGRESS_LAB` -> `PENDING_RETURN_DELIVERY` -> `IN_TRANSIT_FROM_LAB` -> (Handover) -> `PENDING_PAYMENT` -> `COMPLETED`.
*   **4.4.7 Engineer Status Updates & Notes:**
    *   Interface: Simple mechanism for engineers to select the next valid status for a job and add text notes (`engineer_notes`). Backend must validate status transitions.
*   **4.4.8 Admin Job Monitoring:**
    *   Interface: Admin dashboard shows all jobs with current `status`, assigned `engineer_id`.

**4.5. Pricing & Quoting**

*   **4.5.1 Admin Price Management:**
    *   Interface: Admin-only section to manage `PricingConfig`.
    *   Process: Add/Edit/Activate/Deactivate flat-rate items (e.g., 'On-site Diagnosis Fee', 'RAM Upgrade 8GB') with associated `base_price`.
*   **4.5.2 Lab Repair Quoting:**
    *   Trigger: Job status is `LAB_DIAGNOSIS`.
    *   Process: Admin/Engineer assesses repair need, calculates cost. Updates `estimated_cost` field in `RepairJob`. Changes status to `PENDING_QUOTE_APPROVAL`. Notify Customer.
*   **4.5.3 Quote Approval/Rejection (Conceptual):**
    *   Process: Customer needs a way to view the quote and approve/reject (could be external communication initially, or simple button in UI - V1.1). Approval changes status to `REPAIR_IN_PROGRESS_LAB`. Rejection might lead to cancellation or return.
*   **4.5.4 Final Cost:**
    *   Process: Upon completion, `final_cost` field in `RepairJob` is updated based on flat rates or approved quote.

**4.6. Communication & Tracking**

*   **4.6.1 Real-time Status Display:**
    *   Interface: Customer and Admin views should display the current `status` string for relevant jobs.
    *   Mechanism: Frontend polls API endpoint (e.g., `GET /api/jobs/{job_id}`) periodically or uses WebSockets (V2) for updates.
*   **4.6.2 Notification Triggers:**
    *   Define specific `status` changes that trigger In-App and/or Email notifications (e.g., `ASSIGNED_TO_ENGINEER`, `ESCALATED_TO_LAB`, `PENDING_QUOTE_APPROVAL`, `PENDING_RETURN_DELIVERY`, `COMPLETED`).
    *   Target: Notify relevant user(s) (Customer, Admin, Engineer).

**4.7. Ratings & Feedback**

*   **4.7.1 Submit Rating (Customer):**
    *   Trigger: After `RepairJob` status is `COMPLETED`.
    *   Interface: Customer view shows completed jobs. Provides option to submit a `Rating` (Score 1-5, optional Comment).
    *   Process: Create `Rating` record linked to `job_id`, `customer_id`, `engineer_id`.
*   **4.7.2 View Ratings (Admin):**
    *   Interface: Admin section to view list/details of `Rating`s. Link back to job and engineer.

**4.8. Reporting & Analytics**

*   **4.8.1 Admin Dashboard Metrics:**
    *   Process: Backend calculates and API provides counts of jobs in key statuses (e.g., PENDING_ASSIGNMENT, REPAIR_IN_PROGRESS_LAB), overall average `Rating` score.
*   **4.8.2 Basic Reports:**
    *   Process: Backend API endpoints to generate simple data summaries:
        *   Jobs completed per engineer per time period.
        *   Average time spent in specific statuses.
        *   List of jobs with low ratings.

**4.9. Payment Recording**

*   **4.9.1 Mark as Paid:**
    *   Interface: Engineer/Admin view of a completed job (`PENDING_PAYMENT` status).
    *   Process: Button/action to mark payment as received. Updates `payment_status` field in `RepairJob` to `PAID`. Could potentially trigger final `COMPLETED` status if needed. 