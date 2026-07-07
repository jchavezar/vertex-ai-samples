// Admin-only side-by-side comparison view for a player's cromo. Renders a tiny
// HTML skeleton with <img> tags that hit /api/maint/cromo-compare/variant on
// demand, so the 4 variants stream in progressively instead of one ~12MB
// monolithic response. Identity pipeline (loadRefPhotos + PLAYER_IDENTITY) lives
// in the variant endpoint and the live cromo route — both share generatePortrait.
//
// GET /api/maint/cromo-compare?playerId=jochabe&secret=...&styles=0,1,3,4

import { NextRequest } from "next/server";
import { promises as fs } from "node:fs";
import path from "node:path";
import { PLAYERS } from "@/data/players";
import { PLAYER_IDENTITY } from "@/data/player-identity";
import { db } from "@/lib/firestore-server";
import { PORTRAIT_STYLES } from "@/app/api/cromos/portrait/route";
import { isAdminRequest } from "@/lib/admin-gate";
import { listKeepers } from "@/app/api/maint/cromo-compare/keeper/route";
import { getIdentityOverride } from "@/lib/identity-override";
import { listDeletedRefs } from "@/lib/deleted-refs";
import { listActiveGcsRefs } from "@/lib/active-gcs-refs";

// Compare page references public/ assets directly via URL — avoids embedding
// 12MB of base64 refs into the HTML. loadRefPhotos is still used by the actual
// generation pipeline (variant endpoint via generatePortrait).
//
// Three buckets returned so the workshop can show what the model USES (active),
// what was set aside as too noisy (archived), and what the player uploaded via
// the app but hasn't been promoted into refs/ yet (uploaded). All three are
// visible so the admin can decide what to promote / demote.
type RefBuckets = {
  active: string[];    // loaded by loadRefPhotos → fed to the model
  archived: string[];  // refs/{id}/_multi-people/* — intentionally excluded
  uploaded: string[];  // GCS player_avatars/{id}/photo_history (source=uploaded)
};
async function listRefUrls(playerId: string): Promise<RefBuckets> {
  const allowed = new Set([".jpg", ".jpeg", ".png", ".webp"]);
  const baseExts = [".jpg", ".jpeg", ".png", ".webp"];
  const active: string[] = [];
  const archived: string[] = [];
  const uploaded: string[] = [];
  const deleted = await listDeletedRefs(playerId);
  const keep = (url: string) => !deleted.has(url);

  for (const ext of baseExts) {
    try {
      await fs.access(path.join(process.cwd(), "public", "players", `${playerId}${ext}`));
      const url = `/players/${playerId}${ext}`;
      if (keep(url)) active.push(url);
      break;
    } catch { /* try next */ }
  }
  try {
    const refsDir = path.join(process.cwd(), "public", "players", "refs", playerId);
    const entries = await fs.readdir(refsDir);
    for (const name of entries.sort()) {
      if (allowed.has(path.extname(name).toLowerCase())) {
        const url = `/players/refs/${playerId}/${name}`;
        if (keep(url)) active.push(url);
      }
    }
  } catch { /* no refs dir */ }
  try {
    const archivedDir = path.join(process.cwd(), "public", "players", "refs", playerId, "_multi-people");
    const entries = await fs.readdir(archivedDir);
    for (const name of entries.sort()) {
      if (allowed.has(path.extname(name).toLowerCase())) {
        const url = `/players/refs/${playerId}/_multi-people/${name}`;
        if (keep(url)) archived.push(url);
      }
    }
  } catch { /* none */ }
  // GCS-backed active refs (uploaded via the workshop drop-zone) — same
  // bucket as the model sees, so list them under "active".
  const gcsRefs = await listActiveGcsRefs(playerId);
  for (const url of gcsRefs) if (keep(url)) active.push(url);
  // Pull every uploaded photo from photo_history. Generated/AI photos are
  // skipped — they would corrupt identity if used as refs.
  try {
    const snap = await db.collection("player_avatars").doc(playerId).collection("photo_history").get();
    for (const doc of snap.docs) {
      const d = doc.data() as { url?: string; source?: string };
      if (d.source === "uploaded" && d.url && keep(d.url)) uploaded.push(d.url);
    }
  } catch { /* firestore unreachable — fine */ }
  return { active, archived, uploaded };
}

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

