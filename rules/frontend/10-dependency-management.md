# Frontend Rule: Dependency Management

    Manage project dependencies effectively to ensure reproducible builds, maintain security, and control bundle size.

    ## Package Manager

    *   Use either `npm` or `yarn` (Classic or Berry) consistently across the project. Decide on one and stick to it.
    *   **Recommendation:** `npm` is bundled with Node.js and is widely used. `yarn` (especially Berry/v2+) offers features like Plug'n'Play which can improve performance and dependency reliability, but might have a steeper learning curve or compatibility issues with some tools.

    ## `package.json`

    *   Clearly define project metadata (name, version, description, license).
    *   List runtime dependencies under `dependencies`.
    *   List development dependencies (testing tools, linters, build tools, type definitions) under `devDependencies`.
    *   Define useful scripts in the `scripts` section (e.g., `dev`, `build`, `test:unit`, `test:e2e`, `lint`, `format`).

    ## Lock Files

    *   **Commit Lock Files:** Always commit the package manager's lock file (`package-lock.json` for npm, `yarn.lock` for yarn) to the repository.
    *   **Purpose:** Lock files ensure that all developers and CI/CD environments install the exact same versions of all dependencies, leading to reproducible builds and avoiding "works on my machine" issues.

    ## Adding Dependencies

    *   Add runtime dependencies using:
        *   `npm install <package-name>`
        *   `yarn add <package-name>`
    *   Add development dependencies using:
        *   `npm install --save-dev <package-name>` (or `-D`)
        *   `yarn add --dev <package-name>` (or `-D`)
    *   **Vetting:** Before adding a new dependency, consider:
        *   Is it actively maintained?
        *   Is it well-documented?
        *   Does it have known security vulnerabilities (check databases like Snyk, npm audit)?
        *   What is its bundle size impact (use tools like `bundlephobia.com`)?
        *   Is there a simpler alternative or can the functionality be implemented reasonably without it?

    ## Updating Dependencies

    *   Regularly update dependencies to benefit from bug fixes, performance improvements, and security patches.
    *   Use commands like:
        *   `npm update`
        *   `npm outdated` (to check for outdated packages)
        *   `yarn upgrade`
        *   `yarn outdated`
    *   For major version updates, carefully review the library's changelog for breaking changes.
    *   Run tests thoroughly after updating dependencies.
    *   Consider using tools like `npm-check-updates` (`ncu`) for a more interactive update process.

    ## Security Auditing

    *   Periodically run security audits using:
        *   `npm audit`
        *   `yarn audit`
    *   Review reported vulnerabilities and update or replace packages as necessary. Use `npm audit fix` or `yarn audit` with appropriate flags cautiously.
    *   Integrate dependency scanning into the CI/CD pipeline using tools like Snyk, Dependabot (GitHub), or Trivy.

    ## Rationale

    *   Ensures consistent development and build environments.
    *   Helps manage security vulnerabilities proactively.
    *   Provides clarity on project dependencies.
    *   Facilitates easier updates and maintenance. 