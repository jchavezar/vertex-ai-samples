// 3D similarity overlay — Three.js scene that lays out the current
// result set in a 3-d PCA projection of the 3072-d embedding space.
// The query lives at the origin; each result is a thumbnail-textured
// billboard, distance-from-origin tracks how far it is from the query.

import * as THREE from 'https://esm.sh/three@0.160.0';
import { OrbitControls } from 'https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js';

const $ = (s) => document.querySelector(s);

const MOD_COLORS = {
  photo:   0x83E509,
  video:   0x6FE3FF,
  audio:   0xFFB347,
  graphic: 0xFF7AD9,
  '':      0x9AA0A8,
};

const state = {
  ready: false,
  scene: null,
  camera: null,
  renderer: null,
  controls: null,
  raf: 0,
  resizeObs: null,
  pickables: [],   // Mesh[] for raycasting
  basePositions: [], // original positions before spread scaling
  lines: [],         // line segments to update on spread
  hoveredId: null,
  raycaster: new THREE.Raycaster(),
  pointer: new THREE.Vector2(-9, -9),
  spread: 1.0,
};

// ---------- modal open/close wiring ----------
function openModal() {
  const m = $('#viz3dModal');
  if (!m) return;
  m.hidden = false;
  document.body.style.overflow = 'hidden';
  // Defer fetch+init so the modal frame paints first.
  requestAnimationFrame(() => loadAndRender());
}

function closeModal() {
  const m = $('#viz3dModal');
  if (!m) return;
  m.hidden = true;
  document.body.style.overflow = '';
  // Soft teardown: dispose scene contents but KEEP the WebGL context alive
  // so that reopening the modal can rebuild without recreating the canvas.
  // forceContextLoss() permanently kills the context — we don't want that.
  if (state.raf) cancelAnimationFrame(state.raf);
  state.raf = 0;
  if (state.resizeObs) state.resizeObs.disconnect();
  if (state.controls) { state.controls.dispose(); state.controls = null; }
  disposeScene();
  if (state.renderer) { state.renderer.dispose(); state.renderer = null; }
  state.scene = null;
  state.camera = null;
  state.pickables = [];
  state.hoveredId = null;
  state.ready = false;
}

function disposeScene() {
  if (!state.scene) return;
  state.scene.traverse(obj => {
    if (obj.geometry) obj.geometry.dispose();
    if (obj.material) {
      if (obj.material.map) obj.material.map.dispose();
      obj.material.dispose();
    }
  });
}

// ---------- data fetch ----------
async function fetchViz() {
  // Reuse the same params as the last /api/search call.
  const ls = window.state || {};
  const q = ls.query || $('#searchInput')?.value?.trim() || '';
  if (!q) throw new Error('Run a search first.');
  const modality = ls.modality || 'all';
  const params = new URLSearchParams({ q, modality, limit: '40' });
  if (ls.filters?.tempo)  params.set('tempo',  ls.filters.tempo);
  if (ls.filters?.length) params.set('length', ls.filters.length);
  const vibe = window.__vibe || null;
  if (vibe) {
    for (const [axis, v] of Object.entries(vibe)) {
      const n = Number(v);
      if (Number.isFinite(n) && Math.abs(n) > 0.001) params.set(`vibe_${axis}`, n.toFixed(3));
    }
  }
  const r = await fetch(`/api/visualize?${params.toString()}`);
  if (!r.ok) throw new Error(`viz HTTP ${r.status}`);
  return r.json();
}

