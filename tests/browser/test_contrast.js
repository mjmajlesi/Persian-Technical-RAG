"use strict";

// F15: every text/background pair the dashboard actually declares must reach
// WCAG AA (4.5:1 normal text). Colours are read from the real stylesheet.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const CSS_PATH = path.join(__dirname, "..", "..", "src", "web", "static", "dashboard.css");
const source = fs.readFileSync(CSS_PATH, "utf8").replace(/\/\*[\s\S]*?\*\//g, "");

const rules = new Map();
for (const match of source.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
  const selector = match[1].trim().replace(/\s+/g, " ");
  const declarations = {};
  for (const part of match[2].split(";")) {
    const split = part.indexOf(":");
    if (split < 0) continue;
    declarations[part.slice(0, split).trim()] = part.slice(split + 1).trim();
  }
  // First declaration wins: later @media overrides must not hide the base rule.
  if (!rules.has(selector)) rules.set(selector, declarations);
}

const root = rules.get(":root") || {};
const declared = (selector, prop) => (rules.get(selector) || {})[prop];

function rgb(value) {
  const text = String(value).trim();
  const varMatch = text.match(/^var\(\s*(--[\w-]+)\s*(?:,\s*(.+))?\)$/);
  if (varMatch) {
    if (root[varMatch[1]] !== undefined) return rgb(root[varMatch[1]]);
    if (varMatch[2]) return rgb(varMatch[2]);
    throw new Error(`unresolved ${varMatch[1]}`);
  }
  const hexMatch = text.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
  if (hexMatch) {
    const hex = hexMatch[1].length === 3
      ? hexMatch[1].split("").map((c) => c + c).join("") : hexMatch[1];
    return [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16)).concat(1);
  }
  const rgbaMatch = text.match(/^rgba?\(([^)]+)\)$/i);
  if (rgbaMatch) {
    const parts = rgbaMatch[1].split(",").map((p) => parseFloat(p.trim()));
    return [parts[0], parts[1], parts[2], parts.length > 3 ? parts[3] : 1];
  }
  throw new Error(`unparsable colour: ${text}`);
}

const over = (front, back) => [0, 1, 2].map((i) => front[i] * front[3] + back[i] * (1 - front[3])).concat(1);
const channel = (value) => {
  const c = value / 255;
  return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
};
const luminance = (c) => 0.2126 * channel(c[0]) + 0.7152 * channel(c[1]) + 0.0722 * channel(c[2]);
const ratio = (a, b) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};

const canvas = rgb(declared("body", "background"));
const card = rgb(root["--card"]);
const accent = rgb(root["--accent"]);

const rows = [];
function check(label, compute, min = 4.5) {
  try {
    rows.push({ label, min, value: compute() });
  } catch (err) {
    rows.push({ label, min, value: 0, note: err.message });
  }
}
const onRule = (sel, prop, bg) => () => ratio(over(rgb(declared(sel, prop)), bg), bg);
const onOwnBg = (sel) => () => {
  const bg = rgb(declared(sel, "background"));
  return ratio(over(rgb(declared(sel, "color")), bg), bg);
};
const disabledPair = () => {
  const decls = rules.get("#ask-btn:disabled") || {};
  const bg = rgb(decls.background || declared("#ask-btn", "background"));
  const fg = rgb(decls.color || declared("#ask-btn", "color"));
  if (decls.opacity) {   // group opacity composites text and fill against the card
    const alpha = parseFloat(decls.opacity);
    const back = over(bg.map((v, i) => (i === 3 ? alpha : v)), card);
    const front = over(fg.map((v, i) => (i === 3 ? alpha : v)), back);
    return ratio(front, back);
  }
  return ratio(over(fg, bg), bg);
};

const ink = () => rgb(declared("body", "color"));
check("body text / canvas", () => ratio(over(ink(), canvas), canvas));
check("tagline / canvas", onRule("#site-header .tagline", "color", canvas));
check("h1 / canvas", onRule("#site-header h1", "color", canvas), 3);
check("sidebar h2 / card", onRule("#language-sidebar h2", "color", card));
check("language item / card", () => ratio(over(ink(), card), card));
check("language status / card", onRule(".lang-status", "color", card));
check("active language / accent", onRule("#lang-list li.active", "color", accent));
check("active status / accent", onRule("li.active .lang-status", "color", accent));
check("empty language / card", onRule("li.empty", "color", card));
check("empty status / card", onRule("li.empty .lang-status", "color", card));
check("ask button / accent", onRule("#ask-btn", "color", accent));
check("ask button disabled", disabledPair);
check("question placeholder / card", onRule("#question-box::placeholder", "color", card));
check("error message / canvas", onRule("#message", "color", canvas));
check("sample chip", onOwnBg(".sample-chip"));
check("citation chip", onOwnBg(".cite-chip"));
check("topic chip", onOwnBg(".topic-chip"));
check("answer text / card", () => ratio(over(ink(), card), card));
check("inline code", onOwnBg("#answer-pane code, #answer-pane .md-code"));
check("code block", onOwnBg("#answer-pane .md-code-block"));
check("reveal title", onRule("#cite-reveal-pane h4", "color", rgb(declared("#cite-reveal-pane", "background"))));
check("reveal section", onRule("#cite-reveal-pane .cite-section", "color",
  rgb(declared("#cite-reveal-pane", "background"))));
check("reveal pre", () => {
  const bg = rgb(declared("#cite-reveal-pane pre", "background"));
  return ratio(over(ink(), bg), bg);
});
check("footer / canvas", onRule("#pack-footer", "color", canvas));
check("welcome text / card", onRule("#welcome-pane", "color", card));
check("sample label / card", onRule("#sample-label", "color", card));

for (const row of rows) {
  const status = row.value >= row.min ? "ok  " : "FAIL";
  const note = row.note ? ` (${row.note})` : "";
  console.log(`${status} ${row.value.toFixed(2)}:1 (min ${row.min}) — ${row.label}${note}`);
}
const failures = rows.filter((row) => row.value < row.min);
assert.deepEqual(failures.map((row) => row.label), [], "contrast below AA");
console.log(`PASS F15 contrast (${rows.length} pairs, worst ${Math.min(...rows.map((r) => r.value)).toFixed(2)}:1)`);
