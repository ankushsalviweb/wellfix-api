# Frontend Rule: Testing

    Implement a comprehensive testing strategy to ensure application correctness, prevent regressions, and facilitate refactoring.

    ## Recommended Tools (Vite/Vue Ecosystem)

    *   **Unit Testing:**
        *   **Test Runner:** `Vitest` (Vite-native, fast, compatible with Jest API).
        *   **Component Testing Library:** `@vue/test-utils` (Official Vue library for mounting components).
        *   **DOM Assertion Library:** `@testing-library/vue` (Provides utilities to query and interact with components like a user would, complements `@vue/test-utils`).
        *   **Assertion Library:** `Vitest` built-ins (Chai/Jest compatible `expect` API).
    *   **End-to-End (E2E) Testing:**
        *   `Cypress` or `Playwright` (Run tests in a real browser, interacting with the application as a user would).

    ## Testing Strategy

    Employ the "Testing Trophy" or "Testing Pyramid" concept as a guide:

    1.  **Unit Tests (`tests/unit/`):**
        *   **Focus:** Test individual units (components, composables, utility functions, Pinia stores) in isolation.
        *   **Scope:**
            *   **Components:** Test prop validation, event emission, conditional rendering based on props/state, basic user interactions (clicks) that trigger events. Use `@vue/test-utils` to mount and `@testing-library/vue` to query/interact.
            *   **Composables:** Test the reactive logic and return values of composable functions.
            *   **Stores (Pinia):** Test actions (including async logic with mocked services), getters, and state mutations in isolation. Use `createPinia()` and `setActivePinia()` for setup.
            *   **Utilities:** Test pure functions with various inputs.
        *   **Mocking:** Mock external dependencies like API services, routing, or other stores heavily.
        *   **Goal:** Fast feedback, easy to write, pinpoint specific failures.

    2.  **Integration Tests (`tests/integration/` or within unit tests):**
        *   **Focus:** Test the interaction *between* several units (e.g., a page component interacting with its child components and a Pinia store).
        *   **Scope:** Verify that components render correctly based on store state, actions are dispatched correctly on user interaction, and the UI updates as expected.
        *   **Mocking:** Mock less aggressively than unit tests. Mock API calls at the service layer boundary but allow components and stores to interact more freely.
        *   **Goal:** Verify collaboration between units, ensure key workflows function correctly without full browser setup.

    3.  **End-to-End (E2E) Tests (`tests/e2e/` or separate `cypress`/`playwright` directory):**
        *   **Focus:** Test complete user flows through the entire application running in a browser, including interaction with the backend API (either mocked or a live test instance).
        *   **Scope:** Simulate real user scenarios (e.g., login -> create job -> view job -> logout).
        *   **Mocking:** Minimal mocking, ideally testing against a real (test) backend or a comprehensive mock server (e.g., MSW - Mock Service Worker).
        *   **Goal:** Highest confidence that the application works as expected from the user's perspective. Slowest and potentially most brittle tests.

    ## Guidelines

    *   **Test Coverage:** Aim for high unit/integration test coverage for critical logic (stores, composables, core components). E2E tests should cover the most important user flows.
    *   **Readability:** Write clear, descriptive test names (`it('should display an error message when login fails')`).
    *   **Maintainability:** Avoid testing implementation details. Focus on testing component behavior from the user's perspective (using `@testing-library/vue`) or the public API of modules/stores.
    *   **Arrange-Act-Assert (AAA):** Structure tests logically: setup prerequisites, perform the action, assert the outcome.
    *   **Test Setup:** Use `beforeEach` / `afterEach` hooks in test files for common setup/teardown logic.
    *   **CI Integration:** Integrate test execution (`npm run test:unit`, `npm run test:e2e`) into the CI/CD pipeline.

    ## Rationale

    *   Increases confidence in code correctness.
    *   Prevents regressions when adding features or refactoring.
    *   Improves code design by encouraging testable units.
    *   Provides living documentation of how components/features are expected to behave. 