// ---------- scene build ----------
function buildScene(viz) {
  const stage = $('#viz3dStage');
  const canvas = $('#viz3dCanvas');
  const w = stage.clientWidth;
  const h = stage.clientHeight;

  const scene = new THREE.Scene();
  scene.background = null;

  const camera = new THREE.PerspectiveCamera(48, w / h, 0.01, 100);
  camera.position.set(2.4, 1.6, 2.6);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(w, h, false);
  renderer.setClearColor(0x000000, 0);

  // Subtle ambient + key light for depth on shaded sprites.
  scene.add(new THREE.AmbientLight(0xffffff, 0.85));
  const key = new THREE.DirectionalLight(0xffffff, 0.4);
  key.position.set(2, 4, 3);
  scene.add(key);

  // Faint axes ("you're inside a vector space" cue).
  const axis = (a, b, color) => {
    const g = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(...a), new THREE.Vector3(...b),
    ]);
    const m = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.18 });
    return new THREE.Line(g, m);
  };
  scene.add(axis([-1.4, 0, 0], [1.4, 0, 0], 0x83E509));
  scene.add(axis([0, -1.4, 0], [0, 1.4, 0], 0x6FE3FF));
  scene.add(axis([0, 0, -1.4], [0, 0, 1.4], 0xFF7AD9));

  // Faint sphere shell at radius=1 to suggest the unit-norm space.
  const shellGeo = new THREE.SphereGeometry(1, 32, 24);
  const shellMat = new THREE.MeshBasicMaterial({
    color: 0x83E509, wireframe: true, transparent: true, opacity: 0.07,
  });
  scene.add(new THREE.Mesh(shellGeo, shellMat));

  // Query node at origin: glowing green disc + halo.
  const qGeo = new THREE.SphereGeometry(0.045, 24, 18);
  const qMat = new THREE.MeshBasicMaterial({ color: 0x83E509 });
  const qMesh = new THREE.Mesh(qGeo, qMat);
  qMesh.userData = { kind: 'query', label: viz.query };
  scene.add(qMesh);

  const haloGeo = new THREE.SphereGeometry(0.1, 24, 18);
  const haloMat = new THREE.MeshBasicMaterial({
    color: 0x83E509, transparent: true, opacity: 0.18,
  });
  scene.add(new THREE.Mesh(haloGeo, haloMat));

  const pickables = [];
  const basePositions = [];
  const lines = [];
  for (const p of viz.points || []) {
    const color = MOD_COLORS[p.modality] ?? MOD_COLORS[''];
    basePositions.push(new THREE.Vector3(p.x, p.y, p.z));

    // Connection line query → point, alpha tied to score (closer → brighter).
    const lineGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(p.x, p.y, p.z),
    ]);
    const lineOpacity = Math.max(0.05, Math.min(0.45, p.score));
    const lineMat = new THREE.LineBasicMaterial({
      color, transparent: true, opacity: lineOpacity,
    });
    const line = new THREE.Line(lineGeo, lineMat);
    line.userData._idx = lines.length;
    lines.push(line);
    scene.add(line);

    // Thumbnail billboard — circle texture with built-in colored rim.
    // Plane is sized so its inscribed circle matches the rim glow ring.
    const DISC = 0.18;  // disc diameter in world units
    const planeGeo = new THREE.PlaneGeometry(DISC, DISC);
    const baseMat = new THREE.MeshBasicMaterial({
      color, transparent: true, opacity: 0.95, side: THREE.DoubleSide,
      depthWrite: false,
    });
    const mesh = new THREE.Mesh(planeGeo, baseMat);
    mesh.position.set(p.x, p.y, p.z);
    mesh.userData = {
      kind: 'point',
      id: p.id,
      asset_id: p.asset_id,
      modality: p.modality,
      score: p.score,
      caption: p.caption,
      thumbnail: p.thumbnail_url,
      _baseScale: 1.0,
      _color: color,
    };
    scene.add(mesh);
    pickables.push(mesh);

    // Outer glow ring sized to wrap the disc — gives a soft halo effect.
    const ringGeo = new THREE.RingGeometry(DISC * 0.55, DISC * 0.62, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color, transparent: true, opacity: 0.45, side: THREE.DoubleSide,
      depthWrite: false,
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.position.copy(mesh.position);
    mesh.userData._ring = ring;
    scene.add(ring);

    if (p.thumbnail_url) {
      loadCircularTexture(p.thumbnail_url, color).then(tex => {
        if (!tex || !mesh.material) return;
        if (mesh.material.map) mesh.material.map.dispose();
        mesh.material.map = tex;
        mesh.material.color.setHex(0xffffff);
        mesh.material.needsUpdate = true;
      }).catch(() => { /* keep colored placeholder on error */ });
    }
  }

  // Camera intro: sweep from far → settled. Stored on state for animate().
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.rotateSpeed = 0.7;
  controls.minDistance = 0.6;
  controls.maxDistance = 8;
  controls.target.set(0, 0, 0);
  controls.update();

  state.scene = scene;
  state.camera = camera;
  state.renderer = renderer;
  state.controls = controls;
  state.pickables = pickables;
  state.basePositions = basePositions;
  state.lines = lines;
  state.spread = 1.0;
  state.ready = true;
  // Reset slider UI to 1.0 on every fresh build.
  const slider = $('#viz3dSpread');
  const sval = $('#viz3dSpreadVal');
  if (slider) slider.value = '1';
  if (sval) sval.textContent = '1.0×';

  // Resize observer keeps the canvas crisp on layout changes.
  if (state.resizeObs) state.resizeObs.disconnect();
  state.resizeObs = new ResizeObserver(() => {
    const W = stage.clientWidth;
    const H = stage.clientHeight;
    if (!W || !H) return;
    camera.aspect = W / H;
    camera.updateProjectionMatrix();
    renderer.setSize(W, H, false);
  });
  state.resizeObs.observe(stage);

  // Animate.
  const clock = new THREE.Clock();
  const tick = () => {
    state.raf = requestAnimationFrame(tick);
    const t = clock.getElapsedTime();
    // Pulse the halo + billboards face camera + hover scale lerp.
    haloMat.opacity = 0.13 + 0.07 * Math.sin(t * 1.6);
    for (const m of pickables) {
      m.lookAt(camera.position);
      m.userData._ring?.lookAt(camera.position);
      const target = m.userData._hoverScale || 1.0;
      const cur = m.scale.x;
      const next = cur + (target - cur) * 0.18;
      m.scale.setScalar(next);
      if (m.userData._ring) m.userData._ring.scale.setScalar(next);
    }
    controls.update();
    renderer.render(scene, camera);
  };
  tick();

  // Pointer events for hover + click-to-focus.
  canvas.addEventListener('pointermove', onPointerMove);
  canvas.addEventListener('pointerleave', onPointerLeave);
  canvas.addEventListener('click', onPointerClick);
  // Track press start so dragging the orbit doesn't fire click.
  canvas.addEventListener('pointerdown', (e) => {
    canvas._downX = e.clientX; canvas._downY = e.clientY;
  });
}

