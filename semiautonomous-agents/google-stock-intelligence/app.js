/**
 * Google Stock Intelligence Platform (GOOGL)
 * Antigravity Multi-Agent System - Subagent 3 UI/UX Architect
 * Data Verified from Subagent 1 (Market Terminal) & Subagent 2 (Sentiment & Catalysts)
 */

// Global State
const stockData = {
  ticker: "GOOGL",
  companyName: "Alphabet Inc. (Class A)",
  exchange: "NASDAQ",
  activeSession: {
    date: "2026-09-03",
    status: "Active Trading Session",
    open: 340.36,
    high: 344.66,
    low: 340.06,
    currentPrice: 342.21,
    changeUSD: 5.09,
    changePct: 1.51,
    volume: 9600000,
    volumeFormatted: "9.60M"
  },
  fundamentals: {
    marketCap: "$4.17 Trillion",
    peRatio: "17.19x",
    forwardPE: "15.80x",
    eps: "$19.90",
    beta: "1.08",
    fiftyTwoWeekRange: "$226.11 - $408.61",
    fiftyTwoWeekLow: 226.11,
    fiftyTwoWeekHigh: 408.61,
    dividendPerShare: "$0.22",
    dividendYield: "0.26%",
    exDividendDate: "2026-09-04",
    sharesOutstanding: "12.19B"
  },
  technicals: {
    tenDayHigh: 351.60,
    tenDayHighDate: "2026-08-24",
    tenDayLow: 332.82,
    tenDayLowDate: "2026-09-02",
    tenDaySpread: 18.78,
    tenDaySpreadPct: 5.64,
    tenDayAvgVolume: "23.49M",
    supportZone: "$332.80 - $333.05",
    resistanceZone: "$350.00 - $351.60",
    trendStatus: "Consolidating with Bullish Rebound at $333 Support",
    rsi: "48.6 (Neutral Rebound)",
    fiftyDayMA: "$328.40",
    twoHundredDayMA: "$294.15"
  },
  consensus: {
    rating: "Strong Buy",
    totalAnalysts: 28,
    buyCount: 24,
    holdCount: 4,
    sellCount: 0,
    lowTarget: 379.00,
    avgTarget: 425.88,
    highTarget: 465.00,
    avgUpsidePct: 24.48,
    highUpsidePct: 35.88,
    lowUpsidePct: 10.75
  },
  sessions: [
    { date: "2026-08-20", open: 343.06, high: 343.90, low: 338.57, close: 340.67, changePct: -1.17, changeUSD: -4.03, volume: 18570000, volumeStr: "18.57M" },
    { date: "2026-08-21", open: 342.58, high: 346.20, low: 340.40, close: 344.82, changePct: 1.22, changeUSD: 4.15, volume: 20850000, volumeStr: "20.85M" },
    { date: "2026-08-24", open: 343.62, high: 351.60, low: 342.49, close: 348.06, changePct: 0.94, changeUSD: 3.24, volume: 26340000, volumeStr: "26.34M" },
    { date: "2026-08-25", open: 349.64, high: 350.16, low: 345.60, close: 346.96, changePct: -0.32, changeUSD: -1.10, volume: 20650000, volumeStr: "20.65M" },
    { date: "2026-08-26", open: 346.62, high: 346.88, low: 340.18, close: 342.00, changePct: -1.43, changeUSD: -4.96, volume: 20420000, volumeStr: "20.42M" },
    { date: "2026-08-27", open: 339.67, high: 341.69, low: 338.52, close: 340.65, changePct: -0.39, changeUSD: -1.35, volume: 23390000, volumeStr: "23.39M" },
    { date: "2026-08-28", open: 340.71, high: 349.14, low: 340.27, close: 346.59, changePct: 1.74, changeUSD: 5.94, volume: 25350000, volumeStr: "25.35M" },
    { date: "2026-08-31", open: 343.83, high: 344.59, low: 337.16, close: 339.35, changePct: -2.09, changeUSD: -7.24, volume: 33490000, volumeStr: "33.49M" },
    { date: "2026-09-01", open: 336.00, high: 337.20, low: 333.05, close: 335.02, changePct: -1.28, changeUSD: -4.33, volume: 23340000, volumeStr: "23.34M" },
    { date: "2026-09-02", open: 334.06, high: 340.00, low: 332.82, close: 337.12, changePct: 0.63, changeUSD: 2.10, volume: 22530000, volumeStr: "22.53M" },
    { date: "2026-09-03 (Active)", open: 340.36, high: 344.66, low: 340.06, close: 342.21, changePct: 1.51, changeUSD: 5.09, volume: 9600000, volumeStr: "9.60M*" }
  ],
  catalysts: [
    {
      id: 1,
      title: "Google Cloud Revenue Surges 82% to $24.8B (AI Backlog $514B)",
      date: "2026-08-28",
      sentiment: "Bullish",
      category: "Cloud & AI",
      impact: "High",
      summary: "Google Cloud posted a record $24.8B in quarterly revenue, up 82% year-over-year. Operating margin expanded to 22.4%, driven by enterprise Vertex AI subscriptions and hyperscale TPU v6e cluster adoption.",
      takeaway: "Demonstrates sustained cloud operating leverage and translates CapEx spend directly into recurring enterprise revenue with contracted $514B backlog.",
      source: "Google Q2 Financial Filings & Bloomberg"
    },
    {
      id: 2,
      title: "Federal Court Rejects DOJ Request to Break Up Google Adtech",
      date: "2026-08-26",
      sentiment: "Bullish",
      category: "Legal & Regulatory",
      impact: "High",
      summary: "The U.S. District Court formally dismissed the Department of Justice's structural remedies seeking a forced breakup of Google's publisher ad server and ad exchange, mandating behavioral compliance audits instead.",
      takeaway: "Removes an existential regulatory overhang on Alphabet's high-margin advertising engine, protecting over $190B in annual ecosystem gross profit.",
      source: "U.S. District Court Ruling & Reuters"
    },
    {
      id: 3,
      title: "2026 CapEx Raised to $195B–$205B & Buyback Pause",
      date: "2026-08-31",
      sentiment: "Bearish",
      category: "Capital Allocation",
      impact: "Medium",
      summary: "Alphabet updated full-year capital expenditure forecast to $195B-$205B to secure long-term gigawatt nuclear power contracts and custom TPU silicon production, while moderating quarterly share repurchases.",
      takeaway: "Triggered a temporary -2.09% pullback on Aug 31 due to near-term free cash flow yield compression, but established rock-solid support at $333.",
      source: "Alphabet Investor Relations Notice"
    },
    {
      id: 4,
      title: "Waymo Expands into Europe (Munich) with 200M+ Autonomous Miles",
      date: "2026-08-24",
      sentiment: "Bullish",
      category: "Autonomous Mobility",
      impact: "High",
      summary: "Waymo One surpassed 200 million fully driverless commercial miles across North America and announced its European expansion in Munich with zero safety incidents and regulatory greenlight.",
      takeaway: "Validates international enterprise scalability for robotaxi operations, positioning Waymo as a multi-hundred billion dollar standalone subsidiary valuation catalyst.",
      source: "Waymo Corporate Press Release"
    },
    {
      id: 5,
      title: "Wiz Cloud Cybersecurity Acquisition Completed",
      date: "2026-08-21",
      sentiment: "Bullish",
      category: "M&A & Security",
      impact: "Medium",
      summary: "Alphabet finalized the integration of Wiz into Google Cloud Security Command Center, immediately contributing $600M+ in recurring annual cyber defense software revenue.",
      takeaway: "Solidifies Google Cloud's security moat against AWS and Azure, accelerating enterprise migrations among Fortune 100 financial and healthcare institutions.",
      source: "Google Cloud Official Release"
    },
    {
      id: 6,
      title: "$84.75B Strategic Capital Raise Closed for AI Compute",
      date: "2026-08-25",
      sentiment: "Neutral",
      category: "Corporate Finance",
      impact: "Medium",
      summary: "Alphabet completed an oversubscribed $84.75B multi-tranche senior note and infrastructure partnership at a favorable weighted average coupon of 3.85% to fund sovereign AI data centers.",
      takeaway: "Locks in ultra-low cost debt financing for the next 10 years without shareholder equity dilution, keeping cash reserves ($135B+) intact.",
      source: "SEC Form 8-K & Wall Street Journal"
    },
    {
      id: 7,
      title: "Gemini 3.8 Flash Rollout & Gemini 4 Training Underway",
      date: "2026-09-01",
      sentiment: "Neutral",
      category: "Foundation Models",
      impact: "Medium",
      summary: "Google DeepMind initiated widespread rollout of Gemini 3.8 Flash across Vertex AI and Workspace with sub-40ms latency, while confirming cluster training of the next-generation Gemini 4 architecture.",
      takeaway: "Maintains clear state-of-the-art inference efficiency and token economics leadership over competing frontier labs.",
      source: "Google DeepMind Engineering Blog"
    },
    {
      id: 8,
      title: "Wall Street Reaffirms Strong Buy Ahead of Goldman Sachs Communacopia",
      date: "2026-09-02",
      sentiment: "Bullish",
      category: "Analyst Research",
      impact: "High",
      summary: "Major Wall Street investment banks (Goldman Sachs, Morgan Stanley, J.P. Morgan) reiterated unanimous Buy ratings with price targets up to $465 ahead of Alphabet's keynote address.",
      takeaway: "Directly fueled the Sept 2 and Sept 3 price rebound (+1.51% to $342.21), validating the $333 support level as an institutional accumulation zone.",
      source: "Consensus Equity Research Reports"
    }
  ]
};

