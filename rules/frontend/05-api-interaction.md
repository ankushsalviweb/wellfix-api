# Frontend Rule: API Interaction

    Standardize communication with the backend WellFix API for consistency, maintainability, and robustness.

    ## Recommended Approach: Centralized Service Layer with Axios

    *   **HTTP Client:** Use `axios` as the primary library for making HTTP requests.
    *   **Centralized Instance:** Create a single, configured Axios instance (`src/services/apiClient.ts`) to handle base URL, headers, timeouts, and interceptors.
        ```typescript
        import axios from 'axios';
        import { useAuthStore } from '@/stores/authStore'; // Assuming Pinia store

        const apiClient = axios.create({
          baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1', // From .env
          timeout: 10000, // 10 seconds
          headers: {
            'Content-Type': 'application/json',
          },
        });

        // Request Interceptor (e.g., to add Auth token)
        apiClient.interceptors.request.use(
          (config) => {
            const authStore = useAuthStore();
            const token = authStore.token; // Get token from Pinia store
            if (token) {
              config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
          },
          (error) => {
            return Promise.reject(error);
          }
        );

        // Response Interceptor (e.g., for global error handling or token refresh)
        apiClient.interceptors.response.use(
          (response) => {
            return response; // Pass through successful responses
          },
          (error) => {
            // Handle specific errors globally (e.g., 401 Unauthorized -> logout)
            if (error.response && error.response.status === 401) {
              const authStore = useAuthStore();
              authStore.logout(); // Example: trigger logout action
              // Optionally redirect to login page
              // router.push('/login');
            }
            // TODO: Add more robust global error handling/logging
            return Promise.reject(error);
          }
        );

        export default apiClient;
        ```
    *   **Service Files:** Create dedicated service files within `src/services/` for different API resource groups (e.g., `authService.ts`, `jobService.ts`, `userService.ts`).
        *   These files import the configured `apiClient`.
        *   Each file exports functions corresponding to specific API endpoints.
        *   These functions encapsulate the request logic (method, URL, data payload) and return Promises.
        ```typescript
        // src/services/jobService.ts
        import apiClient from './apiClient';
        import type { Job, JobCreatePayload, JobListResponse } from '@/types/job';

        export const jobService = {
          async createJob(payload: JobCreatePayload): Promise<Job> {
            const response = await apiClient.post<Job>('/jobs', payload);
            return response.data;
          },

          async getJobs(params?: Record<string, any>): Promise<JobListResponse> {
            const response = await apiClient.get<JobListResponse>('/jobs', { params });
            return response.data;
          },

          async getJobById(jobId: number): Promise<Job> {
            const response = await apiClient.get<Job>(`/jobs/${jobId}`);
            return response.data;
          },

          // ... other job-related API functions
        };
        ```
    *   **Usage in Stores/Components:**
        *   Import service functions into Pinia stores (primarily in actions) or directly into components (if state management isn't strictly needed for that data, though stores are preferred).
        *   Call the service functions to interact with the API.
        *   Handle the returned Promises (e.g., using `async/await` within Pinia actions).

    ## Error Handling

    *   **Global Handling:** Use Axios interceptors for common errors (like 401 Unauthorized). Log errors or trigger global actions (like logout).
    *   **Local Handling:** Use `try...catch` blocks within Pinia actions or component methods where specific error handling logic is needed (e.g., displaying user-facing error messages based on API response).
    *   **User Feedback:** Provide clear feedback to the user during API calls (loading states) and upon errors.

    ## Loading States

    *   Manage loading states (e.g., `isLoading` boolean flags) within Pinia stores or component state.
    *   Set `isLoading` to `true` before an API call and `false` in `finally` block of the `try...catch` to ensure it resets correctly on success or error.

    ## Type Safety

    *   Use TypeScript interfaces/types (`src/types/`) to define the expected shapes of API request payloads and response data.
    *   Use these types in service function signatures and with Axios generic type arguments (`apiClient.get<User>('...')`) for compile-time checks and better developer experience.
    *   Consider generating types automatically from the backend OpenAPI spec using tools like `openapi-typescript` or similar.

    ## Rationale

    *   Centralizes API logic, making it easier to manage and update.
    *   Decouples UI components from direct API interaction.
    *   Provides a single point for configuring base URL, headers, and interceptors.
    *   Promotes consistent error handling and loading state management.
    *   Enhances type safety when used with TypeScript.
    