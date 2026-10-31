"use strict";

// F08: the Latin-run wrapper must never split an HTML entity that escapeHtml emits.
const assert = require("node:assert/strict");
const path = require("node:path");
const app = require(path.join(__dirname, "..", "..", "src", "web", "static", "app.js"));

// 1) Enumerate what escapeHtml actually emits, straight from the implementation.
//    Today: & < > " become named entities; the single quote stays literal.
const OBSERVED = [];
for (let code = 32; code < 127; code++) {
  const ch = String.fromCharCode(code);
  const escaped = app.escapeHtml(ch);
  if (escaped !== ch) OBSERVED.push([ch, escaped]);
}
const EXPECTED_MAP = [['"', "&quot;"], ["&", "&amp;"], ["<", "&lt;"], [">", "&gt;"]];
assert.deepEqual(OBSERVED, EXPECTED_MAP, "escapeHtml mapping changed; update this test");
assert.equal(app.escapeHtml("'"), "'", "single quote is emitted literally, not as &#39;/&#x27;");

// 2) Every emitted entity must be atomic for the wrapper: nothing may sit inside the
//    "&" + name + ";" shape, otherwise a <span> would be injected in the middle.
const ATOMIC = /^&(?:amp;)?(?:lt|gt|amp|quot);$/;
for (const [, escaped] of OBSERVED) {
  assert.match(escaped, ATOMIC, `wrapper cannot see ${escaped} atomically`);
}

const CASES = [
  "#include <stdio.h>",
  'scanf("%d", &x)',
  "if (a < b && c > d)",
  "متن لفظی &lt; و &amp; و &quot; در منبع",
  "a < b & c",
  "char c = 'a';",
  "printf(\"%c\\n\", 'x');",
  "p->next = q;",
  "1 << 3", "16 >> 2",
  "a && b", "a || b",
  "<script>alert(1)</script>",
  "<img src=x onerror=alert(1)>",
  "&#39; و &#x27; به‌صورت متن",
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

// Markdown code is escaped and never passed through the Latin-run wrapper.
const inline = app.renderMarkdownAnswer("`a < b`");
assert.ok(inline.includes('<code class="md-code" dir="auto">a &lt; b</code>'), inline);
assert.doesNotMatch(inline, /<code[^>]*>[^<]*<span/, "inline code must not be wrapped");
const fenced = app.renderMarkdownAnswer("```\n#include <stdio.h>\nint main(void) { return 0; }\n```");
assert.ok(fenced.includes('<code class="md-code-block" dir="ltr">#include &lt;stdio.h&gt;'), fenced);
assert.doesNotMatch(fenced, /<code[^>]*>[^<]*<span/, "fenced code must not be wrapped");

// 3) Untrusted markup stays text: no element is ever created from answer text.
for (const input of ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"]) {
  const html = app.renderMarkdownAnswer(input);
  const stripped = html
    .replace(/<p dir="auto">/g, "").replace(/<\/p>/g, "")
    .replace(/<span dir="auto">/g, "").replace(/<\/span>/g, "");
  assert.doesNotMatch(html, /<(?:script|img|onerror)\b/i, `raw tag leaked: ${input}`);
  assert.equal(stripped, app.escapeHtml(input), `payload not escaped: ${input}`);
}

console.log("PASS F08 entity-safe Latin wrapping (" + OBSERVED.length + " entities enumerated)");