// Global Chart Instance
let stockChartInstance = null;
let currentChartMode = 'close'; // 'close', 'range', 'volume', 'combined'

// Utility: format currency
function formatUSD(num) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(num);
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  renderHeaderTicker();
  renderKPIs();
  renderTechnicals();
  renderAnalystConsensus();
  renderChart('close');
  renderHistoricalTable();
  renderCatalysts('all');
  setupEventListeners();
  updateROICalculator();
});

// Render Header Ticker
function renderHeaderTicker() {
  const priceElem = document.getElementById('ticker-price');
  const changeElem = document.getElementById('ticker-change');
  const sessionStatus = document.getElementById('ticker-status');

  if (priceElem) priceElem.textContent = `$${stockData.activeSession.currentPrice.toFixed(2)}`;
  if (changeElem) {
    const isPositive = stockData.activeSession.changePct >= 0;
    changeElem.textContent = `${isPositive ? '+' : ''}$${stockData.activeSession.changeUSD.toFixed(2)} (${isPositive ? '+' : ''}${stockData.activeSession.changePct.toFixed(2)}%)`;
    changeElem.className = isPositive 
      ? 'px-2.5 py-1 text-xs font-mono font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
      : 'px-2.5 py-1 text-xs font-mono font-bold rounded bg-rose-500/20 text-rose-400 border border-rose-500/30';
  }
  if (sessionStatus) {
    sessionStatus.textContent = `${stockData.activeSession.date} • ${stockData.activeSession.status} • Vol: ${stockData.activeSession.volumeFormatted}`;
  }
}

