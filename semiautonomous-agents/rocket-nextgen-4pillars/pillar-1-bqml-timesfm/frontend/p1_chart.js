/**
 * Pillar 1: BigQuery ML TimesFM 2.0 (AI.FORECAST) Interactive Fan Chart
 * Renders dual-zone SVG fan chart:
 *   - Left zone: 28-week historical baseline
 *   - Dividing line: TimesFM Zero-Shot Horizon separator
 *   - Right zone: P10-P90 translucent prediction interval cone + forecasted trajectory
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.P1ChartModule = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /**
   * Fetches the TimesFM forecast from the microservice backend.
   */
  async function fetchForecast(params) {
    const opts = Object.assign(
      {
        metric_id: 'mrcooper_refi_locks',
        horizon: 12,
        confidence_level: 0.9,
        rate_shock_bps: -50
      },
      params || {}
    );

    const response = await fetch('/api/pillar1/forecast', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(opts)
    });

    if (!response.ok) {
      throw new Error('Pillar 1 forecast failed with HTTP ' + response.status);
    }
    return await response.json();
  }

  /**
   * Fetches the available metric catalog.
   */
  async function fetchCatalog() {
    const response = await fetch('/api/pillar1/catalog');
    if (!response.ok) {
      throw new Error('Failed to fetch metric catalog');
    }
    return await response.json();
  }

  /**
   * Renders the SVG fan chart into a specified SVG element or selector.
   */
  function renderTimesFmSvg(svgTarget, historical, forecast, customOpts) {
    const svg =
      typeof svgTarget === 'string'
        ? document.querySelector(svgTarget)
        : svgTarget;
    if (!svg) return;

    if (!historical || !historical.length || !forecast || !forecast.length) {
      svg.innerHTML =
        '<text x="50%" y="50%" text-anchor="middle" fill="#94A3B8" font-size="14">No forecast data loaded</text>';
      return;
    }

    const opts = Object.assign(
      {
        width: 860,
        height: 300,
        padL: 58,
        padR: 24,
        padT: 28,
        padB: 36,
        primaryColor: '#D81E28', // Rocket red
        coneColor: 'rgba(216, 30, 40, 0.16)',
        histColor: '#0F172A',
        gridColor: 'rgba(148, 163, 184, 0.22)'
      },
      customOpts || {}
    );

    const W = opts.width;
    const H = opts.height;
    const padL = opts.padL;
    const padR = opts.padR;
    const padT = opts.padT;
    const padB = opts.padB;

    const allVals = [];
    historical.forEach(function (d) {
      allVals.push(d.value);
      if (typeof d.baseline === 'number') allVals.push(d.baseline);
    });
    forecast.forEach(function (d) {
      allVals.push(d.forecast, d.lower, d.upper);
    });

    const minV = Math.min.apply(null, allVals) * 0.94;
    const maxV = Math.max.apply(null, allVals) * 1.05;
    const totalPts = historical.length + forecast.length;

    const xOf = function (idx) {
      return (
        padL + (idx / Math.max(1, totalPts - 1)) * (W - padL - padR)
      );
    };
    const yOf = function (v) {
      return (
        padT +
        (1 - (v - minV) / Math.max(1e-6, maxV - minV)) *
          (H - padT - padB)
      );
    };

    // 1. Grid lines and Y-axis labels
    let gridHtml = '';
    for (let i = 0; i <= 4; i++) {
      const gv = minV + (i / 4) * (maxV - minV);
      const gy = yOf(gv);
      const label =
        gv >= 1000000
          ? (gv / 1000000).toFixed(1) + 'M'
          : gv >= 1000
          ? (gv / 1000).toFixed(1) + 'k'
          : gv.toFixed(1);

      gridHtml +=
        '<line x1="' +
        padL +
        '" y1="' +
        gy +
        '" x2="' +
        (W - padR) +
        '" y2="' +
        gy +
        '" stroke="' +
        opts.gridColor +
        '" stroke-dasharray="3,3"/>' +
        '<text x="' +
        (padL - 8) +
        '" y="' +
        (gy + 4) +
        '" text-anchor="end" font-size="10.5" font-family="JetBrains Mono, monospace" fill="#64748B">' +
        label +
        '</text>';
    }

    // 2. Historical polyline
    const histPts = historical
      .map(function (d, i) {
        return xOf(i).toFixed(1) + ',' + yOf(d.value).toFixed(1);
      })
      .join(' ');

    const splitIdx = historical.length - 1;
    const splitX = xOf(splitIdx);

    // 3. Prediction interval cone polygon (P10 - P90)
    const upperPts = [splitX.toFixed(1) + ',' + yOf(historical[splitIdx].value).toFixed(1)];
    const lowerPts = [];
    forecast.forEach(function (d, j) {
      const xi = xOf(historical.length + j).toFixed(1);
      upperPts.push(xi + ',' + yOf(d.upper).toFixed(1));
      lowerPts.unshift(xi + ',' + yOf(d.lower).toFixed(1));
    });
    const conePolygon = upperPts.concat(lowerPts).join(' ');

    // 4. Forecast dotted trajectory line
    const fcPts = [splitX.toFixed(1) + ',' + yOf(historical[splitIdx].value).toFixed(1)];
    forecast.forEach(function (d, j) {
      fcPts.push(xOf(historical.length + j).toFixed(1) + ',' + yOf(d.forecast).toFixed(1));
    });

    // 5. Data circles with tooltips
    let dotsHtml = '';
    forecast.forEach(function (d, j) {
      const cx = xOf(historical.length + j);
      const cy = yOf(d.forecast);
      dotsHtml +=
        '<circle cx="' +
        cx +
        '" cy="' +
        cy +
        '" r="4" fill="' +
        opts.primaryColor +
        '" stroke="#FFF" stroke-width="1.5">' +
        '<title>' +
        d.date +
        ': ' +
        d.forecast.toLocaleString() +
        ' [' +
        d.lower.toLocaleString() +
        ' - ' +
        d.upper.toLocaleString() +
        ']</title>' +
        '</circle>';
    });

    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.innerHTML =
      gridHtml +
      '<polygon points="' +
      conePolygon +
      '" fill="' +
      opts.coneColor +
      '" stroke="none" />' +
      '<line x1="' +
      splitX +
      '" y1="' +
      padT +
      '" x2="' +
      splitX +
      '" y2="' +
      (H - padB) +
      '" stroke="#1A73E8" stroke-width="1.5" stroke-dasharray="5,4" />' +
      '<rect x="' +
      (splitX - 100) +
      '" y="' +
      (padT - 8) +
      '" width="200" height="20" rx="6" fill="#1A73E8" />' +
      '<text x="' +
      splitX +
      '" y="' +
      (padT + 6) +
      '" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace" font-weight="700" fill="#FFF">TIMESFM ZERO-SHOT HORIZON</text>' +
      '<polyline fill="none" stroke="' +
      opts.histColor +
      '" stroke-width="2.8" points="' +
      histPts +
      '" />' +
      '<polyline fill="none" stroke="' +
      opts.primaryColor +
      '" stroke-width="3" stroke-dasharray="6,4" points="' +
      fcPts.join(' ') +
      '" />' +
      dotsHtml +
      '<text x="' +
      (padL + 10) +
      '" y="' +
      (H - 12) +
      '" font-size="11" font-family="JetBrains Mono, monospace" fill="#64748B">Historical (' +
      historical[0].date +
      ' to ' +
      historical[historical.length - 1].date +
      ')</text>' +
      '<text x="' +
      (W - padR - 10) +
      '" y="' +
      (H - 12) +
      '" text-anchor="end" font-size="11" font-family="JetBrains Mono, monospace" fill="' +
      opts.primaryColor +
      '" font-weight="700">TimesFM Forecast (to ' +
      forecast[forecast.length - 1].date +
      ')</text>';
  }

  return {
    fetchForecast: fetchForecast,
    fetchCatalog: fetchCatalog,
    renderTimesFmSvg: renderTimesFmSvg
  };
});
