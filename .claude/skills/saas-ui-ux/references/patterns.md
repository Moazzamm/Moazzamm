# Pattern library

Each section: the rules, then **Who does it best**, meaning products to cite and study
on Mobbin or SaaSFrame.

---

## Data tables & lists

- Compact rows, sticky header, sortable columns, column show/hide and reorder.
- Right-align numbers and money; use tabular figures; left-align text.
- First column = the object's name (link to detail). Status as icon + label.
- Row hover reveals secondary actions (⋯ menu); never hide the primary action.
- Bulk select: a checkbox column appears on hover; selecting rows swaps the
  toolbar for a bulk-action bar ("3 selected · Assign · Archive · Delete").
- Truncate long text with a tooltip on hover; never wrap names into 3 lines.
- Pagination for financial or auditable data (Stripe); infinite scroll or
  virtualized lists for work items (Linear). Always show the total count.
- Saved views: users save a filter + sort + column set as a named view (tabs above
  the table).
- Inline editing for quick fields (status, assignee, date) via click-to-edit
  popovers.

**Who does it best:** Stripe (payments and customers tables), Linear (issue lists),
Attio (spreadsheet-like CRM records), Airtable, Notion databases, Vercel
(deployments list).

## Filters & search

- Filter bar above content: "+ Filter" opens a combobox of fields → operator →
  value. Applied filters render as removable chips ("Status is In progress ×").
- Date ranges: presets (Today, Last 7 days, Last 30 days, This month) +
  "Custom" (Stripe).
- One global filter (date, workspace) updates every widget on the page.
- Search: instant results, highlight matches, keyboard navigable, recent searches.
- ⌘K command menu = search + navigation + actions in one place (Linear, Vercel,
  Raycast).

**Who does it best:** Linear (filter chips), Stripe (date presets), Notion (⌘K),
Attio.

## Empty states (the most under-designed screens)

Distinguish them; each needs different copy and action:

| State | Copy | Action |
|---|---|---|
| **First use** (nothing exists yet) | What this area is for + the value | Primary CTA to create; optional "import" or "use sample data" |
| **Filtered to zero** | "No customers match those filters" | "Clear filters". Never a "create" CTA (Stripe, Shopify Polaris) |
| **Search no results** | Repeat the query | Suggestions, clear search |
| **Cleared / done** (inbox zero) | Celebrate lightly | Nothing, or next task |
| **No permission** | Why + who can grant access | "Request access" |

- Treat a first-use empty state like a mini landing page: preview of what it
  looks like with data (sample data or a ghosted skeleton), one CTA.
- Dashboards with no data: don't render blank charts. Explain how to get data
  flowing, with a CTA (SaaSFrame: Cake Equity).

**Who does it best:** Stripe, Shopify Polaris, Linear, Notion, Cake Equity.

## Loading, saving, errors

- Skeletons that match the final layout for page loads; spinners only inside
  buttons or small areas. Don't show a loader for anything under ~300ms.
- Optimistic updates for low-risk actions (status change, rename) with undo
  toast; roll back with an error toast if the server fails.