// Render Top KPI Badges
function renderKPIs() {
  document.getElementById('kpi-market-cap').textContent = stockData.fundamentals.marketCap;
  document.getElementById('kpi-pe').textContent = stockData.fundamentals.peRatio;
  document.getElementById('kpi-eps').textContent = stockData.fundamentals.eps;
  document.getElementById('kpi-range').textContent = stockData.fundamentals.fiftyTwoWeekRange;
  document.getElementById('kpi-dividend').textContent = `${stockData.fundamentals.dividendPerShare} (Ex-Div: ${stockData.fundamentals.exDividendDate})`;
  document.getElementById('kpi-avg-vol').textContent = stockData.technicals.tenDayAvgVolume;
}

// Render Technicals
function renderTechnicals() {
  document.getElementById('tech-high').textContent = `$${stockData.technicals.tenDayHigh.toFixed(2)}`;
  document.getElementById('tech-low').textContent = `$${stockData.technicals.tenDayLow.toFixed(2)}`;
  document.getElementById('tech-spread').textContent = `$${stockData.technicals.tenDaySpread.toFixed(2)} (${stockData.technicals.tenDaySpreadPct}%)`;
  document.getElementById('tech-support').textContent = stockData.technicals.supportZone;
  document.getElementById('tech-resistance').textContent = stockData.technicals.resistanceZone;
  document.getElementById('tech-trend').textContent = stockData.technicals.trendStatus;
  document.getElementById('tech-rsi').textContent = stockData.technicals.rsi;
}