// ---------- hover / tooltip ----------
function onPointerMove(e) {
  const canvas = state.renderer?.domElement;
  if (!canvas || !state.ready) return;
  const rect = canvas.getBoundingClientRect();
  state.pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
  state.pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
  state.raycaster.setFromCamera(state.pointer, state.camera);
  const hits = state.raycaster.intersectObjects(state.pickables, false);
  const top = hits[0]?.object;

  // Reset previous hover.
  if (state.hoveredId && (!top || top.userData.id !== state.hoveredId)) {
    for (const m of state.pickables) {
      if (m.userData.id === state.hoveredId) m.userData._hoverScale = 1.0;
    }
    state.hoveredId = null;
    hideTip();
  }

  if (top && top.userData.kind === 'point') {
    if (top.userData.id !== state.hoveredId) {
      top.userData._hoverScale = 1.55;
      state.hoveredId = top.userData.id;
    }
    canvas.style.cursor = 'pointer';
    showTip(e.clientX, e.clientY, top.userData);
  } else {
    canvas.style.cursor = 'grab';
  }
}

// Click on a point → fly camera into that point so user can inspect the
// local neighborhood (especially useful for mixed-modality clusters).
function onPointerClick(e) {
  if (!state.ready) return;
  const canvas = state.renderer?.domElement;
  if (!canvas) return;
  // Suppress click after orbit drag (>5px movement).
  const dx = (e.clientX - (canvas._downX || e.clientX));
  const dy = (e.clientY - (canvas._downY || e.clientY));
  if (Math.hypot(dx, dy) > 5) return;

  const rect = canvas.getBoundingClientRect();
  const ndc = new THREE.Vector2(
    ((e.clientX - rect.left) / rect.width) * 2 - 1,
    -((e.clientY - rect.top) / rect.height) * 2 + 1,
  );
  state.raycaster.setFromCamera(ndc, state.camera);
  const hits = state.raycaster.intersectObjects(state.pickables, false);
  const top = hits[0]?.object;
  if (!top || top.userData.kind !== 'point') return;
  focusOnPoint(top);
}

// Compute neighborhood radius based on distance to 5 nearest points,
// then pull the camera in to fill the view with that local cluster.
function focusOnPoint(mesh) {
  const target = mesh.position.clone();
  // Find distances to the 5 nearest pickables (excluding self).
  const dists = state.pickables
    .filter(m => m !== mesh)
    .map(m => m.position.distanceTo(target))
    .sort((a, b) => a - b);
  const k = Math.min(5, dists.length);
  const localRadius = k > 0 ? (dists.slice(0, k).reduce((a, b) => a + b, 0) / k) : 0.2;
  const fov = state.camera.fov * (Math.PI / 180);
  const dist = Math.max(0.18, localRadius / Math.tan(fov / 2) * 1.3);

  const dir = new THREE.Vector3()
    .subVectors(state.camera.position, state.controls.target)
    .normalize();
  // If the camera is straight on the target, nudge the dir so we don't get
  // a degenerate view of the disc edge.
  if (dir.lengthSq() < 0.001) dir.set(0.6, 0.5, 0.7).normalize();
  tweenCamera(
    target.clone().add(dir.multiplyScalar(dist)),
    target.clone(),
    480,
  );

  // Briefly highlight the focused point.
  mesh.userData._hoverScale = 1.8;
  setTimeout(() => { mesh.userData._hoverScale = 1.0; }, 700);
}

