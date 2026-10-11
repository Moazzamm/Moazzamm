# Sources & live access

## Where this playbook comes from (researched Oct 2026)

Primary sources (the companies themselves):
- Linear: "A calmer interface for a product in motion" (Mar 2026 refresh):
  https://linear.app/now/behind-the-latest-design-refresh
- Linear: "How we redesigned the Linear UI (part II)" (LCH theming, density,
  Inter Display): https://linear.app/now/how-we-redesigned-the-linear-ui
- Shopify Polaris empty state:
  https://shopify.dev/docs/api/app-home/latest/web-components/feedback-and-status-indicators/empty-state.md
- Stripe Apps empty state pattern: https://docs.stripe.com/stripe-apps/patterns/empty-state.md
- Mobbin pricing (Pro includes MCP + downloads): https://mobbin.com/pricing.md

Inspiration libraries and secondary analysis:
- SaaSFrame (B2B SaaS screens, flows, and ~100 pattern categories):
  https://www.saasframe.io and its 2026 dashboard anatomy article
- SaaSUI pattern library: https://www.saasui.design
- Atlassian on AI UX patterns: https://www.atlassian.com/blog/developer/ai-user-experience-patterns
- 925studios / UXMagic write-ups on onboarding and empty states (secondary, treat
  as directional)

Also good to browse when you need more examples: Mobbin (mobile + web apps,
flows), SaaSFrame, Page Flows, Refero, saaspo (SaaS landing pages),
Godly, Land-book, and the design systems Primer (GitHub), Polaris (Shopify),
Atlassian Design System, Carbon (IBM), Geist (Vercel), Radix / shadcn/ui.

## Giving Claude live Mobbin access

Mobbin's library is behind a login, so this playbook is built from public
sources. For live screens, connect the **Mobbin MCP** (included in Mobbin Pro
and Team plans; https://mobbin.com/mcp). Once it's connected, Claude can search
real screens and flows for any pattern before answering.

In a cloud session, the environment's network policy must allow Mobbin's MCP
host. Downloading files from Google Drive over 10 MB doesn't work from cloud
sessions: share individual screens (PNG/JPG < 10 MB each) instead of large PDFs.