// Render Analyst Consensus
function renderAnalystConsensus() {
  document.getElementById('consensus-badge').textContent = stockData.consensus.rating;
  document.getElementById('consensus-target-avg').textContent = `$${stockData.consensus.avgTarget.toFixed(2)}`;
  document.getElementById('consensus-upside').textContent = `+${stockData.consensus.avgUpsidePct}% Upside`;
  document.getElementById('target-high').textContent = `$${stockData.consensus.highTarget.toFixed(2)}`;
  document.getElementById('target-low').textContent = `$${stockData.consensus.lowTarget.toFixed(2)}`;
  document.getElementById('target-current-marker').textContent = `$${stockData.activeSession.currentPrice.toFixed(2)}`;

  // Set Progress Bar Position
  // Range from $342.21 to $465.00
  const rangeMin = 330;
  const rangeMax = 470;
  const currentPct = ((stockData.activeSession.currentPrice - rangeMin) / (rangeMax - rangeMin)) * 100;
  const avgPct = ((stockData.consensus.avgTarget - rangeMin) / (rangeMax - rangeMin)) * 100;

  const currentMarkerElem = document.getElementById('target-progress-current');
  const avgMarkerElem = document.getElementById('target-progress-avg');
  if (currentMarkerElem) currentMarkerElem.style.left = `${Math.min(Math.max(currentPct, 5), 95)}%`;
  if (avgMarkerElem) avgMarkerElem.style.left = `${Math.min(Math.max(avgPct, 5), 95)}%`;
}

