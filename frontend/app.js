const runtime = window.AI_TIME_MACHINE_RUNTIME || { mode: "local" };
const state = {
  events: [],
  selectedId: null,
  filter: "all",
  investigation: null,
  answers: {},
  traceReturnFocus: null,
  askReturnFocus: null,
};

const timeline = document.querySelector("#timeline");
const detail = document.querySelector("#detail-panel");

document.querySelector("#runtime-label").textContent = runtime.mode === "snapshot"
  ? "Git snapshot verified"
  : "Git evidence verified";

async function requestJson(apiPath, snapshotPath, options = undefined) {
  const response = runtime.mode === "snapshot"
    ? await fetch(snapshotPath)
    : await fetch(apiPath, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}

const icons = {
  feature: "✦",
  bug: "!",
  fix: "✓",
  refactor: "⌁",
  performance: "↗",
  rollback: "↶",
  test: "◆",
  change: "•",
};

const labels = {
  feature: "Feature",
  bug: "Incident",
  fix: "Fix",
  refactor: "Architecture",
  performance: "Performance",
  rollback: "Rollback",
  test: "Verification",
  change: "Change",
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  return new Intl.DateTimeFormat("en", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));
}

function visibleEvents() {
  if (state.filter === "all") return state.events;
  if (state.filter === "fix") return state.events.filter((event) => ["fix", "rollback", "test"].includes(event.type));
  return state.events.filter((event) => event.type === state.filter);
}

function renderTimeline() {
  const events = visibleEvents();
  document.querySelector("#event-count").textContent = `${events.length} EVENT${events.length === 1 ? "" : "S"}`;
  if (!events.length) {
    timeline.innerHTML = '<div class="loading-state"><p>No events match this view.</p></div>';
    return;
  }
  timeline.innerHTML = events
    .map(
      (event) => `
        <button class="event-card ${event.type} ${event.id === state.selectedId ? "selected" : ""}" data-event-id="${escapeHtml(event.id)}" aria-pressed="${event.id === state.selectedId}">
          <span class="event-node">${icons[event.type] || "•"}</span>
          <span class="event-content">
            <span class="event-meta"><span class="type-badge">${labels[event.type] || "Change"}</span><time>${formatDate(event.occurred_at)}</time></span>
            <strong>${escapeHtml(event.title)}</strong>
            <span class="event-summary">${escapeHtml(event.summary)}</span>
            <span class="event-footer"><code>${escapeHtml(event.short_hash)}</code><span>${event.files.length} file${event.files.length === 1 ? "" : "s"}</span><span class="certainty"><i></i>${escapeHtml(event.certainty)}</span></span>
          </span>
        </button>`,
    )
    .join("");

  timeline.querySelectorAll(".event-card").forEach((card) => {
    card.addEventListener("click", () => selectEvent(card.dataset.eventId));
  });
}

function selectEvent(id) {
  state.selectedId = id;
  const event = state.events.find((item) => item.id === id);
  if (!event) return;
  renderTimeline();
  renderDetail(event);
}

function showAllEvents() {
  state.filter = "all";
  document.querySelectorAll(".filter").forEach((filter) => {
    const isAll = filter.dataset.filter === "all";
    filter.classList.toggle("active", isAll);
    filter.setAttribute("aria-pressed", String(isAll));
  });
}

