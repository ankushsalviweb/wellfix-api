# Frontend Rule: State Management (Pinia)

    Utilize Pinia for centralized state management to handle shared application state effectively and predictably.

    ## Core Concepts

    *   **Store:** A container for state, getters, and actions related to a specific domain (e.g., authentication, jobs, user profile).
    *   **State:** The raw data held within the store (defined as a function returning an object).
    *   **Getters:** Computed properties derived from the store's state (similar to computed properties in components).
    *   **Actions:** Functions used to modify the store's state. Actions can be asynchronous and often encapsulate business logic or API calls.

    ## Implementation Guidelines

    *   **Store Definition:**
        *   Define stores in the `src/stores/` directory.
        *   Use the `defineStore` function from Pinia.
        *   Provide a unique, descriptive ID as the first argument (e.g., `'auth'`, `'jobs'`).
        *   Use the setup store syntax (`() => { ... return { state, getters, actions } }`) for better TypeScript inference and composable usage, or the options API syntax based on team preference.
        *   Strongly type the state, getters, and action parameters/return types using TypeScript.
        ```typescript
        // Example using setup store syntax
        import { ref, computed } from 'vue';
        import { defineStore } from 'pinia';
        import type { User } from '@/types/user';

        export const useAuthStore = defineStore('auth', () => {
          // State
          const currentUser = ref<User | null>(null);
          const token = ref<string | null>(localStorage.getItem('authToken'));

          // Getters
          const isAuthenticated = computed(() => !!token.value && !!currentUser.value);
          const isAdmin = computed(() => currentUser.value?.role === 'ADMIN');

          // Actions
          async function login(credentials: ...) {
            // ... call authService.login
            // ... update currentUser and token
            // ... save token to localStorage
          }

          function logout() {
            // ... clear currentUser and token
            // ... remove token from localStorage
          }

          return { currentUser, token, isAuthenticated, isAdmin, login, logout };
        });
        ```
    *   **Using Stores in Components:**
        *   Import the store definition (e.g., `import { useAuthStore } from '@/stores/authStore';`).
        *   Instantiate the store within the component's `setup` function: `const authStore = useAuthStore();`.
        *   Access state and getters directly (e.g., `authStore.isAuthenticated`, `authStore.currentUser`). Pinia automatically handles reactivity.
        *   Call actions as methods (e.g., `authStore.login(credentials)`).
        *   Use `storeToRefs` from Pinia if you need to destructure state properties while maintaining reactivity, especially when passing them as props.
    *   **Organization:**
        *   Create separate stores for distinct domains (e.g., `authStore`, `jobStore`, `uiStore`).
        *   Avoid putting unrelated state into a single monolithic store.
    *   **Asynchronous Actions:**
        *   Handle asynchronous operations (like API calls) within actions.
        *   Manage loading and error states within the store itself (e.g., add `isLoading` and `error` refs to the state).
    *   **State Modification:**
        *   **ONLY** modify state directly within actions (or via direct assignment inside setup stores, though actions are preferred for encapsulation).
        *   Do **NOT** modify store state directly from components.
    *   **Persistence:** For state that needs to persist across page reloads (like authentication tokens or user preferences), use mechanisms like `localStorage` or `sessionStorage` within actions, or consider using Pinia plugins like `pinia-plugin-persistedstate`.

    ## Rationale

    *   Provides a centralized, predictable way to manage shared state.
    *   Improves code organization by separating state logic from UI components.
    *   Enhances testability of state logic.
    *   Leverages Vue's reactivity system effectively.
    *   Offers excellent TypeScript support for type safety.
    *   Pinia's developer experience is generally considered very good. 