// Render Chart
function renderChart(mode = 'close') {
  currentChartMode = mode;
  const ctx = document.getElementById('stockMainChart');
  if (!ctx) return;

  if (stockChartInstance) {
    stockChartInstance.destroy();
  }

  const labels = stockData.sessions.map(s => s.date.replace("2026-", "").replace(" (Active)", "*"));
  const closePrices = stockData.sessions.map(s => s.close);
  const highPrices = stockData.sessions.map(s => s.high);
  const lowPrices = stockData.sessions.map(s => s.low);
  const volumes = stockData.sessions.map(s => s.volume / 1000000); // in Millions

  let datasets = [];

  if (mode === 'close') {
    datasets = [
      {
        label: 'Closing Price ($USD)',
        data: closePrices,
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.12)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.25,
        pointBackgroundColor: stockData.sessions.map((s, idx) => idx === stockData.sessions.length - 1 ? '#10b981' : '#38bdf8'),
        pointBorderColor: '#0f172a',
        pointBorderWidth: 2,
        pointRadius: stockData.sessions.map((s, idx) => idx === stockData.sessions.length - 1 ? 7 : 4),
        pointHoverRadius: 7,
        yAxisID: 'y'
      },
      {
        label: 'Support Zone ($333.00)',
        data: Array(stockData.sessions.length).fill(333.00),
        borderColor: 'rgba(16, 185, 129, 0.65)',
        borderDash: [5, 5],
        borderWidth: 1.5,
        fill: false,
        pointRadius: 0,
        yAxisID: 'y'
      },
      {
        label: 'Resistance ($350.00)',
        data: Array(stockData.sessions.length).fill(350.00),
        borderColor: 'rgba(244, 63, 94, 0.65)',
        borderDash: [5, 5],
        borderWidth: 1.5,
        fill: false,
        pointRadius: 0,
        yAxisID: 'y'
      }
    ];
  } else if (mode === 'range') {
    datasets = [
      {
        label: 'Session High',
        data: highPrices,
        borderColor: '#10b981',
        borderWidth: 1.5,
        fill: '+1',
        backgroundColor: 'rgba(56, 189, 248, 0.08)',
        pointRadius: 3,
        yAxisID: 'y'
      },
      {
        label: 'Session Low',
        data: lowPrices,
        borderColor: '#f43f5e',
        borderWidth: 1.5,
        fill: false,
        pointRadius: 3,
        yAxisID: 'y'
      },
      {
        label: 'Close Price',
        data: closePrices,
        borderColor: '#38bdf8',
        borderWidth: 2.5,
        fill: false,
        tension: 0.2,
        pointRadius: 4,
        yAxisID: 'y'
      }
    ];
  } else if (mode === 'volume') {
    datasets = [
      {
        type: 'bar',
        label: 'Trading Volume (Millions)',
        data: volumes,
        backgroundColor: stockData.sessions.map(s => s.changePct >= 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(244, 63, 94, 0.6)'),
        borderColor: stockData.sessions.map(s => s.changePct >= 0 ? '#10b981' : '#f43f5e'),
        borderWidth: 1,
        borderRadius: 4,
        yAxisID: 'yVol'
      }
    ];
  } else if (mode === 'combined') {
    datasets = [
      {
        type: 'line',
        label: 'Closing Price ($)',
        data: closePrices,
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.08)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.2,
        pointRadius: 4,
        yAxisID: 'y'
      },
      {
        type: 'bar',
        label: 'Volume (M)',
        data: volumes,
        backgroundColor: stockData.sessions.map(s => s.changePct >= 0 ? 'rgba(16, 185, 129, 0.35)' : 'rgba(244, 63, 94, 0.35)'),
        borderColor: stockData.sessions.map(s => s.changePct >= 0 ? '#10b981' : '#f43f5e'),
        borderWidth: 1,
        borderRadius: 3,
        yAxisID: 'yVol'
      }
    ];
  }

  stockChartInstance = new Chart(ctx, {
    type: mode === 'volume' ? 'bar' : 'line',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: '#94a3b8',
            font: { family: 'Inter', size: 12 },
            boxWidth: 14,
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          padding: 12,
          boxPadding: 6,
          usePointStyle: true,
          callbacks: {
            label: function(context) {
              const label = context.dataset.label || '';
              const val = context.parsed.y;
              if (label.includes('Volume')) {
                return `${label}: ${val.toFixed(2)}M shares`;
              }
              return `${label}: $${val.toFixed(2)}`;
            },
            afterBody: function(context) {
              const idx = context[0].dataIndex;
              const session = stockData.sessions[idx];
              return [
                `--- Session Detail ---`,
                `Open: $${session.open.toFixed(2)} | High: $${session.high.toFixed(2)}`,
                `Low: $${session.low.toFixed(2)} | Close: $${session.close.toFixed(2)}`,
                `Change: ${session.changePct >= 0 ? '+' : ''}${session.changePct}% ($${session.changeUSD >= 0 ? '+' : ''}${session.changeUSD.toFixed(2)})`,
                `Volume: ${session.volumeStr}`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(255, 255, 255, 0.05)'
          },
          ticks: {
            color: '#94a3b8',
            font: { family: 'JetBrains Mono', size: 11 }
          }
        },
        y: {
          display: mode !== 'volume',
          position: 'left',
          grid: {
            color: 'rgba(255, 255, 255, 0.05)'
          },
          ticks: {
            color: '#94a3b8',
            font: { family: 'JetBrains Mono', size: 11 },
            callback: value => `$${value.toFixed(1)}`
          },
          min: mode === 'range' ? 330 : 330,
          max: 355
        },
        yVol: {
          display: mode === 'volume' || mode === 'combined',
          position: 'right',
          grid: {
            drawOnChartArea: mode === 'volume',
            color: 'rgba(255, 255, 255, 0.03)'
          },
          ticks: {
            color: '#64748b',
            font: { family: 'JetBrains Mono', size: 11 },
            callback: value => `${value}M`
          },
          min: 0,
          max: 40
        }
      }
    }
  });

  // Update button active state
  document.querySelectorAll('.chart-toggle-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === mode);
  });
}

