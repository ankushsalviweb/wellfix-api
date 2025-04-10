# Frontend Rule: Documentation

    Maintain clear and concise documentation to improve code understanding, onboarding, and maintainability.

    ## Code Comments

    *   **When to Comment:** Comment complex logic, non-obvious code sections, workarounds, or parts of the code with important context that isn't immediately clear from the code itself.
    *   **Avoid Obvious Comments:** Do not comment on code that is self-explanatory.
    *   **Style:** Use standard JavaScript/TypeScript comment syntax (`//` for single-line, `/** ... */` for multi-line/JSDoc).
    *   **TODOs/FIXMEs:** Use `// TODO:` or `// FIXME:` prefixes for temporary notes or areas needing attention, ideally linking to an issue tracker item.

    ## Component Documentation

    *   **Props & Events:** Use TypeScript in `<script setup>` to implicitly document prop types and emitted events via `defineProps` and `defineEmits`.
    *   **JSDoc (Optional but Recommended):** Add JSDoc blocks above component definitions (`<script setup>`) or composable functions to explain their purpose, parameters (if applicable beyond props), and usage.
        ```typescript
        /**
         * Displays user profile information and allows editing.
         * Emits `profile-updated` event on successful update.
         */
        import { defineProps, defineEmits } from 'vue';
        // ... rest of <script setup>
        ```
    *   **Storybook (Optional but Recommended):** For larger component libraries or design systems, consider using Storybook to create interactive documentation and examples for components in isolation.

    ## Type Definitions (`src/types/`)

    *   Maintain clear and well-organized TypeScript interfaces and types for data structures (especially API payloads/responses and Pinia store state).
    *   Add JSDoc comments to explain complex types or properties if needed.

    ## README.md

    *   Maintain a comprehensive `README.md` file in the project root.
    *   **Contents:**
        *   Project Title and brief description.
        *   Key Features (high-level).
        *   Tech Stack used.
        *   Prerequisites (Node version, package manager).
        *   Getting Started / Installation guide.
        *   Running the Development Server.
        *   Running Tests (unit, e2e).
        *   Linting and Formatting commands.
        *   Building for Production.
        *   Environment Variables setup (`.env.example` explanation).
        *   Project Structure overview.
        *   (Optional) Deployment instructions.
        *   (Optional) Contribution guidelines.
        *   License information.
    *   Keep the README up-to-date as the project evolves.

    ## Commit Messages

    *   Follow conventional commit message standards (e.g., `feat: add user login page`, `fix: correct validation error on job form`, `docs: update README setup instructions`, `refactor: simplify state management in auth store`, `test: add unit tests for JobCard component`).
    *   Write clear and concise messages explaining the *what* and *why* of the change.

    ## Rationale

    *   Improves onboarding for new developers.
    *   Makes code easier to understand and maintain.
    *   Facilitates collaboration within the team.
    *   Provides essential information for setting up and running the project.
    *   Conventional commits can enable automated changelog generation.
    