// SpaceSentinel 360 // Client Controller
// Secure Vanilla JS with Zero innerHTML Sinks

document.addEventListener('DOMContentLoaded', () => {
  let allFiles = [];
  let presets = [];
  let activeCategory = 'ALL';
  let pendingDeleteFile = null;

  // DOM elements
  const elStatusPill = document.getElementById('status-text-span');
  const elTotalCap = document.getElementById('badge-total-capacity');
  const elGaugeProgress = document.getElementById('gauge-circle-progress');
  const elFreePercent = document.getElementById('val-free-percent');
  const elFreeBytes = document.getElementById('stat-free-bytes');
  const elUsedBytes = document.getElementById('stat-used-bytes');
  const elHomeBytes = document.getElementById('stat-home-bytes');
  const elReclaimTotal = document.getElementById('val-reclaimable-total');
  const elQuarantineCountBadge = document.getElementById('badge-quarantine-count');
  const elStagedBytes = document.getElementById('val-staged-bytes');
  const elPresetGrid = document.getElementById('preset-cards-container');
  const elFileCountTag = document.getElementById('tag-file-count');
  const elSelectMinSize = document.getElementById('select-min-size');
  const elInputSearch = document.getElementById('input-search-filter');
  const elBtnRefresh = document.getElementById('btn-refresh-scan');
  const elTreemapStrip = document.getElementById('visual-treemap-container');
  const elFileTilesGrid = document.getElementById('file-tiles-container');
  const elBtnPurgeAllCaches = document.getElementById('btn-purge-all-caches');

  // Modals
  const modalQuarantine = document.getElementById('modal-quarantine-drawer');
  const elModalQCountSpan = document.getElementById('modal-quarantine-count-span');
  const elModalQList = document.getElementById('modal-quarantine-list');
  const btnCloseQModal = document.getElementById('btn-close-quarantine-modal');
  const btnViewQuarantine = document.getElementById('btn-view-quarantine');
  const btnCommitEmptyQuarantine = document.getElementById('btn-commit-empty-quarantine');
  const btnRestoreAllModal = document.getElementById('btn-restore-all-modal');
  const btnCommitEraseModal = document.getElementById('btn-commit-erase-modal');

  const modalConfirmDelete = document.getElementById('modal-confirm-delete');
  const elConfirmFilePath = document.getElementById('confirm-target-filepath');
  const elConfirmFileSize = document.getElementById('confirm-target-filesize');
  const btnCloseConfirmModal = document.getElementById('btn-close-confirm-modal');
  const btnCancelConfirmDelete = document.getElementById('btn-cancel-confirm-delete');
  const btnExecuteDelete = document.getElementById('btn-execute-permanent-delete');

  // Helper formatting
  function formatBytes(bytes) {
    if (!bytes || bytes <= 0) return '0.0 MB';
    const gb = bytes / (1024 * 1024 * 1024);
    if (gb >= 1.0) {
      return gb.toFixed(2) + ' GB';
    }
    const mb = bytes / (1024 * 1024);
    return mb.toFixed(1) + ' MB';
  }

  function safeClear(container) {
    container.replaceChildren();
  }

  // API Client
  async function fetchTelemetry() {
    try {
      elStatusPill.textContent = 'SYNCING SENSOR...';
      const res = await fetch('/api/telemetry');
      if (!res.ok) throw new Error('Sensor offline');
      const data = await res.json();
      renderTelemetry(data);
      elStatusPill.textContent = 'TELEMETRY LIVE // APFS CONNECTED';
    } catch (err) {
      elStatusPill.textContent = 'SENSOR OFFLINE';
      console.warn('Telemetry error:', err);
    }
  }

  async function fetchFiles() {
    const minMb = elSelectMinSize.value || '100';
    elFileCountTag.textContent = 'DISCOVERING LARGE HEAVY FILES...';
    try {
      const res = await fetch(`/api/files?min_mb=${minMb}`);
      if (!res.ok) throw new Error('File scan error');
      const data = await res.json();
      allFiles = data.files || [];
      renderFiles();
    } catch (err) {
      elFileCountTag.textContent = 'SCAN FAILED';
      console.warn(err);
    }
  }

  async function fetchQuarantineList() {
    try {
      const res = await fetch('/api/quarantine/list');
      const data = await res.json();
      renderQuarantineModal(data.quarantine || []);
    } catch (err) {
      console.warn(err);
    }
  }

  // Render Telemetry
  function renderTelemetry(data) {
    const disk = data.disk || {};
    const totalGb = (disk.total_bytes / (1024 * 1024 * 1024)).toFixed(0);
    elTotalCap.textContent = `${totalGb} GiB TOTAL`;

    const freePercent = disk.free_percent || 0;
    elFreePercent.textContent = `${freePercent}%`;

    // Update SVG gauge arc
    const circumference = 314.15;
    const offset = circumference - (freePercent / 100) * circumference;
    elGaugeProgress.style.strokeDashoffset = offset;

    elFreeBytes.textContent = formatBytes(disk.free_bytes);
    elUsedBytes.textContent = formatBytes(disk.used_bytes);

    presets = data.presets || [];
    renderPresets();

    // Calculate quick reclaim opportunity (sum safe_to_wipe presets)
    const safeWipeBytes = presets
      .filter(p => p.safe_to_wipe && p.exists)
      .reduce((acc, p) => acc + p.size_bytes, 0);

    elReclaimTotal.textContent = `~${formatBytes(safeWipeBytes)}`;
    elBtnPurgeAllCaches.textContent = `⚡ ONE-CLICK SWEEP ALL SAFE CACHES (${formatBytes(safeWipeBytes)})`;
    if (safeWipeBytes === 0) {
      elBtnPurgeAllCaches.disabled = true;
      elBtnPurgeAllCaches.style.opacity = '0.5';
    } else {
      elBtnPurgeAllCaches.disabled = false;
      elBtnPurgeAllCaches.style.opacity = '1';
    }

    const qCount = data.quarantine_count || 0;
    const qBytes = data.quarantine_bytes || 0;
    elQuarantineCountBadge.textContent = `${qCount} ITEM${qCount === 1 ? '' : 'S'}`;
    elStagedBytes.textContent = formatBytes(qBytes);
    elModalQCountSpan.textContent = String(qCount);
  }

  // Render Preset Sweeper Cards
  function renderPresets() {
    safeClear(elPresetGrid);

    presets.forEach(preset => {
      const card = document.createElement('article');
      card.className = 'preset-item-card';

      const topRow = document.createElement('div');
      topRow.className = 'preset-top-row';

      const nameBox = document.createElement('div');
      nameBox.className = 'preset-name-box';

      const nameEl = document.createElement('span');
      nameEl.className = 'preset-name';
      nameEl.textContent = preset.name;

      const catEl = document.createElement('span');
      catEl.className = 'preset-cat';
      catEl.textContent = `${preset.category} // ${preset.exists ? 'FOUND' : 'EMPTY'}`;

      nameBox.appendChild(nameEl);
      nameBox.appendChild(catEl);

      const sizeBadge = document.createElement('span');
      sizeBadge.className = 'preset-size-badge';
      sizeBadge.textContent = preset.exists ? formatBytes(preset.size_bytes) : '0 B';

      topRow.appendChild(nameBox);
      topRow.appendChild(sizeBadge);

      const descEl = document.createElement('p');
      descEl.className = 'preset-desc';
      descEl.textContent = preset.description;

      const actionBar = document.createElement('div');
      actionBar.className = 'preset-action-bar';

      if (preset.safe_to_wipe) {
        const wipeBtn = document.createElement('button');
        wipeBtn.className = 'btn-mini-cyber';
        wipeBtn.type = 'button';
        wipeBtn.textContent = preset.exists && preset.size_bytes > 0 ? '🧹 PURGE CACHE' : 'CLEANED';
        wipeBtn.disabled = !preset.exists || preset.size_bytes === 0;

        wipeBtn.addEventListener('click', async () => {
          wipeBtn.textContent = 'PURGING...';
          try {
            const res = await fetch('/api/wipe_preset', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ preset_id: preset.id })
            });
            const out = await res.json();
            if (out.success) {
              fetchTelemetry();
              fetchFiles();
            }
          } catch (e) {
            alert('Purge error: ' + e.message);
          }
        });
        actionBar.appendChild(wipeBtn);
      } else {
        const inspectBtn = document.createElement('button');
        inspectBtn.className = 'btn-mini-cyber btn-mini-stage';
        inspectBtn.type = 'button';
        inspectBtn.textContent = '🔍 FILTER WEIGHTS';
        inspectBtn.addEventListener('click', () => {
          elInputSearch.value = preset.name.toLowerCase().includes('ollama') ? '.ollama' : 'gemma';
          filterAndRenderFiles();
        });
        actionBar.appendChild(inspectBtn);
      }

      card.appendChild(topRow);
      card.appendChild(descEl);
      card.appendChild(actionBar);

      elPresetGrid.appendChild(card);
    });
  }

  // Category Filter Tabs
  document.querySelectorAll('#category-tabs-bar .filter-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('#category-tabs-bar .filter-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      activeCategory = tab.dataset.cat;
      filterAndRenderFiles();
    });
  });

  elInputSearch.addEventListener('input', () => filterAndRenderFiles());
  elSelectMinSize.addEventListener('change', () => fetchFiles());
  elBtnRefresh.addEventListener('click', () => {
    fetchTelemetry();
    fetchFiles();
  });

  function getFilteredFiles() {
    const q = (elInputSearch.value || '').trim().toLowerCase();
    return allFiles.filter(item => {
      const matchCat = activeCategory === 'ALL' || item.category === activeCategory;
      const matchSearch = !q || item.name.toLowerCase().includes(q) || item.path.toLowerCase().includes(q);
      return matchCat && matchSearch;
    });
  }

  function filterAndRenderFiles() {
    const filtered = getFilteredFiles();
    elFileCountTag.textContent = `${filtered.length} FILE${filtered.length === 1 ? '' : 'S'} DISPLAYED (${formatBytes(filtered.reduce((acc, f) => acc + f.size_bytes, 0))})`;
    renderTreemap(filtered);
    renderFileTiles(filtered);
  }

  function renderFiles() {
    filterAndRenderFiles();
  }

  // Render Visual Strip Treemap Chart
  function renderTreemap(files) {
    safeClear(elTreemapStrip);
    if (!files || files.length === 0) return;

    const maxTiles = Math.min(files.length, 25);
    const topSlice = files.slice(0, maxTiles);
    const totalBytes = topSlice.reduce((acc, f) => acc + f.size_bytes, 0);

    const palette = ['#00F2FE', '#FF2A6D', '#B026FF', '#00FF87', '#FFB800', '#38BDF8', '#F43F5E'];

    topSlice.forEach((file, idx) => {
      const share = (file.size_bytes / totalBytes) * 100;
      if (share < 0.8) return;

      const tile = document.createElement('div');
      tile.className = 'treemap-tile';
      tile.style.width = `${share}%`;
      tile.style.backgroundColor = palette[idx % palette.length];
      tile.title = `${file.name} (${formatBytes(file.size_bytes)})`;

      if (share > 5) {
        const label = document.createElement('span');
        label.className = 'treemap-tile-label';
        label.textContent = `${file.name.slice(0, 14)} (${formatBytes(file.size_bytes)})`;
        tile.appendChild(label);
      }

      tile.addEventListener('click', () => {
        elInputSearch.value = file.name;
        filterAndRenderFiles();
      });

      elTreemapStrip.appendChild(tile);
    });
  }

  // Category Icon Resolver
  function getCategoryEmoji(cat) {
    switch (cat) {
      case 'AI & ML Weights': return '🤖';
      case 'Archives & Disk Images': return '📦';
      case 'Media & Video': return '🎬';
      case 'Cache File': return '⚡';
      case 'System & Index Logs': return '📊';
      default: return '📄';
    }
  }

  // Render Individual File Tiles
  function renderFileTiles(files) {
    safeClear(elFileTilesGrid);

    if (!files || files.length === 0) {
      const emptyBox = document.createElement('div');
      emptyBox.style.gridColumn = '1 / -1';
      emptyBox.style.textAlign = 'center';
      emptyBox.style.padding = '40px';
      emptyBox.style.color = 'var(--text-muted)';
      emptyBox.style.fontFamily = 'var(--font-mono)';
      emptyBox.textContent = 'NO HEAVY FILES FOUND MATCHING THIS SENSOR FILTER.';
      elFileTilesGrid.appendChild(emptyBox);
      return;
    }

    const largestSingleByte = files[0] ? files[0].size_bytes : 1;

    files.forEach(file => {
      const card = document.createElement('article');
      card.className = 'file-tile-card';

      // Top Header
      const cardTop = document.createElement('div');
      cardTop.className = 'file-card-top';

      const iconBox = document.createElement('div');
      iconBox.className = 'file-icon-box';
      iconBox.textContent = getCategoryEmoji(file.category);

      const mainInfo = document.createElement('div');
      mainInfo.className = 'file-main-info';

      const nameHeading = document.createElement('h3');
      nameHeading.className = 'file-name-heading';
      nameHeading.textContent = file.name;
      nameHeading.title = file.name;

      const pathSub = document.createElement('p');
      pathSub.className = 'file-path-sub';
      pathSub.textContent = file.path;
      pathSub.title = file.path;

      mainInfo.appendChild(nameHeading);
      mainInfo.appendChild(pathSub);

      const sizeCallout = document.createElement('div');
      sizeCallout.className = 'file-size-callout';

      const sizeGb = document.createElement('div');
      sizeGb.className = 'file-size-gb';
      sizeGb.textContent = formatBytes(file.size_bytes);

      const catPill = document.createElement('div');
      catPill.className = 'file-cat-pill';
      catPill.textContent = file.category;

      sizeCallout.appendChild(sizeGb);
      sizeCallout.appendChild(catPill);

      cardTop.appendChild(iconBox);
      cardTop.appendChild(mainInfo);
      cardTop.appendChild(sizeCallout);

      // Relative Proportional Bar
      const sizeMeter = document.createElement('div');
      sizeMeter.className = 'tile-size-meter';
      const sizeFill = document.createElement('div');
      sizeFill.className = 'tile-size-fill';
      const fillPct = Math.max(4, (file.size_bytes / largestSingleByte) * 100);
      sizeFill.style.width = `${fillPct}%`;
      sizeMeter.appendChild(sizeFill);

      // Card Footer with Actions
      const cardFooter = document.createElement('div');
      cardFooter.className = 'file-card-footer';

      const modDate = document.createElement('span');
      modDate.className = 'file-modified-date';
      modDate.textContent = `MODIFIED: ${file.modified_human}`;

      const actionsRow = document.createElement('div');
      actionsRow.className = 'file-actions-row';

      // Button: Stage in Quarantine
      const stageBtn = document.createElement('button');
      stageBtn.className = 'btn-mini-cyber btn-mini-stage';
      stageBtn.type = 'button';
      stageBtn.textContent = '🛡️ STAGE';
      stageBtn.title = 'Reversibly move item to safe Quarantine staging buffer';
      stageBtn.addEventListener('click', async () => {
        stageBtn.textContent = 'STAGING...';
        try {
          const res = await fetch('/api/quarantine/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: file.path })
          });
          const out = await res.json();
          if (out.success) {
            fetchTelemetry();
            fetchFiles();
          } else {
            alert('Quarantine error: ' + (out.error || 'Failed'));
            stageBtn.textContent = '🛡️ STAGE';
          }
        } catch (e) {
          alert(e.message);
          stageBtn.textContent = '🛡️ STAGE';
        }
      });

      // Button: Gzip Compress
      const compressBtn = document.createElement('button');
      compressBtn.className = 'btn-mini-cyber';
      compressBtn.type = 'button';
      compressBtn.textContent = '🗜️ GZIP';
      compressBtn.title = 'Compress file in-place into .gz archive';
      if (file.extension === '.gz' || file.extension === '.zip') {
        compressBtn.disabled = true;
        compressBtn.style.opacity = '0.4';
      }
      compressBtn.addEventListener('click', async () => {
        compressBtn.textContent = 'COMPRESSING...';
        try {
          const res = await fetch('/api/compress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: file.path })
          });
          const out = await res.json();
          if (out.success) {
            fetchTelemetry();
            fetchFiles();
          } else {
            alert('Compression failed: ' + (out.error || 'Check file'));
            compressBtn.textContent = '🗜️ GZIP';
          }
        } catch (e) {
          alert(e.message);
          compressBtn.textContent = '🗜️ GZIP';
        }
      });

      // Button: Permanent Delete
      const deleteBtn = document.createElement('button');
      deleteBtn.className = 'btn-mini-cyber btn-mini-delete';
      deleteBtn.type = 'button';
      deleteBtn.textContent = '🗑️ ERASE';
      deleteBtn.title = 'Permanently delete this file';
      deleteBtn.addEventListener('click', () => {
        pendingDeleteFile = file;
        elConfirmFilePath.textContent = file.path;
        elConfirmFileSize.textContent = formatBytes(file.size_bytes);
        modalConfirmDelete.showModal();
      });

      actionsRow.appendChild(stageBtn);
      actionsRow.appendChild(compressBtn);
      actionsRow.appendChild(deleteBtn);

      cardFooter.appendChild(modDate);
      cardFooter.appendChild(actionsRow);

      card.appendChild(cardTop);
      card.appendChild(sizeMeter);
      card.appendChild(cardFooter);

      elFileTilesGrid.appendChild(card);
    });
  }

  // Batch Cache Sweep Button
  elBtnPurgeAllCaches.addEventListener('click', async () => {
    const safePresets = presets.filter(p => p.safe_to_wipe && p.exists && p.size_bytes > 0);
    if (safePresets.length === 0) return;

    elBtnPurgeAllCaches.textContent = '⚡ PURGING ALL SAFE CACHES...';
    for (const p of safePresets) {
      try {
        await fetch('/api/wipe_preset', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ preset_id: p.id })
        });
      } catch (e) {
        console.warn(e);
      }
    }
    fetchTelemetry();
    fetchFiles();
  });

  // Quarantine Modal Controls
  btnViewQuarantine.addEventListener('click', () => {
    fetchQuarantineList();
    modalQuarantine.showModal();
  });

  btnCloseQModal.addEventListener('click', () => modalQuarantine.close());

  function renderQuarantineModal(items) {
    safeClear(elModalQList);
    elModalQCountSpan.textContent = String(items.length);

    if (items.length === 0) {
      const p = document.createElement('p');
      p.style.fontFamily = 'var(--font-mono)';
      p.style.color = 'var(--text-muted)';
      p.style.padding = '20px 0';
      p.textContent = 'STAGING BUFFER IS EMPTY. NO FILES ARE WAITING IN QUARANTINE.';
      elModalQList.appendChild(p);
      return;
    }

    items.forEach(item => {
      const row = document.createElement('div');
      row.className = 'q-item-row';

      const info = document.createElement('div');
      info.className = 'q-item-info';

      const name = document.createElement('span');
      name.className = 'q-item-name';
      name.textContent = `${item.name} (${formatBytes(item.size_bytes)})`;

      const origPath = document.createElement('span');
      origPath.className = 'q-item-path';
      origPath.textContent = `Original: ${item.original_path}`;

      info.appendChild(name);
      info.appendChild(origPath);

      const actions = document.createElement('div');
      actions.className = 'q-item-actions';

      const restoreBtn = document.createElement('button');
      restoreBtn.className = 'btn-mini-cyber';
      restoreBtn.type = 'button';
      restoreBtn.textContent = '↩️ RESTORE';
      restoreBtn.addEventListener('click', async () => {
        try {
          const res = await fetch('/api/quarantine/restore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: item.id })
          });
          const out = await res.json();
          if (out.success) {
            fetchQuarantineList();
            fetchTelemetry();
            fetchFiles();
          }
        } catch (e) {
          alert(e.message);
        }
      });

      actions.appendChild(restoreBtn);
      row.appendChild(info);
      row.appendChild(actions);

      elModalQList.appendChild(row);
    });
  }

  btnCommitEmptyQuarantine.addEventListener('click', async () => {
    if (!confirm('Permanently purge all items held in Quarantine buffer?')) return;
    try {
      await fetch('/api/quarantine/empty', { method: 'POST' });
      fetchTelemetry();
      fetchFiles();
    } catch (e) {
      alert(e.message);
    }
  });

  btnCommitEraseModal.addEventListener('click', async () => {
    if (!confirm('Permanently delete all staged Quarantine items from your SSD?')) return;
    try {
      await fetch('/api/quarantine/empty', { method: 'POST' });
      modalQuarantine.close();
      fetchTelemetry();
      fetchFiles();
    } catch (e) {
      alert(e.message);
    }
  });

  btnRestoreAllModal.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/quarantine/list');
      const data = await res.json();
      const list = data.quarantine || [];
      for (const item of list) {
        await fetch('/api/quarantine/restore', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: item.id })
        });
      }
      fetchQuarantineList();
      fetchTelemetry();
      fetchFiles();
    } catch (e) {
      alert(e.message);
    }
  });

  // Execute Permanent Delete Confirm Modal
  btnCloseConfirmModal.addEventListener('click', () => modalConfirmDelete.close());
  btnCancelConfirmDelete.addEventListener('click', () => modalConfirmDelete.close());

  btnExecuteDelete.addEventListener('click', async () => {
    if (!pendingDeleteFile) return;
    btnExecuteDelete.textContent = 'ERASING...';
    try {
      const res = await fetch('/api/delete_permanent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: pendingDeleteFile.path, confirm: true })
      });
      const out = await res.json();
      modalConfirmDelete.close();
      btnExecuteDelete.textContent = 'YES, DELETE PERMANENTLY';
      pendingDeleteFile = null;
      if (out.success) {
        fetchTelemetry();
        fetchFiles();
      } else {
        alert('Deletion error: ' + (out.error || 'Failed'));
      }
    } catch (e) {
      btnExecuteDelete.textContent = 'YES, DELETE PERMANENTLY';
      alert(e.message);
    }
  });

  // Initial Sync
  fetchTelemetry();
  fetchFiles();
});