// Render Historical Sessions Table
function renderHistoricalTable() {
  const tbody = document.getElementById('historical-table-body');
  if (!tbody) return;

  tbody.replaceChildren();

  const maxVol = Math.max(...stockData.sessions.map(s => s.volume));

  stockData.sessions.forEach((s) => {
    const tr = document.createElement('tr');
    tr.className = 'table-row-hover border-b border-slate-800/60 transition-colors text-sm font-mono';

    const isPositive = s.changePct >= 0;
    const volPct = (s.volume / maxVol) * 100;

    // Date Cell
    const tdDate = document.createElement('td');
    tdDate.className = 'py-3.5 px-4 font-semibold text-slate-200';
    tdDate.textContent = s.date;
    if (s.date.includes('Active')) {
      const activeBadge = document.createElement('span');
      activeBadge.className = 'ml-2 text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-sans uppercase font-bold border border-emerald-500/30';
      activeBadge.textContent = 'Active';
      tdDate.appendChild(activeBadge);
    }
    tr.appendChild(tdDate);

    // Open
    const tdOpen = document.createElement('td');
    tdOpen.className = 'py-3.5 px-4 text-slate-300';
    tdOpen.textContent = `$${s.open.toFixed(2)}`;
    tr.appendChild(tdOpen);

    // High
    const tdHigh = document.createElement('td');
    tdHigh.className = 'py-3.5 px-4 text-emerald-400 font-medium';
    tdHigh.textContent = `$${s.high.toFixed(2)}`;
    tr.appendChild(tdHigh);

    // Low
    const tdLow = document.createElement('td');
    tdLow.className = 'py-3.5 px-4 text-rose-400 font-medium';
    tdLow.textContent = `$${s.low.toFixed(2)}`;
    tr.appendChild(tdLow);

    // Close
    const tdClose = document.createElement('td');
    tdClose.className = 'py-3.5 px-4 font-bold text-white';
    tdClose.textContent = `$${s.close.toFixed(2)}`;
    tr.appendChild(tdClose);

    // Change %
    const tdChange = document.createElement('td');
    tdChange.className = 'py-3.5 px-4';
    const changeBadge = document.createElement('span');
    changeBadge.className = `inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${
      isPositive ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
    }`;
    changeBadge.textContent = `${isPositive ? '+' : ''}${s.changePct.toFixed(2)}% ($${isPositive ? '+' : ''}${s.changeUSD.toFixed(2)})`;
    tdChange.appendChild(changeBadge);
    tr.appendChild(tdChange);

    // Volume with visual bar
    const tdVol = document.createElement('td');
    tdVol.className = 'py-3.5 px-4';
    const volContainer = document.createElement('div');
    volContainer.className = 'flex items-center space-x-2';
    
    const volText = document.createElement('span');
    volText.className = 'w-16 text-slate-300';
    volText.textContent = s.volumeStr;

    const barBg = document.createElement('div');
    barBg.className = 'flex-1 bg-slate-800 rounded-full h-1.5 overflow-hidden max-w-[100px]';
    const barFill = document.createElement('div');
    barFill.className = `h-full rounded-full ${isPositive ? 'bg-emerald-500' : 'bg-rose-500'}`;
    barFill.style.width = `${volPct}%`;
    barBg.appendChild(barFill);

    volContainer.appendChild(volText);
    volContainer.appendChild(barBg);
    tdVol.appendChild(volContainer);
    tr.appendChild(tdVol);

    tbody.appendChild(tr);
  });
}

