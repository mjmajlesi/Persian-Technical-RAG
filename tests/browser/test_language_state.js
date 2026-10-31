"use strict";

// F16: GET /api/languages must never be treated as "fine" unless it really
// carries a non-empty pack list, and every failure must produce a distinct
// Persian sentence that tells the student what to do next.
const assert = require("node:assert/strict");
const path = require("node:path");
const app = require(path.join(__dirname, "..", "..", "src", "web", "static", "app.js"));

const PACKS = [
  { language_id: "c", display_name: "C", status: "ready" },
  { language_id: "python", display_name: "Python", status: "ready" },
];

// 1) Happy path keeps the server-declared default.
const ok = app.validateLanguagesPayload(200, { default: "python", languages: PACKS });
assert.equal(ok.ok, true);
assert.equal(ok.defaultLanguage, "python");
assert.deepEqual(ok.packs.map((p) => p.language_id), ["c", "python"]);

// 2) A missing or unknown default must still leave a usable selection.
assert.equal(app.validateLanguagesPayload(200, { languages: PACKS }).defaultLanguage, "c");
assert.equal(app.validateLanguagesPayload(200, { default: "java", languages: PACKS }).defaultLanguage, "c");
assert.equal(app.validateLanguagesPayload(200, { default: "", languages: PACKS }).defaultLanguage, "c");

// 3) Non-2xx is a failure even when the body looks usable.
for (const status of [400, 404, 500, 502, 503]) {
  const verdict = app.validateLanguagesPayload(status, { default: "c", languages: PACKS });
  assert.equal(verdict.ok, false, `status ${status} accepted`);
  assert.equal(verdict.reason, "http");
  assert.equal(verdict.status, status);
}

// 4) Anything that is not a non-empty array of packs is an empty list.
const EMPTY_BODIES = [
  null,
  undefined,
  {},
  { default: "c" },
  { default: "c", languages: [] },
  { default: "c", languages: null },
  { default: "c", languages: "c" },
  { default: "c", languages: { c: {} } },
];
for (const body of EMPTY_BODIES) {
  const verdict = app.validateLanguagesPayload(200, body);
  assert.equal(verdict.ok, false, `body accepted: ${JSON.stringify(body)}`);
  assert.equal(verdict.reason, "empty", `wrong reason for ${JSON.stringify(body)}`);
}

// 5) Each failure reason has its own message, and every message offers the
//    retry action. The HTTP variant names the status the server returned.
const reasons = ["network", "http", "json", "empty"];
const messages = reasons.map((reason) => app.languageErrorMessage(reason));
assert.equal(new Set(messages).size, reasons.length, "messages must be distinct");
for (const [i, text] of messages.entries()) {
  assert.match(text, /[\u0600-\u06FF]/, `message ${reasons[i]} is not Persian`);
  assert.match(text, /دوباره تلاش کنید/, `message ${reasons[i]} has no call to action`);
}
assert.match(app.languageErrorMessage("http", 503), /HTTP 503/);
assert.match(app.languageErrorMessage("http", 500), /HTTP 500/);
assert.equal(app.languageErrorMessage("http"), app.languageErrorMessage("http", 0));
assert.equal(app.languageErrorMessage("unknown-reason"), app.languageErrorMessage("http"));

console.log("PASS F16 language payload classification (" + EMPTY_BODIES.length
  + " empty shapes, " + reasons.length + " messages)");