function renderDetail(event) {
  const traceable = event.title.toLowerCase().includes("stale checkout");
  const related = event.related_event_ids
    .map((id) => state.events.find((item) => item.id === id))
    .filter(Boolean);
  detail.innerHTML = `
    <header class="detail-header ${event.type}">
      <div class="detail-title-row">
        <span class="large-icon">${icons[event.type] || "•"}</span>
        <div><span class="type-badge">${labels[event.type] || "Change"}</span><h2>${escapeHtml(event.title)}</h2></div>
      </div>
      <div class="detail-meta"><time>${formatDate(event.occurred_at)}</time><span>by ${escapeHtml(event.author)}</span><code>${escapeHtml(event.short_hash)}</code></div>
    </header>
    ${traceable ? `
      <section class="trace-cta">
        <div><span class="trace-kicker">✦ CAUSAL INVESTIGATION</span><strong>Find where this bug really began</strong><p>Replay a validated Codex analysis grounded in Git evidence.</p></div>
        <button class="trace-button" id="trace-origin-button"><span>↶</span> Trace bug origin</button>
      </section>` : ""}
    <div class="detail-body">
      <section class="insight primary-insight">
        <p class="section-label">WHAT CHANGED</p>
        <p>${escapeHtml(event.summary)}</p>
      </section>
      <section class="insight why-insight">
        <p class="section-label">WHY IT MATTERED</p>
        <p>${escapeHtml(event.why)}</p>
      </section>
      <section>
        <div class="section-heading"><p class="section-label">EVIDENCE</p><span class="confidence"><i></i>${Math.round(event.confidence * 100)}% confidence</span></div>
        <div class="evidence-list">
          ${event.evidence.map((item) => `<div class="evidence-item"><span>${item.kind === "commit" ? "⑂" : "⌘"}</span><div><strong>${escapeHtml(item.label)}</strong><p>${escapeHtml(item.value)}</p></div></div>`).join("")}
        </div>
      </section>
      <section>
        <p class="section-label">AFFECTED FILES</p>
        <div class="file-list">${event.files.map((file) => `<span><b>${escapeHtml(file.status)}</b>${escapeHtml(file.path)}</span>`).join("")}</div>
      </section>
      <section class="risk-box">
        <span>△</span><div><p class="section-label">RECORDED RISK</p><p>${escapeHtml(event.risks[0])}</p></div>
      </section>
      ${related.length ? `<section><p class="section-label">CONNECTED HISTORY</p><div class="related-list">${related.map((item) => `<button data-related-id="${escapeHtml(item.id)}"><span>${icons[item.type]}</span><div><strong>${escapeHtml(item.title)}</strong><small>${formatDate(item.occurred_at)}</small></div></button>`).join("")}</div></section>` : ""}
    </div>`;
  detail.querySelectorAll("[data-related-id]").forEach((button) => button.addEventListener("click", () => selectEvent(button.dataset.relatedId)));
  document.querySelector("#trace-origin-button")?.addEventListener("click", openTrace);
}

function closeTrace() {
  document.querySelector("#trace-overlay").hidden = true;
  document.body.classList.remove("trace-open");
  state.traceReturnFocus?.focus();
}

function closeAsk() {
  document.querySelector("#ask-overlay").hidden = true;
  document.body.classList.remove("ask-open");
  state.askReturnFocus?.focus();
}

function answerSource(answer) {
  if (answer.source === "codex-gpt-5.6") return { label: "GPT-5.6 Sol in Codex · validated", className: "codex" };
  return { label: "Evidence fallback · demo safe", className: "fallback" };
}

function renderAskAnswer(answer) {
  const source = answerSource(answer);
  const provenance = answer.provenance || null;
  return `
    <header class="ask-answer-header">
      <div><p class="eyebrow">ASK THE REPO / ${escapeHtml(answer.question_id)}</p><h2 id="ask-answer-title">${escapeHtml(answer.question)}</h2></div>
      <div class="trace-header-actions"><span class="analysis-source ${source.className}"><i></i>${escapeHtml(source.label)}</span><button class="trace-close" data-close-ask aria-label="Close answer">×</button></div>
    </header>
    <div class="ask-answer-body">
      <section class="ask-verdict">
        <div class="ask-verdict-mark">⌁</div>
        <div><span class="trace-kicker">EVIDENCE-GROUNDED ANSWER</span><h3>${escapeHtml(answer.headline)}</h3><p>${escapeHtml(answer.answer)}</p></div>
        <div class="trace-score"><span>${Math.round(answer.confidence * 100)}%</span><small>${escapeHtml(answer.certainty)} confidence</small></div>
      </section>
      <section class="ask-citations">
        <div class="ask-section-title"><div><p class="section-label">TRACEABLE EVIDENCE</p><h3>Open any citation in the timeline</h3></div><span>${answer.evidence.length} VERIFIED LINKS</span></div>
        <div class="ask-evidence-grid">
          ${answer.evidence.map((citation, index) => {
            const event = state.events.find((candidate) => candidate.id === citation.event_id);
            return `<button class="ask-evidence-card" data-ask-event="${escapeHtml(citation.event_id)}">
              <span class="ask-evidence-index">${String(index + 1).padStart(2, "0")}</span>
              <span class="type-badge">${escapeHtml(event ? labels[event.type] : "Evidence")}</span>
              <strong>${escapeHtml(event?.title || citation.event_id)}</strong>
              <p>${escapeHtml(citation.claim)}</p>
              <span class="ask-ref-row"><code>${escapeHtml(event?.short_hash || citation.event_id)}</code><span>${citation.evidence_refs.length} refs</span><b>OPEN EVENT →</b></span>
            </button>`;
          }).join("")}
        </div>
      </section>
      <section class="ask-unknowns">
        <p class="section-label">WHAT THE REPOSITORY CANNOT PROVE</p>
        <ul>${answer.missing_evidence.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </section>
    </div>
    ${provenance ? `<footer class="trace-audit"><span><i></i>Answer set verified against current Git evidence</span><code>evidence ${escapeHtml(provenance.evidence_sha256.slice(0, 10))}</code><code>session ${escapeHtml(provenance.codex_session_id?.slice(0, 13) || "not recorded")}</code></footer>` : ""}`;
}

