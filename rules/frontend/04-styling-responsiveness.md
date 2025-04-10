# Frontend Rule: Styling & Responsiveness

    Ensure a consistent, maintainable, and responsive visual presentation across the application.

    ## Core Principles

    *   **Mobile-First:** Design and implement styles starting with mobile viewports and progressively enhance for larger screens using media queries (`min-width`).
    *   **Consistency:** Maintain a consistent look and feel throughout the application using predefined design tokens.
    *   **Maintainability:** Write clean, organized, and reusable styles.

    ## Recommended Approach: SCSS + Scoped Styles + Utility Classes (Optional)

    *   **SCSS/Sass:** Utilize SCSS (`.scss`) for enhanced CSS capabilities:
        *   **Variables:** Define design tokens (colors, fonts, spacing, breakpoints) in global SCSS variables (`src/styles/_variables.scss`).
        *   **Mixins:** Create reusable style patterns (e.g., for flexbox centering, responsive typography) using mixins (`src/styles/_mixins.scss`).
        *   **Nesting:** Use nesting judiciously to improve readability without creating overly specific selectors.
        *   **Partials:** Organize global styles into partials (`_variables.scss`, `_mixins.scss`, `_base.scss`, `_typography.scss`) imported into a main file (`src/styles/main.scss`).
    *   **Scoped Styles:** Use Vue's `<style scoped>` in Single-File Components for styles that only apply to the current component. This prevents style leakage and conflicts.
        ```vue
        <template>
          <div class="job-card">...</div>
        </template>

        <style scoped lang="scss">
        // These styles only apply to elements within this JobCard component
        .job-card {
          border: 1px solid var(--color-border);
          padding: var(--space-md);
        }
        </style>
        ```
    *   **Global Styles:** Define base element styles, typography defaults, and layout resets in global SCSS files (`src/styles/`) imported in `main.ts`.
    *   **Utility Classes (Optional but Recommended):** Consider integrating a utility-first CSS framework like **Tailwind CSS** or define your own minimal set of utility classes for common styling tasks (e.g., margins, padding, flexbox alignment). This can significantly speed up development and reduce the need for custom component styles.
        *   *If using Tailwind:* Follow its standard setup and configuration process.
        *   *If using custom utilities:* Define them globally (`src/styles/_utilities.scss`).
    *   **CSS Variables:** Leverage CSS Custom Properties (Variables) for dynamic styling (e.g., theming) and to expose design tokens from SCSS to component styles or inline styles if needed.

    ## Responsiveness

    *   **Breakpoints:** Define standard breakpoints in SCSS variables (e.g., `$breakpoint-sm`, `$breakpoint-md`, `$breakpoint-lg`).
    *   **Media Queries:** Use `min-width` media queries for the mobile-first approach.
        ```scss
        // Mobile styles first
        .container {
          width: 100%;
          padding: 0 var(--space-sm);
        }

        // Tablet and up
        @media (min-width: $breakpoint-sm) {
          .container {
            max-width: 720px;
            margin: 0 auto;
          }
        }

        // Desktop and up
        @media (min-width: $breakpoint-lg) {
          .container {
            max-width: 1140px;
          }
        }
        ```
    *   **Flexible Layouts:** Use CSS Flexbox and Grid for creating fluid and adaptable layouts.
    *   **Relative Units:** Prefer relative units (`rem`, `em`, `%`, `vw`, `vh`) over absolute units (`px`) for font sizes, padding, margins where appropriate to aid scaling.
    *   **Image Optimization:** Ensure images are responsive (e.g., `max-width: 100%`, `height: auto`) and consider using `<picture>` element or `srcset` for different resolutions.

    ## Rationale

    *   Mobile-first ensures a good experience on all devices.
    *   SCSS enhances CSS capabilities and maintainability.
    *   Scoped styles prevent global scope pollution.
    *   Consistent use of design tokens ensures visual harmony.
    *   Utility classes (optional) can accelerate development. 