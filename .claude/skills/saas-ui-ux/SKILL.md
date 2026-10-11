---
name: saas-ui-ux
description: Moazzam's UI/UX knowledge base, built from Mobbin-style real-app research and B2B SaaS inspiration (Linear, Stripe, Attio, Notion, Vercel, Shopify Polaris, GitHub Primer, SaaSFrame patterns). Use for ANY UI/UX request — designing screens, flows, dashboards, tables, onboarding, settings, billing, empty states, AI features, mobile app screens, design critiques, or writing frontend UI code — so answers are grounded in patterns from shipped products, not generic defaults.
---

# SaaS & app UI/UX playbook

Apply this whenever the user asks for anything UI/UX. Answer like a senior product
designer who has studied thousands of shipped screens on Mobbin and SaaSFrame:
cite the real product a pattern comes from, then adapt it to the user's case.

## How to answer a UI/UX request

1. **Name the job of the screen.** What is the user trying to finish here? One
   primary action per screen.
2. **Find the precedent.** Pick 2–3 shipped products that solved the same problem
   (see `references/patterns.md` → "Who does it best"). Say which pattern you're
   borrowing and from whom ("filter bar like Linear's, empty state like Stripe's").
3. **Cover every state**, not just the happy path: empty (first-use vs.
   filtered-to-zero), loading, partial, error, success, permission-denied,
   overflow (long names, 10k rows).
4. **Specify concretely**: layout, hierarchy, component choices, copy, spacing
   tokens, keyboard behaviour. Avoid vague advice like "make it clean".
5. **Flag trade-offs** and what to validate with users.
6. If the Mobbin MCP is connected (`mcp__mobbin__*` or similar via ToolSearch),
   search it for live screens of the pattern before answering. If not connected,
   rely on this playbook and say so when it matters.

## Core principles (distilled from the best B2B products)

1. **Don't compete for attention you haven't earned** (Linear, 2026 refresh).
   Navigation and chrome recede; the work area gets the contrast. Dim the
   sidebar, shrink tabs, cut decorative icons and colored icon backgrounds.
2. **Structure should be felt, not seen** (Linear). Fewer borders and
   separators, softer contrast, rounded edges. Group with spacing and
   background tints before reaching for lines.
3. **Density with hierarchy.** Power users want information-dense screens
   (Linear, Stripe, Attio), but density only works with strong type hierarchy,
   alignment and consistent placement of actions.
4. **Predictable placement.** The same action (share, copy link, more menu)
   lives in the same spot on every page header. Linear's refresh was largely
   about fixing drift here.
5. **Status before title.** In lists of work items, status (icon + color, never
   color alone) is scanned first, then title (Linear).
6. **Operational, not decorative.** Dashboards should lead to a next action, not
   just report numbers (SaaSFrame analysis of high-retention dashboards).
7. **Progressive disclosure.** Show the 20% used 80% of the time; tuck the rest
   behind "More", side panels, advanced sections, or the command menu.
8. **Keyboard-first for power users.** ⌘K command menu, single-key shortcuts,
   shortcut hints in tooltips and menus.
9. **Classic charts win.** Line for trends, bar for comparison, donut only for
   ≤3 parts. If you must hover to get the gist, the chart failed.
10. **Accessibility is a baseline.** WCAG AA contrast (4.5:1 text), focus rings,
    icon+text for status, real `<table>` semantics, a high-contrast theme option.

## Default visual system (use unless the user has their own)

- **Spacing:** 4px base; use 4/8/12/16/24/32/48/64. Dense lists use 32–36px row
  height; comfortable lists 44–48px.
- **Type:** Inter (or Geist / SF) for UI; a display cut (Inter Display) for
  headings. Scale: 12 / 13 / 14 (body in dense apps) / 16 / 20 / 24 / 32.
  Weight for hierarchy: 400 body, 500 labels and buttons, 600 headings.
  Tabular numbers for any numeric column.
- **Color:** neutral-first UI with one accent. Build themes in a perceptual
  space (LCH/OKLCH) from 3 inputs: base, accent, contrast (Linear's approach),
  so light, dark and high-contrast themes stay consistent. Current trend: warm,
  low-saturation grays over cool blue-grays. Semantic colors only for meaning
  (success, warning, danger, info).
- **Radius:** 6–8px controls, 10–12px cards and modals, full pill for tags and
  segmented controls.
- **Elevation:** prefer tinted surfaces over shadows; shadows only for floating
  layers (menus, popovers, dialogs).
- **Motion:** 120–200ms ease-out for UI feedback; never animate layout on every
  keystroke; respect `prefers-reduced-motion`.
- **Dark mode:** expected in power-user tools. Design both themes from tokens,
  not by inverting.

## B2B app shell (the default layout)

```
┌──────────────┬───────────────────────────────────────────────┐
│ Workspace ▾  │ Breadcrumb / Page title        [Share] [⋯] [+] │
│ ⌘K Search    ├───────────────────────────────────────────────┤
│ Inbox    3   │ View tabs · Filter bar · Display options       │
│ My issues    ├───────────────────────────────────────┬───────┤
│ ── Teams ──  │ Main content (list / table / board)   │ Detail│
│ ── Favs ──   │                                       │ panel │
│ Settings     │                                       │       │
└──────────────┴───────────────────────────────────────┴───────┘
```

- Collapsible left sidebar (the dominant 2026 pattern; scales to many modules).
  Users can reorder, hide and favorite items (Linear's personalized sidebar).
- Workspace switcher top-left; user and account menu top-left or bottom-left.
- Page header holds title, view switcher and a fixed action cluster on the right.
- Detail opens in a right side panel (keeps list context) with an "open full
  page" option. Use modals only for short, blocking tasks.

## Where to go deeper

- `references/patterns.md`: pattern-by-pattern rules (tables, filters,
  forms, settings, billing, onboarding, empty/loading/error states, AI
  features, notifications, mobile app patterns) plus "who does it best".
- `references/sources.md`: where this knowledge came from, and how to give
  Claude live Mobbin access.
