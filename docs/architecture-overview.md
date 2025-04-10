# WellFix - Architecture Overview & Technology Stack

## 1. Architecture Style

The WellFix platform will initially be developed using a **Modular Monolithic** architecture. This approach provides a balance between development simplicity (single codebase, single deployment) and organizational structure, aligning with the `python-project-structure-rule.mdc` and `python-modular-design-rule.mdc`.

- **Monolith:** A single backend application deployment containing all core logic.
- **Modular:** The codebase will be internally structured into distinct modules with clear boundaries and responsibilities (see Section 3). This facilitates maintainability, testability, and potential future refactoring into microservices if scale demands it.

## 2. Technology Stack (Proposed)

- **Backend Language:** Python (Version 3.10+)
- **Web Framework:** **FastAPI** or **Django**
    - *FastAPI:* Chosen for its modern features, performance, automatic API documentation (crucial for frontend integration and adhering to `python-documentation-rule.mdc`), and asynchronous capabilities.
    - *Django:* Alternatively, considered for its batteries-included nature, built-in ORM, and robust admin interface (useful for admin functionalities). The choice depends on team familiarity and preference.
- **Database:** **PostgreSQL** (Version 14+) - A robust relational database suitable for structured data like users, jobs, addresses, ensuring data integrity.
- **Frontend:** Standard Web Technologies (HTML, CSS, JavaScript). A modern JavaScript framework (e.g., React, Vue, or HTMX for server-rendered HTML) will be used to build the responsive user interfaces.
- **API Communication:** RESTful API principles will be used for communication between the frontend and backend. FastAPI/Django simplifies REST API creation.
- **Deployment (Initial):** For Local Test(Dev) on Windows system and then Containerization using Docker, potentially deployed on a cloud platform (e.g., AWS, Google Cloud, Azure) or a VPS.
- **Dependency Management:** `pip` with `requirements.txt` or `Poetry`, following `python-dependency-management-rule.mdc`.
- **Configuration:** Environment variables and/or configuration files (`.env`, `.yaml`), adhering to `python-configuration-management-rule.mdc`.
- **Logging/Error Handling:** Standard Python logging library, configured as per `python-error-handling-and-logging-rule.mdc`.

## 3. Core Backend Modules (Conceptual)

Based on functional requirements and the modular design rule, the backend will be structured around these core logical units:

- **`users`:** Handles user registration, authentication (email/password for customers, predefined for staff), authorization (role-based access), and profile management.
- **`addresses`:** Manages customer addresses and performs pincode validation against serviceable areas.
- **`jobs`:** Core module for managing repair jobs - creation, details (laptop info, symptoms), status tracking, linking customers, engineers, and addresses.
- **`scheduling`:** Logic for displaying availability (conceptual calendar view support) and assisting admins in assigning jobs based on engineer skills, location (pincode), and workload.
- **`pricing`:** Handles the logic for different repair types (on-site, lab diagnosis, motherboard) and calculates costs based on admin-defined rates or quotes.
- **`notifications`:** Manages sending real-time updates (in-app conceptually, potentially email(Only for Certain status)) for status changes.
- **`ratings`:** Handles customer feedback submission and retrieval.
- **`admin_tools`:** Backend logic supporting admin-specific functions like managing serviceable areas, viewing metrics, managing users/engineers and Application settings.
- **`reporting`:** Logic for generating statistics and reports based on job data, ratings, and engineer performance.
- **`payments`:** (Potential future or basic implementation) Logic for recording payments (manual initially) or integrating with payment gateways.

## 4. Frontend Structure

- A single responsive web application serving different views based on user role (Customer, Engineer, Admin).
- Communicates with the backend via the REST API.

## 5. Scalability Considerations

- The modular monolith allows for scaling the entire application vertically (more powerful server) or horizontally (multiple instances behind a load balancer).
- Clear module boundaries facilitate potential future extraction into separate microservices if needed.
- Database optimization and appropriate indexing will be crucial. 