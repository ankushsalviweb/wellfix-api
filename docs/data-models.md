# WellFix - Core Data Models & Relationships

This document outlines the conceptual data models required to support the WellFix application's functional requirements. These models would typically be implemented as tables in a relational database (e.g., PostgreSQL).

## Core Entities

1.  **`User`**
    *   Purpose: Stores information about all system users (Customers, Engineers, Admins).
    *   Key Attributes:
        *   `user_id` (Primary Key)
        *   `email` (Unique, for login)
        *   `password_hash` (Hashed password)
        *   `first_name`
        *   `last_name`
        *   `phone_number`
        *   `role` (Enum: CUSTOMER, ENGINEER, ADMIN)
        *   `is_active` (Boolean, for disabling accounts)
        *   `created_at`
        *   `updated_at`
    *   Relationships:
        *   One User (Customer) has Many `Address`es.
        *   One User (Customer) has Many `RepairJob`s (as creator).
        *   One User (Engineer) has Many `RepairJob`s (as assignee).
        *   One User (Customer) has Many `Rating`s (as author).
        *   One User (Engineer) receives Many `Rating`s.

2.  **`Address`**
    *   Purpose: Stores customer addresses.
    *   Key Attributes:
        *   `address_id` (Primary Key)
        *   `user_id` (Foreign Key to `User` - Customer)
        *   `street_address`
        *   `city`
        *   `state`
        *   `pincode` (String - Important for serviceability check)
        *   `is_default` (Boolean)
        *   `created_at`
        *   `updated_at`
    *   Relationships:
        *   Belongs to one `User` (Customer).
        *   One Address can be associated with Many `RepairJob`s.

3.  **`ServiceableArea`**
    *   Purpose: Defines the pincodes where services are offered, managed by Admins.
    *   Key Attributes:
        *   `pincode` (Primary Key, String)
        *   `is_active` (Boolean)
        *   `added_by_admin_id` (Foreign Key to `User` - Admin)
        *   `created_at`
    *   Relationships:
        *   Managed by `User` (Admin).

4.  **`RepairJob`**
    *   Purpose: The central entity tracking a single repair request from start to finish.
    *   Key Attributes:
        *   `job_id` (Primary Key)
        *   `customer_id` (Foreign Key to `User` - Customer)
        *   `engineer_id` (Foreign Key to `User` - Engineer, nullable initially)
        *   `address_id` (Foreign Key to `Address` - Service location)
        *   `laptop_manufacturer`
        *   `laptop_model`
        *   `laptop_serial_number` (Optional)
        *   `reported_symptoms` (Text)
        *   `repair_type_requested` (Enum: ON_SITE_PART, LAB_DIAGNOSIS, LAB_MOTHERBOARD)
        *   `status` (Enum: PENDING_APPROVAL, PENDING_ASSIGNMENT, ASSIGNED_TO_ENGINEER, EN_ROUTE, ON_SITE_DIAGNOSIS, PARTS_ORDERED, REPAIR_IN_PROGRESS_ON_SITE, ESCALATED_TO_LAB, PENDING_PICKUP_FOR_LAB, IN_TRANSIT_TO_LAB, LAB_DIAGNOSIS, PENDING_QUOTE_APPROVAL, REPAIR_IN_PROGRESS_LAB, PENDING_RETURN_DELIVERY, IN_TRANSIT_FROM_LAB, PENDING_PAYMENT, COMPLETED, CANCELLED)
        *   `scheduled_datetime` (Timestamp, optional, for appointments)
        *   `estimated_cost` (Decimal, initial estimate)
        *   `final_cost` (Decimal, after quote/completion)
        *   `payment_status` (Enum: PENDING, PAID, WAIVED)
        *   `engineer_notes` (Text, nullable)
        *   `admin_notes` (Text, nullable)
        *   `customer_consent_for_lab` (Boolean, default False)
        *   `cancellation_reason` (Text, nullable)
        *   `created_at`
        *   `updated_at`
    *   Relationships:
        *   Belongs to one `User` (Customer).
        *   Belongs to one `Address`.
        *   Assigned to one `User` (Engineer).
        *   Has one `Rating` (potentially, or link via Rating table).
        *   Can have multiple `JobStatusUpdate` records.

5.  **`JobStatusUpdate`** (Optional but recommended for history)
    *   Purpose: Logs changes to a job's status for tracking history.
    *   Key Attributes:
        *   `update_id` (Primary Key)
        *   `job_id` (Foreign Key to `RepairJob`)
        *   `user_id` (Foreign Key to `User` - who made the update)
        *   `previous_status` (Enum)
        *   `new_status` (Enum)
        *   `timestamp`
        *   `notes` (Optional text)
    *   Relationships:
        *   Belongs to one `RepairJob`.
        *   Belongs to one `User` (who performed the update).

6.  **`Rating`**
    *   Purpose: Stores customer feedback for a completed job.
    *   Key Attributes:
        *   `rating_id` (Primary Key)
        *   `job_id` (Foreign Key to `RepairJob`, Unique - one rating per job)
        *   `customer_id` (Foreign Key to `User` - Customer)
        *   `engineer_id` (Foreign Key to `User` - Engineer)
        *   `score` (Integer, e.g., 1-5)
        *   `comment` (Text, optional)
        *   `created_at`
    *   Relationships:
        *   Belongs to one `RepairJob`.
        *   Submitted by one `User` (Customer).
        *   Rates one `User` (Engineer).

7.  **`PricingConfig`** (Conceptual - could be simpler for initial phase)
    *   Purpose: Store admin-defined pricing rules.
    *   Key Attributes:
        *   `config_id`
        *   `repair_type` (Enum: ON_SITE_PART, LAB_DIAGNOSIS, etc.)
        *   `item_name` (e.g., 'RAM Upgrade', 'Screen Replacement', 'Diagnosis Fee')
        *   `base_price` (Decimal)
        *   `is_active` (Boolean)
        *   `updated_by_admin_id`
        *   `updated_at`

## Relationships Summary

- **User <-> Address:** One-to-Many (Customer can have multiple addresses)
- **User <-> RepairJob:** 
    - One-to-Many (Customer creates many jobs)
    - One-to-Many (Engineer assigned many jobs)
- **Address <-> RepairJob:** One-to-Many (An address can be the location for multiple jobs)
- **User <-> ServiceableArea:** Many-to-Many (Admins manage Pincodes - conceptually, link table might not be needed if only storing `added_by`)
- **RepairJob <-> JobStatusUpdate:** One-to-Many (A job has a history of status changes)
- **RepairJob <-> Rating:** One-to-One (A completed job can have one rating)
- **User <-> Rating:**
    - One-to-Many (Customer gives many ratings)
    - One-to-Many (Engineer receives many ratings)

This model provides a foundation for building the API endpoints and business logic required by the functional requirements. 