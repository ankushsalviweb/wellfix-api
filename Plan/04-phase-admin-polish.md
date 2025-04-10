# WellFix - Plan: Phase 4 - Admin Tools, Ratings & Polish

**Phase Goal:** Implement remaining admin functionalities (pricing configuration), the customer ratings system, basic reporting endpoints, and refine existing workflows based on initial testing and feedback.

**Depends On:** Phase 3 Completion

**Related Documentation:**
*   `docs/data-models.md` (Rating, PricingConfig models)
*   `docs/api-design.md` (Sections 6.9, 7, 8, 9)
*   `docs/functional-requirements.md` (Sections 4.3.4 [Cancel], 4.5.1, 4.7, 4.8)
*   `docs/non-functional-requirements.mdc`
*   Relevant `/rules/*.mdc` files

---

## Tasks Breakdown (Check -> Code -> Test -> Iterate)

**1. PricingConfig Model & Admin Management**
    *   [ ] **Check:** Review `docs/data-models.md` (PricingConfig) and `docs/api-design.md` (Section 8).
    *   [ ] **Code:** Define SQLAlchemy model for `PricingConfig` (`models/pricing.py`).
    *   [ ] **Code:** Create Alembic migration for `PricingConfig` table.
    *   [ ] **Code:** Define Pydantic schemas for `PricingConfig` (`schemas/pricing.py`).
    *   [ ] **Code:** Implement CRUD functions for `PricingConfig` (`crud/crud_pricing.py`).
    *   [ ] **Code:** Implement Admin API endpoints:
        *   `GET /admin/pricing` (List configs).
        *   `POST /admin/pricing` (Create config).
        *   `PATCH /admin/pricing/{config_id}` (Update config).
    *   [ ] **Test:** Run migrations. Unit tests for CRUD. Integration tests for API endpoints, including Admin role checks.
    *   [ ] **Iterate:** Refine model, schemas, CRUD, and API logic.

**2. Rating Model & Migrations**
    *   [ ] **Check:** Review `docs/data-models.md` for the `Rating` entity and its relationships (User, Job).
    *   [ ] **Code:** Define SQLAlchemy model for `Rating` (`models/rating.py`). Establish relationships.
    *   [ ] **Code:** Create Alembic migration script for the `Rating` table.
    *   [ ] **Test:** Run migrations. Basic tests for model creation/retrieval.
    *   [ ] **Iterate:** Refine model and migration.

**3. Rating Schemas & CRUD**
    *   [ ] **Check:** Map `Rating` model to API schemas in `docs/api-design.md`.
    *   [ ] **Code:** Define Pydantic schemas for `Rating` (`schemas/rating.py`).
    *   [ ] **Code:** Implement CRUD functions for `Rating` (`crud/crud_rating.py`).
    *   [ ] **Test:** Unit tests for `Rating` CRUD functions.
    *   [ ] **Iterate:** Adjust schemas and CRUD.

**4. Submit Rating API (/jobs/{job_id}/ratings - POST)**
    *   [ ] **Check:** Review `docs/api-design.md` (7.1) and functional requirements (4.7.1).
    *   [ ] **Code:** Implement `POST /jobs/{job_id}/ratings` endpoint for Customers.
    *   [ ] **Code:** Validate: Job exists, belongs to customer, is `COMPLETED`, rating doesn't already exist.
    *   [ ] **Code:** Use `crud_rating` to create the rating, linking `customer_id` and `engineer_id` from the job.
    *   [ ] **Test:** Integration tests for submitting ratings (success, job not found, wrong owner, not completed, already rated).
    *   [ ] **Iterate:** Refine submission logic and validation.

**5. Get/List Ratings APIs**
    *   [ ] **Check:** Review `docs/api-design.md` (7.2, 7.3).
    *   [ ] **Code:** Implement `GET /jobs/{job_id}/ratings` endpoint (accessible by Customer, Engineer, Admin with permission checks).
    *   [ ] **Code:** Implement `GET /admin/ratings` endpoint for Admins (with filtering).
    *   [ ] **Test:** Integration tests for getting a specific rating and listing ratings (as Admin) with filters.
    *   [ ] **Iterate:** Refine retrieval logic and filtering.

**6. Cancel Job API (/jobs/{job_id}/cancel - POST)**
    *   [ ] **Check:** Review `docs/api-design.md` (6.9) and functional requirements (4.3.4).
    *   [ ] **Code:** Implement `POST /jobs/{job_id}/cancel` endpoint for Customers and Admins.
    *   [ ] **Code:** Add authorization (Customer owns job or user is Admin).
    *   [ ] **Code:** Implement validation logic based on job status (define cancellable statuses).
    *   [ ] **Code:** Update job status to `CANCELLED` and store `reason`.
    *   [ ] **Test:** Integration tests for cancelling jobs (as Customer, as Admin), including authorization and status validation.
    *   [ ] **Iterate:** Refine cancellation logic and rules.

**7. Basic Reporting Endpoints (/admin/reports)**
    *   [ ] **Check:** Review `docs/api-design.md` (Section 9) and functional requirements (4.8).
    *   [ ] **Code:** Implement `GET /admin/reports/dashboard` endpoint.
    *   [ ] **Code:** Implement `GET /admin/reports/engineer-productivity` endpoint.
    *   [ ] **Code:** Write necessary database queries (potentially complex, focus on read performance) using SQLAlchemy to aggregate data.
    *   [ ] **Test:** Integration tests for reporting endpoints (Admin access, basic response structure check). Performance testing might be needed later.
    *   [ ] **Iterate:** Refine query logic and response formats. Optimize queries if performance issues arise.

**8. Workflow Polish & Refinement**
    *   [ ] **Check:** Review previous phases based on internal testing or early feedback.
    *   [ ] **Code:** Address any identified bugs or minor usability issues in existing endpoints.
    *   [ ] **Code:** Improve error messages and logging where needed.
    *   [ ] **Code:** Refactor code for clarity or performance based on reviews.
    *   [ ] **Test:** Ensure refactoring doesn't break existing tests. Add tests for fixed bugs.
    *   [ ] **Iterate:** Based on ongoing testing and review.

---

**Phase 4 Definition of Done:**
*   Admin Pricing Configuration management is functional via API.
*   `Rating` model and migrations are complete.
*   Customers can submit ratings for completed jobs via API.
*   Relevant users (Customer, Engineer, Admin) can retrieve ratings.
*   Admins can list and filter ratings.
*   Job cancellation API is functional with rules.
*   Basic Admin reporting endpoints (dashboard, productivity) are implemented.
*   Known bugs from previous phases are addressed.
*   All new/modified code has corresponding tests and passes.
*   Code adheres to rules. 