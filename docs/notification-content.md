# WellFix - Notification Content Examples

**Version:** 1.0
**Date:** 2023-10-27

This document provides example content and triggers for user notifications (Email and potentially In-App) as referenced in the functional requirements. The final wording should be reviewed for clarity, tone, and consistency.

**Placeholders:** `{customer_name}`, `{job_id}`, `{engineer_name}`, `{status}`, `{quote_amount}`, `{pincode}`

---

## Notification Triggers & Example Content

**1. New Job Created (Admin Notification)**
   *   **Trigger:** `RepairJob` created (Status: `PENDING_ASSIGNMENT`). Functional Req: 4.4.1
   *   **Channel:** Email, In-App Alert
   *   **Subject (Email):** New Repair Request Received - Job #{job_id}
   *   **Body:**
     ```
     A new repair request (Job #{job_id}) has been submitted by {customer_name} for pincode {pincode}.

     Please log in to the Admin dashboard to review and assign the job.
     ```

**2. Job Assigned to Engineer (Engineer Notification)**
   *   **Trigger:** Admin assigns `engineer_id` to `RepairJob` (Status changes to `ASSIGNED_TO_ENGINEER`). Functional Req: 4.4.2
   *   **Channel:** Email, In-App Alert
   *   **Subject (Email):** New Job Assigned - Job #{job_id}
   *   **Body:**
     ```
     Hi {engineer_name},

     You have been assigned a new repair job:
     Job ID: {job_id}
     Customer: {customer_name}
     Location Pincode: {pincode}

     Please review the details in your dashboard.
     ```

**3. Job Assigned to Engineer (Customer Notification - Optional but Recommended)**
   *   **Trigger:** Admin assigns `engineer_id` to `RepairJob` (Status changes to `ASSIGNED_TO_ENGINEER`).
   *   **Channel:** Email, In-App Alert
   *   **Subject (Email):** Your WellFix Repair #{job_id} Has Been Assigned
   *   **Body:**
     ```
     Hi {customer_name},

     Good news! Your repair request (Job #{job_id}) has been assigned to an engineer, {engineer_name}.

     You can track the status of your repair in your WellFix dashboard.
     ```

**4. Job Status Update (Customer Notification - Key Statuses)**
   *   **Trigger:** `RepairJob` status changes to key states (e.g., `EN_ROUTE`, `ESCALATED_TO_LAB`, `PENDING_QUOTE_APPROVAL`, `REPAIR_IN_PROGRESS_LAB`, `PENDING_RETURN_DELIVERY`, `COMPLETED`). Functional Req: 4.6.2
   *   **Channel:** Email, In-App Alert
   *   **Subject (Email):** Update on Your WellFix Repair #{job_id}
   *   **Body (Example - Escalated to Lab):**
     ```
     Hi {customer_name},

     An update on your repair Job #{job_id}: Our engineer has assessed the issue and determined that your laptop requires further diagnosis/repair at our lab. We will arrange pickup shortly.

     Current Status: {status}

     You can track progress in your WellFix dashboard.
     ```
   *   **Body (Example - Completed):**
     ```
     Hi {customer_name},

     Great news! The repair for Job #{job_id} is complete.

     [Include details based on final status - e.g., next steps for payment/delivery if applicable]

     Current Status: {status}
     ```

**5. Quote Ready (Customer Notification)**
   *   **Trigger:** Admin/Engineer updates quote and sets status to `PENDING_QUOTE_APPROVAL`. Functional Req: 4.5.2
   *   **Channel:** Email, In-App Alert
   *   **Subject (Email):** Quote Ready for Your WellFix Repair #{job_id}
   *   **Body:**
     ```
     Hi {customer_name},

     We have prepared a quote for the lab repair of your laptop (Job #{job_id}). The estimated cost is {quote_amount}.

     Please log in to your dashboard to review and approve the quote to proceed with the repair.
     ```

**6. Job Cancelled (Customer/Admin/Engineer Notification)**
   *   **Trigger:** Job status changes to `CANCELLED`. Functional Req: 4.3.4 / 6.9
   *   **Channel:** Email, In-App Alert
   *   **Subject (Email):** WellFix Repair Job #{job_id} Cancelled
   *   **Body:**
     ```
     Repair Job #{job_id} has been cancelled.

     Reason: [Cancellation Reason]

     If you have questions, please contact support.
     ```

---

**Note:** The implementation should include configuration options to enable/disable specific notifications and potentially allow limited template customization by Admins in future versions. 