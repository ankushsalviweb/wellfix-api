# Frontend Rule: Continuous Integration & Deployment (CI/CD)

    Implement automated CI/CD pipelines to streamline testing, building, and deployment processes.

    ## Platform

    *   Use **GitHub Actions** (or GitLab CI, Jenkins, etc., based on hosting and team preference). GitHub Actions is often convenient for projects hosted on GitHub.

    ## Pipeline Goals

    *   **Continuous Integration (CI):** Automatically build and test the application on every push to main branches (e.g., `main`, `develop`) and on pull requests.
    *   **Continuous Deployment/Delivery (CD):** Automatically deploy the application to staging and/or production environments upon successful merge to specific branches.

    ## CI Pipeline (Triggered on Push/Pull Request)

    A typical CI workflow (`.github/workflows/ci.yml`) should include the following steps:

    1.  **Checkout Code:** Use `actions/checkout@vX`.
    2.  **Setup Node.js:** Use `actions/setup-node@vX` to specify the Node.js version.
    3.  **Install Dependencies:** Cache dependencies (e.g., using `actions/cache@vX` with `package-lock.json` or `yarn.lock`) and run `npm install` or `yarn install`.
    4.  **Linting:** Run ESLint (`npm run lint` or `yarn lint`). Fail the build if errors occur.
    5.  **Formatting Check:** Run Prettier check (`npm run format:check` or `yarn format:check` - requires a check script in `package.json`). Fail the build if formatting issues exist.
    6.  **Unit/Integration Tests:** Run Vitest (`npm run test:unit` or `yarn test:unit`). Fail the build if tests fail.
    7.  **Type Checking:** Run TypeScript compiler check (`npm run typecheck` or `yarn typecheck` - using `vue-tsc --noEmit`). Fail the build on type errors.
    8.  **Build:** Run the production build (`npm run build` or `yarn build`). Ensure it completes successfully.
    9.  **(Optional) E2E Tests:** Run Cypress/Playwright tests (`npm run test:e2e` or `yarn test:e2e`). Often run conditionally or on specific triggers due to longer execution time.
    10. **(Optional) Code Coverage:** Upload test coverage reports (e.g., using `actions/upload-artifact@vX` or specialized actions like `codecov/codecov-action@vX`).
    11. **(Optional) Bundle Size Check:** Add a step to check if the build bundle size exceeds predefined limits.

    ## CD Pipeline (Triggered on Merge to `main` / Push to `production`)

    A deployment workflow (e.g., `.github/workflows/deploy-prod.yml`) typically builds upon the CI steps:

    1.  **Run CI Checks:** Either duplicate essential CI steps (install, lint, test, build) or trigger the deployment workflow *after* a successful CI run on the target branch.
    2.  **Build Application:** Ensure the production build (`npm run build`) is created.
    3.  **Configure Environment:** Set up environment variables specific to the target environment (staging, production) using GitHub Secrets.
    4.  **Deploy:** Deploy the built static assets (`dist/` directory) to the hosting provider.
        *   **Examples:**
            *   **Static Hosting (Netlify, Vercel, GitHub Pages):** Use official GitHub Actions provided by the hosting platform or simple commands (`rsync`, `aws s3 sync`).
            *   **Cloud Storage (S3/GCS):** Sync the `dist/` directory to the configured bucket.
            *   **Server:** Use `scp` or `rsync` to transfer files, potentially followed by SSH commands to restart services if needed (though less common for pure frontend deployments).
    5.  **(Optional) Cache Invalidation:** If using a CDN, trigger cache invalidation after deployment.
    6.  **(Optional) Health Checks/Smoke Tests:** Run basic checks against the deployed application URL.
    7.  **(Optional) Notifications:** Notify the team (e.g., via Slack) about deployment status.

    ## Best Practices

    *   **Secrets Management:** Store all sensitive information (API keys, deployment credentials) as encrypted secrets in the CI/CD platform's settings (e.g., GitHub Secrets).
    *   **Environment Variables:** Manage environment-specific configurations (like `VITE_API_BASE_URL`) through environment variables set in the CI/CD pipeline or deployment environment, not hardcoded.
    *   **Caching:** Utilize caching mechanisms for dependencies (`node_modules`) to speed up pipeline execution.
    *   **Fail Fast:** Structure pipelines to run faster checks (linting, unit tests) before slower ones (E2E tests, deployment).
    *   **Keep Pipelines Maintainable:** Use descriptive job/step names. Consider reusable workflows or composite actions for complex pipelines.
    *   **Branching Strategy:** Align triggers with your branching strategy (e.g., deploy `main` to production, `develop` to staging).

    ## Rationale

    *   Automates repetitive tasks, saving developer time.
    *   Provides fast feedback on code quality and correctness.
    *   Ensures consistent builds and deployments.
    *   Reduces the risk of manual deployment errors.
    *   Facilitates faster release cycles. 