function onPointerLeave() {
  if (state.hoveredId) {
    for (const m of state.pickables) {
      if (m.userData.id === state.hoveredId) m.userData._hoverScale = 1.0;
    }
    state.hoveredId = null;
  }
  hideTip();
}

function showTip(cx, cy, d) {
  const tip = $('#viz3dTooltip');
  if (!tip) return;
  const stage = $('#viz3dStage').getBoundingClientRect();
  const x = Math.min(stage.right - 240, Math.max(stage.left + 8, cx + 14));
  const y = Math.min(stage.bottom - 120, Math.max(stage.top + 8, cy + 14));
  tip.style.left = `${x - stage.left}px`;
  tip.style.top  = `${y - stage.top}px`;
  const pct = Math.round((d.score || 0) * 100);
  tip.innerHTML = `
    <div class="viz3d-tip__head">
      <span class="viz3d-tip__mod viz3d-tip__mod--${d.modality || 'na'}">${d.modality || '—'}</span>
      <span class="viz3d-tip__score">${pct}%</span>
    </div>
    <div class="viz3d-tip__cap">${escapeHtml(d.caption || d.asset_id || d.id)}</div>
    <div class="viz3d-tip__id">${escapeHtml(d.asset_id || d.id)}</div>
  `;
  tip.hidden = false;
}