- Autosave + quiet "Saved" indicator for editors; explicit Save button for
  settings forms with a sticky save bar when dirty ("You have unsaved changes ·
  Discard · Save").
- Errors: say what happened, why, and what to do next. Inline errors under the
  field; page-level errors in a banner; keep user input intact.
- Destructive actions: confirmation dialog that names the object; for
  irreversible high-impact ones, type-to-confirm ("Type the project name to
  delete") (GitHub, Vercel). Prefer undo over confirm for reversible actions.

## Forms

- Single column; labels above inputs; helper text below; mark optional fields,
  not required ones.
- Group into titled sections; long forms → wizard/stepper with progress.
- Smart defaults, autofill, input masks; validate on blur, not on every keystroke.
- Primary button names the outcome ("Create project", not "Submit"). Right-aligned
  in dialogs, left-aligned at the end of page forms.

## Settings

- Two-level structure: settings sidebar (Account · Workspace · Members ·
  Billing · Integrations · API · Security) and content pages.
- Each setting = label + description + control in a row; group with section
  headers; dangerous settings in a red-bordered "Danger zone" at the bottom.
- Members page: table of people with role dropdown, pending invites section,
  "Invite" button opening a modal that accepts multiple emails + role.
- Roles & permissions: matrix or role cards with a plain-language summary of
  what each role can do.
- API keys: show once on creation with copy button; afterwards masked
  (`sk_live_…4f2a`), with created/last-used dates and revoke.
- Audit log: filterable table of who did what, when, from where.

**Who does it best:** Vercel, Linear, GitHub, Stripe, Slack admin.

## Billing, plans & upgrades

- Current plan card: plan name, price, renewal date, usage meters with limits
  ("8,200 / 10,000 events"), "Change plan".
- Usage-based billing: show usage-to-date, projected bill, and warn at 80% and
  100%.
- Upgrade prompts in context: when the user hits a limit, show what unlocks and the
  price, with a one-click path (like Mobbin's "Download all screens · PRO" menu
  item: the locked feature stays visible with a badge, it isn't hidden).
- Plan comparison: 3 tiers, highlight the recommended one, annual toggle showing
  savings, feature table below.
- Invoices: table with date, amount, status, PDF download.

**Who does it best:** Stripe, Vercel, Linear, Paddle, Hyperline, Mobbin
(feature gating with PRO badges).

## Onboarding & activation

- Define ONE activation event (e.g. "created first project and invited 1
  teammate") and design onboarding to reach it fastest.
- Ask 1–3 intake questions (role, team size, use case) that change what the
  user gets (templates, sample data), not just the copy (Notion).
- One input per step for workspace setup; show progress and time expectation;
  allow skip (Linear).
- Never land users in an empty product: pre-populate with editable templates or
  sample data (Notion), or an active space (Slack's default channels plus a bot
  already posting).
- Onboarding checklist lives in the sidebar or a dismissible card, not a modal
  (Notion). 3–6 items, each linking straight to the action, auto-ticking.
- Invite teammates right after the first moment of value; admins see
  accepted vs. pending invites.
- Product tours: short, contextual, skippable; prefer empty-state teaching and
  tooltips on first use over 8-step modals.

**Who does it best:** Notion, Linear, Slack, Loom, Figma, Attio.

## Dashboards & analytics

- Top-left = the North Star metric. Then supporting KPIs in a row of stat
  tiles (value, delta vs. previous period with arrow + color, sparkline).
- Below: trend chart, then breakdown tables. Every widget links to its detail
  view.
- Global date picker + compare-to-previous toggle.
- Role-based or customizable layouts (drag widgets, saved dashboards) for
  mixed audiences (Stripe).
- Include a "next best action" or tasks widget so the dashboard drives work.

**Who does it best:** Stripe, Vercel analytics, PostHog, Plausible, Linear
insights, Hyperline.

## Notifications & inbox

- In-app inbox for things that need action (mentions, assignments, approvals),
  with read/unread, snooze, and "mark all read". Toasts only for feedback on the
  user's own actions.
- Toasts: bottom (center or right), 4–6s, with Undo when possible; stack, don't
  overlap.
- Granular notification settings per channel (in-app, email, Slack) and per
  event type.

**Who does it best:** Linear inbox, GitHub notifications, Slack.

## Collaboration

- Presence avatars in header; avatar group with +N overflow.
- Comments anchored to objects (and to text selections in editors) with
  threads, @mentions, resolve.
- Share dialog: invite by email with role, link access level, copy link.
- Activity timeline on detail pages: field changes and comments interleaved.

**Who does it best:** Figma, Notion, Linear, Google Docs.

## AI features in B2B products

- Put AI inside the workflow, not in a floating chat widget bolted on. Example:
  Attio's "Ask Attio" inside the record view explains data and suggests next
  actions.
- Inline actions on selected content (summarize, rewrite, extract) via a
  floating toolbar or `/` command.
- Ghost-text suggestions accepted with Tab, ignored by typing (Atlassian, Gmail
  Smart Compose).
- Generation state: stream output, show what the AI is doing ("Reading 12
  issues…"), allow Stop.
- Always reviewable: accept / reject / edit / undo for AI changes; show diffs
  for edits to existing content.
- Show sources/citations for answers built from user data; label AI-generated
  content.
- Prompt input: multiline, attach context (@mention objects/files), suggested
  prompts in the empty state.
- Agents acting in the product (Linear's agent integrations): show them as
  assignees/actors with clear activity logs, so humans can audit and take over.

**Who does it best:** Attio, Notion AI, Linear (agents), GitHub Copilot,
Cursor, Intercom Fin.

## Mobile app patterns (Mobbin's core strength)

- Bottom tab bar with 3–5 destinations; primary action in reach of the thumb.
- **Map + bottom sheet** (Uber, Waymo, Google Maps): map is context; the sheet
  holds the task, at three heights (peek / half / full). Search field
  ("Where to?") at the top of the sheet; recent and saved places below; chips
  for quick options (time slots, "Pick-up ASAP").
- Status-forward screens for live processes (ride, delivery): big ETA headline
  ("19 min to pick-up"), timeline of steps, single primary action.
- Large, bold headlines (iOS large title style); generous touch targets ≥44pt.
- Sheets and modals over full-page pushes for quick tasks; swipe actions on
  list rows.
- Onboarding: permission requests in context with a pre-prompt explaining why.
- Paywalls: show value first (what you get), plan options with the recommended
  one preselected, clear trial terms, restore purchases link.

**Who does it best:** Waymo, Uber, Airbnb, Revolut, Duolingo, Headspace,
Apple's own apps.

## Marketing site patterns (B2B landing pages)

- Hero: outcome-led headline, one-line subhead, primary CTA + secondary
  ("Book demo"), product screenshot or video, logo bar.
- Bento grids for feature overviews; real product UI over illustrations.
- Social proof with specific numbers and named customers; pricing with an annual
  toggle; FAQ to handle objections; changelog as a trust signal (Linear).

**Who does it best:** Linear, Vercel, Stripe, Raycast, Attio, Resend.
