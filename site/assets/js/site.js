// Quick Dungeon: progressive enhancement. Every page is complete without this script;
// it adds the home-page search, the route-map stepper and the copy-to-chat buttons.
document.documentElement.classList.add("js");

const announcer = () => document.getElementById("announcer");
const announce = (msg) => {
  const el = announcer();
  if (!el) return;
  el.textContent = "";
  requestAnimationFrame(() => { el.textContent = msg; });
};

// ---- home: filter the dungeon list -------------------------------------------
function initSearch() {
  const q = document.getElementById("q");
  if (!q) return;
  q.closest(".search").hidden = false;

  const items = [...document.querySelectorAll(".dungeon")];
  const sections = [...document.querySelectorAll(".expansion")];
  const empty = document.querySelector(".no-results");
  const fold = (s) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/['’‘]/g, "");

  const filter = () => {
    const terms = fold(q.value).split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const li of items) {
      const hay = li.dataset.search || "";
      const match = terms.every((t) => hay.includes(t));
      li.hidden = !match;
      if (match) shown++;
    }
    for (const s of sections) s.hidden = !s.querySelector(".dungeon:not([hidden])");
    if (empty) {
      empty.hidden = shown > 0;
      empty.querySelector(".no-results-term").textContent = q.value.trim();
    }
  };

  q.addEventListener("input", filter);
  q.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const first = items.find((li) => !li.hidden);
      if (first) first.querySelector("a").click();
    } else if (e.key === "Escape" && q.value) {
      q.value = "";
      filter();
    }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.target.closest("input, textarea, select, [contenteditable]")) return;
    e.preventDefault();
    q.focus();
  });
  if (q.value) filter(); // restored by the browser on back-navigation
}

// ---- guide: route maps as a stepper ------------------------------------------
function initRoute() {
  const wrap = document.querySelector(".route-maps");
  if (!wrap) return;
  const steps = [...wrap.querySelectorAll(".route-step")];
  if (steps.length < 2) return;

  const short = (label) => (label.match(/^map\s*(\d+)$/i) || [])[1] || label.replace(/\s*map$/i, "");
  const nav = document.createElement("div");
  nav.className = "route-nav";
  const prev = Object.assign(document.createElement("button"), { type: "button", className: "route-arrow", innerHTML: "&#8249;" });
  prev.setAttribute("aria-label", "Previous map");
  const next = Object.assign(document.createElement("button"), { type: "button", className: "route-arrow", innerHTML: "&#8250;" });
  next.setAttribute("aria-label", "Next map");
  const list = document.createElement("div");
  list.className = "route-tabs";
  list.setAttribute("role", "tablist");
  list.setAttribute("aria-label", "Route maps");
  const status = document.createElement("span");
  status.className = "route-status";

  const tabs = steps.map((step, i) => {
    const label = step.dataset.label || `Map ${i + 1}`;
    const tab = document.createElement("button");
    tab.type = "button";
    tab.id = `tab-${step.id}`;
    tab.textContent = short(label);
    tab.setAttribute("role", "tab");
    tab.setAttribute("aria-controls", step.id);
    if (tab.textContent !== label) tab.setAttribute("aria-label", label);
    step.setAttribute("role", "tabpanel");
    step.setAttribute("aria-labelledby", tab.id);
    list.append(tab);
    return tab;
  });
  nav.append(prev, list, next, status);
  wrap.before(nav);

  let current = 0;
  const show = (i, { focus = false, updateHash = true } = {}) => {
    current = Math.max(0, Math.min(steps.length - 1, i));
    steps.forEach((s, k) => { s.hidden = k !== current; });
    tabs.forEach((t, k) => {
      t.setAttribute("aria-selected", String(k === current));
      t.tabIndex = k === current ? 0 : -1;
    });
    prev.disabled = current === 0;
    next.disabled = current === steps.length - 1;
    const label = steps[current].dataset.label || `Map ${current + 1}`;
    status.textContent = /^map\s*\d+$/i.test(label) ? `${label} of ${steps.length}` : label;
    if (focus) tabs[current].focus();
    if (updateHash) history.replaceState(null, "", `#${steps[current].id}`);
  };

  tabs.forEach((t, i) => t.addEventListener("click", () => show(i)));
  prev.addEventListener("click", () => show(current - 1));
  next.addEventListener("click", () => show(current + 1));
  list.addEventListener("keydown", (e) => {
    const moves = { ArrowLeft: current - 1, ArrowRight: current + 1, Home: 0, End: steps.length - 1 };
    if (e.key in moves) { e.preventDefault(); show(moves[e.key], { focus: true }); }
  });

  const fromHash = () => steps.findIndex((s) => `#${s.id}` === location.hash);
  show(Math.max(0, fromHash()), { updateHash: false });
  window.addEventListener("hashchange", () => {
    const i = fromHash();
    if (i >= 0) show(i, { updateHash: false });
  });
}

// ---- guide: copy /i lines for instance chat ----------------------------------
async function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch {
      // denied (permissions policy, unfocused document); try the older method below
    }
  }
  // Plain http:// hosting has no Clipboard API at all; fall back to a selection copy.
  const area = Object.assign(document.createElement("textarea"), { value: text, readOnly: true });
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.append(area);
  area.select();
  const ok = document.execCommand("copy");
  area.remove();
  if (!ok) throw new Error("copy failed");
}

function initCopy() {
  for (const btn of document.querySelectorAll("button.copy")) {
    btn.hidden = false;
    const chat = btn.closest(".chat");
    let timer;
    btn.addEventListener("click", async () => {
      try {
        await copyText(btn.dataset.copy);
        btn.textContent = "Copied";
        chat.classList.remove("is-copied");
        void chat.offsetWidth; // restart the confirmation animation
        chat.classList.add("is-copied");
        announce("Copied. Paste it into chat.");
      } catch {
        btn.textContent = "Select and copy";
        const range = document.createRange();
        range.selectNodeContents(chat.querySelector(".chat-line"));
        getSelection().removeAllRanges();
        getSelection().addRange(range);
        announce("Couldn't copy automatically. The line is selected; press Ctrl+C to copy it.");
      }
      clearTimeout(timer);
      timer = setTimeout(() => { btn.textContent = "Copy"; chat.classList.remove("is-copied"); }, 1800);
    });
  }
}

initSearch();
initRoute();
initCopy();
