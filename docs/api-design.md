# WellFix - REST API Design

**Version:** 1.0
**Date:** 2023-10-27

This document specifies the REST API endpoints for the WellFix backend application. It is based on the requirements outlined in `docs/functional-requirements.md`, `docs/data-models.md`, and `docs/architecture-overview.md`.

**Base URL:** `/api/v1` (All endpoints are prefixed with this)

**Authentication:** Primarily uses token-based authentication (e.g., JWT). A login endpoint returns a token, which must be included in the `Authorization: Bearer <token>` header for subsequent requests to protected endpoints.

**Standard Responses:**
- **Success:** 200 OK, 201 Created, 204 No Content
- **Client Errors:** 400 Bad Request (validation issues), 401 Unauthorized (not logged in), 403 Forbidden (logged in but insufficient permissions), 404 Not Found, 422 Unprocessable Entity (valid data, but violates business rules)
- **Server Errors:** 500 Internal Server Error

Error responses should follow a consistent format, e.g.:
```json
{
  "detail": "Error message explaining the issue."
}
```

---

## 1. Authentication (`/auth`)

Handles user registration, login, and potentially token management.

### 1.1 Register Customer

*   **Endpoint:** `POST /auth/register`
*   **Description:** Allows a new customer to register an account.
*   **Role(s):** Public
*   **Request Body:**
    ```json
    {
      "first_name": "string",
      "last_name": "string",
      "email": "user@example.com",
      "phone_number": "string",
      "password": "string"
    }
    ```
*   **Success Response:** `201 Created`
    *   Body: Contains the access token and user details (excluding password).
    ```json
    {
      "access_token": "string (jwt)",
      "token_type": "bearer",
      "user": {
          "user_id": "uuid",
          "email": "user@example.com",
          "first_name": "string",
          "last_name": "string",
          "phone_number": "string",
          "role": "CUSTOMER"
      }
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input data (e.g., invalid email format, weak password).
    *   `422 Unprocessable Entity`: Email already exists.

### 1.2 Login

*   **Endpoint:** `POST /auth/login`
*   **Description:** Authenticates a user (Customer, Engineer, or Admin) and returns an access token.
*   **Role(s):** Public
*   **Request Body:**
    ```json
    {
      "username": "user@example.com", // Typically the email
      "password": "string"
    }
    ```
    *(Note: Uses `username` for compatibility with standard OAuth2 forms, but maps to email)*
*   **Success Response:** `200 OK`
    *   Body: Same structure as registration success (access token + user info).
*   **Error Responses:**
    *   `400 Bad Request`: Missing email or password.
    *   `401 Unauthorized`: Invalid credentials (wrong email/password) or inactive account.

### 1.3 Get Current User (Me)

*   **Endpoint:** `GET /auth/me`
*   **Description:** Returns the details of the currently authenticated user.
*   **Role(s):** Customer, Engineer, Admin (Any authenticated user)
*   **Request Body:** None
*   **Success Response:** `200 OK`
    *   Body: User details (excluding password).
    ```json
    {
        "user_id": "uuid",
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string",
        "phone_number": "string",
        "role": "CUSTOMER | ENGINEER | ADMIN"
    }
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: No valid token provided.

---

## 2. Users (`/users`)

Handles user profile information.

### 2.1 Get My Profile

*   **Endpoint:** `GET /users/me`
*   **Description:** Returns the profile details of the currently authenticated user. (Functionally similar to `GET /auth/me`, often included for RESTful consistency under the `/users` resource).
*   **Role(s):** Customer, Engineer, Admin
*   **Request Body:** None
*   **Success Response:** `200 OK`
    *   Body: User details (excluding password, same as `GET /auth/me` response).
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.

### 2.2 Update My Profile

*   **Endpoint:** `PATCH /users/me`
*   **Description:** Allows the authenticated user to update their own profile information (e.g., name, phone).
*   **Role(s):** Customer, Engineer, Admin
*   **Request Body:** Include only fields to be updated.
    ```json
    {
      "first_name": "string (optional)",
      "last_name": "string (optional)",
      "phone_number": "string (optional)"
    }
    ```
*   **Success Response:** `200 OK`
    *   Body: Updated user details.
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input data.
    *   `401 Unauthorized`: Not authenticated.

---

## 3. Admin: User Management (`/admin/users`)

Endpoints restricted to users with the Admin role for managing other users.

### 3.1 List Users

