/* Demo Q&A rendering (T019) + citation click-reveal (T020). */
(function (root) {
  "use strict";

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // Pure helper (node-testable): reveal markup for one citation.
  function buildReveal(c) {
    return (
      "<div class=\"cite-reveal\"><h4>" + escapeHtml(c.doc_title) + "</h4>" +
      "<div class=\"cite-section\">" + escapeHtml(c.section_heading) + "</div>" +
      "<pre dir=\"auto\">" + escapeHtml(c.excerpt) + "</pre></div>"
    );
  }

  // Pure helper (node-testable): bidi-safe rendering of mixed
  // Persian/English answer text. Latin/code runs get dir="auto" spans so
  // identifiers and numbers don't jump around inside RTL paragraphs.
  // Dots/dashes join only *inside* a run (stdio.h stays whole) so
  // sentence-ending periods are never swallowed into the span.
  // Order matters: split the RAW text first, escape each part, then wrap —
  // escaping first would shred the &lt;/&amp; entities into spans.
  const CODE_RUN_RE = /([A-Za-z0-9_#+]+(?:[.\-][A-Za-z0-9_#+]+)*)/g;
  function renderBidi(text) {
    return String(text)
      .split(CODE_RUN_RE)
      .map((part, i) =>
        i % 2 === 1
          ? "<span dir=\"auto\">" + escapeHtml(part) + "</span>"
          : escapeHtml(part)
      )
      .join("")
      .replace(/\n/g, "<br>");
  }

  // Export for node-based verification; browsers ignore this branch.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      escapeHtml: escapeHtml,
      buildReveal: buildReveal,
      renderBidi: renderBidi,
    };
    return;
  }

  const form = document.getElementById("ask-form");
  const box = document.getElementById("question-box");
  const pane = document.getElementById("answer-pane");
  const cites = document.getElementById("citations");
  const message = document.getElementById("message");
  const reveal = document.createElement("div");
  reveal.id = "cite-reveal-pane";
  cites.after(reveal);

  // T020: click a chip to reveal its source title + section + full excerpt.
  // T025: suggested topics render as clickable chips; clicking one fills
  // the question box (no auto-submit) so the student can ask about it.
  function topicChip(topic) {
    const el = document.createElement("span");
    el.className = "topic-chip";
    el.textContent = topic;
    return el;
  }

  cites.addEventListener("click", (ev) => {
    const topicEl = ev.target.closest(".topic-chip");
    if (topicEl) {
      box.value = "درباره " + topicEl.textContent + " توضیح بده";
      box.focus();
      return;
    }
    if (!chipEl) return;
    reveal.innerHTML = buildReveal({
      doc_title: chipEl.dataset.docTitle || chipEl.textContent,
      section_heading: chipEl.dataset.section || "",
      excerpt: chipEl.dataset.excerpt || "",
    });
  });

  function chip(c) {
    const el = document.createElement("span");
    el.className = "cite-chip";
    el.textContent = c.doc_title + " — " + c.section_heading;
    el.dataset.chunkId = c.chunk_id;
    el.dataset.docTitle = c.doc_title;
    el.dataset.section = c.section_heading;
    el.dataset.excerpt = c.excerpt;
    return el;
  }

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    message.textContent = "";
    pane.textContent = "در حال جست‌وجو…";
    cites.innerHTML = "";
    reveal.innerHTML = "";
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: box.value }),
    });
    const body = await res.json();
    if (body.type === "answer") {
      pane.innerHTML = renderBidi(body.answer_text);
      body.citations.forEach((c) => cites.appendChild(chip(c)));
    } else if (body.type === "abstain" || body.type === "clarify") {
      pane.textContent = "";
      reveal.innerHTML = "";
      message.textContent = body.message;
      (body.suggested_topics || []).forEach((t) => cites.appendChild(topicChip(t)));
    } else {
      message.textContent = "خطای غیرمنتظره: " + JSON.stringify(body).slice(0, 200);
    }
  });
})();
