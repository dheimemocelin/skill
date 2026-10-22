---
name: ui-ux-design
description: Design, critique, or refine product flows, visual interfaces, and design systems. Use when a task changes user experience, accessibility, responsive behavior, interaction design, or visual quality.
---

# ui-ux-design


## Approach (inspired by pbakaus/impeccable; external skill is optional)
1. **Product truth:** capture audience, tasks, constraints, product voice, accessibility needs and success measure in PRODUCT.md or existing project docs.
2. **Shape before styling:** map flows, information hierarchy, empty/loading/error states, user permissions and responsive layouts.
3. **Design language:** reuse existing DESIGN.md/tokens/components; if absent propose spacing, type scale, colors, density, radii, motion and contrast appropriate to context.
4. **Implement:** semantic HTML/accessible interactions, keyboard navigation, visible focus, sensible loading skeletons, tables with sorting/filter states and mobile behavior.
5. **Critique:** user-task clarity, visual hierarchy, consistency, readability, density, visual noise and originality. Avoid generic dashboard templates and unnecessary cards.
6. **Audit:** keyboard/a11y checks, contrast, overflow, internationalization, responsive breakpoints, performance and reduced motion.
7. **Polish:** remove clutter, align typography and spacing, improve microcopy and edge states; don't replace product truth with trend-driven aesthetics.

## Optional official Impeccable integration
If `impeccable` is installed, use the original tool's `init`, `shape`, `critique`, `audit`, `polish`, `distill`, `adapt` and `extract` flows according to its actual version and user request. Do not assert these commands are implemented by this skill. Install separately and evaluate executable/hook trust before enabling automatic actions. Source: https://github.com/pbakaus/impeccable

## Deliverable
Explain user task served, changed screens/components, states checked, accessibility evidence and known gaps.
