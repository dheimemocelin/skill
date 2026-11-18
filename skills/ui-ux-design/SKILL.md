---
name: ui-ux-design
description: Design, build, critique or polish user interfaces and flows, including screens, forms, navigation, design systems, responsive layout, accessibility and visual quality. Use when the user asks to create or improve a page or component, make it look better, fix layout or mobile issues, review UX, or check accessibility. Not for backend errors behind a screen (software-engineering) or metric correctness (data-engineering).
---

# UI/UX design

The interface must help the user finish their task, look intentional and work for everyone.

## 1. Understand the screen's job

From the request and existing product, identify: who uses it, the main task, what success looks like, and constraints (brand, existing design system, devices). Reuse existing components, tokens, spacing and colors before creating new ones.

## 2. Structure before style

1. List the content and actions in priority order — the primary action must be the most visible element.
2. Define every state: **loading, empty, error, success, partial data, no permission**.
3. Define behavior on mobile (≤ 480px), tablet and desktop, including long text, long names and large numbers.

## 3. Visual quality rules

- **Hierarchy:** one clear focal point per screen; at most 3 text sizes in a section; group related items and separate groups with space, not lines.
- **Spacing:** use a consistent scale (e.g. 4/8/12/16/24/32 px); align to a grid; equal spacing for equal relationships.
- **Typography:** body text ≥ 16px on mobile, line length 45–80 characters, line height ~1.5.
- **Color:** text contrast ≥ 4.5:1 (3:1 for large text and UI controls); never use color alone to convey status — add icon or text.
- **Restraint:** avoid generic card grids, gratuitous gradients, shadows and animation that compete with the content. Every element must earn its place.
- **Motion:** short (150–250ms), purposeful, and disabled under `prefers-reduced-motion`.

## 4. Accessibility (non-negotiable)

- Semantic HTML: real `<button>`, `<a>`, `<label>`, headings in order, landmarks.
- Full keyboard use with visible focus; logical tab order; focus moves into dialogs and returns after closing.
- Every input has a label; errors say what is wrong and how to fix it, next to the field; user input is kept after an error.
- Images have meaningful `alt` (or empty `alt` if decorative); touch targets ≥ 44×44px.

## 5. Verify for real

Render and look at the result when a browser or preview is available: check mobile and desktop widths, every state from step 2, keyboard navigation and contrast. Code or DOM assertions alone do not prove visual quality. If rendering is not available, say exactly what was not visually verified.

## Scope discipline

Small request → change only the affected component and its states; do not redesign the page or introduce a new design system. Critique-only request → prioritized findings, no edits:

```
[high] Checkout, mobile — "Pay" button is below the fold and same color as "Back"
  Fix: make Pay the only filled button and stick it to the bottom on ≤ 480px.
```

## Deliver

```
**Result:** what improved for the user
**Changed:** screens / components / states
**Verified:** widths, states, keyboard, contrast — how
**Not verified:** e.g. screen reader, real devices
```

Never display real personal data in mockups or screenshots; use realistic synthetic data.