function hideTip() {
  const tip = $('#viz3dTooltip');
  if (tip) tip.hidden = true;
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

// ---------- orchestration ----------
async function loadAndRender() {
  const loading = $('#viz3dLoading');
  const sub = $('#viz3dSub');
  if (loading) loading.hidden = false;
  if (sub) sub.textContent = 'Reading 3072-d vectors from Vector Search…';
  try {
    const viz = await fetchViz();
    if (loading) loading.hidden = true;
    if (sub) {
      const ev = (viz.explained_variance ?? 0) * 100;
      sub.textContent = `${viz.points.length} points · ${viz.dim}-d → 3-d · ${ev.toFixed(0)}% variance preserved · ${Math.round(viz.total_ms)}ms`;
    }
    teardownPartial();
    buildScene(viz);
  } catch (err) {
    console.error(err);
    if (loading) {
      loading.innerHTML = `<div class="viz3d__loading-msg" style="color:#ff8d8d">Failed: ${escapeHtml(err.message || err)}</div>`;
    }
  }
}

// Like teardown() but keeps the canvas + modal so we can re-init in place.
function teardownPartial() {
  if (state.raf) cancelAnimationFrame(state.raf);
  state.raf = 0;
  if (state.resizeObs) state.resizeObs.disconnect();
  if (state.controls) { state.controls.dispose(); state.controls = null; }
  disposeScene();
  if (state.renderer) { state.renderer.dispose(); state.renderer = null; }
  state.scene = null;
  state.camera = null;
  state.pickables = [];
  state.hoveredId = null;
  state.ready = false;
}

// ---------- spread + fit cluster ----------
// Spread multiplies all base positions by `factor` so the user can pull
// dense clusters apart and dive in. Lines are updated in lockstep.
function applySpread(factor) {
  if (!state.ready) return;
  state.spread = factor;
  for (let i = 0; i < state.pickables.length; i++) {
    const m = state.pickables[i];
    const bp = state.basePositions[i];
    if (!bp) continue;
    m.position.set(bp.x * factor, bp.y * factor, bp.z * factor);
    if (m.userData._ring) m.userData._ring.position.copy(m.position);
    const line = state.lines[i];
    if (line) {
      const pos = line.geometry.attributes.position;
      pos.array[3] = m.position.x;
      pos.array[4] = m.position.y;
      pos.array[5] = m.position.z;
      pos.needsUpdate = true;
    }
  }
}

// Fit camera to the bounding box of all pickables, then nudge slightly
// further so the cluster isn't crammed into the viewport edges.
function fitCluster() {
  if (!state.ready || !state.pickables.length) return;
  const box = new THREE.Box3();
  for (const m of state.pickables) box.expandByPoint(m.position);
  // Always include the query at the origin so the user keeps the anchor.
  box.expandByPoint(new THREE.Vector3(0, 0, 0));
  const size = new THREE.Vector3();
  const center = new THREE.Vector3();
  box.getSize(size);
  box.getCenter(center);
  const maxDim = Math.max(size.x, size.y, size.z) || 1;
  const fov = state.camera.fov * (Math.PI / 180);
  const dist = (maxDim / 2) / Math.tan(fov / 2) * 1.6;  // 1.6 = breathing room
  const dir = new THREE.Vector3().subVectors(state.camera.position, state.controls.target).normalize();
  // Animate camera position + target via a short tween.
  tweenCamera(
    center.clone().add(dir.multiplyScalar(dist)),
    center.clone(),
    420,
  );
}

function tweenCamera(toPos, toTarget, durMs) {
  if (!state.camera || !state.controls) return;
  const fromPos = state.camera.position.clone();
  const fromTgt = state.controls.target.clone();
  const t0 = performance.now();
  const ease = t => 1 - Math.pow(1 - t, 3);  // cubic out
  const step = () => {
    const now = performance.now();
    const t = Math.min(1, (now - t0) / durMs);
    const k = ease(t);
    state.camera.position.lerpVectors(fromPos, toPos, k);
    state.controls.target.lerpVectors(fromTgt, toTarget, k);
    state.controls.update();
    if (t < 1) requestAnimationFrame(step);
  };
  step();
}

// ---------- circular thumbnail texture ----------
// Draws the image into a square canvas with a circular alpha clip and a
// subtle colored ring stroke that matches the modality color, then returns
// a CanvasTexture. This gives us round disc thumbnails that align with the
// glow rim instead of overflowing as squares.
function loadCircularTexture(url, ringHex) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const SZ = 256;
      const c = document.createElement('canvas');
      c.width = c.height = SZ;
      const ctx = c.getContext('2d');
      // Soft outer halo background (transparent edges).
      ctx.save();
      ctx.beginPath();
      ctx.arc(SZ / 2, SZ / 2, SZ / 2 - 4, 0, Math.PI * 2);
      ctx.closePath();
      ctx.clip();
      // cover-fit the image inside the circle.
      const ratio = Math.max(SZ / img.width, SZ / img.height);
      const w = img.width * ratio;
      const h = img.height * ratio;
      ctx.drawImage(img, (SZ - w) / 2, (SZ - h) / 2, w, h);
      ctx.restore();
      // Thin colored rim so the disc reads against any background.
      ctx.beginPath();
      ctx.arc(SZ / 2, SZ / 2, SZ / 2 - 5, 0, Math.PI * 2);
      ctx.lineWidth = 4;
      ctx.strokeStyle = '#' + (ringHex >>> 0).toString(16).padStart(6, '0');
      ctx.globalAlpha = 0.85;
      ctx.stroke();
      const tex = new THREE.CanvasTexture(c);
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.anisotropy = 4;
      resolve(tex);
    };
    img.onerror = () => reject(new Error('img load failed'));
    img.src = url;
  });
}

// ---------- bootstrap ----------
function bind() {
  const btn = $('#viz3dBtn');
  if (btn) btn.addEventListener('click', openModal);
  const modal = $('#viz3dModal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target.matches('[data-close]')) closeModal();
    });
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !$('#viz3dModal')?.hidden) closeModal();
  });

  // Spread slider — live-updates positions as user drags.
  const slider = $('#viz3dSpread');
  const sval = $('#viz3dSpreadVal');
  if (slider) {
    slider.addEventListener('input', () => {
      const f = Number(slider.value) || 1;
      if (sval) sval.textContent = `${f.toFixed(1)}×`;
      applySpread(f);
    });
  }

  const fit = $('#viz3dFitBtn');
  if (fit) fit.addEventListener('click', fitCluster);

  const reset = $('#viz3dResetBtn');
  if (reset) reset.addEventListener('click', () => {
    if (slider) slider.value = '1';
    if (sval) sval.textContent = '1.0×';
    applySpread(1.0);
    tweenCamera(new THREE.Vector3(2.4, 1.6, 2.6), new THREE.Vector3(0, 0, 0), 420);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bind);
} else {
  bind();
}
