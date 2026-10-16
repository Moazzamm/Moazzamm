(() => {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const icon = (id) => `<svg class="icon" aria-hidden="true"><use href="#${id}"/></svg>`;

  /* ---------------------------------------------------------------
     Header: scrolled state, current section, mobile menu
     --------------------------------------------------------------- */
  const header = $("[data-header]");
  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
      ticking = false;
    });
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  const navLinks = $$(".nav-list a");
  if ("IntersectionObserver" in window) {
    const byId = new Map(navLinks.map((a) => [a.getAttribute("href").slice(1), a]));
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navLinks.forEach((a) => a.classList.remove("is-current"));
        const link = byId.get(entry.target.id);
        if (link) link.classList.add("is-current");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    byId.forEach((_, id) => { const el = document.getElementById(id); if (el) spy.observe(el); });
    const top = document.getElementById("top");
    if (top) spy.observe(top);
  }

  const menuToggle = $("[data-menu-toggle]");
  const menu = $("#mobile-menu");
  const menuLabel = $("[data-menu-label]");
  const setMenu = (open) => {
    menu.hidden = !open;
    menuToggle.setAttribute("aria-expanded", String(open));
    menuLabel.textContent = open ? "Close menu" : "Open menu";
    menuToggle.querySelector("use").setAttribute("href", open ? "#i-close" : "#i-menu");
    document.documentElement.style.overflow = open ? "hidden" : "";
  };
  menuToggle.addEventListener("click", () => setMenu(menu.hidden));
  menu.addEventListener("click", (e) => { if (e.target.closest("a, button")) setMenu(false); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !menu.hidden) { setMenu(false); menuToggle.focus(); }
  });
  window.matchMedia("(min-width: 1001px)").addEventListener("change", (e) => { if (e.matches) setMenu(false); });

  /* ---------------------------------------------------------------
     Scaled product mockups (designed in fixed px, fitted to width)
     --------------------------------------------------------------- */
  const figure = $("[data-hero-figure]");
  const app = $("[data-app]");
  const phoneWrap = $("[data-phone-wrap]");

  const fitHero = () => {
    const W = figure.clientWidth;
    if (!W) return;
    const compact = W < 700;
    app.classList.toggle("is-compact", compact);
    const designW = compact ? 984 : 1200;
    let appX, s, ps, phX, phY;
    if (!compact) {
      appX = W * 0.07;
      s = (W - appX) / designW;
      ps = Math.max(s * 0.98, 0.56);
      phX = 0;
      phY = 720 * s * 0.38;
    } else {
      appX = 0;
      s = W / designW;
      ps = Math.min(Math.max(s * 1.35, 0.5), 0.72);
      phX = W - 264 * ps;
      phY = 720 * s * 0.52;
    }
    const phoneH = phoneWrap.offsetHeight * ps;
    const figH = Math.max(720 * s, phY + phoneH);
    figure.style.setProperty("--s", s.toFixed(4));
    figure.style.setProperty("--app-x", appX.toFixed(1));
    figure.style.setProperty("--ps", ps.toFixed(4));
    figure.style.setProperty("--ph-x", phX.toFixed(1));
    figure.style.setProperty("--ph-y", phY.toFixed(1));
    figure.style.setProperty("--fig-h", Math.ceil(figH));
    figure.classList.add("is-fitted");
  };

  const fitBlocks = () => {
    $$("[data-fit]").forEach((el) => {
      const dw = Number(el.dataset.fit);
      const dh = Number(el.dataset.fitHeight);
      const s = el.clientWidth / dw;
      el.style.setProperty("--s", s.toFixed(4));
      el.style.setProperty("--fit-h", Math.ceil(dh * s));
    });
  };

  const fitAll = () => { fitHero(); fitBlocks(); };
  fitAll();
  if ("ResizeObserver" in window) {
    const ro = new ResizeObserver(fitAll);
    ro.observe(figure);
    $$("[data-fit]").forEach((el) => ro.observe(el));
  } else {
    window.addEventListener("resize", fitAll);
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitAll);

  /* ---------------------------------------------------------------
     Hero: typed prompt, then a single pass linking each citation
     to the element it explains. Hover does the same afterwards.
     --------------------------------------------------------------- */
  const promptText = $(".prompt-text");
  if (!reduced && promptText) {
    const full = promptText.dataset.type;
    promptText.textContent = "";
    promptText.classList.add("is-typing");
    let i = 0;
    const type = () => {
      i += 1;
      promptText.textContent = full.slice(0, i);
      if (i < full.length) setTimeout(type, 11 + Math.random() * 14);
      else setTimeout(() => promptText.classList.remove("is-typing"), 1200);
    };
    setTimeout(type, 450);
  }

  const linkCite = (n) => {
    $$(".is-linked", app).forEach((el) => el.classList.remove("is-linked"));
    if (!n) return;
    $$(`[data-cite-item="${n}"], [data-cite-target="${n}"]`, app).forEach((el) => el.classList.add("is-linked"));
  };
  let tour = null;
  const stopTour = () => { if (tour) { clearTimeout(tour); tour = null; } };
  app.addEventListener("pointerover", (e) => {
    const item = e.target.closest("[data-cite-item], [data-cite-target]");
    stopTour();
    linkCite(item ? (item.dataset.citeItem || item.dataset.citeTarget) : null);
  });
  app.addEventListener("pointerleave", () => linkCite(null));
  if (!reduced) {
    const seq = ["1", "2", "3", "4", null];
    let k = 0;
    const step = () => {
      linkCite(seq[k]);
      k += 1;
      if (k < seq.length) tour = setTimeout(step, 1100);
      else tour = null;
    };
    tour = setTimeout(step, 3300);
  }

  /* Hero phone prototype */
  const proto = $("[data-proto]");
  const pscreens = $$(".pscreen", proto);
  const protoLive = $("[data-proto-live]");
  let pIndex = 0;
  proto.setAttribute("data-hint", "");
  proto.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-proto-next]");
    if (!btn) return;
    proto.removeAttribute("data-hint");
    const hadFocus = document.activeElement === btn;
    const prev = pscreens[pIndex];
    pIndex = (pIndex + 1) % pscreens.length;
    const next = pscreens[pIndex];
    prev.classList.add("is-leaving");
    prev.classList.remove("is-active");
    setTimeout(() => prev.classList.remove("is-leaving"), 380);
    next.classList.add("is-active");
    protoLive.textContent = `Screen: ${next.getAttribute("aria-label")}`;
    if (hadFocus) next.querySelector("[data-proto-next]").focus({ preventScroll: true });
  });

  /* ---------------------------------------------------------------
     Tabs (ARIA tabs pattern, arrow keys in both orientations)
     --------------------------------------------------------------- */
  const initTabs = (tablist, onChange) => {
    const tabs = $$('[role="tab"]', tablist);
    const select = (tab, focus) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        const panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
      if (onChange) onChange(tab);
    };
    tablist.addEventListener("click", (e) => {
      const t = e.target.closest('[role="tab"]');
      if (t) select(t, false);
    });
    tablist.addEventListener("keydown", (e) => {
      const i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      let n = null;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") n = (i + 1) % tabs.length;
      if (e.key === "ArrowLeft" || e.key === "ArrowUp") n = (i - 1 + tabs.length) % tabs.length;
      if (e.key === "Home") n = 0;
      if (e.key === "End") n = tabs.length - 1;
      if (n !== null) { e.preventDefault(); select(tabs[n], true); }
    });
    return { select, tabs };
  };

  /* ---------------------------------------------------------------
     Interactive demo
     --------------------------------------------------------------- */
  const DEMO = {
    clinic: {
      name: "Clinic booking",
      platform: "mobile",
      brand: "#2E6E8E",
      sources: ["Booking PRD", "Patient interviews (12)", "Reception call log"],
      researchNote: "from 12 patient interviews and a reception call log",
      problem: "Patients think about rebooking outside clinic hours, so changes turn into phone calls, or into no-shows.",
      question: "Do patients want to see the price before they choose a therapist?",
      insights: [
        { title: "Rebooking happens the night before", quote: "“I only remember to move it when the reminder comes in at eight.”", src: "Patient interview, P3", use: "Reschedule from the reminder" },
        { title: "Patients want the same therapist", quote: "“I’d rather wait two days than explain my knee to someone new.”", src: "Patient interview, P8", use: "Therapist is chosen first" },
        { title: "Fees stop people from cancelling", quote: "“Most no-shows say they didn’t know if cancelling would cost them.”", src: "Reception call log, week 3", use: "Fee shown before confirming" }
      ],
      flow: ["Open reminder", "Choose therapist", "Pick a time", "Review fee policy", "Confirm booking"],
      gap: { at: 2, title: "No free slots this week.", text: "The brief doesn’t say what happens when a therapist is fully booked.", button: "Add a waitlist step", node: "Join waitlist" },
      screens: [
        { name: "Choose therapist", blocks: [
          { t: "bar", text: "Who would you like to see?" },
          { t: "person", name: "Amara Okafor", meta: "Your last 4 sessions", on: true },
          { t: "person", name: "Jonah Reyes", meta: "Next free Thursday" },
          { t: "note", text: "Staying with one therapist keeps your plan in one place." },
          { t: "btn", text: "Choose a time" }
        ] },
        { name: "Pick a time", blocks: [
          { t: "bar", text: "Pick a time" },
          { t: "muted", text: "With Amara Okafor" },
          { t: "chips", items: ["Mon 13", "Tue 14", "Wed 15", "Thu 16"], on: 1 },
          { t: "chips", items: ["08:30", "10:00", "12:30", "17:45"], on: 3 },
          { t: "note", text: "Free to move until 24 hours before." },
          { t: "btn", text: "Review booking" }
        ] },
        { name: "Review booking", blocks: [
          { t: "bar", text: "Review booking" },
          { t: "rows", items: [["Therapist", "Amara Okafor"], ["When", "Tue 14 Oct, 17:45"], ["Where", "Room 2, Canal St"]] },
          { t: "note", warn: true, text: "Cancelling within 24 hours costs $15." },
          { t: "btn", text: "Confirm booking" }
        ] }
      ],
      done: { title: "You’re booked", text: "We’ll remind you Monday at 8 pm, with a link to move it." }
    },
    expenses: {
      name: "Expense approvals",
      platform: "web",
      brand: "#1F5F7A",
      sources: ["Approvals PRD", "Manager interviews (6)", "Expense policy"],
      researchNote: "from 6 manager interviews and the expense policy",
      problem: "Managers clear approvals in one weekly sitting and find policy problems after the money has gone.",
      question: "Should expenses over $1,000 need a second approver?",
      insights: [
        { title: "Problems surface after approval", quote: "“I usually find the policy issue after I’ve already approved it.”", src: "Manager interview, M2", use: "Policy flags in the list" },
        { title: "Approvals happen in one sitting", quote: "“Friday afternoon is when I clear the whole queue.”", src: "Manager interview, M5", use: "Approve clean expenses together" },
        { title: "Receipts slow everything down", quote: "“Opening every receipt is what takes the time.”", src: "Manager interview, M1", use: "Receipt beside the row" }
      ],
      flow: ["Open approvals", "Review flagged", "Check receipt", "Approve or return", "Notify employee"],
      gap: { at: 3, title: "Partial approval.", text: "The policy allows approving part of an expense, but the brief has no step for it.", button: "Add a partial approval step", node: "Approve part" },
      screens: [
        { name: "Approval queue", blocks: [
          { t: "bar", text: "Approvals" },
          { t: "tabs", items: ["To review 12", "Flagged 3", "Done"], on: 0 },
          { t: "table", items: [["Hotel, Lisbon", "$712", "Over limit"], ["Team lunch", "$186", ""], ["Taxi", "$48", "No receipt"]] },
          { t: "btn", text: "Review 3 flagged" }
        ] },
        { name: "Expense detail", blocks: [
          { t: "bar", text: "Hotel, Lisbon" },
          { t: "muted", text: "Priya N., 2 nights" },
          { t: "rows", items: [["Amount", "$712.00"], ["Limit", "$600.00"], ["Over by", "$112.00"]] },
          { t: "btns", items: [{ text: "Approve anyway", quiet: true }, { text: "Return with note" }] }
        ] },
        { name: "Return with note", blocks: [
          { t: "bar", text: "Return to Priya" },
          { t: "chips", items: ["Over limit", "Missing receipt", "Wrong category"], on: 0 },
          { t: "field", label: "Note", value: "Please move the extra night to your own card." },
          { t: "btn", text: "Send back" }
        ] }
      ],
      done: { title: "Returned to Priya", text: "She gets your note and can resubmit from her phone." }
    },
    api: {
      name: "API onboarding",
      platform: "web",
      brand: "#8A3B5E",
      sources: ["Onboarding PRD", "Session recordings (20)", "Support tickets"],
      researchNote: "from 20 session recordings and support tickets",
      problem: "New developers lose their first session hunting for a key and pasting a sample that fails.",
      question: "Which language should the first sample show to someone arriving from search?",
      insights: [
        { title: "Keys are hard to find", quote: "“I had the docs open but no idea where my key lived.”", src: "Session recording, R7", use: "Create a key in step one" },
        { title: "Developers copy the first sample", quote: "“Whatever code is on screen first, I paste it.”", src: "Developer interview, D3", use: "Language chosen before the sample" },
        { title: "The first error ends the session", quote: "“401 Unauthorized” is the most common first response in tickets.", src: "Support tickets, March", use: "Test key filled into the sample" }
      ],
      flow: ["Sign up", "Create test key", "Choose language", "Run first request", "See response"],
      gap: { at: 3, title: "First request fails.", text: "There is no plan for a first request that returns an error.", button: "Add an error recovery step", node: "Fix and retry" },
      screens: [
        { name: "Create a key", blocks: [
          { t: "bar", text: "Create your first key" },
          { t: "field", label: "Key name", value: "local-testing" },
          { t: "chips", items: ["Test mode", "Live mode"], on: 0 },
          { t: "note", text: "Test keys never move real money." },
          { t: "btn", text: "Create key" }
        ] },
        { name: "First request", blocks: [
          { t: "bar", text: "Make your first request" },
          { t: "chips", items: ["curl", "Node", "Python"], on: 1 },
          { t: "code", html: "const pay = new Paylane(\"sk_test_4eC…\");\nawait pay.charges.create({\n  amount: 2000,\n  currency: \"usd\"\n});" },
          { t: "btn", text: "Run request" }
        ] },
        { name: "It worked", blocks: [
          { t: "bar", text: "It worked" },
          { t: "code", html: "<span class=\"ok\">200 OK</span>\n{\n  \"id\": \"ch_3Pq…\",\n  \"status\": \"succeeded\"\n}" },
          { t: "note", text: "Your test charge is in the dashboard." },
          { t: "btn", text: "Go to dashboard" }
        ] }
      ],
      done: { title: "You’re set up", text: "Switch to a live key when you’re ready to take payments." }
    }
  };

  const initials = (name) => name.split(" ").map((p) => p[0]).join("");

  const renderBlock = (b, interactive) => {
    switch (b.t) {
      case "bar": return `<p class="b-bar">${b.text}</p>`;
      case "muted": return `<p class="b-muted">${b.text}</p>`;
      case "person": return `<div class="b-person${b.on ? " is-on" : ""}"><i>${initials(b.name)}</i><div><b>${b.name}</b><small>${b.meta}</small></div></div>`;
      case "chips": return `<div class="b-chips">${b.items.map((x, i) => `<span class="${i === b.on ? "is-on" : ""}">${x}</span>`).join("")}</div>`;
      case "note": return `<p class="b-note${b.warn ? " b-note--warn" : ""}">${b.text}</p>`;
      case "rows": return `<div class="b-rows">${b.items.map(([k, v]) => `<p><span>${k}</span><span>${v}</span></p>`).join("")}</div>`;
      case "field": return `<div class="b-field"><span>${b.label}</span><b>${b.value}</b></div>`;
      case "code": return `<pre class="b-code">${b.html}</pre>`;
      case "tabs": return `<div class="b-tabs">${b.items.map((x, i) => `<span class="${i === b.on ? "is-on" : ""}">${x}</span>`).join("")}</div>`;
      case "table": return `<div class="b-table">${b.items.map(([n, a, f]) => `<p><span>${n}</span><span>${a}</span>${f ? `<em>${f}</em>` : `<em class="ok">OK</em>`}</p>`).join("")}</div>`;
      case "btn": return interactive
        ? `<button type="button" class="b-btn" data-demo-next>${b.text}</button>`
        : `<span class="b-btn">${b.text}</span>`;
      case "btns": return `<div class="b-btn-row">${b.items.map((x) => x.quiet
        ? `<span class="b-btn b-btn--quiet">${x.text}</span>`
        : interactive ? `<button type="button" class="b-btn" data-demo-next>${x.text}</button>` : `<span class="b-btn">${x.text}</span>`).join("")}</div>`;
      default: return "";
    }
  };

  const renderScreen = (brief, screen, opts = {}) => {
    const cls = `scr scr--${brief.platform}${opts.large ? " scr--lg" : ""}`;
    return `<div class="${cls}" style="--brand:${brief.brand}">${screen.blocks.map((b) => renderBlock(b, opts.interactive)).join("")}</div>`;
  };

  const renderDone = (brief, opts = {}) => {
    const cls = `scr scr--${brief.platform}${opts.large ? " scr--lg" : ""}`;
    return `<div class="${cls}" style="--brand:${brief.brand}"><div class="b-done"><i>${icon("i-check")}</i><b>${brief.done.title}</b><span>${brief.done.text}</span></div></div>`;
  };

  const panels = {
    research: $('[data-panel="research"]'),
    flow: $('[data-panel="flow"]'),
    screens: $('[data-panel="screens"]'),
    proto: $('[data-panel="proto"]')
  };
  const demoName = $("[data-demo-name]");
  const demoLive = $("[data-demo-live]");
  const demoStage = $("[data-demo-stage]");
  const progress = $("[data-demo-progress]");
  const sourcesList = $("[data-brief-sources]");
  const briefCurrent = $("[data-brief-current]");
  let current = "clinic";
  let protoIndex = 0;
  let gapAdded = false;

  const renderResearch = (brief) => {
    panels.research.innerHTML = `
      <p class="panel-caption"><span><b>3 insights</b> ${brief.researchNote}</span><span>Highlighted lines are cited in the design</span></p>
      <div class="research-problem"><p class="rp-label">Problem statement, drafted from your sources</p><p class="rp-text">${brief.problem}</p></div>
      <div class="insights">${brief.insights.map((x) => `
        <article class="insight">
          <p class="insight-title">${x.title}</p>
          <p class="insight-quote"><mark>${x.quote}</mark></p>
          <p class="insight-src">${icon("i-doc")}${x.src}</p>
          <p class="insight-use">Shapes <b>${x.use}</b></p>
        </article>`).join("")}
      </div>
      <p class="research-question">${icon("i-alert")}<span><b>Not covered by your sources.</b> ${brief.question} Forma will mark related decisions as assumptions.</span></p>`;
  };

  const renderFlow = (brief) => {
    const steps = brief.flow.slice();
    if (gapAdded) steps.splice(brief.gap.at, 0, brief.gap.node);
    panels.flow.innerHTML = `
      <p class="panel-caption"><span><b>User flow</b> ${steps.length} steps</span><span>${gapAdded ? "Gap resolved" : "1 gap found in the brief"}</span></p>
      <div class="flow-wrap">
      <ol class="flow">${steps.map((s, i) => `
        <li class="flow-node${gapAdded && i === brief.gap.at ? " is-new" : ""}${!gapAdded && i === brief.gap.at - 1 ? " has-gap" : ""}">${s}</li>`).join("")}
      </ol>
      <div class="flow-aside">
      <div class="flow-gap">
        ${icon("i-alert")}
        <p class="flow-gap-text">${gapAdded
          ? `<b>Added “${brief.gap.node}”.</b> Forma will draft its screen with your library.`
          : `<b>Gap: ${brief.gap.title}</b> ${brief.gap.text}`}</p>
        <button type="button" class="app-chip-btn" data-add-gap ${gapAdded ? "disabled" : ""}>${gapAdded ? `${icon("i-check")}Added to flow` : `${icon("i-plus")}${brief.gap.button}`}</button>
      </div>
      <p class="flow-legend"><span><i></i>Prototype link</span><span>Numbers show step order</span></p>
      </div>
      </div>`;
  };

  const renderScreens = (brief) => {
    panels.screens.innerHTML = `
      <p class="panel-caption"><span><b>${brief.screens.length} screens</b> composed from your component library</span><span>Scroll to pan</span></p>
      <div class="screens-row">${brief.screens.map((s, i) => `
        ${i > 0 ? `<span class="screen-link" aria-hidden="true"></span>` : ""}
        <div class="screen-item"><p class="screen-label">${i + 1}. ${s.name}</p>${renderScreen(brief, s)}</div>`).join("")}
      </div>`;
  };

  const renderProto = (brief, focus) => {
    const total = brief.screens.length;
    const isDone = protoIndex >= total;
    const frame = isDone ? renderDone(brief, { large: true, interactive: true }) : renderScreen(brief, brief.screens[protoIndex], { large: true, interactive: true });
    panels.proto.innerHTML = `
      <div class="proto-stage">
        <div class="proto-frame">${frame}</div>
        <div class="proto-side">
          <p class="proto-step">${isDone ? "Finished" : `Screen ${protoIndex + 1} of ${total}`}</p>
          <p class="proto-name">${isDone ? brief.done.title : brief.screens[protoIndex].name}</p>
          <p class="proto-help">${isDone ? "That’s the whole flow. Testers see exactly this from a shared link." : "Click the highlighted button to move through the flow, the way a tester would."}</p>
          <div class="proto-dots" aria-hidden="true">${brief.screens.map((_, i) => `<i class="${i <= protoIndex ? "is-on" : ""}"></i>`).join("")}<i class="${isDone ? "is-on" : ""}"></i></div>
          ${isDone ? `<div class="proto-cta"><p>Want this for your own product? Start with a sentence about it.</p><button type="button" class="app-chip-btn" data-open-signup>Start designing</button></div>` : ""}
          <button type="button" class="proto-restart" data-demo-restart>Restart prototype</button>
        </div>
      </div>`;
    if (focus) {
      const target = panels.proto.querySelector("[data-demo-next]") || panels.proto.querySelector(".proto-cta .app-chip-btn");
      if (target) target.focus({ preventScroll: true });
    }
  };

  const renderAll = (key) => {
    const brief = DEMO[key];
    renderResearch(brief);
    renderFlow(brief);
    renderScreens(brief);
    renderProto(brief, false);
  };

  const renderBriefMeta = (key) => {
    const brief = DEMO[key];
    demoName.textContent = brief.name;
    sourcesList.innerHTML = brief.sources.map((s) => `<li>${icon("i-doc")}${s}</li>`).join("");
    const checked = $(`[data-briefs] input[value="${key}"]`);
    briefCurrent.textContent = checked ? checked.closest(".brief").querySelector(".brief-text").textContent : "";
  };

  const visiblePanel = () => Object.values(panels).find((p) => !p.hidden);
  const animatePanel = (panel) => {
    if (reduced || !panel) return;
    panel.classList.remove("is-entering");
    void panel.offsetWidth;
    panel.classList.add("is-entering");
  };

  let genToken = 0;
  const generate = async (key, instant) => {
    const token = ++genToken;
    current = key;
    protoIndex = 0;
    gapAdded = false;
    renderBriefMeta(key);
    if (instant || reduced) {
      renderAll(key);
      if (!instant) demoLive.textContent = `Generated ${DEMO[key].name}.`;
      return;
    }
    const steps = $$("li", progress);
    steps.forEach((li) => li.classList.remove("is-active", "is-done"));
    progress.hidden = false;
    demoStage.setAttribute("aria-busy", "true");
    demoLive.textContent = `Generating ${DEMO[key].name}.`;
    for (const li of steps) {
      li.classList.add("is-active");
      await wait(360);
      if (token !== genToken) return;
      li.classList.remove("is-active");
      li.classList.add("is-done");
    }
    await wait(160);
    if (token !== genToken) return;
    renderAll(key);
    progress.hidden = true;
    demoStage.removeAttribute("aria-busy");
    animatePanel(visiblePanel());
    demoLive.textContent = `${DEMO[key].name} is ready: research, flow, ${DEMO[key].screens.length} screens, and a prototype.`;
  };

  initTabs($(".demo [data-tabs]"), () => animatePanel(visiblePanel()));

  $("[data-briefs]").addEventListener("change", (e) => {
    if (e.target.name === "brief") generate(e.target.value, false);
  });

  panels.flow.addEventListener("click", (e) => {
    if (!e.target.closest("[data-add-gap]") || gapAdded) return;
    gapAdded = true;
    renderFlow(DEMO[current]);
    const btn = panels.flow.querySelector("[data-add-gap]");
    const node = panels.flow.querySelector(".flow-node.is-new");
    if (node && !reduced) node.animate([{ opacity: 0, transform: "scale(0.9)" }, { opacity: 1, transform: "none" }], { duration: 320, easing: "cubic-bezier(.2,.7,.2,1)" });
    if (btn) btn.focus({ preventScroll: true });
    demoLive.textContent = `Added ${DEMO[current].gap.node} to the flow.`;
  });

  panels.proto.addEventListener("click", (e) => {
    const brief = DEMO[current];
    if (e.target.closest("[data-demo-next]")) {
      protoIndex = Math.min(protoIndex + 1, brief.screens.length);
      renderProto(brief, true);
      demoLive.textContent = protoIndex >= brief.screens.length ? brief.done.title : `Screen ${protoIndex + 1}: ${brief.screens[protoIndex].name}`;
    } else if (e.target.closest("[data-demo-restart]")) {
      protoIndex = 0;
      renderProto(brief, true);
      demoLive.textContent = `Restarted. Screen 1: ${brief.screens[0].name}`;
    }
  });

  generate("clinic", true);

  /* ---------------------------------------------------------------
     Feature: prototype states
     --------------------------------------------------------------- */
  const stateSeg = $("[data-state-seg]");
  stateSeg.addEventListener("change", (e) => {
    const v = e.target.value;
    $$("[data-state-view]").forEach((el) => { el.hidden = el.dataset.stateView !== v; });
  });

  /* ---------------------------------------------------------------
     Before and after slider
     --------------------------------------------------------------- */
  const ba = $("[data-ba]");
  const baRange = $("[data-ba-range]");
  const setPos = (v) => ba.style.setProperty("--pos", `${v}%`);
  baRange.addEventListener("input", () => setPos(baRange.value));
  let dragging = false;
  const fromPointer = (e) => {
    const r = ba.getBoundingClientRect();
    const v = Math.min(100, Math.max(0, ((e.clientX - r.left) / r.width) * 100));
    baRange.value = Math.round(v);
    setPos(v.toFixed(2));
  };
  baRange.addEventListener("pointerdown", (e) => {
    dragging = true;
    try { baRange.setPointerCapture(e.pointerId); } catch (_) { /* not capturable */ }
    fromPointer(e);
  });
  baRange.addEventListener("pointermove", (e) => { if (dragging) fromPointer(e); });
  const endDrag = () => { dragging = false; };
  baRange.addEventListener("pointerup", endDrag);
  baRange.addEventListener("pointercancel", endDrag);
  setPos(baRange.value);

  // One gentle sweep the first time the comparison is in view, so it reads as draggable.
  let touched = false;
  ["pointerdown", "keydown"].forEach((ev) => baRange.addEventListener(ev, () => { touched = true; }));
  if (!reduced && "IntersectionObserver" in window) {
    const peek = new IntersectionObserver((entries) => {
      if (!entries[0].isIntersecting) return;
      peek.disconnect();
      const keys = [[0, 50], [520, 34], [1180, 64], [1700, 50]];
      const start = performance.now();
      const ease = (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
      const frame = (now) => {
        if (touched) return;
        const t = now - start;
        let i = 0;
        while (i < keys.length - 2 && t > keys[i + 1][0]) i += 1;
        const [t0, v0] = keys[i];
        const [t1, v1] = keys[i + 1];
        const p = Math.min(1, Math.max(0, (t - t0) / (t1 - t0)));
        const v = v0 + (v1 - v0) * ease(p);
        setPos(v.toFixed(2));
        baRange.value = Math.round(v);
        if (t < keys[keys.length - 1][0]) requestAnimationFrame(frame);
      };
      setTimeout(() => requestAnimationFrame(frame), 250);
    }, { threshold: 0.6 });
    peek.observe(ba);
  }

  /* ---------------------------------------------------------------
     Use cases
     --------------------------------------------------------------- */
  initTabs($(".usecases [data-tabs]"));

  /* ---------------------------------------------------------------
     Pricing
     --------------------------------------------------------------- */
  const billing = $("[data-billing]");
  const getBilling = () => (billing.querySelector("input:checked") || {}).value || "yearly";
  const updatePrices = (animate) => {
    const yearly = getBilling() === "yearly";
    $$("[data-price]").forEach((el) => {
      el.textContent = `$${yearly ? el.dataset.yearly : el.dataset.monthly}`;
      if (animate && !reduced) {
        el.classList.remove("is-changing");
        void el.offsetWidth;
        el.classList.add("is-changing");
      }
    });
    $("[data-per]").textContent = yearly ? "per month, billed yearly" : "per month, billed monthly";
    $("[data-per-team]").textContent = yearly ? "per editor per month, billed yearly" : "per editor per month, billed monthly";
  };
  billing.addEventListener("change", () => updatePrices(true));
  updatePrices(false);

  /* ---------------------------------------------------------------
     FAQ accordion
     --------------------------------------------------------------- */
  $("[data-accordion]").addEventListener("click", (e) => {
    const btn = e.target.closest(".acc-btn");
    if (!btn) return;
    const open = btn.getAttribute("aria-expanded") !== "true";
    btn.setAttribute("aria-expanded", String(open));
    btn.closest(".acc").classList.toggle("is-open", open);
  });

  /* ---------------------------------------------------------------
     Sign-up dialog, reached from every "Start designing" action
     --------------------------------------------------------------- */
  const dlg = $("[data-signup]");
  const form = $("[data-signup-form]");
  const email = $("#signup-email");
  const err = $("[data-signup-error]");
  const formView = $("[data-signup-form-view]");
  const doneView = $("[data-signup-done-view]");
  const titleEl = $("[data-signup-title]");
  const subEl = $("[data-signup-sub]");
  const ctxEl = $("[data-signup-context]");
  const submitEl = $("[data-signup-submit]");
  const doneTitle = $("[data-done-title]");
  const doneText = $("[data-done-text]");
  let mode = null;
  let lastTrigger = null;

  const escapeHtml = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c]));

  const MODES = {
    start: { title: "Start designing with Forma", sub: "Create a free workspace. Your first three projects are included.", submit: "Create workspace", doneTitle: "Check your inbox", done: (m) => `We sent a link to ${m}. Open it to start your first project.` },
    idea: { title: "Start designing with Forma", sub: "Create a free workspace and we’ll open this brief as your first project.", submit: "Create workspace", doneTitle: "Check your inbox", done: (m) => `We sent a link to ${m}. Your brief will be waiting as your first project.` },
    plan: { title: "", sub: "", submit: "", doneTitle: "Check your inbox", done: (m) => `We sent a link to ${m}. Open it to set up your workspace.` },
    signin: { title: "Sign in to Forma", sub: "We’ll email you a secure sign-in link.", submit: "Email me a sign-in link", doneTitle: "Sign-in link sent", done: (m) => `Open the link we sent to ${m} on this device to sign in.` },
    sales: { title: "Talk to us about Enterprise", sub: "Leave your work email and we’ll reply within one business day to find a time.", submit: "Send request", doneTitle: "Request sent", done: (m) => `We’ll write to ${m} within one business day.` }
  };

  const openSignup = (opts) => {
    mode = MODES[opts.mode] || MODES.start;
    let title = mode.title;
    let sub = mode.sub;
    let submit = mode.submit;
    ctxEl.hidden = true;
    ctxEl.innerHTML = "";
    if (opts.mode === "plan") {
      const yearly = getBilling() === "yearly";
      const priceEl = $(`#plan-${opts.plan.toLowerCase()}`).closest(".plan").querySelector("[data-price]");
      if (opts.plan === "Starter") {
        title = "Start designing with Forma";
        sub = "Create a free workspace. Your first three projects are included.";
        submit = "Create workspace";
      } else {
        const price = priceEl ? `$${yearly ? priceEl.dataset.yearly : priceEl.dataset.monthly}` : "";
        title = `Start your ${opts.plan} trial`;
        sub = "Every feature, free for 14 days. No card needed until you choose to upgrade.";
        submit = `Start ${opts.plan} trial`;
        ctxEl.innerHTML = `<b>Plan</b>${opts.plan}, ${price} ${opts.plan === "Team" ? "per editor " : ""}per month after the trial, billed ${yearly ? "yearly" : "monthly"}`;
        ctxEl.hidden = false;
      }
    }
    if (opts.mode === "idea" && opts.idea) {
      ctxEl.innerHTML = `<b>Your brief</b>${escapeHtml(opts.idea)}`;
      ctxEl.hidden = false;
    }
    titleEl.textContent = title;
    subEl.textContent = sub;
    submitEl.textContent = submit;
    formView.hidden = false;
    doneView.hidden = true;
    err.hidden = true;
    email.removeAttribute("aria-invalid");
    if (typeof dlg.showModal === "function") dlg.showModal();
    else dlg.setAttribute("open", "");
    email.focus();
  };

  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-open-signup]");
    if (!t) return;
    lastTrigger = t;
    const m = t.dataset.openSignup;
    if (t.dataset.plan) openSignup({ mode: "plan", plan: t.dataset.plan });
    else openSignup({ mode: m || "start" });
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const value = email.value.trim();
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);
    if (!ok) {
      err.textContent = value ? "That email address looks incomplete. Use a format like name@company.com." : "Enter your work email so we can send your link.";
      err.hidden = false;
      email.setAttribute("aria-invalid", "true");
      email.focus();
      return;
    }
    err.hidden = true;
    email.removeAttribute("aria-invalid");
    doneTitle.textContent = mode.doneTitle;
    doneText.textContent = mode.done(value);
    formView.hidden = true;
    doneView.hidden = false;
    doneTitle.focus();
  });
  email.addEventListener("input", () => {
    if (!err.hidden) { err.hidden = true; email.removeAttribute("aria-invalid"); }
  });

  dlg.addEventListener("click", (e) => {
    if (e.target === dlg || e.target.closest("[data-close-dialog]")) dlg.close();
  });
  dlg.addEventListener("close", () => {
    form.reset();
    if (lastTrigger && document.contains(lastTrigger)) lastTrigger.focus({ preventScroll: true });
  });

  const ownBrief = $("[data-own-brief]");
  ownBrief.addEventListener("submit", (e) => {
    e.preventDefault();
    lastTrigger = ownBrief.querySelector("button");
    const idea = $("#own-brief-input").value.trim();
    openSignup({ mode: idea ? "idea" : "start", idea });
  });

  const ideaForm = $("[data-idea-form]");
  ideaForm.addEventListener("submit", (e) => {
    e.preventDefault();
    lastTrigger = ideaForm.querySelector("button");
    const idea = $("#idea-input").value.trim();
    openSignup({ mode: idea ? "idea" : "start", idea });
  });

  /* ---------------------------------------------------------------
     Layout grid overlay (a designer's courtesy)
     --------------------------------------------------------------- */
  const gridBtn = $("[data-grid-toggle]");
  const gridEl = $("[data-layout-grid]");
  gridBtn.addEventListener("click", () => {
    const on = gridBtn.getAttribute("aria-pressed") !== "true";
    gridBtn.setAttribute("aria-pressed", String(on));
    gridEl.hidden = !on;
    gridBtn.lastChild.textContent = on ? "Hide layout grid" : "Show layout grid";
  });
})();
