# Frontend Rule: Code Style & Linting

    Enforce consistent code style and identify potential errors early using automated tools.

    ## Core Tools

    *   **Formatter:** `Prettier` (Opinionated code formatter to ensure uniform style).
    *   **Linter:** `ESLint` (Analyzes code for problematic patterns and enforces coding standards).
        *   **Parser:** `@typescript-eslint/parser` (Allows ESLint to understand TypeScript).
        *   **Plugins:**
            *   `@typescript-eslint/eslint-plugin` (Provides TypeScript-specific linting rules).
            *   `eslint-plugin-vue` (Provides Vue-specific linting rules, including template analysis).
            *   (Optional) `eslint-plugin-prettier` / `eslint-config-prettier` (Integrates Prettier rules into ESLint to avoid conflicts).
            *   (Optional) `eslint-plugin-testing-library`, `eslint-plugin-vitest` (For testing best practices).
            *   (Optional) `eslint-plugin-vuejs-accessibility` (For accessibility rules in templates).

    ## Configuration

    *   **Prettier:** Configure via `.prettierrc.json` (or other supported formats). Define options like `semi`, `singleQuote`, `tabWidth`, `printWidth`.
        ```json
        // .prettierrc.json (Example)
        {
          "semi": true,
          "singleQuote": true,
          "tabWidth": 2,
          "printWidth": 100,
          "trailingComma": "es5"
        }
        ```
    *   **ESLint:** Configure via `.eslintrc.cjs` (or other supported formats).
        *   Specify the parser (`@typescript-eslint/parser`).
        *   Enable necessary parser options (e.g., `ecmaVersion`, `sourceType`).
        *   Extend recommended configurations (e.g., `eslint:recommended`, `plugin:@typescript-eslint/recommended`, `plugin:vue/vue3-recommended`).
        *   Add required plugins.
        *   Define specific rules overrides or additions in the `rules` section.
        ```javascript
        // .eslintrc.cjs (Example - Structure)
        module.exports = {
          root: true,
          env: {
            browser: true,
            es2021: true,
            node: true,
            'vue/setup-compiler-macros': true // Important for <script setup>
          },
          parser: 'vue-eslint-parser', // Use vue-eslint-parser for .vue files
          parserOptions: {
            parser: '@typescript-eslint/parser', // Specify TS parser for <script>
            ecmaVersion: 'latest',
            sourceType: 'module',
          },
          extends: [
            'eslint:recommended',
            'plugin:@typescript-eslint/recommended',
            'plugin:vue/vue3-recommended', // Or vue3-essential, vue3-strongly-recommended
            // 'prettier' // Add this if using eslint-config-prettier to disable conflicting rules
          ],
          plugins: [
            '@typescript-eslint',
            // 'prettier' // Add this if using eslint-plugin-prettier
            // 'testing-library', 'vitest', 'vuejs-accessibility' // Optional plugins
          ],
          rules: {
            // --- Prettier Integration --- (If using eslint-plugin-prettier)
            // "prettier/prettier": "warn",

            // --- General Overrides ---
            'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
            'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',

            // --- TypeScript Specific ---
            '@typescript-eslint/no-unused-vars': ['warn', { 'argsIgnorePattern': '^_' }],
            '@typescript-eslint/no-explicit-any': 'warn',

            // --- Vue Specific ---
            'vue/multi-word-component-names': 'off', // Personal preference, adjust as needed
            'vue/no-v-html': 'warn',
            'vue/component-name-in-template-casing': ['error', 'PascalCase'],

            // --- Optional Plugin Rules ---
            // "testing-library/await-async-queries": "error",
            // "vitest/no-focused-tests": "warn",
            // "vuejs-accessibility/alt-text": "warn",
          },
        };
        ```

    ## Integration

    *   **IDE Integration:** Configure your IDE (e.g., VS Code) to use ESLint and Prettier for real-time feedback and formatting on save.
        *   Install relevant IDE extensions (e.g., ESLint, Prettier - Code formatter).
        *   Configure settings (`settings.json` in VS Code) to enable format on save and default formatters.
    *   **Git Hooks:** Use tools like `husky` and `lint-staged` to automatically run linters and formatters on staged files before commits, preventing bad code from entering the repository.
        ```json
        // package.json (Example with lint-staged)
        {
          "scripts": {
            "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix",
            "format": "prettier --write src/ tests/"
          },
          "lint-staged": {
            "*.{vue,js,jsx,cjs,mjs,ts,tsx,cts,mts}": "eslint --fix",
            "*.{vue,js,jsx,cjs,mjs,ts,tsx,cts,mts,json,css,scss,md}": "prettier --write"
          }
        }
        ```
        *   Setup `husky` to run `npx lint-staged` on pre-commit hook.
    *   **CI Pipeline:** Include linting and formatting checks as steps in the CI pipeline to catch issues automatically.

    ## Rationale

    *   Ensures consistent code formatting across the team, improving readability.
    *   Catches potential errors and anti-patterns early in the development cycle.
    *   Automates code quality checks, reducing manual review effort.
    *   Improves overall code maintainability and reduces technical debt. 