# WellFix - Product Requirements Document (PRD)

**Version:** 1.0
**Date:** 2023-10-27

## 1. Introduction

WellFix is a Software-as-a-Service (SaaS) application designed to be the central management system for a laptop repair business operating within specific pincodes in a city. It facilitates the entire repair lifecycle, connecting customers needing repairs, the engineers performing the work (both on-site and in a lab), and the administrators overseeing operations. The primary goal is to streamline the repair process, improve efficiency, enhance transparency for customers, and provide a scalable platform for future growth.

## 2. Goals

- **Efficiency:** Minimize repair request-to-completion time.
- **Quality:** Ensure high standards for repairs, including tracking parts and potential warranty information.
- **Usability:** Provide an intuitive and responsive web interface accessible on both desktop and mobile devices for all user types.
- **Transparency:** Offer real-time job status tracking for customers and admins.
- **Scalability:** Build a foundation that supports future expansion to new service areas and potentially new features.

## 3. User Roles & Personas

1.  **Customer:** Individuals or businesses requiring laptop repair services.
    *   *Needs:* Easy scheduling, clear communication, status tracking, reliable repairs, simple feedback mechanism.
2.  **Engineer:** Full-time technical staff performing repairs.
    *   *Needs:* Clear job details, efficient workflow for on-site and lab tasks, easy status updates, communication channel for escalation/quotes, payment collection process.
3.  **Admin:** Operational staff managing the service.
    *   *Needs:* Overview of all jobs, ability to assign/manage jobs and engineers, tools to manage service areas and pricing, performance monitoring, user management.

## 4. Key Features & Functional Requirements

This section outlines the core functionality required. Refer to detailed functional requirements documentation for specifics.

**4.1. Authentication & User Management**
    - Secure registration/login for Customers (email/password).
    - Secure login for pre-registered Engineers and Admins.
    - Role-based access control restricting features by user type (Customer, Engineer, Admin).
    - Customer profile management (name, contact, addresses).
    - Admin capabilities for managing Engineer/Admin accounts and roles.

**4.2. Address & Service Area Management**
    - Customers can store multiple addresses; one default.
    - Automatic pincode validation during scheduling against admin-defined serviceable areas.
    - Admin interface to manage the list of active serviceable pincodes.

**4.3. Repair Scheduling & Management**
    - Customer interface to initiate repair requests, providing device details and symptoms.
    - Selection of repair type (On-site Part Replacement, Lab Diagnosis, Lab Chipl-level Repair).
    - Display of estimated pricing based on repair type/flat rates and Repair ETA based on status.
    - (Optional V1.1) Interactive calendar for preferred date/time selection based on availability.
    - Ability for customers/admins to reschedule/cancel jobs (with rules/logging).
**4.4. Job Assignment & Workflow**
    - Admin notification (in-app, email) for new repair requests.
    - Admin dashboard to view pending/active jobs and assign them to available Engineers based on location/skill.
    - Engineer interface to view assigned jobs, customer details, and location (map integration desirable).
    - Workflow support for:
        - On-site assessment & completion (part replacement).
        - Escalation process to lab repair (diagnosis, motherboard) with customer consent capture.
        - Secure laptop pickup/delivery tracking for lab jobs.
    - Engineers update job status, log detailed notes, record parts used.
    - Admins monitor progress of all jobs (on-site and lab).

**4.5. Pricing & Quoting**
    - Admin interface to manage pricing for flat-rate services (on-site, diagnosis fee).
    - Mechanism for Engineers/Admins to provide custom quotes for complex lab repairs after diagnosis.
    - Display upfront estimated costs; finalize costs upon completion or quote approval.

**4.6. Communication & Tracking**
    - Real-time status updates visible to Customers and Admins throughout the repair lifecycle.
    - In-app and email notifications for critical status changes (e.g., assigned, escalated to lab, quote ready, completed, ready for delivery).

**4.7. Ratings & Feedback**
    - Customers can rate completed jobs and provide comments on engineer service.
    - Admins can view ratings and feedback for performance monitoring.

**4.8. Reporting & Analytics**
    - Admin dashboard displaying key metrics (e.g., jobs pending, jobs completed, average rating).
    - Basic reports on repair turnaround times, engineer productivity, customer satisfaction trends.

**4.9. Payment Recording**
    - Simple mechanism for Engineers/Admins to mark jobs as paid (initially manual recording for Cash/UPI).
    - Track payment status against jobs.

## 5. Non-Functional Requirements

- **Responsiveness:** The web interface must adapt gracefully to various screen sizes (desktop, tablet, mobile).
- **Usability:** Interfaces should be intuitive and easy to navigate for each user role.
- **Performance:** Application should respond quickly, especially for status updates and job lists.
- **Reliability:** The system must be stable and minimize errors, with robust error handling and logging (`python-error-handling-and-logging-rule.mdc`).
- **Security:** Standard security practices for authentication, data storage (hashed passwords), and authorization must be implemented.
- **Maintainability:** Code should follow defined style guides (`python-code-style-consistency-rule.mdc`), be well-documented (`python-documentation-rule.mdc`), and modular (`python-modular-design-rule.mdc`) for ease of future development.

## 6. Data Overview

The system will manage core data entities including `Users` (with roles), `Addresses`, `ServiceableAreas` (pincodes), `RepairJobs` (tracking details, status, assigned engineer, costs), `JobStatusUpdates` (history log), and `Ratings`. Relationships between these entities are defined (e.g., Customer owns Jobs/Addresses, Job assigned to Engineer). Refer to `docs/data-models.md` for details.

## 7. Architecture Overview

The backend will be developed as a **Modular Monolith** using **Python** (likely with **FastAPI** or **Django**) and **PostgreSQL**. It will expose a **REST API** for the frontend. The frontend will be a single responsive web application built with standard web technologies (HTML/CSS/JS, potentially a framework like React/Vue). Refer to `docs/architecture-overview.md` for details.

## 8. Out of Scope (Initial Version - V1.0)

- Automated payment gateway integration.
- Detailed inventory management for parts.
- Automated engineer scheduling/optimization.
- Native mobile applications.
- Advanced analytics and predictive reporting.
- Customer self-service for complex diagnostics. 