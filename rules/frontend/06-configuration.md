# Frontend Rule: Configuration Management

    Manage application configuration effectively using environment variables, suitable for different deployment environments.

    ## Approach: Vite Environment Variables

    Vue projects bootstrapped with Vite have built-in support for managing environment variables using `.env` files.

    *   **`.env` Files:**
        *   `.env`: Default values, loaded in all cases. **Should NOT be committed to Git.**
        *   `.env.development`: Loaded only in development mode. **Should NOT be committed to Git.**
        *   `.env.production`: Loaded only in production mode. **Should NOT be committed to Git.**
        *   `.env.local`: Loaded in all cases, overrides defaults. **Should NOT be committed to Git.** Used for local developer overrides.
        *   `.env.development.local`: Loaded in development, overrides `.env.development`. **Should NOT be committed to Git.**
        *   `.env.production.local`: Loaded in production, overrides `.env.production`. **Should NOT be committed to Git.**

    *   **`.env.example`:**
        *   Create and **commit** a `.env.example` file to the repository.
        *   This file should list all required environment variables with placeholder or sensible default values.
        *   It serves as documentation and a template for developers to create their local `.env` file.
        ```.env.example
        # Base URL for the WellFix Backend API
        VITE_API_BASE_URL=/api/v1

        # Optional: Google Maps API Key for map features
        VITE_GOOGLE_MAPS_API_KEY=

        # Optional: Feature Flags
        VITE_FEATURE_FLAG_NEW_DASHBOARD=false
        ```

    *   **Variable Naming:**
        *   Only variables prefixed with `VITE_` are exposed to the client-side code (`import.meta.env`).
        *   Use uppercase letters and underscores (`UPPER_SNAKE_CASE`).
        ```env
        VITE_API_BASE_URL=http://localhost:8000/api/v1
        ```

    *   **Accessing Variables in Code:**
        *   Use `import.meta.env.VITE_VARIABLE_NAME` to access the variables in your TypeScript/JavaScript code (e.g., in `src/services/apiClient.ts`).
        ```typescript
        const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
        ```
        *   Vite performs static replacement during the build process.

    *   **Type Safety (Optional but Recommended):**
        *   To get type checking and autocompletion for environment variables, you can extend Vite's `ImportMetaEnv` interface in a declaration file (e.g., `src/env.d.ts` or `src/vite-env.d.ts`):
        ```typescript
        /// <reference types="vite/client" />

        interface ImportMetaEnv {
          readonly VITE_API_BASE_URL: string;
          readonly VITE_GOOGLE_MAPS_API_KEY?: string; // Optional variable
          // add other env variables here...
        }

        interface ImportMeta {
          readonly env: ImportMetaEnv;
        }
        ```

    ## Security

    *   **NEVER** commit sensitive information (API keys, secrets) directly into the codebase or `.env.example`.
    *   Client-side environment variables (prefixed with `VITE_`) are embedded in the built JavaScript bundle. They are **NOT** secure for storing secrets meant only for the server.
    *   Secrets needed for build time but not runtime should not be prefixed with `VITE_`.

    ## Rationale

    *   Provides a standard way to manage configuration across different environments (development, production).
    *   Keeps sensitive information out of the committed codebase.
    *   Leverages Vite's built-in mechanism, requiring minimal setup.
    *   `.env.example` serves as clear documentation for required configuration. 