function escape(s: string): string {
  return s.replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]!));
}

export async function GET(req: NextRequest) {
  if (!(await isAdminRequest(req))) {
    return new Response("forbidden", { status: 403 });
  }
  const { searchParams } = new URL(req.url);
  const playerId = (searchParams.get("playerId") ?? "").trim();
  if (!playerId) return new Response("playerId required", { status: 400 });
  if (!PLAYERS.some(p => p.id === playerId)) {
    return new Response("unknown player", { status: 400 });
  }
  // Probe mode: 6 diagnostic styles covering each failure mode (photoreal
  // baseline, photoreal stress, illustrated baseline, illustrated stress,
  // mask coverage, extreme stylization). If face holds across these, the
  // other 34 styles will too — saves the cost of generating all 40 blind.
  const PROBE_NAMES = [
    "ultimate-team",   // photoreal baseline
    "polaroid",        // photoreal stress (film grain / light leak)
    "manga-shonen",    // illustrated baseline
    "comic-pop",       // illustrated stress (heavy pop-art)
    "lucha-libre",     // wearable / mask translucent guardrail
    "alebrije",        // extreme stylization
  ];
  const stylesParam = searchParams.get("styles");
  const probe = searchParams.get("probe") === "1";
  const styleIdxs = stylesParam
    ? stylesParam.split(",").map(s => parseInt(s, 10)).filter(n => Number.isFinite(n) && n >= 0 && n < PORTRAIT_STYLES.length)
    : probe
      ? PROBE_NAMES.map(n => PORTRAIT_STYLES.findIndex(s => s.name === n)).filter(i => i >= 0)
      : PORTRAIT_STYLES.map((_, i) => i);

  // Load refs + current cromo doc + keeper list — all small, non-blocking for the model.
  const [refUrls, cromoSnap, keeperSet] = await Promise.all([
    listRefUrls(playerId),
    (async () => {
      try {
        const today = new Intl.DateTimeFormat("en-CA", {
          timeZone: "America/New_York",
          year: "numeric", month: "2-digit", day: "2-digit",
        }).format(new Date());
        const s = await db.collection("cromo_portraits").doc(`${playerId}_${today}`).get();
        return s.exists ? (s.data() as { url?: string; style?: string; createdAt?: number }) : null;
      } catch (err) {
        console.warn("[cromo-compare] firestore lookup failed (non-fatal)", err instanceof Error ? err.message : err);
        return null;
      }
    })(),
    listKeepers(playerId),
  ]);

  const identityOverride = await getIdentityOverride(playerId);
  const identityFile = PLAYER_IDENTITY[playerId] ?? "";
  const identityEffective = identityOverride ?? identityFile ?? "(no entry — using generic fallback)";
  const identitySource = identityOverride ? "firestore-override" : identityFile ? "file" : "fallback";
  const renderRef = (url: string, i: number, label: string) =>
    `<figure class="ref-fig" data-ref-url="${escape(url)}">
      <img src="${escape(url)}" alt="${escape(label)} ${i + 1}" loading="lazy"/>
      <button type="button" class="ref-delete" title="eliminar permanentemente">×</button>
      <figcaption>${escape(label)} ${i + 1}</figcaption>
    </figure>`;
  const activeImgs   = refUrls.active.map((u, i) => renderRef(u, i, "active")).join("");
  const archivedImgs = refUrls.archived.map((u, i) => renderRef(u, i, "archived")).join("");
  const uploadedImgs = refUrls.uploaded.map((u, i) => renderRef(u, i, "uploaded")).join("");
  const variantImgs = styleIdxs.map((idx, i) => {
    const styleName = PORTRAIT_STYLES[idx]?.name ?? `style-${idx}`;
    const isKeeper = keeperSet.has(styleName);
    const src = `/api/maint/cromo-compare/variant?playerId=${encodeURIComponent(playerId)}&style=${idx}`;
    return `<figure class="variant${isKeeper ? " keeper" : ""}" data-variant="${i}" data-style="${escape(styleName)}" data-idx="${idx}" data-src="${src}">
      <div class="img-wrap">
        <div class="spinner">${isKeeper ? "cargando keeper…" : "generando…"}</div>
        <img src="${src}" alt="${escape(styleName)}" loading="lazy" onload="this.previousElementSibling && this.previousElementSibling.remove()" onerror="this.parentElement.innerHTML='<div class=\\'error\\'>generation failed</div>'"/>
      </div>
      <figcaption>${escape(styleName)} <button type="button" class="reroll" title="regenerar (bypass keeper)">🎲</button></figcaption>
      <div class="vote">
        <button type="button" data-vote="face_good">👍 cara</button>
        <button type="button" data-vote="face_bad">👎 cara</button>
        <button type="button" data-vote="style_good">✨ estilo</button>
        <button type="button" class="keeper-btn${isKeeper ? " active" : ""}" data-vote="keeper">⭐ keeper</button>
      </div>
      <div class="extra-row">
        <input type="text" class="extra-input" placeholder="tweak: ej. 'mirando 3/4 a la izquierda, sonrisa más amplia'" />
        <button type="button" class="reroll-extra" title="regenerar con esta indicación">↻</button>
      </div>
    </figure>`;
  }).join("");
  const currentImg = cromoSnap?.url
    ? `<figure><img src="${escape(cromoSnap.url)}?v=${cromoSnap.createdAt ?? 0}" alt="current"/><figcaption>actual prod · ${escape(cromoSnap.style ?? "?")}</figcaption></figure>`
    : `<p>no cached cromo today</p>`;

  const html = `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>cromo-compare · ${escape(playerId)}</title>
<style>
  :root { color-scheme: dark; }
  body { font-family: ui-sans-serif, system-ui, sans-serif; background: #0b0d12; color: #e6e9f0; margin: 0; padding: 24px; }
  h1 { margin: 0 0 4px 0; font-size: 20px; }
  h2 { margin: 32px 0 12px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 0.06em; color: #9aa3b2; }
  .identity { background: #161a22; border: 1px solid #232836; border-radius: 8px; padding: 12px 14px; font-size: 13px; line-height: 1.55; color: #cfd6e2; }
  .row { display: flex; flex-wrap: wrap; gap: 16px; }
  figure { margin: 0; max-width: 280px; }
  figure img { width: 100%; height: auto; border-radius: 10px; display: block; background: #1a1f2b; }
  figcaption { font-size: 12px; color: #9aa3b2; margin-top: 6px; text-align: center; }
  figure.variant .img-wrap { position: relative; width: 280px; min-height: 280px; }
  figure.variant img { border: 2px solid #2c7bff; transition: border-color 0.15s; }
  figure.variant.keeper img { border-color: #ffd54f; box-shadow: 0 0 18px #ffd54f55; }
  .spinner { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: #1a1f2b; border: 2px solid #2c7bff; border-radius: 10px; color: #9aa3b2; font-size: 12px; }
  .error { width: 280px; height: 280px; display: flex; align-items: center; justify-content: center; background: #2a0e0e; color: #ff6b6b; border-radius: 10px; font-size: 13px; }
  .meta { font-size: 12px; color: #7f8a9b; margin-top: 4px; }
  .vote { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; justify-content: center; }
  .vote button { background: #1c2230; color: #e6e9f0; border: 1px solid #2e3647; border-radius: 6px; padding: 4px 8px; font-size: 11px; cursor: pointer; }
  .vote button:hover { background: #2a3344; }
  .vote button.active { background: #2c7bff; border-color: #2c7bff; color: #fff; }
  .reroll { background: none; border: 1px solid #2e3647; color: #9aa3b2; border-radius: 4px; padding: 0 6px; font-size: 11px; cursor: pointer; margin-left: 4px; }
  .reroll:hover { background: #1c2230; color: #e6e9f0; }
  .extra-row { display: flex; gap: 4px; margin-top: 6px; }
  .extra-input { flex: 1; background: #0b0d12; color: #e6e9f0; border: 1px solid #2e3647; border-radius: 4px; padding: 4px 6px; font-size: 11px; font-family: inherit; min-width: 0; }
  .reroll-extra { background: #2c7bff; border: 1px solid #2c7bff; color: #fff; border-radius: 4px; padding: 0 10px; font-size: 11px; cursor: pointer; }
  .reroll-extra:hover { background: #4090ff; }
  .identity-editor { background: #161a22; border: 1px solid #232836; border-radius: 8px; padding: 12px 14px; }
  .identity-editor textarea { width: 100%; min-height: 140px; background: #0b0d12; color: #e6e9f0; border: 1px solid #2e3647; border-radius: 6px; padding: 8px 10px; font-family: inherit; font-size: 13px; line-height: 1.55; box-sizing: border-box; resize: vertical; }
  .identity-editor .row-actions { display: flex; gap: 8px; align-items: center; margin-top: 10px; flex-wrap: wrap; }
  .identity-editor button { background: #2c7bff; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; }
  .identity-editor button:hover { background: #4090ff; }
  .identity-editor button.danger { background: #1c2230; color: #ff8a8a; border: 1px solid #532a2a; }
  .identity-editor button.danger:hover { background: #2a1414; }
  .identity-editor .source { font-size: 11px; color: #7f8a9b; }
  .identity-editor .status { font-size: 12px; color: #6dd5a0; }
  .ref-fig { position: relative; }
  .ref-delete { position: absolute; top: 6px; right: 6px; width: 26px; height: 26px; border-radius: 50%; border: 1px solid #532a2a; background: rgba(11,13,18,0.85); color: #ff8a8a; font-size: 16px; line-height: 1; cursor: pointer; display: grid; place-items: center; opacity: 0; transition: opacity 0.15s; }
  .ref-fig:hover .ref-delete { opacity: 1; }
  .ref-delete:hover { background: #2a1414; }
  .ref-fig.deleting { opacity: 0.4; pointer-events: none; }
  .dropzone { background: #11151d; border: 2px dashed #2e3647; border-radius: 10px; padding: 18px 16px; margin-bottom: 14px; text-align: center; cursor: pointer; transition: border-color 0.15s, background 0.15s; }
  .dropzone:hover, .dropzone.over { border-color: #2c7bff; background: #141a26; }
  .dz-text { color: #cfd6e2; font-size: 13px; line-height: 1.5; }
  .dz-text strong { color: #fff; }
  .dz-hint { font-size: 11px; color: #7f8a9b; margin-top: 4px; }
  .dz-status { margin-top: 8px; font-size: 12px; color: #6dd5a0; min-height: 16px; }
  .feedback { margin-top: 24px; background: #161a22; border: 1px solid #232836; border-radius: 8px; padding: 14px; }
  .feedback textarea { width: 100%; min-height: 80px; background: #0b0d12; color: #e6e9f0; border: 1px solid #2e3647; border-radius: 6px; padding: 8px 10px; font-family: inherit; font-size: 13px; box-sizing: border-box; resize: vertical; }
  .feedback button.submit { margin-top: 10px; background: #2c7bff; color: #fff; border: none; padding: 8px 18px; border-radius: 6px; cursor: pointer; font-size: 13px; }
  .feedback button.submit:hover { background: #4090ff; }
  .feedback .status { margin-top: 8px; font-size: 12px; color: #9aa3b2; }
</style>
</head>
<body>
<h1>cromo-compare · ${escape(playerId)}</h1>
<div class="meta">${refUrls.active.length} active · ${refUrls.archived.length} archived · ${refUrls.uploaded.length} uploaded via app · ${styleIdxs.length} variants on demand (lazy) · ${keeperSet.size} keeper${keeperSet.size === 1 ? "" : "s"} saved</div>

<h2>identity lock · editor</h2>
<div class="identity-editor">
  <textarea id="id-text" placeholder="describe la cara (anti-celebridad, anclas físicas, etc)">${escape(identityEffective)}</textarea>
  <div class="row-actions">
    <button id="id-save" type="button">guardar override</button>
    <button id="id-reset" type="button" class="danger" ${identitySource === "firestore-override" ? "" : "disabled style=\"opacity:.4;cursor:not-allowed\""}>quitar override (volver a archivo)</button>
    <span class="source">fuente actual: <strong>${identitySource}</strong></span>
    <span class="status" id="id-status"></span>
  </div>
  <p style="font-size:11px;color:#7f8a9b;margin:8px 0 0 0">El texto se inyecta en los 40 estilos automáticamente. Cambios aplican en la siguiente generación (re-rolear cromos para que tome efecto).</p>
</div>

<h2>reference photos · active (fed to the model)</h2>
<div id="dropzone" class="dropzone">
  <input type="file" id="ref-file" accept="image/png,image/jpeg,image/webp" multiple style="display:none"/>
  <div class="dz-text">
    <strong>Arrastra una foto aquí</strong>, click para elegir, o <strong>pega del portapapeles (⌘V)</strong> con la página enfocada.
    <div class="dz-hint">Se guarda en GCS y se vuelve ref activa al instante — sin redeploy.</div>
  </div>
  <div class="dz-status" id="dz-status"></div>
</div>
<div class="row">${activeImgs || "<p style=\"color:#9aa3b2\">(none — model has nothing to anchor identity to)</p>"}</div>

<h2>archived refs · in _multi-people/ (NOT fed to the model)</h2>
<div class="row">${archivedImgs || "<p style=\"color:#9aa3b2\">(none)</p>"}</div>

<h2>uploaded via app · not yet promoted to active refs</h2>
<div class="row">${uploadedImgs || "<p style=\"color:#9aa3b2\">(none uploaded in /perfil/foto)</p>"}</div>

<h2>cromo actual en prod</h2>
<div class="row">${currentImg}</div>

<h2>variantes generadas con el nuevo pipeline (multi-foto + identity lock)</h2>
<div class="row">${variantImgs}</div>

<div class="feedback">
  <h2 style="margin-top:0">tu feedback (HIL → claude)</h2>
  <p style="font-size:12px;color:#9aa3b2;margin:0 0 10px 0">Marca los votos en cada variante. Escribe abajo dirección concreta: ej. "la cara de la #2 pero el estilo de la #4", "subir cachetes", "ojos más cerrados, sonrisa más abierta".</p>
  <textarea id="fb-notes" placeholder="ej. la #2 tiene la mejor cara. la #4 buen estilo pero cara delgada. probemos variantes con más volumen de cachetes."></textarea>
  <button class="submit" id="fb-submit" type="button">enviar feedback</button>
  <div class="status" id="fb-status"></div>
</div>

<script>
(function() {
  const votes = {};
  const playerId = ${JSON.stringify(playerId)};
  const keeperUrl = (idx) => '/api/maint/cromo-compare/keeper?playerId=' + encodeURIComponent(playerId) + '&style=' + idx;
  document.querySelectorAll('figure.variant').forEach(fig => {
    const i = fig.dataset.variant;
    const styleIdx = fig.dataset.idx;
    const style = fig.dataset.style;
    votes[i] = { style, votes: fig.classList.contains('keeper') ? ['keeper'] : [] };
    fig.querySelectorAll('button[data-vote]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const v = btn.dataset.vote;
        const arr = votes[i].votes;
        const j = arr.indexOf(v);
        const wasActive = j >= 0;
        if (wasActive) { arr.splice(j, 1); btn.classList.remove('active'); }
        else { arr.push(v); btn.classList.add('active'); }
        if (v === 'keeper') {
          fig.classList.toggle('keeper', !wasActive);
          if (!wasActive) {
            btn.disabled = true; btn.textContent = '⭐ guardando…';
            try {
              const im = fig.querySelector('img');
              const blob = await fetch(im.src).then(r => r.blob());
              const r = await fetch(keeperUrl(styleIdx), { method: 'POST', headers: { 'content-type': 'image/png' }, body: blob });
              if (!r.ok) throw new Error('save failed');
              btn.textContent = '⭐ keeper';
            } catch (e) {
              btn.textContent = '⭐ keeper'; alert('keeper save failed: ' + e.message);
              arr.pop(); btn.classList.remove('active'); fig.classList.remove('keeper');
            } finally { btn.disabled = false; }
          } else {
            btn.disabled = true; btn.textContent = '⭐ quitando…';
            try {
              await fetch(keeperUrl(styleIdx), { method: 'DELETE' });
              btn.textContent = '⭐ keeper';
            } finally { btn.disabled = false; }
          }
        }
      });
    });
    const doReroll = (withExtra) => {
      const wrap = fig.querySelector('.img-wrap');
      const base = fig.dataset.src;
      let fresh = base + '&force=1&_r=' + Date.now();
      if (withExtra) {
        const extraInput = fig.querySelector('.extra-input');
        const v = extraInput && extraInput.value.trim();
        if (v) fresh += '&extra=' + encodeURIComponent(v);
      }
      wrap.innerHTML = '';
      const sp = document.createElement('div');
      sp.className = 'spinner';
      sp.textContent = withExtra ? 'aplicando tweak…' : 'regenerando…';
      wrap.appendChild(sp);
      const im = document.createElement('img');
      im.alt = '';
      im.loading = 'eager';
      im.addEventListener('load', () => sp.remove());
      im.addEventListener('error', () => { wrap.innerHTML = '<div class="error">generation failed</div>'; });
      wrap.appendChild(im);
      im.src = fresh;
    };
    const reroll = fig.querySelector('.reroll');
    if (reroll) reroll.addEventListener('click', () => doReroll(false));
    const rerollExtra = fig.querySelector('.reroll-extra');
    if (rerollExtra) rerollExtra.addEventListener('click', () => doReroll(true));
  });

  // Per-ref delete (× button on each photo)
  document.querySelectorAll('.ref-fig').forEach(fig => {
    const btn = fig.querySelector('.ref-delete');
    if (!btn) return;
    btn.addEventListener('click', async () => {
      const url = fig.dataset.refUrl;
      if (!url) return;
      if (!confirm('¿Eliminar esta foto permanentemente?\\n\\n' + url)) return;
      fig.classList.add('deleting');
      try {
        const r = await fetch('/api/maint/cromo-compare/ref?playerId=' + encodeURIComponent(playerId) + '&url=' + encodeURIComponent(url), { method: 'DELETE' });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        fig.remove();
      } catch (e) {
        fig.classList.remove('deleting');
        alert('falló: ' + e.message);
      }
    });
  });

  // Drop-zone + clipboard paste upload
  const dz = document.getElementById('dropzone');
  const dzStatus = document.getElementById('dz-status');
  const fileInput = document.getElementById('ref-file');
  const uploadBlob = async (blob) => {
    if (!blob) return;
    if (!blob.type || !blob.type.startsWith('image/')) {
      dzStatus.textContent = '✗ no es imagen (' + (blob.type || 'unknown') + ')';
      dzStatus.style.color = '#ff8a8a';
      return;
    }
    dz.classList.add('over');
    dzStatus.textContent = 'subiendo ' + Math.round(blob.size / 1024) + ' KB…';
    dzStatus.style.color = '#9aa3b2';
    try {
      const r = await fetch('/api/maint/cromo-compare/upload-ref?playerId=' + encodeURIComponent(playerId), {
        method: 'POST',
        headers: { 'content-type': blob.type },
        body: blob,
      });
      const j = await r.json().catch(() => ({}));
      if (!r.ok || !j.ok) throw new Error(j.error || ('HTTP ' + r.status));
      dzStatus.textContent = '✓ subido como ref activa · recarga para verla en su sección';
      dzStatus.style.color = '#6dd5a0';
    } catch (e) {
      dzStatus.textContent = '✗ ' + e.message;
      dzStatus.style.color = '#ff8a8a';
    } finally {
      dz.classList.remove('over');
    }
  };
  dz.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    const files = Array.from(fileInput.files || []);
    files.forEach(f => uploadBlob(f));
    fileInput.value = '';
  });
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('over'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('over'));
  dz.addEventListener('drop', e => {
    e.preventDefault();
    dz.classList.remove('over');
    const files = Array.from(e.dataTransfer.files || []);
    files.forEach(f => uploadBlob(f));
  });
  // Clipboard paste anywhere on the page (avoids needing dz focus on mobile)
  document.addEventListener('paste', e => {
    const items = (e.clipboardData && e.clipboardData.items) || [];
    for (const it of items) {
      if (it.kind === 'file') {
        const blob = it.getAsFile();
        if (blob) uploadBlob(blob);
      }
    }
  });

  // Identity-lock editor
  const idText = document.getElementById('id-text');
  const idSave = document.getElementById('id-save');
  const idReset = document.getElementById('id-reset');
  const idStatus = document.getElementById('id-status');
  idSave.addEventListener('click', async () => {
    const text = idText.value.trim();
    if (!text) { idStatus.textContent = '✗ texto vacío'; idStatus.style.color = '#ff8a8a'; return; }
    idSave.disabled = true;
    idStatus.textContent = 'guardando…';
    idStatus.style.color = '#7f8a9b';
    try {
      const r = await fetch('/api/maint/identity-override?playerId=' + encodeURIComponent(playerId), {
        method: 'PUT',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (!r.ok) {
        const j = await r.json().catch(() => ({}));
        throw new Error(j.error || ('HTTP ' + r.status));
      }
      idStatus.textContent = '✓ override guardado · re-roll para aplicar';
      idStatus.style.color = '#6dd5a0';
      if (idReset) { idReset.disabled = false; idReset.style.opacity = '1'; idReset.style.cursor = 'pointer'; }
    } catch (e) {
      idStatus.textContent = '✗ ' + e.message;
      idStatus.style.color = '#ff8a8a';
    } finally { idSave.disabled = false; }
  });
  if (idReset) idReset.addEventListener('click', async () => {
    if (!confirm('¿Quitar override y volver al texto del archivo?')) return;
    idReset.disabled = true;
    idStatus.textContent = 'quitando…';
    try {
      const r = await fetch('/api/maint/identity-override?playerId=' + encodeURIComponent(playerId), { method: 'DELETE' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      idStatus.textContent = '✓ override removido · recarga la página';
      idStatus.style.color = '#6dd5a0';
    } catch (e) {
      idStatus.textContent = '✗ ' + e.message;
      idStatus.style.color = '#ff8a8a';
    } finally { idReset.disabled = false; }
  });
  document.getElementById('fb-submit').addEventListener('click', async () => {
    const notes = document.getElementById('fb-notes').value.trim();
    const status = document.getElementById('fb-status');
    status.textContent = 'enviando…';
    try {
      const res = await fetch('/api/maint/cromo-compare/feedback', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          playerId,
          variants: votes,
          notes,
        }),
      });
      const j = await res.json();
      status.textContent = res.ok ? '✓ guardado · feedback_id: ' + j.id : '✗ error: ' + (j.error || res.status);
    } catch (e) {
      status.textContent = '✗ network error: ' + e.message;
    }
  });
})();
</script>
</body>
</html>`;

  return new Response(html, {
    status: 200,
    headers: { "content-type": "text/html; charset=utf-8" },
  });
}