*   **Endpoint:** `GET /admin/users`
*   **Description:** Returns a list of all users, potentially with filtering.
*   **Role(s):** Admin
*   **Query Parameters:**
    *   `role` (optional, string: `CUSTOMER`, `ENGINEER`, `ADMIN`): Filter by user role.
    *   `limit` (optional, integer): Number of results per page.
    *   `offset` (optional, integer): Pagination offset.
*   **Success Response:** `200 OK`
    ```json
    {
      "count": 150, // Total number of users matching filter
      "users": [
        {
          "user_id": "uuid",
          "email": "user@example.com",
          "first_name": "string",
          "last_name": "string",
          "phone_number": "string",
          "role": "CUSTOMER | ENGINEER | ADMIN",
          "is_active": true
        },
        // ... other users
      ]
    }
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.

### 3.2 Create Engineer/Admin User

*   **Endpoint:** `POST /admin/users`
*   **Description:** Creates a new user with the Engineer or Admin role.
*   **Role(s):** Admin
*   **Request Body:**
    ```json
    {
      "first_name": "string",
      "last_name": "string",
      "email": "newstaff@example.com",
      "phone_number": "string",
      "role": "ENGINEER | ADMIN",
      "password": "string (initial temporary password)"
    }
    ```
*   **Success Response:** `201 Created`
    *   Body: Details of the newly created user (excluding password).
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input data (e.g., invalid email, role not Engineer/Admin).
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.
    *   `422 Unprocessable Entity`: Email already exists.

### 3.3 Get User Details (Admin)

*   **Endpoint:** `GET /admin/users/{user_id}`
*   **Description:** Returns details for a specific user.
*   **Role(s):** Admin
*   **Path Parameter:** `user_id` (string/uuid)
*   **Success Response:** `200 OK`
    *   Body: User details (excluding password).
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.
    *   `404 Not Found`: User with the specified `user_id` does not exist.

### 3.4 Update User Details (Admin)

*   **Endpoint:** `PATCH /admin/users/{user_id}`
*   **Description:** Allows an Admin to update another user's details (e.g., name, phone, role, active status).
*   **Role(s):** Admin
*   **Path Parameter:** `user_id` (string/uuid)
*   **Request Body:** Include only fields to be updated.
    ```json
    {
      "first_name": "string (optional)",
      "last_name": "string (optional)",
      "phone_number": "string (optional)",
      "role": "CUSTOMER | ENGINEER | ADMIN (optional)",
      "is_active": "boolean (optional)"
    }
    ```
*   **Success Response:** `200 OK`
    *   Body: Updated user details.
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input data.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.
    *   `404 Not Found`: User with the specified `user_id` does not exist.

---

## 4. Addresses (`/addresses`)

Endpoints for managing customer addresses. These are typically accessed by the owning customer.

### 4.1 List My Addresses

*   **Endpoint:** `GET /addresses`
*   **Description:** Returns a list of all addresses associated with the currently authenticated customer.
*   **Role(s):** Customer
*   **Success Response:** `200 OK`
    ```json
    [
      {
        "address_id": "uuid",
        "user_id": "uuid (current user)",
        "street_address": "string",
        "city": "string",
        "state": "string",
        "pincode": "string",
        "is_default": true
      },
      // ... other addresses
    ]
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not a Customer (or potentially Admin if needed).

### 4.2 Create Address

*   **Endpoint:** `POST /addresses`
*   **Description:** Creates a new address for the currently authenticated customer.
*   **Role(s):** Customer
*   **Request Body:**
    ```json
    {
      "street_address": "string",
      "city": "string",
      "state": "string",
      "pincode": "string",
      "is_default": "boolean (optional, default false)"
    }
    ```
*   **Success Response:** `201 Created`
    *   Body: Details of the newly created address.
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input data (e.g., missing fields).
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not a Customer.
    *   `422 Unprocessable Entity`: Pincode is not in a serviceable area.

### 4.3 Get Address Details

*   **Endpoint:** `GET /addresses/{address_id}`
*   **Description:** Returns details for a specific address belonging to the authenticated customer.
*   **Role(s):** Customer
*   **Path Parameter:** `address_id` (string/uuid)
*   **Success Response:** `200 OK`
    *   Body: Address details.
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not the owner of the address.
    *   `404 Not Found`: Address with the specified `address_id` does not exist or does not belong to the user.

### 4.4 Update Address

