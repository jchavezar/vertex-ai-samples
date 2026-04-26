/* Vector Search Canvas — single-file front end.
   No frameworks, no build step. Reads toggle state, fires /api/search,
   renders both columns side-by-side, computes recall delta. */

const $  = sel => document.querySelector(sel);
const $$ = sel => Array.from(document.querySelectorAll(sel));

const STATE = {
  algorithm: "both",
  k: 20,
  leaf: 0,
  crowd: 0,
  modality_allow: new Set(),
  modality_deny:  new Set(),
  return_full:    false,
};

// ───────────────────────── toggle wiring ─────────────────────────
function wireSeg(rootSel, key, onchange) {
  const root = $(rootSel);
  if (!root) return;
  root.addEventListener("click", e => {
    const btn = e.target.closest(".seg__btn");
    if (!btn) return;
    root.querySelectorAll(".seg__btn").forEach(b => b.classList.remove("is-active"));
    btn.classList.add("is-active");
    STATE[key] = btn.dataset.v;
    onchange?.();
  });
}

function wireSlider(inputSel, valSel, key, onchange) {
  const input = $(inputSel);
  const val   = $(valSel);
  input.addEventListener("input", () => {
    STATE[key] = Number(input.value);
    if (val) val.textContent = input.value;
    onchange?.();
  });
}

function wireChips(rootSel, key, onchange) {
  const root = document.querySelector(`.chips[data-name="${key}"]`);
  if (!root) return;
  root.addEventListener("click", e => {
    const c = e.target.closest(".chip");
    if (!c) return;
    c.classList.toggle("is-active");
    const set = STATE[key];
    if (c.classList.contains("is-active")) set.add(c.dataset.v);
    else set.delete(c.dataset.v);
    onchange?.();
  });
}

function wireSwitch(inputSel, key, onchange) {
  $(inputSel).addEventListener("change", e => {
    STATE[key] = e.target.checked;
    onchange?.();
  });
}

// ───────────────────────── code preview ─────────────────────────
function buildKwargsPreview() {
  const lines = [];
  lines.push(`<span class="c"># server side — these are the find_neighbors() kwargs</span>`);
  lines.push(`endpoint.find_neighbors(`);

  const algo = STATE.algorithm;
  if (algo === "tree_ah" || algo === "both") {
    lines.push(`  <span class="k">deployed_index_id</span>=<span class="s">"vs_canvas_tree_ah"</span>,  <span class="c"># TREE_AH (ScaNN, approximate)</span>`);
  } else {
    lines.push(`  <span class="k">deployed_index_id</span>=<span class="s">"vs_canvas_brute"</span>,  <span class="c"># BRUTE_FORCE (exact)</span>`);
  }
  lines.push(`  <span class="k">queries</span>=[q_vec],  <span class="c"># 3072-d gemini-embedding-2</span>`);
  lines.push(`  <span class="k">num_neighbors</span>=<span class="n">${STATE.k}</span>,`);
  lines.push(`  <span class="k">return_full_datapoint</span>=<span class="b">${STATE.return_full ? "True" : "False"}</span>,`);

  const allow = [...STATE.modality_allow];
  const deny  = [...STATE.modality_deny];
  if (allow.length || deny.length) {
    lines.push(`  <span class="k">filter</span>=[`);
    lines.push(`    Namespace(`);
    lines.push(`      <span class="k">name</span>=<span class="s">"modality"</span>,`);
    if (allow.length) lines.push(`      <span class="k">allow_tokens</span>=[${allow.map(v => `<span class="s">"${v}"</span>`).join(", ")}],`);
    if (deny.length)  lines.push(`      <span class="k">deny_tokens</span>=[${deny.map(v => `<span class="s">"${v}"</span>`).join(", ")}],`);
    lines.push(`    ),`);
    lines.push(`  ],`);
  }
  if (STATE.crowd > 0) {
    lines.push(`  <span class="k">per_crowding_attribute_num_neighbors</span>=<span class="n">${STATE.crowd}</span>,`);
  }
  if (STATE.leaf > 0 && (algo === "tree_ah" || algo === "both")) {
    lines.push(`  <span class="k">leaf_nodes_to_search_percent_override</span>=<span class="n">${STATE.leaf}</span>,  <span class="c"># default = 10</span>`);
  }
  lines.push(`)`);

  if (algo === "both") {
    lines.push(``);
    lines.push(`<span class="c"># …then we run the same query against vs_canvas_brute and</span>`);
    lines.push(`<span class="c"># compute |approx ∩ exact| / |exact| → recall@k</span>`);
  }
  return lines.join("\n");
}

function refreshCode() {
  $("#code").innerHTML = buildKwargsPreview();
}

