# Frontend Rule: Accessibility (a11y)

    Ensure the application is usable by people with disabilities, adhering to Web Content Accessibility Guidelines (WCAG) 2.1 AA standards.

    ## Core Principles

    *   **Perceivable:** Information and user interface components must be presentable to users in ways they can perceive (e.g., alt text for images, captions for media).
    *   **Operable:** User interface components and navigation must be operable (e.g., keyboard navigable, sufficient time limits).
    *   **Understandable:** Information and the operation of user interface must be understandable (e.g., clear language, predictable navigation).
    *   **Robust:** Content must be robust enough that it can be interpreted reliably by a wide variety of user agents, including assistive technologies.

    ## Implementation Guidelines

    *   **Semantic HTML:**
        *   Use HTML elements for their intended purpose (e.g., `<button>` for buttons, `<nav>` for navigation, `<main>` for main content, `<header>`, `<footer>`, `<article>`, `<aside>`).
        *   Avoid using `<div>` or `<span>` for interactive elements; use appropriate elements or add ARIA roles if absolutely necessary.
    *   **Keyboard Navigation:**
        *   Ensure all interactive elements (links, buttons, form inputs) are focusable and operable using the keyboard alone.
        *   Maintain a logical focus order (usually the DOM order).
        *   Provide clear visual focus indicators (`:focus-visible` styles) for interactive elements.
        *   Implement keyboard traps appropriately for modals, ensuring focus stays within the modal until closed.
    *   **Images:**
        *   Provide descriptive `alt` text for all informative images (`<img alt="Description">`).
        *   Use empty `alt=""` for decorative images so screen readers ignore them.
    *   **Forms:**
        *   Use `<label>` elements correctly associated with their form controls (using `for` attribute matching the control's `id`).
        *   Use `<fieldset>` and `<legend>` to group related form controls (e.g., radio buttons).
        *   Provide clear instructions and error messages associated with form fields (use `aria-describedby` or `aria-errormessage` if needed).
        *   Ensure form validation errors are clearly communicated to assistive technologies.
    *   **ARIA (Accessible Rich Internet Applications):**
        *   Use ARIA attributes sparingly and correctly, primarily when semantic HTML is insufficient to convey the role, state, or properties of custom widgets or dynamic content.
        *   Common uses: `role`, `aria-label`, `aria-labelledby`, `aria-describedby`, `aria-hidden`, `aria-expanded`, `aria-haspopup`, `aria-live` (for dynamic content updates).
        *   Validate ARIA usage; incorrect ARIA can be worse than no ARIA.
    *   **Color Contrast:**
        *   Ensure sufficient color contrast between text and background (at least 4.5:1 for normal text, 3:1 for large text) according to WCAG AA standards.
        *   Use browser developer tools or online contrast checkers to verify.
        *   Do not rely on color alone to convey information.
    *   **Content Structure:**
        *   Use proper heading levels (`<h1>` to `<h6>`) to structure content hierarchically.
        *   Use lists (`<ul>`, `<ol>`, `<dl>`) for list content.
    *   **Dynamic Content:**
        *   Use techniques like ARIA live regions (`aria-live="polite"` or `aria-live="assertive"`) to announce dynamic content changes (e.g., status messages, notifications) to screen reader users.

    ## Testing & Validation

    *   **Manual Keyboard Testing:** Regularly navigate the application using only the keyboard (Tab, Shift+Tab, Enter, Space, Arrow keys).
    *   **Automated Tools:** Use browser extensions (e.g., Axe DevTools, WAVE) or linters (`eslint-plugin-vuejs-accessibility`) to catch common accessibility issues.
    *   **Screen Reader Testing:** Test key user flows using a screen reader (e.g., NVDA for Windows, VoiceOver for macOS, TalkBack for Android).
    *   **User Testing (Recommended):** Involve users with disabilities in testing if possible.

    ## Rationale

    *   Ensures the application is usable by the widest possible audience, including people with disabilities.
    *   Often required by law or policy in various sectors.
    *   Improves overall user experience and SEO.
    *   Promotes better code structure and semantic HTML usage. 