*   **Endpoint:** `PATCH /addresses/{address_id}`
*   **Description:** Updates details for a specific address belonging to the authenticated customer.
*   **Role(s):** Customer
*   **Path Parameter:** `address_id` (string/uuid)
*   **Request Body:** Include only fields to be updated.
    ```json
    {
      "street_address": "string (optional)",
      "city": "string (optional)",
      "state": "string (optional)",
      "pincode": "string (optional)",
      "is_default": "boolean (optional)"
    }
    ```
*   **Success Response:** `200 OK`
    *   Body: Updated address details.
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input data.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not the owner of the address.
    *   `404 Not Found`: Address not found or not owned by user.
    *   `422 Unprocessable Entity`: Updated pincode is not in a serviceable area.

### 4.5 Delete Address

*   **Endpoint:** `DELETE /addresses/{address_id}`
*   **Description:** Deletes a specific address belonging to the authenticated customer.
*   **Role(s):** Customer
*   **Path Parameter:** `address_id` (string/uuid)
*   **Success Response:** `204 No Content`
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not the owner of the address.
    *   `404 Not Found`: Address not found or not owned by user.
    *   `422 Unprocessable Entity`: Cannot delete address if it's linked to active repair jobs (business rule TBD).

---

## 5. Admin: Serviceable Areas (`/admin/serviceable-areas`)

Endpoints restricted to Admins for managing pincodes where service is offered.

### 5.1 List Serviceable Areas

*   **Endpoint:** `GET /admin/serviceable-areas`
*   **Description:** Returns a list of all pincodes defined as serviceable.
*   **Role(s):** Admin
*   **Query Parameters:**
    *   `is_active` (optional, boolean): Filter by active status.
