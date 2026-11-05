---
name: ui-ux-design
description: Design, critique, or refine product flows, visual interfaces, and design systems. Use when a task changes user experience, accessibility, responsive behavior, interaction design, or visual quality.
---

# UI/UX design

Use for interfaces, user flows, accessibility and visual quality. An API failure alone uses software-engineering. Apply these Impeccable-inspired practices only when user experience is involved; external Impeccable tooling is optional and is not bundled.

## Shape and implement

- Establish the user's task, audience, constraints, product voice and success measure from existing context. Add durable product/design documentation only when a wider decision needs it.
- Map information hierarchy, navigation, permissions, responsive behavior and loading/empty/error/success states before styling. Reuse existing components, tokens and design language.
- Give new work an intentional identity appropriate to the product: typography, type scale, spacing/alignment, color/contrast, density and purposeful motion. Avoid generic card grids and decorative trends that obscure the task.
- Implement semantic structure, labels, keyboard navigation, visible focus, readable content and reduced-motion behavior. Preserve form input on errors; explain recovery and submission results. Navigation needs clear location and focus/return behavior; async views preserve user context.

## Critique and verify

Inspect hierarchy, consistency, readability, visual noise and finishing details. Check relevant mobile/desktop layouts, overflow, long/localized content, contrast and interactions. Use rendered visual inspection and interaction checks when available; code/DOM assertions alone do not establish visual quality. Do not skip these checks to save context.

For small adjustments, change the affected component and states without imposing a full redesign or new design system. Critique-only requests produce prioritized findings, not unsolicited edits. If browser or assistive technology is unavailable, state what was checked and what remains unverified.

Deliver the user benefit, changed screens/states, visual and accessibility evidence, and known gaps. If external Impeccable tooling is already available, use only capabilities supported by its actual version and the request; install nothing automatically. Source: https://github.com/pbakaus/impeccable
