"use strict";

// Node standard-library harness executes the real browser app script without a server.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

class Element {
  constructor() {
    this.children = []; this.listeners = {}; this.dataset = {};
    this.value = ""; this.textContent = ""; this.innerHTML = "";
    this.disabled = false; this.classList = { add() {}, remove() {}, toggle() {} };
  }
  appendChild(child) { this.children.push(child); return child; }
  after() {}
  addEventListener(name, callback) { this.listeners[name] = callback; }
  click() { return this.listeners.click(); }
  requestSubmit() { return this.listeners.submit({ preventDefault() {} }); }
}

async function run() {
  const elements = Object.fromEntries([
    "ask-form", "question-box", "answer-pane", "citations", "message", "lang-list",
    "ask-btn", "sample-questions", "sample-lang-name", "pack-footer", "welcome-text",
  ].map(id => [id, new Element()]));
  const requests = [];
  const packs = { default: "c", languages: [
    { language_id: "c", display_name: "C", status: "ready" },
    { language_id: "python", display_name: "Python", status: "ready" },
  ] };
  const document = {
    getElementById: id => elements[id],
    createElement: () => new Element(),
    createTextNode: text => ({ textContent: text }),
  };
  const fetch = (url, options) => {
    if (url === "/api/languages") return Promise.resolve({ json: async () => packs });
    return new Promise((resolve, reject) => requests.push({ resolve, reject,
      question: JSON.parse(options.body).question }));
  };
  vm.runInNewContext(fs.readFileSync("src/web/static/app.js", "utf8"), { document, fetch });
  await new Promise(resolve => setImmediate(resolve));
  const [a, b] = elements["lang-list"].children;
  const box = elements["question-box"], form = elements["ask-form"];
  box.value = "old question";
  const old = form.requestSubmit();
  b.click(); a.click();
  box.value = "new question";
  const current = form.requestSubmit();
  assert.equal(requests.length, 2, "A→B→A must allow a new request");
  const answer = text => ({ ok: true, json: async () => ({ type: "answer", answer_text: text, citations: [] }) });
  requests[1].resolve(answer("NEW"));
  await current;
  requests[0].resolve(answer("OLD"));
  await old;
  assert.match(elements["answer-pane"].innerHTML, /NEW/, "stale answer must not replace new answer");
  assert.doesNotMatch(elements["answer-pane"].innerHTML, /OLD/);

  box.value = "third question";
  const third = form.requestSubmit();
  b.click(); a.click();
  box.value = "fourth question";
  const fourth = form.requestSubmit();
  assert.equal(requests.length, 4);
  requests[2].reject(new Error("old failure"));
  await third;
  assert.equal(elements["ask-btn"].disabled, true, "old finally must not unlock active request");
  assert.equal(elements.message.textContent, "", "stale error must not appear");
  requests[3].resolve(answer("FOURTH"));
  await fourth;
  assert.match(elements["answer-pane"].innerHTML, /FOURTH/);
  assert.equal(elements["ask-btn"].disabled, false);
}

run().then(() => console.log("PASS F07 A→B→A request ownership"), error => {
  console.error(error); process.exitCode = 1;
});
