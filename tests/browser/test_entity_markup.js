"use strict";

// F08: the Latin-run wrapper must never split an HTML entity produced by escapeHtml.
const assert = require("node:assert/strict");
const path = require("node:path");
const app = require(path.join(__dirname, "..", "..", "src", "web", "static", "app.js"));

const CASES = [
  "#include <stdio.h>",
  'scanf("%d", &x)',
  "if (a < b && c > d)",
  "متن لفظی &lt; و &amp; و &quot; در منبع",
  "a < b & c",
];

for (const input of CASES) {
  const html = app.renderMarkdownAnswer(input);
  const stripped = html
    .replace(/<p dir="auto">/g, "")
    .replace(/<\/p>/g, "")
    .replace(/<span dir="auto">/g, "")
    .replace(/<\/span>/g, "");
  assert.doesNotMatch(html, /<span[^>]*>(?:lt|gt|amp|quot)<\/span>;/, `entity name wrapped: ${input}`);
  assert.equal(stripped, app.escapeHtml(input), `escaped text changed: ${input}`);
}

console.log("PASS F08 entity-safe Latin wrapping");
