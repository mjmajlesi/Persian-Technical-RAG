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

  // Latin/code run wrapper (002 docstring): applied to ESCAPED PLAIN text
  // (never to HTML strings, so tag names can't be shredded), wrapping each
  // Latin/number/code run in dir="auto" so identifiers and numbers don't
  // jump around inside RTL paragraphs. Content of style/code markup still
  // joined correctly inside its own element below.
  const CODE_RUN_RE = /([A-Za-z0-9_#+]+(?:[.\-][A-Za-z0-9_#+]+)*)/g;
  function wrapCodeRuns(escaped) {
    return escaped.replace(CODE_RUN_RE, '<span dir="auto">$1</span>');
  }

  // Inline markdown for one plain line (T015d groundwork): inline `code`,
  // **bold**, then bidi runs — everything escaped first, no raw HTML risk.
  function inlineMarkup(line) {
    return String(line).split(/`([^`]+)`/g).map((part, i) =>
      i % 2 === 1
        ? '<code class="md-code" dir="auto">' + escapeHtml(part) + "</code>"
        : wrapCodeRuns(escapeHtml(part))
            .replace(/\*\*([^*]+)\*\*/g, '<strong dir="auto">$1</strong>')
    ).join("");
  }

  // Markdown answer renderer (owner-requested fix: the model answers in
  // Markdown; previously raw '#' and lists showed literally). Blocks:
  // headings #..####, fenced ``` code blocks, bullet lists (- * •),
  // inline `code` / **bold**; paragraphs joined with <br>. MR-safe: all
  // markdown input goes through escapeHtml — no raw HTML passthrough.
  function renderMarkdownAnswer(text) {
    const lines = String(text).split("\n");
    const out = [];
    let listOpen = false;
    let para = [];
    let inCode = false;
    let codeBuf = [];
    const flushPara = () => {
      if (para.length) {
        out.push('<p dir="auto">' + para.map(inlineMarkup).join("<br>") + "</p>");
        para = [];
      }
    };
    const closeList = () => {
      if (listOpen) { out.push("</ul>"); listOpen = false; }
    };
    for (const raw of lines) {
      const line = raw.replace(/\s+$/, "");
      if (inCode) {
        if (/^```/.test(line)) {
          out.push('<code class="md-code-block" dir="ltr">' +
                   escapeHtml(codeBuf.join("\n")) + "</code>");
          codeBuf = [];
          inCode = false;
        } else {
          codeBuf.push(raw);
        }
        continue;
      }
      if (/^```/.test(line)) { flushPara(); closeList(); inCode = true; continue; }
      const heading = line.match(/^(#{1,4})\s+(.*)$/);
      if (heading) {
        flushPara(); closeList();
        const level = heading[1].length;
        const tag = level <= 2 ? "h3" : (level === 3 ? "h4" : "h5");
        out.push('<' + tag + ' dir="auto" class="md-head">' +
                 inlineMarkup(heading[2]) + "</" + tag + ">");
        continue;
      }
      const bullet = line.match(/^\s*[-*•]\s+(.*)$/);
      if (bullet) {
        flushPara();
        if (!listOpen) { out.push('<ul class="md-list">'); listOpen = true; }
        out.push('<li dir="auto">' + inlineMarkup(bullet[1]) + "</li>");
        continue;
      }
      if (line.trim() === "") { flushPara(); closeList(); continue; }
      para.push(line);
    }
    if (inCode && codeBuf.length) {
      out.push('<code class="md-code-block" dir="ltr">' +
               escapeHtml(codeBuf.join("\n")) + "</code>");
    }
    flushPara(); closeList();
    return out.join("\n");
  }

  // Export for node-based verification; browsers ignore this branch.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      escapeHtml: escapeHtml,
      buildReveal: buildReveal,
      renderMarkdownAnswer: renderMarkdownAnswer,
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

  // 002-T013: dashboard sidebar state. Packs come live from
  // GET /api/languages; body.default ("c") is preselected. Switching
  // language resets the question view state (clears answer/citations/
  // messages) so no answer leaks context across packs on screen.
  const langList = document.getElementById("lang-list");
  const STATUS_LABEL = { ready: "آماده", empty: "کورپوس در دسترس نیست" };
  let currentLanguage = null;

  // 002-T015d: friendly Persian states (RTL-consistent).
  const ERR_MESSAGE = "خطای ارتباط با سرور — لطفاً دوباره تلاش کنید.";

  function clearViewState() {
    message.textContent = "";
    pane.textContent = "";
    cites.innerHTML = "";
    reveal.innerHTML = "";
  }

  function setLoading(on) {
    if (on) {
      pane.classList.add("loading");
      pane.innerHTML = '<div class="loading-row" dir="auto">'
        + '<span class="spinner" aria-hidden="true"></span>'
        + "در حال جست‌وجو…</div>";
      askBtn.disabled = true;
    } else {
      pane.classList.remove("loading");
      askBtn.disabled = false;
    }
  }

  let inFlight = false;
  let askBtn = document.getElementById("ask-btn");

  // T013: switching language resets the question view state. T015d: an
  // empty pack shows its explicit state right away (contracts/languages-api.md).
  const EMPTY_PACK_MESSAGE = "کورپوس این زبان هنوز آماده نیست.";

  function selectLanguage(langId, silent) {
    currentLanguage = langId;
    Array.prototype.forEach.call(langList.children, (li) => {
      li.classList.toggle("active", li.dataset.lang === langId);
    });
    const pack = packs.filter((p) => p.language_id === langId)[0];
    const name = (pack ? pack.display_name.split("/")[0] : langId).trim();
    box.placeholder = "سوال فنی " + name + " را به فارسی بنویسید…";
    clearViewState();
    if (pack && pack.status !== "ready") {
      box.placeholder = name + ": کورپوس در دسترس نیست…";
      box.disabled = true;
      pane.textContent = EMPTY_PACK_MESSAGE;
      return;
    }
    box.disabled = false;
    if (langList.children.length) renderSampleQuestions();
  }

  let packs = [];

  // 002-T015c: one-click demo flow. Curated in-corpus Persian probes per
  // ready pack (top-1 scores above the provisional 0.81 gate and empirically
  // answered; see tasks.md T012/T015 notes). Clicking a chip FILLS AND
  // SUBMITS — intentional, documented exception to the no-auto-submit rule,
  // which still applies to abstention topic chips (T025). Source: 002 spec.
  const SAMPLE_QUESTIONS = {
    "c": [
      "تفاوت malloc و calloc چیست؟",
      "حلقه for در C چگونه کار می‌کند؟",
      "تفاوت printf و scanf در خواندن ورودی چیست؟",
    ],
    "cpp": [
      "کلاس در ++C چیست و چگونه تعریف می‌شود؟",
      "تفاوت کلاس و شیء در ++C چیست؟",
      "چگونه توابع inline در ++C کار می‌کنند؟",
    ],
    "python": [
      "تابع range در پایتون چگونه کار می‌کند؟",
      "چگونه در پایتون استثنا بگیریم؟",
      "چگونه در پایتون ورودی از کاربر بگیریم؟",
    ],
    "java": [
      "وراثت (inheritance) در جاوا چگونه کار می‌کند؟",
      "چگونه در جاوا متغیر تعریف کنیم؟",
      "چگونه از کالکشن‌های استاندارد جاوا استفاده کنیم؟",
    ],
  };

  function renderSampleQuestions() {
    const wrap = document.getElementById("sample-questions");
    const langName = document.getElementById("sample-lang-name");
    const pack = packs.filter((p) => p.language_id === currentLanguage)[0];
    langName.textContent = pack ? pack.display_name : currentLanguage;
    wrap.textContent = "";
    (SAMPLE_QUESTIONS[currentLanguage] || []).forEach((question) => {
      const el = document.createElement("button");
      el.type = "button";
      el.className = "sample-chip";
      el.textContent = question;
      // one-click demo flow: fill AND submit (documented T015c exception)
      el.addEventListener("click", () => {
        box.value = question;
        form.requestSubmit();
      });
      wrap.appendChild(el);
    });
  }

  function renderFooter() {
    // T015b: per-pack corpus snapshot info (manifest data via /api/languages).
    const footer = document.getElementById("pack-footer");
    footer.textContent = "";
    packs.forEach((p) => {
      const item = document.createElement("span");
      item.className = "pack-footer-item";
      item.textContent = (p.display_name || p.language_id)
        + " — اسنپ‌شات کورپوس: " + (p.snapshot || "نامشخص")
        + " · مجموعه ارزیابی: " + (p.eval_set_version || "-");
      footer.appendChild(item);
    });
  }

  function renderSidebar(body) {
    packs = body.languages || [];
    langList.innerHTML = "";
    packs.forEach((p) => {
      const li = document.createElement("li");
      li.className = p.status;
      li.dataset.lang = p.language_id;
      li.appendChild(document.createTextNode(p.display_name));
      const badge = document.createElement("span");
      badge.className = "lang-status";
      badge.textContent = STATUS_LABEL[p.status] || p.status;
      li.appendChild(badge);
      li.addEventListener("click", () => selectLanguage(p.language_id, false));
      langList.appendChild(li);
    });
    selectLanguage(body.default || "c", true);
    renderFooter();
  }

  fetch("/api/languages").then((res) => res.json()).then(renderSidebar);

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
    // T020: citation chip click reveals source title + section + excerpt.
    // (bugfix during 002-T015c: chipEl was referenced undefined here since
    // the T013 refactor, breaking the reveal with a ReferenceError.)
    const chipEl = ev.target.closest(".cite-chip");
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
    if (inFlight) return; // T015d: no parallel asks, button stays disabled
    inFlight = true;
    clearViewState();
    // T015c: keep the promo text but collapse it after use so the demo
    // viewport leads with the live Q&A; sample chips stay available.
    const welcomeText = document.getElementById("welcome-text");
    if (welcomeText) welcomeText.classList.add("hidden");
    setLoading(true);
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: box.value,
                               language: currentLanguage || "c" }),
      });
      let body = {};
      try { body = await res.json(); } catch (_) { /* non-JSON body */ }
      if (!res.ok) {
        // T015d: friendly Persian error tree. Our backend 422/500s carry a
        // plain Persian string in `detail` (HTTPException); a pydantic-style
        // array detail (or missing field) falls back to the generic message.
        const detail = body && body.detail;
        message.textContent = typeof detail === "string" && detail
          ? detail
          : ERR_MESSAGE;
        pane.textContent = "";
        return;
      }
      if (body.type === "answer") {
        pane.innerHTML = renderMarkdownAnswer(body.answer_text);
        body.citations.forEach((c) => cites.appendChild(chip(c)));
      } else if (body.type === "abstain" || body.type === "clarify") {
        pane.textContent = "";
        message.textContent = body.message;
        (body.suggested_topics || []).forEach((t) => cites.appendChild(topicChip(t)));
      } else if (body.type === "unavailable") {
        // T015d: empty-pack state per contracts/languages-api.md.
        pane.textContent = body.message || EMPTY_PACK_MESSAGE;
      } else {
        message.textContent = "خطای غیرمنتظره: " + JSON.stringify(body).slice(0, 200);
      }
    } catch (err) {
      // T015d: network/server failure → same friendly Persian error.
      message.textContent = ERR_MESSAGE;
      pane.textContent = "";
    } finally {
      inFlight = false;
      setLoading(false);
    }
  });
})();
