# Frontend Rule: Component Design (Vue 3)

    Adhere to best practices for component design to promote reusability, maintainability, and testability.

    ## Guiding Principles

    *   **Single Responsibility Principle (SRP):** Components should ideally do one thing well. Avoid monolithic components handling too much logic or UI.
    *   **Reusability:** Design components to be reusable across different parts of the application where applicable.
    *   **Composition:** Build complex UI by composing smaller, simpler components.
    *   **Props Down, Events Up:** Data should flow down from parent to child components via props. Child components should communicate changes or actions to parents via emitted events.

    ## Component Types

    Distinguish between different types of components:
    *   **Presentational/Dumb Components (`src/components/common/`, `src/components/features/`):**
        *   Primarily concerned with how things look.
        *   Receive data via props.
        *   Emit events for user interactions.
        *   Rarely have their own significant state (usually just UI state like open/closed).
        *   Do not interact directly with stores or API services.
    *   **Container/Smart Components (Often found in `src/pages/` or complex feature components):**
        *   Primarily concerned with how things work.
        *   May manage their own state or fetch data from stores/services.
        *   Pass data down to presentational components via props.
        *   Handle events emitted by presentational components, often triggering actions or store updates.
    *   **Layout Components (`src/layouts/`):**
        *   Define the overall structure of pages (e.g., header, footer, sidebar, main content area).
        *   Use slots (`<slot>`) to inject page-specific content.

    ## Best Practices

    *   **Props:**
        *   Use TypeScript interfaces or `<script setup lang="ts">` with `defineProps` for type safety.
        *   Define props clearly and make them required (`required: true`) unless they are truly optional.
        *   Provide default values for optional props where sensible.
        *   Use prop validators for complex validation logic if needed.
    *   **Events:**
        *   Use `defineEmits` in `<script setup>` for declaring emitted events.
        *   Use descriptive event names (e.g., `@update:modelValue`, `@form-submitted`, `@item-selected`).
        *   Pass relevant data payload with events.
    *   **Slots:**
        *   Use slots for content projection to make components more flexible (default slot, named slots).
    *   **Composition API (`<script setup>`):**
        *   Prefer `<script setup>` syntax for its conciseness and better TypeScript integration.
        *   Organize logic within `setup` using composables (`src/composables/`) for reusable stateful logic.
    *   **Keep Templates Clean:** Avoid complex JavaScript logic directly in the `<template>`. Use computed properties or methods/functions in `<script setup>` instead.
    *   **File Structure:** Place components in relevant directories (`common`, `features`).
    *   **v-model:** Use `v-model` (with `defineModel` in Vue 3.3+ or `props`/`emits` for older versions) for two-way data binding on form inputs within custom components.

    ## Rationale

    *   Improves code organization and readability.
    *   Enhances reusability and reduces code duplication.
    *   Makes components easier to test in isolation.
    *   Facilitates easier refactoring and maintenance. 