async function askRepo(questionId) {
  const overlay = document.querySelector("#ask-overlay");
  const window = document.querySelector("#ask-answer-window");
  overlay.hidden = false;
  state.askReturnFocus = document.activeElement;
  document.body.classList.add("ask-open");
  window.innerHTML = `<button class="trace-close loading-close" data-close-ask aria-label="Close answer">×</button><div class="ask-loading"><div class="ask-loader">?</div><p class="eyebrow">READING REPOSITORY EVIDENCE</p><h2 id="ask-answer-title">Following commits, files, and recorded risks…</h2></div>`;
  window.querySelectorAll("[data-close-ask]").forEach((button) => button.addEventListener("click", closeAsk));
  try {
    if (!state.answers[questionId]) {
      state.answers[questionId] = await requestJson(
        "/api/projects/orbitcart/ask",
        `./demo-data/ask-${questionId}.json`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question_id: questionId }),
        },
      );
    }
    window.innerHTML = renderAskAnswer(state.answers[questionId]);
    window.scrollTop = 0;
    window.querySelectorAll("[data-close-ask]").forEach((button) => button.addEventListener("click", closeAsk));
    window.querySelector("[data-close-ask]")?.focus();
    window.querySelectorAll("[data-ask-event]").forEach((button) => {
      button.addEventListener("click", () => {
        closeAsk();
        showAllEvents();
        selectEvent(button.dataset.askEvent);
        document.querySelector(".workspace").scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  } catch (error) {
    window.innerHTML = `<button class="trace-close loading-close" data-close-ask aria-label="Close answer">×</button><div class="ask-loading"><strong>Answer unavailable</strong><p>${escapeHtml(error.message)}</p></div>`;
    window.querySelectorAll("[data-close-ask]").forEach((button) => button.addEventListener("click", closeAsk));
  }
}

function traceNode(item, index, analysis) {
  const event = state.events.find((candidate) => candidate.id === item.event_id);
  if (!event) return "";
  const isOrigin = item.event_id === analysis.origin_event_id;
  return `
    <button class="trace-node ${escapeHtml(item.role)} ${isOrigin ? "suspected-origin" : ""}" data-trace-event="${escapeHtml(item.event_id)}" style="--step:${index}">
      <span class="trace-node-index">${String(index + 1).padStart(2, "0")}</span>
      <span class="trace-node-role">${escapeHtml(item.role)}</span>
      <strong>${escapeHtml(event.title)}</strong>
      <p>${escapeHtml(item.explanation)}</p>
      <span class="trace-evidence"><code>${escapeHtml(event.short_hash)}</code>${item.evidence_refs.length} evidence refs</span>
      ${isOrigin ? '<span class="origin-flag">LIKELY ORIGIN</span>' : ""}
    </button>`;
}

function renderInvestigation(analysis) {
  const sourceLabel = analysis.source === "codex-gpt-5.6"
    ? "GPT-5.6 Sol in Codex · validated"
    : analysis.source === "gpt-5.6"
      ? `GPT-5.6 API · ${analysis.delivery}`
      : "Evidence fallback · demo safe";
  const sourceClass = analysis.source === "codex-gpt-5.6" ? "codex" : analysis.source === "gpt-5.6" ? "live" : "fallback";
  const origin = state.events.find((event) => event.id === analysis.origin_event_id);
  const provenance = analysis.provenance || null;
  return `
    <header class="trace-header">
      <div><p class="eyebrow">BUG ORIGIN TRACE / OC-52</p><h2 id="trace-title">Rewinding the stale-price incident</h2></div>
      <div class="trace-header-actions"><span class="analysis-source ${sourceClass}"><i></i>${escapeHtml(sourceLabel)}</span><button class="trace-close" data-close-trace aria-label="Close investigation">×</button></div>
    </header>
    <div class="trace-summary">
      <div class="trace-verdict-icon"><span>↶</span></div>
      <div class="trace-verdict"><span class="trace-kicker">CAUSAL VERDICT</span><h3>${escapeHtml(analysis.headline)}</h3><p>${escapeHtml(analysis.finding)}</p></div>
      <div class="trace-score"><span>${Math.round(analysis.confidence * 100)}%</span><small>${escapeHtml(analysis.certainty)} confidence</small></div>
    </div>
    <div class="trace-map-heading"><span>EARLIER</span><p>ENGINEERING CAUSAL CHAIN</p><span>LATER →</span></div>
    <div class="trace-map">
      ${analysis.causal_chain.map((item, index) => traceNode(item, index, analysis)).join('<span class="trace-arrow">→</span>')}
    </div>
    <div class="trace-footer-grid">
      <section class="origin-evidence">
        <p class="section-label">WHY THIS IS THE LIKELY ORIGIN</p>
        <div><span class="origin-pulse"></span><p><strong>${escapeHtml(origin?.short_hash || "Unknown")}</strong> explicitly introduced indefinite price storage while recording that no invalidation path existed.</p></div>
      </section>
      <section>
        <p class="section-label">WHAT WE STILL DON'T KNOW</p>
        <ul>${analysis.missing_evidence.slice(0, 2).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </section>
      <section>
        <p class="section-label">REMAINING RISK</p>
        <ul>${analysis.risks.slice(0, 2).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </section>
    </div>
    ${provenance ? `<footer class="trace-audit"><span><i></i>Artifact verified against current Git evidence</span><code>evidence ${escapeHtml(provenance.evidence_sha256.slice(0, 10))}</code><code>session ${escapeHtml(provenance.codex_session_id?.slice(0, 13) || "not recorded")}</code></footer>` : ""}`;
}

async function openTrace() {
  const overlay = document.querySelector("#trace-overlay");
  const window = document.querySelector("#trace-window");
  overlay.hidden = false;
  state.traceReturnFocus = document.activeElement;
  document.body.classList.add("trace-open");
  window.innerHTML = `
    <button class="trace-close loading-close" data-close-trace aria-label="Close investigation">×</button>
    <div class="trace-loading"><div class="rewind-loader"><span></span><i></i></div><p class="eyebrow">RECONSTRUCTING CAUSALITY</p><h2 id="trace-title">Rewinding repository evidence…</h2><small>Commits, file changes, risks, and fixes are being connected.</small></div>`;
  window.querySelectorAll("[data-close-trace]").forEach((button) => button.addEventListener("click", closeTrace));
  try {
    if (!state.investigation) {
      state.investigation = await requestJson(
        "/api/projects/orbitcart/investigations/bug-origin",
        "./demo-data/investigation.json",
        { method: "POST" },
      );
    }
    window.innerHTML = renderInvestigation(state.investigation);
    window.scrollTop = 0;
    window.querySelectorAll("[data-close-trace]").forEach((button) => button.addEventListener("click", closeTrace));
    window.querySelector("[data-close-trace]")?.focus();
    window.querySelectorAll("[data-trace-event]").forEach((button) => {
      button.addEventListener("click", () => {
        closeTrace();
        showAllEvents();
        selectEvent(button.dataset.traceEvent);
      });
    });
  } catch (error) {
    window.innerHTML = `<button class="trace-close loading-close" data-close-trace aria-label="Close investigation">×</button><div class="trace-loading"><strong>Trace unavailable</strong><p>${escapeHtml(error.message)}</p></div>`;
    window.querySelectorAll("[data-close-trace]").forEach((button) => button.addEventListener("click", closeTrace));
  }
}

async function loadTimeline() {
  try {
    const data = await requestJson(
      "/api/projects/orbitcart/timeline",
      "./demo-data/timeline.json",
    );
    state.events = data.events;
    document.querySelector("#project-name").textContent = data.project.name;
    document.querySelector("#project-description").textContent = data.project.description;
    document.querySelector("#branch-name").textContent = data.project.branch;
    document.querySelector("#stat-commits").textContent = data.stats.commits;
    document.querySelector("#stat-bugs").textContent = data.stats.bugs;
    document.querySelector("#stat-files").textContent = data.stats.files_touched;
    document.querySelector("#stat-coverage").textContent = `${Math.round((data.stats.confirmed / data.stats.commits) * 100)}%`;
    renderTimeline();
    const headline = state.events.find((event) => event.title.toLowerCase().includes("stale checkout"));
    selectEvent(headline?.id || state.events.at(-1)?.id);
  } catch (error) {
    timeline.innerHTML = `<div class="error-state"><strong>History unavailable</strong><p>${escapeHtml(error.message)}</p><small>Run python3 scripts/create_orbitcart.py, then restart the server.</small></div>`;
  }
}

document.querySelectorAll(".filter").forEach((button) => {
  button.addEventListener("click", () => {
    state.filter = button.dataset.filter;
    document.querySelectorAll(".filter").forEach((item) => {
      item.classList.toggle("active", item === button);
      item.setAttribute("aria-pressed", String(item === button));
    });
    renderTimeline();
  });
});

document.querySelectorAll("[data-close-trace]").forEach((element) => element.addEventListener("click", closeTrace));
document.querySelectorAll("[data-ask-question]").forEach((button) => button.addEventListener("click", () => askRepo(button.dataset.askQuestion)));
document.querySelectorAll("[data-close-ask]").forEach((element) => element.addEventListener("click", closeAsk));
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !document.querySelector("#trace-overlay").hidden) closeTrace();
  if (event.key === "Escape" && !document.querySelector("#ask-overlay").hidden) closeAsk();
});

loadTimeline();
