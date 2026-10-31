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
  const CODE_RUN_RE = /&(?:amp;)?(?:lt|gt|amp|quot);|([A-Za-z0-9_#+]+(?:[.\-][A-Za-z0-9_#+]+)*)/g;
  // F08: HTML entities are matched whole, so the wrapper can never split one
  // (`&lt;` stays one text node; a literal `&lt;` stays `&amp;lt;`).
  function wrapCodeRuns(escaped) {
    return escaped.replace(CODE_RUN_RE, (match, run) =>
      run ? '<span dir="auto">' + run + "</span>" : match);
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

  // F16: GET /api/languages is the one response the whole page depends on, so
  // its payload is classified explicitly instead of trusting any 200 body.
  // Pure helper (node-testable): HTTP status + parsed body -> verdict.
  function validateLanguagesPayload(status, body) {
    if (typeof status === "number" && (status < 200 || status > 299)) {
      return { ok: false, reason: "http", status: status };
    }
    const list = body && body.languages;
    if (!Array.isArray(list) || list.length === 0) {
      return { ok: false, reason: "empty" };
    }
    const ids = list.map((p) => p && p.language_id);
    const wanted = body && body.default;
    return {
      ok: true,
      packs: list,
      // An unknown default must never leave the form pointing at no pack.
      defaultLanguage: ids.indexOf(wanted) >= 0 ? wanted : ids[0],
    };
  }

  // F16: every language-fetch failure gets its own Persian sentence, and every
  // one of them tells the student what to do next (the retry button).
  const LANGUAGE_ERROR_MESSAGES = {
    network: "فهرست زبان‌ها دریافت نشد؛ اتصال به سرور برقرار نیست. دوباره تلاش کنید.",
    http: "سرور در ارسال فهرست زبان‌ها خطا داد. دوباره تلاش کنید.",
    json: "پاسخ سرور برای فهرست زبان‌ها خوانا نبود. دوباره تلاش کنید.",
    empty: "هیچ زبانی از سرور دریافت نشد. دوباره تلاش کنید.",
  };

  function languageErrorMessage(reason, status) {
    const base = LANGUAGE_ERROR_MESSAGES[reason] || LANGUAGE_ERROR_MESSAGES.http;
    return reason === "http" && status
      ? "سرور در ارسال فهرست زبان‌ها خطا داد (HTTP " + status + "). دوباره تلاش کنید."
      : base;
  }

  // Export for node-based verification; browsers ignore this branch.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      escapeHtml: escapeHtml,
      buildReveal: buildReveal,
      renderMarkdownAnswer: renderMarkdownAnswer,
      validateLanguagesPayload: validateLanguagesPayload,
      languageErrorMessage: languageErrorMessage,
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
    openChip = null;
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
  let requestVersion = 0;
  let askBtn = document.getElementById("ask-btn");
  // F15: the citation chip whose source is currently revealed (Escape closes it).
  let openChip = null;

  // T013: switching language resets the question view state. T015d: an
  // empty pack shows its explicit state right away (contracts/languages-api.md).
  const EMPTY_PACK_MESSAGE = "کورپوس این زبان هنوز آماده نیست.";

  function selectLanguage(langId, silent) {
    requestVersion++;
    inFlight = false;
    setLoading(false);
    currentLanguage = langId;
    Array.prototype.forEach.call(langList.children, (li) => {
      const active = li.dataset.lang === langId;
      li.classList.toggle("active", active);
      const button = li.querySelector ? li.querySelector(".lang-item") : null;
      if (button) button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    const pack = packs.filter((p) => p.language_id === langId)[0];
    const name = (pack ? pack.display_name.split("/")[0] : langId).trim();
    box.placeholder = "سوال فنی " + name + " را به فارسی بنویسید…";
    box.value = "";
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

  function renderSidebar(verdict) {
    packs = verdict.packs;
    langList.textContent = "";
    packs.forEach((p) => {
      const li = document.createElement("li");
      li.className = p.status;
      li.dataset.lang = p.language_id;
      // F15: native button inside the card, so keyboard users can switch packs.
      const button = document.createElement("button");
      button.type = "button";
      button.className = "lang-item";
      button.setAttribute("aria-pressed", "false");
      button.appendChild(document.createTextNode(p.display_name));
      const badge = document.createElement("span");
      badge.className = "lang-status";
      badge.textContent = STATUS_LABEL[p.status] || p.status;
      button.appendChild(badge);
      li.appendChild(button);
      li.addEventListener("click", () => selectLanguage(p.language_id, false));
      langList.appendChild(li);
    });
    selectLanguage(verdict.defaultLanguage, true);
    renderFooter();
  }

  // F16: explicit loading / ready / error states for the pack list. A failed
  // fetch used to leave an empty sidebar and currentLanguage === null, which
  // silently swallowed every answer, so the form stays unusable until a pack
  // is actually known, and the failure speaks (role="alert") with a retry.
  const langStateBox = document.getElementById("lang-state");
  let langState = "loading";

  function showLanguageLoading() {
    if (langStateBox) {
      langStateBox.textContent = "";
      const row = document.createElement("p");
      row.className = "lang-loading";
      row.setAttribute("role", "status");
      const spin = document.createElement("span");
      spin.className = "spinner";
      spin.setAttribute("aria-hidden", "true");
      row.appendChild(spin);
      row.appendChild(document.createTextNode("در حال دریافت فهرست زبان‌ها…"));
      langStateBox.appendChild(row);
    }
    langList.textContent = "";
  }

  function showLanguageError(text) {
    if (langStateBox) {
      langStateBox.textContent = "";
      const err = document.createElement("p");
      err.className = "lang-error";
      err.setAttribute("role", "alert");
      err.textContent = text;
      const retry = document.createElement("button");
      retry.type = "button";
      retry.id = "lang-retry";
      retry.className = "lang-retry";
      retry.textContent = "تلاش دوباره";
      retry.addEventListener("click", loadLanguages);
      langStateBox.appendChild(err);
      langStateBox.appendChild(retry);
      retry.focus();
    }
    langList.textContent = "";
    packs = [];
    currentLanguage = null;
    box.disabled = true;
    askBtn.disabled = true;
    clearViewState();
  }

  function failLanguages(reason, status) {
    langState = "error";
    showLanguageError(languageErrorMessage(reason, status));
  }

  async function loadLanguages() {
    const hadError = langState === "error";
    langState = "loading";
    box.disabled = true;
    askBtn.disabled = true;
    showLanguageLoading();
    let res = null;
    try {
      res = await fetch("/api/languages", { headers: { Accept: "application/json" } });
    } catch (_) {
      failLanguages("network");
      return;
    }
    if (!res.ok) { failLanguages("http", res.status); return; }
    let body = null;
    try {
      body = await res.json();
    } catch (_) {
      failLanguages("json");
      return;
    }
    const verdict = validateLanguagesPayload(res.status, body);
    if (!verdict.ok) { failLanguages(verdict.reason, verdict.status); return; }
    langState = "ready";
    if (langStateBox) langStateBox.textContent = "";
    renderSidebar(verdict);
    if (hadError) {
      // Focus lands on the pack that is now selected; the form is usable again.
      const active = langList.querySelector("li.active .lang-item");
      const target = active || langList.querySelector(".lang-item") || box;
      target.focus();
    }
  }

  loadLanguages();

  // T020: click a chip to reveal its source title + section + full excerpt.
  // T025: suggested topics render as clickable chips; clicking one fills
  // the question box (no auto-submit) so the student can ask about it.
  function topicChip(topic) {
    const el = document.createElement("button");
    el.type = "button";
    el.className = "topic-chip";
    el.textContent = topic;
    return el;
  }

  function closeReveal() {
    if (openChip) openChip.setAttribute("aria-expanded", "false");
    openChip = null;
    reveal.innerHTML = "";
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
    if (openChip === chipEl) {   // F15: same chip closes its own reveal
      closeReveal();
      return;
    }
    if (openChip) openChip.setAttribute("aria-expanded", "false");
    openChip = chipEl;
    chipEl.setAttribute("aria-expanded", "true");
    reveal.innerHTML = buildReveal({
      doc_title: chipEl.dataset.docTitle || chipEl.textContent,
      section_heading: chipEl.dataset.section || "",
      excerpt: chipEl.dataset.excerpt || "",
    });
  });

  // F15: Escape closes the reveal and returns focus to the chip that opened it.
  cites.addEventListener("keydown", (ev) => {
    if (ev.key !== "Escape" || !openChip) return;
    const opener = openChip;
    closeReveal();
    opener.focus();
    ev.preventDefault();
  });

  function chip(c) {
    const el = document.createElement("button");
    el.type = "button";
    el.className = "cite-chip";
    el.textContent = c.doc_title + " — " + c.section_heading;
    el.dataset.chunkId = c.chunk_id;
    el.dataset.docTitle = c.doc_title;
    el.dataset.section = c.section_heading;
    el.dataset.excerpt = c.excerpt;
    el.setAttribute("aria-expanded", "false");
    el.setAttribute("aria-controls", "cite-reveal-pane");
    return el;
  }

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    // F16: never post a question for a language the page has not received.
    if (langState !== "ready" || !currentLanguage) {
      message.textContent =
        "زبان انتخاب نشده است؛ ابتدا فهرست زبان‌ها را دوباره بارگذاری کنید.";
      return;
    }
    if (inFlight) return; // T015d: no parallel asks, button stays disabled
    inFlight = true;
    const version = ++requestVersion;
    clearViewState();
    // T015c: keep the promo text but collapse it after use so the demo
    // viewport leads with the live Q&A; sample chips stay available.
    const welcomeText = document.getElementById("welcome-text");
    if (welcomeText) welcomeText.classList.add("hidden");
    setLoading(true);
    const askedLanguage = currentLanguage || "c";
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: box.value,
                               language: askedLanguage }),
      });
      let body = {};
      try { body = await res.json(); } catch (_) { /* non-JSON body */ }
      if (version !== requestVersion || currentLanguage !== askedLanguage) return;
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
      if (version !== requestVersion || currentLanguage !== askedLanguage) return;
      // T015d: network/server failure → same friendly Persian error.
      message.textContent = ERR_MESSAGE;
      pane.textContent = "";
    } finally {
      if (version === requestVersion) {
        inFlight = false;
        setLoading(false);
      }
    }
  });
})();
