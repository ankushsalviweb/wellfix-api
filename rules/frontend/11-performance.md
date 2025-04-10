# Frontend Rule: Performance

    Optimize frontend performance to ensure a fast, responsive, and efficient user experience.

    ## Key Areas

    *   **Bundle Size:** Minimize the amount of JavaScript, CSS, and other assets downloaded by the browser.
    *   **Loading Performance:** Reduce the time it takes for the application to become interactive (Time to Interactive - TTI).
    *   **Runtime Performance:** Ensure smooth animations, fast UI updates, and efficient processing during user interaction.

    ## Optimization Techniques

    *   **Code Splitting (Vite/Vue Router):**
        *   Leverage Vite's automatic code splitting based on dynamic imports.
        *   Implement route-based code splitting using dynamic imports in Vue Router configuration:
            ```typescript
            // src/router/index.ts
            const routes = [
              {
                path: '/',
                component: () => import('@/pages/HomePage.vue') // Dynamic import
              },
              {
                path: '/admin',
                component: () => import('@/layouts/AdminLayout.vue'),
                children: [
                  { path: '', component: () => import('@/pages/admin/DashboardPage.vue') },
                  // ... other admin routes dynamically imported
                ]
              }
            ];
            ```
        *   Consider component-level dynamic imports (`defineAsyncComponent`) for large components not needed on initial load.
    *   **Lazy Loading:**
        *   Lazy load images that are off-screen using the `loading="lazy"` attribute or libraries like `vue-lazyload`.
        *   Lazy load non-critical third-party scripts or components.
    *   **Tree Shaking:**
        *   Ensure tree shaking is effective by writing ES6 module-compatible code and avoiding side effects in module top-level scope.
        *   Vite handles tree shaking automatically during the production build.
        *   Import specific functions from libraries instead of the entire library where possible (e.g., `import { debounce } from 'lodash-es';` instead of `import _ from 'lodash';`).
    *   **Asset Optimization:**
        *   **Images:** Use modern formats (WebP, AVIF), compress images appropriately, and serve responsive images using `srcset` or `<picture>`.
        *   **Fonts:** Load only necessary font weights/styles. Use `font-display: swap;` to prevent blocking rendering. Consider self-hosting fonts for better control.
        *   **CSS:** Minify CSS during the build process (handled by Vite). Remove unused CSS (can be assisted by tools like PurgeCSS if needed, though often handled well by framework scoping).
    *   **Bundle Analysis:**
        *   Use tools like `rollup-plugin-visualizer` (configured in `vite.config.ts`) to analyze the production bundle and identify large modules or dependencies that could be optimized or split.
    *   **Memoization / Caching:**
        *   Use Vue's `computed` properties effectively to cache derived values.
        *   For expensive calculations within components, consider manual memoization techniques if needed.
        *   Utilize HTTP caching headers effectively on the backend API for static assets and API responses.
    *   **Efficient Component Rendering:**
        *   Use `v-if` vs `v-show` appropriately (`v-if` avoids rendering altogether, `v-show` uses `display: none`).
        *   Avoid unnecessary re-renders by optimizing reactive dependencies in computed properties and watchers.
        *   Use `v-for` with keys correctly.
        *   Consider `v-memo` for performance-critical lists where applicable.
    *   **Debouncing/Throttling:**
        *   Debounce or throttle event handlers for frequent events (e.g., window resize, scroll, input events) to limit the rate of execution.
    *   **Web Workers:**
        *   For computationally intensive tasks that could block the main thread, consider offloading them to Web Workers.

    ## Monitoring & Measurement

    *   **Browser DevTools:** Use the Network and Performance tabs in browser developer tools to analyze loading times, asset sizes, rendering performance, and identify bottlenecks.
    *   **Lighthouse:** Regularly run Lighthouse audits (available in Chrome DevTools) to get performance scores and actionable suggestions.
    *   **Real User Monitoring (RUM) (Optional):** Implement RUM tools (e.g., Sentry Performance, Datadog RUM) in production to understand real-world user performance.

    ## Rationale

    *   Improves user satisfaction and engagement.
    *   Positively impacts SEO rankings.
    *   Reduces bounce rates.
    *   Ensures accessibility for users on slower connections or less powerful devices.
    *   Lowers bandwidth costs. 