// Render Filterable Catalysts
function renderCatalysts(filter = 'all', searchQuery = '') {
  const container = document.getElementById('catalysts-container');
  if (!container) return;

  container.replaceChildren();

  const filtered = stockData.catalysts.filter(cat => {
    const matchesFilter = filter === 'all' || cat.sentiment.toLowerCase() === filter.toLowerCase();
    const matchesSearch = !searchQuery || 
      cat.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      cat.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cat.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  if (filtered.length === 0) {
    const emptyMsg = document.createElement('div');
    emptyMsg.className = 'col-span-full py-12 text-center text-slate-400';
    emptyMsg.textContent = 'No catalysts matched the current filter or search criteria.';
    container.appendChild(emptyMsg);
    return;
  }

  filtered.forEach(cat => {
    const card = document.createElement('div');
    card.className = 'glass-card rounded-xl p-5 flex flex-col justify-between';

    // Header
    const cardHeader = document.createElement('div');
    cardHeader.className = 'flex items-center justify-between gap-2 mb-3';

    const catBadge = document.createElement('span');
    catBadge.className = 'text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-cyan-400 border border-slate-700';
    catBadge.textContent = cat.category;

    const sentimentBadge = document.createElement('span');
    let sentimentStyle = 'bg-slate-800 text-slate-300 border-slate-700';
    if (cat.sentiment === 'Bullish') sentimentStyle = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    if (cat.sentiment === 'Bearish') sentimentStyle = 'bg-rose-500/20 text-rose-400 border-rose-500/30';
    if (cat.sentiment === 'Neutral') sentimentStyle = 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    sentimentBadge.className = `text-xs font-bold px-2.5 py-0.5 rounded border ${sentimentStyle}`;
    sentimentBadge.textContent = `${cat.sentiment} • Impact: ${cat.impact}`;

    cardHeader.appendChild(catBadge);
    cardHeader.appendChild(sentimentBadge);

    // Title & Date
    const titleContainer = document.createElement('div');
    titleContainer.className = 'mb-2';
    const dateSpan = document.createElement('div');
    dateSpan.className = 'text-[11px] font-mono text-slate-400 mb-1';
    dateSpan.textContent = `${cat.date} • ${cat.source}`;
    const h3 = document.createElement('h3');
    h3.className = 'text-base font-bold text-white leading-snug hover:text-cyan-400 transition-colors cursor-pointer';
    h3.textContent = cat.title;

    titleContainer.appendChild(dateSpan);
    titleContainer.appendChild(h3);

    // Summary
    const summaryP = document.createElement('p');
    summaryP.className = 'text-xs text-slate-300 leading-relaxed mb-4';
    summaryP.textContent = cat.summary;

    // Takeaway block
    const takeawayBlock = document.createElement('div');
    takeawayBlock.className = 'mt-auto bg-slate-900/80 rounded-lg p-3 border-l-2 border-cyan-400';
    const takeawayTitle = document.createElement('div');
    takeawayTitle.className = 'text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider mb-1';
    takeawayTitle.textContent = 'Strategic Market Takeaway';
    const takeawayText = document.createElement('p');
    takeawayText.className = 'text-[11px] text-slate-300 italic';
    takeawayText.textContent = `"${cat.takeaway}"`;
    takeawayBlock.appendChild(takeawayTitle);
    takeawayBlock.appendChild(takeawayText);

    card.appendChild(cardHeader);
    card.appendChild(titleContainer);
    card.appendChild(summaryP);
    card.appendChild(takeawayBlock);

    container.appendChild(card);
  });
}

// Interactive Investment & ROI Calculator
function updateROICalculator() {
  const sharesInput = document.getElementById('calc-shares');
  if (!sharesInput) return;

  const shares = parseFloat(sharesInput.value) || 0;
  const currentPrice = stockData.activeSession.currentPrice;
  const avgTarget = stockData.consensus.avgTarget;
  const highTarget = stockData.consensus.highTarget;
  const lowTarget = stockData.consensus.lowTarget;
  const dividendPerShare = 0.22;

  const capital = shares * currentPrice;
  const valueAtAvg = shares * avgTarget;
  const profitAtAvg = valueAtAvg - capital;
  const profitPctAvg = capital > 0 ? (profitAtAvg / capital) * 100 : 0;

  const valueAtHigh = shares * highTarget;
  const profitAtHigh = valueAtHigh - capital;
  const profitPctHigh = capital > 0 ? (profitAtHigh / capital) * 100 : 0;

  const valueAtLow = shares * lowTarget;
  const profitAtLow = valueAtLow - capital;
  const profitPctLow = capital > 0 ? (profitAtLow / capital) * 100 : 0;

  const dividendPayout = shares * dividendPerShare;

  document.getElementById('calc-res-capital').textContent = formatUSD(capital);
  document.getElementById('calc-res-avg-val').textContent = formatUSD(valueAtAvg);
  document.getElementById('calc-res-avg-profit').textContent = `+${formatUSD(profitAtAvg)} (+${profitPctAvg.toFixed(2)}%)`;
  document.getElementById('calc-res-high-profit').textContent = `+${formatUSD(profitAtHigh)} (+${profitPctHigh.toFixed(2)}%)`;
  document.getElementById('calc-res-low-profit').textContent = `+${formatUSD(profitAtLow)} (+${profitPctLow.toFixed(2)}%)`;
  document.getElementById('calc-res-dividend').textContent = `${formatUSD(dividendPayout)} (Payout Sep 4)`;
}

// Export Historical Data as CSV
function exportCSV() {
  const headers = ["Date", "Open", "High", "Low", "Close", "Change_Pct", "Change_USD", "Volume"];
  const rows = stockData.sessions.map(s => [
    s.date,
    s.open,
    s.high,
    s.low,
    s.close,
    s.changePct,
    s.changeUSD,
    s.volume
  ]);

  let csvContent = "data:text/csv;charset=utf-8," + headers.join(",") + "\n"
    + rows.map(e => e.join(",")).join("\n");

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `GOOGL_Market_Intelligence_2026-09-03.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Event Listeners
function setupEventListeners() {
  // Chart view toggles
  document.querySelectorAll('.chart-toggle-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const mode = e.currentTarget.dataset.mode;
      renderChart(mode);
    });
  });

  // Catalyst Filter Pills
  document.querySelectorAll('.catalyst-filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.catalyst-filter-btn').forEach(b => b.classList.remove('active', 'bg-cyan-500/20', 'text-cyan-300'));
      btn.classList.add('active', 'bg-cyan-500/20', 'text-cyan-300');
      const filter = btn.dataset.filter;
      const searchVal = document.getElementById('catalyst-search')?.value || '';
      renderCatalysts(filter, searchVal);
    });
  });

  // Catalyst Search Bar
  const searchInput = document.getElementById('catalyst-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const activeFilterBtn = document.querySelector('.catalyst-filter-btn.active');
      const filter = activeFilterBtn ? activeFilterBtn.dataset.filter : 'all';
      renderCatalysts(filter, e.target.value);
    });
  }

  // Calculator inputs and quick chips
  const sharesInput = document.getElementById('calc-shares');
  if (sharesInput) {
    sharesInput.addEventListener('input', updateROICalculator);
  }

  document.querySelectorAll('.calc-chip').forEach(chip => {
    chip.addEventListener('click', (e) => {
      const count = e.currentTarget.dataset.shares;
      if (sharesInput && count) {
        sharesInput.value = count;
        updateROICalculator();
      }
    });
  });

  // Export CSV button
  const exportBtn = document.getElementById('btn-export-csv');
  if (exportBtn) {
    exportBtn.addEventListener('click', exportCSV);
  }
}
