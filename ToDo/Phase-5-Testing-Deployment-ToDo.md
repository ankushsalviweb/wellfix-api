# WellFix - Phase 5 ToDo: Testing, Deployment Prep & Documentation Review

**Goal:** Comprehensive testing, NFR validation, code/docs review, deployment prep.

**Reference Plan:** `Plan/05-phase-testing-deployment.md`

**Instructions:** Follow Check -> Code/Test/Review -> Iterate. Ensure adherence to `/rules` and alignment with `/docs`.

---

### 1. Comprehensive Integration Testing

*   [ ] **Task 1.1:** Define key end-to-end scenarios (e.g., Customer registers -> schedules on-site -> Engineer completes; Customer schedules -> Engineer escalates -> Admin quotes -> Engineer returns -> Customer rates).
*   [ ] **Task 1.2:** Write integration tests (`tests/integration/`) covering these E2E scenarios, making multiple API calls.
*   [ ] **Task 1.3:** Conduct exploratory testing: Focus on invalid inputs, unexpected sequences, role permission boundaries, concurrent access (if applicable).
*   [ ] **Task 1.4:** Log bugs found in the issue tracker.
*   [ ] **Task 1.5:** Fix identified bugs, ensuring corresponding tests pass.

### 2. Non-Functional Requirements Testing & Validation

*   [ ] **Task 2.1 (Perf):** Setup load testing tool (e.g., `locust`). Write basic load test scripts for key endpoints (login, get jobs, update status).
*   [ ] **Task 2.2 (Perf):** Run load tests, analyze results (response times, error rates). Identify bottlenecks if targets from NFRs are not met.
*   [ ] **Task 2.3 (Perf):** Optimize identified bottlenecks (e.g., DB query tuning, caching strategies - if necessary).
*   [ ] **Task 2.4 (Security):** Run dependency vulnerability scanner (e.g., `safety check`, `pip-audit`). Update vulnerable dependencies if safe.
*   [ ] **Task 2.5 (Security):** Manually review critical endpoints for potential security flaws (Auth checks, input validation effectiveness).
*   [ ] **Task 2.6 (Reliability):** Review logs generated during integration/load tests. Ensure critical errors are logged effectively and stack traces are captured.
*   [ ] **Task 2.7 (Reliability):** Review error responses for consistency and user-friendliness.
*   [ ] **Task 2.8:** Fix any NFR-related issues identified.

### 3. Code Quality & Rule Adherence Review

*   [ ] **Task 3.1:** Run code formatter (e.g., `black .`) and linter (e.g., `flake8 .` or `ruff check .`) across the entire codebase. Fix all reported issues.
*   [ ] **Task 3.2:** Manually review code structure against modularity rules.
*   [ ] **Task 3.3:** Manually review key functions/classes for clarity, comments, and docstrings.
*   [ ] **Task 3.4:** Verify `.env.example` is up-to-date and dependency files (`pyproject.toml`/`requirements.txt`) are clean.
*   [ ] **Task 3.5:** Conduct final peer code reviews for major features or complex modules.
*   [ ] **Task 3.6:** Refactor code based on review feedback.

### 4. Documentation Finalization

*   [ ] **Task 4.1:** Review `docs/api-design.md`, `docs/data-models.md`, etc., against the final code. Update any discrepancies.
*   [ ] **Task 4.2:** Create/Update `README.md`: Include project summary, tech stack, installation guide (using Poetry/pip), local running instructions (Uvicorn, Docker Compose), testing instructions, basic API usage examples.
*   [ ] **Task 4.3:** Ensure docstrings are complete for all public APIs, classes, and functions.
*   [ ] **Task 4.4:** (Optional) Configure and run Sphinx or other tool to generate HTML documentation from docstrings.
*   [ ] **Task 4.5:** Final proofread of all `/docs` and the `README.md`.

### 5. Deployment Preparation

*   [ ] **Task 5.1:** Write `Dockerfile` defining build stages, dependencies, application execution (using `uvicorn`). Ensure non-root user execution.
*   [ ] **Task 5.2:** Write `docker-compose.yml` defining services (backend API, PostgreSQL DB), networks, volumes, environment variables (linking to `.env` file).
*   [ ] **Task 5.3:** Update `.env.example` with all required variables for Dockerized deployment.
*   [ ] **Task 5.4:** Create utility scripts (`scripts/`) for common tasks (e.g., `run-migrations.sh`, `start-dev-server.sh`).
*   [ ] **Task 5.5:** Test building the image (`docker build .`).
*   [ ] **Task 5.6:** Test running the application stack (`docker-compose up`). Verify connectivity and basic functionality.

### 6. Final Test Suite Run & Verification

*   [ ] **Task 6.1:** Execute the entire test suite (`pytest`) in the final code state. Ensure 100% pass rate.
*   [ ] **Task 6.2:** Perform a final smoke test: Manually run through 1-2 core user scenarios using the locally running Dockerized application. 