# Frontend Rule: Project Structure (Vue 3)

    Maintain a consistent and logical project structure to enhance navigability and maintainability.

    ## Recommended Structure (Vite Standard)

    ```
    wellfix-frontend/
    ├── public/             # Static assets copied directly to build output
    │   └── favicon.ico
    ├── src/
    │   ├── assets/         # Static assets processed by Vite (fonts, images)
    │   ├── components/     # Reusable UI components (dumb components)
    │   │   ├── common/     # General-purpose components (Button, Input, Modal)
    │   │   └── features/   # Feature-specific reusable components (JobCard, UserForm)
    │   ├── composables/    # Reusable Vue Composition API functions (use...)
    │   ├── layouts/        # Layout components (DefaultLayout, AuthLayout)
    │   ├── pages/          # Route-level components (views)
    │   │   ├── admin/
    │   │   ├── auth/
    │   │   ├── customer/
    │   │   └── engineer/
    │   ├── router/         # Vue Router configuration (index.ts)
    │   │   └── routes.ts   # Route definitions
    │   ├── services/       # API interaction logic (axios instances, endpoints)
    │   ├── stores/         # Pinia state management stores
    │   ├── styles/         # Global styles, variables, mixins (e.g., SCSS)
    │   │   └── main.scss
    │   ├── types/          # TypeScript type definitions (interfaces, enums)
    │   ├── App.vue         # Root Vue component
    │   └── main.ts         # Application entry point
    ├── tests/              # Test files (unit, integration)
    │   └── unit/
    │   └── integration/
    ├── .env                # Local environment variables (DO NOT COMMIT)
    ├── .env.example        # Example environment variables
    ├── .eslintrc.cjs       # ESLint configuration
    ├── .gitignore          # Git ignore rules
    ├── .prettierrc.json    # Prettier configuration
    ├── index.html          # Main HTML entry point
    ├── package.json        # Project dependencies and scripts
    ├── README.md           # Project documentation
    ├── tsconfig.json       # TypeScript configuration
    ├── vite.config.ts      # Vite build tool configuration
    └── (yarn.lock/package-lock.json) # Dependency lock file
    ```

    ## Naming Conventions

    *   **Components:** Use `PascalCase` for Single-File Components (`.vue` files) (e.g., `UserProfile.vue`, `BaseButton.vue`). Prefix generic/base components with `Base` or `App`.
    *   **Composables:** Use `camelCase` prefixed with `use` (e.g., `useAuth.ts`, `useFormValidation.ts`).
    *   **Stores (Pinia):** Use `camelCase` suffixed with `Store` (e.g., `authStore.ts`, `jobStore.ts`). Store ID should be descriptive (e.g., `'auth'`, `'jobs'`).
    *   **Pages/Views:** Use `PascalCase` suffixed with `Page` or `View` (e.g., `LoginPage.vue`, `AdminDashboardView.vue`).
    *   **Layouts:** Use `PascalCase` suffixed with `Layout` (e.g., `DefaultLayout.vue`).
    *   **Services:** Use `camelCase` suffixed with `Service` (e.g., `authService.ts`).
    *   **TypeScript Files (`.ts`):** Use `camelCase` (e.g., `apiClient.ts`, `routeGuards.ts`).
    *   **Type Definitions:** Use `PascalCase` for interfaces and types (e.g., `interface UserProfile`, `type JobStatus`).
    *   **Directories:** Use `kebab-case` or `camelCase` (prefer `kebab-case` for consistency if applicable, e.g., `service-areas`, but `camelCase` is common in JS/TS world). Be consistent.

    ## Rationale

    *   Clear separation of concerns (UI, state, routing, API logic).
    *   Improved discoverability of files.
    *   Consistency across the development team.
    *   Alignment with common Vue project structures.
    