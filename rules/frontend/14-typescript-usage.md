# Frontend Rule: TypeScript Usage (Vue 3)

    Leverage TypeScript effectively throughout the Vue application to enhance type safety, developer experience, and maintainability.

    ## Core Principles

    *   **Type Everything:** Aim for strong type coverage across the codebase.
    *   **Leverage Inference:** Utilize TypeScript's type inference where possible, but provide explicit types when clarity is needed or inference is insufficient.
    *   **Strict Mode:** Enable `strict` mode (or specific strict checks like `strictNullChecks`, `noImplicitAny`) in `tsconfig.json` for maximum type safety.

    ## Implementation Guidelines

    *   **`<script setup lang="ts">`:**
        *   Use `<script setup lang="ts">` in all Single-File Components (.vue) to enable TypeScript within the setup context.
    *   **Props:**
        *   Define props using `defineProps` with TypeScript types or interfaces:
            ```typescript
            interface Props {
              jobId: number;
              initialStatus?: JobStatus; // Optional prop
              user: User;
            }
            const props = withDefaults(defineProps<Props>(), {
              initialStatus: 'PENDING' // Default value for optional prop
            });
            ```
    *   **Emits:**
        *   Define emitted events using `defineEmits` with type annotations for the payload:
            ```typescript
            const emit = defineEmits<{ 
              (e: 'update:modelValue', value: string): void;
              (e: 'formSubmit', payload: { email: string; name: string }): void;
            }>();
            ```
    *   **Refs and Reactives:**
        *   Provide explicit types when creating `ref` or `reactive` state, especially for complex objects or when the initial value is `null` or `undefined`:
            ```typescript
            import type { User } from '@/types/user';
            const currentUser = ref<User | null>(null);
            const jobDetails = reactive<{ job: Job | null; isLoading: boolean }>({ job: null, isLoading: false });
            ```
    *   **Computed Properties:**
        *   TypeScript can usually infer the return type of computed properties, but add explicit types if the logic is complex or involves external types.
            ```typescript
            const isJobEditable = computed<boolean>(() => { ... });
            ```
    *   **Functions and Methods:**
        *   Provide type annotations for function parameters and return types.
            ```typescript
            async function fetchJob(id: number): Promise<Job | null> { ... }

            const formatUserName = (user: User): string => { ... };
            ```
    *   **Pinia Stores:**
        *   Strongly type state properties, getter return types, and action parameters/return types as defined in the Pinia rule.
    *   **API Services:**
        *   Use TypeScript interfaces/types (`src/types/`) for API request payloads and response data, and use them in service function signatures and Axios calls, as defined in the API Interaction rule.
    *   **Composables:**
        *   Type the arguments and return values of composable functions.
    *   **Utility Types:**
        *   Utilize TypeScript utility types (`Partial`, `Required`, `Readonly`, `Pick`, `Omit`, etc.) to create new types based on existing ones effectively.
    *   **Enums:**
        *   Use TypeScript `enum` or string literal unions for representing fixed sets of values (e.g., job statuses, user roles) imported from `src/types/`.
            ```typescript
            // src/types/enums.ts
            export enum JobStatus { ... }
            // or
            export type UserRole = 'ADMIN' | 'CUSTOMER' | 'ENGINEER';
            ```
    *   **Avoid `any`:**
        *   Minimize the use of `any`. If type information is truly unavailable or overly complex to define, consider using `unknown` and performing type checks/assertions instead.
    *   **Type Imports:**
        *   Use `import type { ... } from '...';` when importing only types to potentially aid build tools and make intent clear.

    ## `tsconfig.json`

    *   Ensure `tsconfig.json` is configured appropriately for a Vue/Vite project.
    *   Enable `strict` mode or relevant strict checks.
    *   Configure `baseUrl` and `paths` for non-relative imports (e.g., `@/*` mapped to `src/*`).

    ## Rationale

    *   Catches type-related errors during development (compile-time) rather than at runtime.
    *   Improves code readability and self-documentation.
    *   Enhances developer experience with autocompletion and refactoring capabilities in IDEs.
    *   Increases code robustness and maintainability, especially in larger projects.
    *   Facilitates better collaboration within the team. 