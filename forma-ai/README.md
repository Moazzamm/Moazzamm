# Forma AI — landing page

A landing page concept for **Forma AI**, a fictional product that turns product requirements and research into user flows, interface designs, and interactive prototypes.

Static HTML, CSS, and vanilla JavaScript. No build step and no dependencies beyond two Google Fonts.

```
forma-ai/
├── index.html   markup for every section
├── styles.css   design tokens, components, sections, responsive rules
└── main.js      scaling of product mockups, demo data and renderer, all interactions
```

Run it by opening `index.html` in a browser, or serve the folder:

```sh
npx serve forma-ai
```

## Design direction

- **Concept: reasoned form.** Forma's difference is that every design decision traces back to evidence, so the page's signature device is the citation marker: a numbered highlighter-yellow tag that links a piece of UI to the interview quote or requirement behind it.
- **Palette.** Cool vellum ground, ink type, a dark editor for the product, highlighter yellow reserved for evidence, and a selection blue used only for canvas chrome, focus, and prototype links.
- **Type.** Newsreader (light, optical sizes) is the editorial voice for headlines and research quotes. Schibsted Grotesk is the product voice for UI, body copy, and controls.
- **Layout.** A 12-column grid. The hero's third line and its supporting copy share an indent axis at column 3, and the closing call to action returns to it.
- **Motion.** One orchestrated moment on load (the prompt types, the dashboard assembles, citations appear). Everything else responds to the visitor. `prefers-reduced-motion` shows the final state immediately.

## What works

- Navigation with current-section tracking and a full-screen mobile menu
- Hero editor with hover-linked citations and a clickable technician-app prototype
- Live demo: three sample briefs, each with Research, Flow, Screens, and Prototype tabs, a gap you can add to the flow, and a prototype you can step through
- A prototype-state switcher (default, loading, empty, error)
- A before-and-after comparison slider (pointer, touch, and keyboard)
- Use-case tabs, monthly and yearly pricing, a plan comparison table, and a FAQ accordion
- A sign-up dialog reached from every "Start designing" action. It carries the chosen plan or the visitor's idea, validates the email, and confirms
- A "Show layout grid" overlay in the footer

## Tokens

All colors, type sizes, spacing, radii, shadows, and motion timings are defined as custom properties at the top of `styles.css`. Product mockups are drawn at fixed design sizes and scaled to fit (`data-fit` and the hero's fit routine in `main.js`), so they keep their proportions at every width.