// ───────────────────────── search ─────────────────────────
async function runSearch() {
  const q = $("#q").value.trim();
  if (!q) return;

  $("#go").disabled = true;
  $("#go").textContent = "…";
  setLoading(true);

  const body = {
    query: q,
    num_neighbors: STATE.k,
    algorithm: STATE.algorithm,
    modality_allow: [...STATE.modality_allow],
    modality_deny:  [...STATE.modality_deny],
    per_crowding_attribute_num_neighbors: STATE.crowd,
    return_full_datapoint: STATE.return_full,
    leaf_nodes_to_search_percent_override: STATE.leaf,
  };

  let data;
  try {
    const resp = await fetch("/api/search", {
      method: "POST",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(body),
    });
    data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || resp.statusText);
  } catch (e) {
    renderError(e.message);
    $("#go").disabled = false;
    $("#go").textContent = "Search";
    setLoading(false);
    return;
  }

  $("#go").disabled = false;
  $("#go").textContent = "Search";
  setLoading(false);

  renderResults(data);
}

function setLoading(on) {
  for (const id of ["m-embed","m-approx","m-exact","m-recall","m-overlap"]) {
    if (on) $("#"+id).textContent = "…";
  }
}

function renderError(msg) {
  $("#list-approx").innerHTML = `<li class="empty">${escapeHtml(msg)}</li>`;
  $("#list-exact").innerHTML  = `<li class="empty">${escapeHtml(msg)}</li>`;
}

function renderResults(d) {
  $("#m-embed").textContent  = d.embed_ms ?? "–";
  $("#m-approx").textContent = d.tree_ah?.latency_ms ?? "–";
  $("#m-exact").textContent  = d.brute_force?.latency_ms ?? "–";

  const approxHits = d.tree_ah?.hits || [];
  const exactHits  = d.brute_force?.hits || [];

  const exactIds  = new Set(exactHits.map(h => h.id));
  const approxIds = new Set(approxHits.map(h => h.id));

  $("#list-approx").innerHTML = approxHits.length
    ? approxHits.map((h, i) => renderHit(h, i, exactIds.has(h.id), false)).join("")
    : `<li class="empty">no approx run for this algorithm choice</li>`;

  $("#list-exact").innerHTML = exactHits.length
    ? exactHits.map((h, i) => renderHit(h, i, approxIds.has(h.id), !approxIds.has(h.id))).join("")
    : `<li class="empty">no brute run for this algorithm choice</li>`;

  // recall metric
  const m = d.recall;
  const box = $(".metric--big");
  box.classList.remove("is-warn", "is-bad");
  if (m && m.recall != null) {
    const pct = Math.round(m.recall * 100);
    $("#m-recall").textContent = pct + "%";
    $("#m-overlap").textContent = `${m.overlap}/${m.k} shared`;
    if (pct < 70) box.classList.add("is-bad");
    else if (pct < 90) box.classList.add("is-warn");
  } else {
    $("#m-recall").textContent = "–";
    $("#m-overlap").textContent = "run both to compare";
  }
}

function renderHit(h, idx, shared, missed) {
  const cls = missed ? "hit hit--missed" : (shared ? "hit hit--shared" : "hit");
  const sim = (h.similarity * 100).toFixed(1);
  return `<li class="${cls}">
    <span class="hit__rank">#${idx+1}</span>
    <span class="hit__id" title="${escapeHtml(h.id)}">${escapeHtml(h.id)}</span>
    <span class="hit__sim">${sim}%</span>
  </li>`;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"
  }[c]));
}

// ───────────────────────── health ─────────────────────────
async function checkHealth() {
  const chip = $("#health");
  try {
    const r = await fetch("/api/health");
    const d = await r.json();
    if (d.tree_ah_ready && d.brute_ready) {
      chip.textContent = "both indexes deployed ●";
      chip.classList.remove("env__chip--warn","env__chip--err");
      chip.classList.add("env__chip--ok");
    } else if (d.tree_ah_ready || d.brute_ready) {
      chip.textContent = `partial: ${d.deployed_ids.join(",")}`;
      chip.classList.add("env__chip--warn");
    } else {
      chip.textContent = "indexes not ready (still deploying)";
      chip.classList.add("env__chip--warn");
    }
  } catch (e) {
    chip.textContent = "offline";
    chip.classList.remove("env__chip--warn","env__chip--ok");
    chip.classList.add("env__chip--err");
  }
}

// ───────────────────────── boot ─────────────────────────
function boot() {
  wireSeg(".seg[data-name=algorithm]", "algorithm", refreshCode);
  wireSlider("#k", "#k-val", "k", refreshCode);
  wireSlider("#leaf", "#leaf-val", "leaf", refreshCode);
  wireSlider("#crowd", "#crowd-val", "crowd", refreshCode);
  wireChips(null, "modality_allow", refreshCode);
  wireChips(null, "modality_deny",  refreshCode);
  wireSwitch("#returnfull", "return_full", refreshCode);

  $("#go").addEventListener("click", runSearch);
  $("#q").addEventListener("keydown", e => { if (e.key === "Enter") runSearch(); });

  refreshCode();
  checkHealth();
  setInterval(checkHealth, 15_000);
}

document.addEventListener("DOMContentLoaded", boot);