*   **Success Response:** `200 OK`
    ```json
    [
      {
        "pincode": "string",
        "is_active": true,
        "added_by_admin_id": "uuid",
        "created_at": "timestamp"
      },
      // ... other pincodes
    ]
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.

### 5.2 Add Serviceable Area

*   **Endpoint:** `POST /admin/serviceable-areas`
*   **Description:** Adds a new pincode to the list of serviceable areas.
*   **Role(s):** Admin
*   **Request Body:**
    ```json
    {
      "pincode": "string"
    }
    ```
*   **Success Response:** `201 Created`
    *   Body: Details of the newly added pincode.
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input (e.g., malformed pincode).
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.
    *   `422 Unprocessable Entity`: Pincode already exists.

### 5.3 Update Serviceable Area Status

*   **Endpoint:** `PATCH /admin/serviceable-areas/{pincode}`
*   **Description:** Activates or deactivates a specific serviceable pincode.
*   **Role(s):** Admin
*   **Path Parameter:** `pincode` (string)
*   **Request Body:**
    ```json
    {
      "is_active": "boolean"
    }
    ```
*   **Success Response:** `200 OK`
    *   Body: Updated details of the pincode.
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.
    *   `404 Not Found`: Pincode does not exist.

---

## 6. Repair Jobs (`/jobs`)

Endpoints for managing the core repair job workflow.

### 6.1 Create Repair Job

*   **Endpoint:** `POST /jobs`
*   **Description:** Allows an authenticated customer to create a new repair job request.
*   **Role(s):** Customer
*   **Request Body:**
    ```json
    {
      "address_id": "uuid",
      "laptop_manufacturer": "string",
      "laptop_model": "string",
      "laptop_serial_number": "string (optional)",
      "reported_symptoms": "string",
      "repair_type_requested": "ON_SITE_PART | LAB_DIAGNOSIS | LAB_CHIP_LEVEL"
      // scheduled_datetime might be added later if calendar implemented
    }
    ```
*   **Success Response:** `201 Created`
    *   Body: Details of the newly created job (including initial status like `PENDING_ASSIGNMENT`).
    ```json
    // Example structure - include relevant fields from data-models.md
    {
        "job_id": "uuid",
        "customer_id": "uuid (current user)",
        "address_id": "uuid",
        "status": "PENDING_ASSIGNMENT",
        "laptop_manufacturer": "string",
        // ... other fields
        "created_at": "timestamp"
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input data.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not a Customer.
    *   `404 Not Found`: Specified `address_id` not found or not owned by customer.
    *   `422 Unprocessable Entity`: Address pincode is not serviceable.

### 6.2 List Repair Jobs (Context-Aware)

*   **Endpoint:** `GET /jobs`
*   **Description:** Returns a list of repair jobs based on the user's role.
    *   Customers see their own jobs.
    *   Engineers see jobs assigned to them.
    *   Admins see all jobs.
*   **Role(s):** Customer, Engineer, Admin
*   **Query Parameters (Common):**
    *   `status` (optional, string): Filter by job status.
    *   `limit` (optional, integer): Pagination.
    *   `offset` (optional, integer): Pagination.
*   **Query Parameters (Admin Only):**
    *   `customer_id` (optional, uuid): Filter by customer.
    *   `engineer_id` (optional, uuid): Filter by assigned engineer.
    *   `pincode` (optional, string): Filter by job address pincode.
*   **Success Response:** `200 OK`
    ```json
    {
      "count": 25, // Total jobs matching filter for the user context
      "jobs": [
        {
            "job_id": "uuid",
            "customer_id": "uuid", // Always shown
            "engineer_id": "uuid | null", // Shown if assigned
            "address": { // Include relevant address summary
                "pincode": "string", 
                "city": "string"
             },
            "status": "string",
            "repair_type_requested": "string",
            "created_at": "timestamp"
            // ... other relevant summary fields
        },
        // ... other jobs
      ]
    }
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.

### 6.3 Get Repair Job Details

*   **Endpoint:** `GET /jobs/{job_id}`
*   **Description:** Returns the full details of a specific repair job.
    *   Customers can only access their own jobs.
    *   Engineers can only access jobs assigned to them.
    *   Admins can access any job.
*   **Role(s):** Customer, Engineer, Admin
*   **Path Parameter:** `job_id` (string/uuid)
*   **Success Response:** `200 OK`
    *   Body: Full details of the `RepairJob` entity, potentially including related info like Customer name/phone, Engineer name, full Address details.
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User does not have permission to view this job.
    *   `404 Not Found`: Job with the specified `job_id` does not exist.

### 6.4 Update Job Status (Engineer/Admin)

*   **Endpoint:** `PATCH /jobs/{job_id}/status`
*   **Description:** Allows an Engineer or Admin to update the status of a job. Backend must validate allowed status transitions based on current status and user role.
*   **Role(s):** Engineer, Admin
*   **Path Parameter:** `job_id` (string/uuid)
*   **Request Body:**
    ```json
    {
      "status": "string (new valid status enum)",
      "notes": "string (optional, appended to engineer_notes or admin_notes based on role)"
      // Might include specific fields needed for certain transitions, e.g.:
      // "customer_consent_for_lab": true (when moving to PENDING_PICKUP_FOR_LAB)
    }
    ```
*   **Success Response:** `200 OK`
    *   Body: Updated job details (at least the new status).
*   **Error Responses:**
    *   `400 Bad Request`: Invalid status value or missing required fields for transition.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User role not allowed to perform this update, or Engineer trying to update unassigned job.
    *   `404 Not Found`: Job not found.
    *   `422 Unprocessable Entity`: Invalid status transition requested (e.g., trying to complete a job that hasn't started diagnosis).

### 6.5 Add Job Notes (Engineer/Admin)

*   **Endpoint:** `POST /jobs/{job_id}/notes`
*   **Description:** Allows an Engineer or Admin to add notes to a job (appends to `engineer_notes` or `admin_notes`). Simpler alternative/complement to updating notes via status change.
*   **Role(s):** Engineer, Admin
*   **Path Parameter:** `job_id` (string/uuid)
*   **Request Body:**
    ```json
    {
      "notes": "string"
    }
    ```
*   **Success Response:** `201 Created` (or `200 OK` returning updated job)
    *   Body: Confirmation or updated job details with new notes.
*   **Error Responses:**
    *   `400 Bad Request`: Missing notes field.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User role not allowed, or Engineer on unassigned job.
    *   `404 Not Found`: Job not found.

### 6.6 Assign Engineer (Admin)

*   **Endpoint:** `PATCH /jobs/{job_id}/assign`
*   **Description:** Allows an Admin to assign or reassign an Engineer to a job.
*   **Role(s):** Admin
*   **Path Parameter:** `job_id` (string/uuid)
*   **Request Body:**
    ```json
    {
      "engineer_id": "uuid | null" // Assign specific engineer or unassign
    }
    ```
*   **Success Response:** `200 OK`
    *   Body: Updated job details showing the new `engineer_id` and potentially updated `status` (e.g., `ASSIGNED_TO_ENGINEER`).
*   **Error Responses:**
    *   `400 Bad Request`: Invalid `engineer_id`.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.
    *   `404 Not Found`: Job or specified Engineer not found.
    *   `422 Unprocessable Entity`: Cannot assign to a user who is not an Engineer, or Job is in a state that cannot be assigned (e.g., Completed).

### 6.7 Update Job Quote (Admin/Engineer)

*   **Endpoint:** `PATCH /jobs/{job_id}/quote`
*   **Description:** Allows Admin/Engineer to set/update the estimated/final costs, typically after lab diagnosis.
*   **Role(s):** Admin, Engineer
*   **Path Parameter:** `job_id` (string/uuid)
*   **Request Body:**
    ```json
    {
      "estimated_cost": "decimal (optional)",
      "final_cost": "decimal (optional)",
      "notes": "string (optional, e.g., quote details)" // Added to admin/engineer notes
    }
    ```
*   **Success Response:** `200 OK`
    *   Body: Updated job details with new cost information.
*   **Error Responses:**
    *   `400 Bad Request`: Invalid cost format.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User role not allowed.
    *   `404 Not Found`: Job not found.
    *   `422 Unprocessable Entity`: Action not allowed based on current job status (e.g., cannot set final cost before completion).

### 6.8 Update Payment Status (Admin/Engineer)

*   **Endpoint:** `PATCH /jobs/{job_id}/payment`
*   **Description:** Allows Admin/Engineer to mark a job's payment status.
*   **Role(s):** Admin, Engineer
*   **Path Parameter:** `job_id` (string/uuid)
*   **Request Body:**
    ```json
    {
      "payment_status": "PAID | WAIVED" 
    }
    ```
*   **Success Response:** `200 OK`
    *   Body: Updated job details.
*   **Error Responses:**
    *   `400 Bad Request`: Invalid payment status value.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User role not allowed.
    *   `404 Not Found`: Job not found.
    *   `422 Unprocessable Entity`: Job status does not allow payment update (e.g., must be PENDING_PAYMENT or COMPLETED).

### 6.9 Cancel Job (Customer/Admin)

*   **Endpoint:** `POST /jobs/{job_id}/cancel`
*   **Description:** Allows a Customer or Admin to cancel a job, providing a reason. Backend enforces rules about when cancellation is allowed.
*   **Role(s):** Customer, Admin
*   **Path Parameter:** `job_id` (string/uuid)
*   **Request Body:**
    ```json
    {
      "reason": "string"
    }
    ```
*   **Success Response:** `200 OK`
    *   Body: Updated job details with status `CANCELLED` and `cancellation_reason` populated.
*   **Error Responses:**
    *   `400 Bad Request`: Missing reason.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: Customer trying to cancel job not owned by them.
    *   `404 Not Found`: Job not found.
    *   `422 Unprocessable Entity`: Job is in a state that cannot be cancelled (e.g., already completed or cancelled).

---

## 7. Ratings (`/ratings`)

Endpoints for managing customer ratings on completed jobs.

### 7.1 Submit Rating for a Job

*   **Endpoint:** `POST /jobs/{job_id}/ratings` (Nested under the job)
*   **Description:** Allows a customer to submit a rating for one of their completed jobs.
*   **Role(s):** Customer
*   **Path Parameter:** `job_id` (string/uuid)
*   **Request Body:**
    ```json
    {
      "score": "integer (e.g., 1-5)",
      "comment": "string (optional)"
    }
    ```
*   **Success Response:** `201 Created`
    *   Body: Details of the newly created rating.
    ```json
    {
        "rating_id": "uuid",
        "job_id": "uuid",
        "customer_id": "uuid (current user)",
        "engineer_id": "uuid",
        "score": 5,
        "comment": "string",
        "created_at": "timestamp"
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input (e.g., score out of range).
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not the customer for this job.
    *   `404 Not Found`: Job not found.
    *   `422 Unprocessable Entity`: Job is not in a state that can be rated (e.g., not `COMPLETED`), or a rating already exists for this job.

### 7.2 Get Rating for a Job

*   **Endpoint:** `GET /jobs/{job_id}/ratings` (Could also be `GET /ratings/{rating_id}` if needed)
*   **Description:** Retrieves the rating associated with a specific job.
*   **Role(s):** Customer (owner), Admin, Engineer (assigned to job)
*   **Path Parameter:** `job_id` (string/uuid)
*   **Success Response:** `200 OK`
    *   Body: Rating details (same as 7.1 success response).
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User does not have permission to view this rating.
    *   `404 Not Found`: Job not found, or no rating submitted for this job.

### 7.3 List Ratings (Admin)

*   **Endpoint:** `GET /admin/ratings`
*   **Description:** Allows an Admin to list all ratings, possibly with filters.
*   **Role(s):** Admin
*   **Query Parameters:**
    *   `engineer_id` (optional, uuid): Filter by engineer.
    *   `min_score` (optional, integer): Filter by minimum score.
    *   `max_score` (optional, integer): Filter by maximum score.
    *   `limit` (optional, integer): Pagination.
    *   `offset` (optional, integer): Pagination.
*   **Success Response:** `200 OK`
    ```json
    {
      "count": 50, // Total ratings matching filter
      "ratings": [
        // Array of rating objects (same structure as 7.1 success response)
      ]
    }
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.

---

## 8. Admin: Pricing Configuration (`/admin/pricing`)

Endpoints restricted to Admins for managing pricing rules (initially flat rates).

### 8.1 List Pricing Configurations

*   **Endpoint:** `GET /admin/pricing`
*   **Description:** Returns a list of all defined pricing configurations.
*   **Role(s):** Admin
*   **Query Parameters:**
    *   `is_active` (optional, boolean): Filter by active status.
    *   `repair_type` (optional, enum): Filter by repair type.
*   **Success Response:** `200 OK`
    ```json
    [
      {
        "config_id": "uuid",
        "repair_type": "ON_SITE_PART | LAB_DIAGNOSIS | ...",
        "item_name": "string",
        "base_price": "decimal",
        "is_active": true,
        "updated_by_admin_id": "uuid",
        "updated_at": "timestamp"
      },
      // ... other configs
    ]
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.

### 8.2 Create Pricing Configuration

*   **Endpoint:** `POST /admin/pricing`
*   **Description:** Creates a new pricing rule.
*   **Role(s):** Admin
*   **Request Body:**
    ```json
    {
      "repair_type": "ON_SITE_PART | LAB_DIAGNOSIS | ...",
      "item_name": "string",
      "base_price": "decimal",
      "is_active": "boolean (optional, default true)"
    }
    ```
*   **Success Response:** `201 Created`
    *   Body: Details of the newly created pricing config.
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input data.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.

### 8.3 Update Pricing Configuration

*   **Endpoint:** `PATCH /admin/pricing/{config_id}`
*   **Description:** Updates an existing pricing rule.
*   **Role(s):** Admin
*   **Path Parameter:** `config_id` (string/uuid)
*   **Request Body:** Include only fields to update.
    ```json
    {
      "repair_type": "enum (optional)",
      "item_name": "string (optional)",
      "base_price": "decimal (optional)",
      "is_active": "boolean (optional)"
    }
    ```
*   **Success Response:** `200 OK`
    *   Body: Updated pricing config details.
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input data.
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.
    *   `404 Not Found`: Config with specified ID not found.

---

## 9. Admin: Reporting (`/admin/reports`)

Endpoints restricted to Admins for retrieving basic analytics and reports.
*(Note: These are conceptual examples; specific reports may vary.)*

### 9.1 Get Dashboard Statistics

*   **Endpoint:** `GET /admin/reports/dashboard`
*   **Description:** Returns key metrics for the admin dashboard.
*   **Role(s):** Admin
*   **Success Response:** `200 OK`
    ```json
    {
      "jobs_pending_assignment": 15,
      "jobs_in_progress_on_site": 8,
      "jobs_in_progress_lab": 5,
      "average_rating_last_30_days": 4.5,
      "jobs_completed_last_7_days": 42
      // ... other key metrics
    }
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.

### 9.2 Get Engineer Productivity Report

*   **Endpoint:** `GET /admin/reports/engineer-productivity`
*   **Description:** Returns a summary of engineer performance over a time period.
*   **Role(s):** Admin
*   **Query Parameters:**
    *   `start_date` (optional, date string): Defaults to 30 days ago.
    *   `end_date` (optional, date string): Defaults to today.
*   **Success Response:** `200 OK`
    ```json
    {
      "report_period": {"start": "date", "end": "date"},
      "engineers": [
        {
          "engineer_id": "uuid",
          "engineer_name": "string",
          "jobs_completed": 25,
          "average_rating": 4.7,
          "average_onsite_completion_time_hours": 2.5 // Example metric
        },
        // ... other engineers
      ]
    }
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: Not authenticated.
    *   `403 Forbidden`: User is not an Admin.

--- 