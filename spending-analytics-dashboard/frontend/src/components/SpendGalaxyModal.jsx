import React, { useState, useMemo, useRef, useEffect } from 'react';
import { X, Sparkles, Orbit, UserCheck, Star, Layers, ZoomIn, ZoomOut, Maximize2, Minimize2, Search, RotateCcw, Compass, Sun } from 'lucide-react';

export default function SpendGalaxyModal({ categoryName, transactions = [], onClose }) {
  const [activeStar, setActiveStar] = useState(null);
  const [filterCardholder, setFilterCardholder] = useState('ALL');
  const [labelMode, setLabelMode] = useState('FULL'); // 'FULL' | 'AMOUNTS' | 'MINIMAL'
  const [activeSubcatFilter, setActiveSubcatFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Pan & Zoom physics
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [isFullscreen, setIsFullscreen] = useState(false);

  const canvasRef = useRef(null);

  // Clean brand label helper
  const getCleanBrandLabel = (tx) => {
    let name = tx.clean_merchant || tx.raw_description || '';
    name = name.replace(/^(AplPay|TST\*|SP\*|BT\*DD \*|DD \*|SP )\s*/i, '');
    name = name.replace(/\s+(NEW YORK|MANHATTAN|BEVERLY HILLS|LOS ANGELES|ATLANTA|MEXICO CITY|SAN FRANCISCO|BROOKLYN|DORAL|HICKSVILLE|WESTBURY)\b.*/i, '');
    name = name.trim();
    return name || tx.clean_merchant;
  };

  // Smart 2-3 letter initials helper
  const getSmartInitials = (tx) => {
    const clean = getCleanBrandLabel(tx);
    const words = clean.split(/\s+/).filter(Boolean);
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return clean.substring(0, 3).toUpperCase();
  };

  // Filter transactions
  const categoryTxs = useMemo(() => {
    return transactions.filter(t => {
      if (filterCardholder !== 'ALL' && t.card_member.toLowerCase() !== filterCardholder.toLowerCase()) return false;
      if (activeSubcatFilter !== 'ALL' && t.subcategory !== activeSubcatFilter) return false;
      if (searchTerm) {
        const s = searchTerm.toLowerCase();
        const m = getCleanBrandLabel(t).toLowerCase();
        const r = t.raw_description.toLowerCase();
        if (!m.includes(s) && !r.includes(s)) return false;
      }
      return true;
    });
  }, [transactions, filterCardholder, activeSubcatFilter, searchTerm]);

  // Subcategories list for solar system clustering
  const subcategories = useMemo(() => {
    const set = new Set(transactions.map(t => t.subcategory).filter(Boolean));
    return ['ALL', ...Array.from(set)];
  }, [transactions]);

  const totalSpent = useMemo(() => {
    return categoryTxs.reduce((sum, t) => sum + (t.amount > 0 ? t.amount : 0), 0);
  }, [categoryTxs]);

  const cardholderSplit = useMemo(() => {
    const split = { DINORAH: 0, JESUS: 0 };
    categoryTxs.forEach(t => {
      if (t.amount > 0) {
        if (t.card_member.includes('DINORAH')) split.DINORAH += t.amount;
        else split.JESUS += t.amount;
      }
    });
    const total = split.DINORAH + split.JESUS;
    return {
      dinorahPct: total > 0 ? ((split.DINORAH / total) * 100).toFixed(1) : 0,
      jesusPct: total > 0 ? ((split.JESUS / total) * 100).toFixed(1) : 0,
      dinorahAmt: split.DINORAH,
      jesusAmt: split.JESUS
    };
  }, [categoryTxs]);

  // Dynamic Spacing & Solar System Coordinates
  const galaxyNodes = useMemo(() => {
    if (categoryTxs.length === 0) return [];
    
    // Sort transactions by amount descending
    const sorted = [...categoryTxs].sort((a, b) => Math.abs(b.amount) - Math.abs(a.amount));

    const centerX = 450;
    const centerY = 360;
    const goldenAngle = 137.5 * (Math.PI / 180);

    return sorted.map((tx, idx) => {
      const absAmt = Math.abs(tx.amount);
      const size = Math.max(20, Math.min(56, Math.sqrt(absAmt) * 1.9 + 14));
      
      // Spacious multi-orbit distribution
      // Expand radius dynamically so planets never cluster tightly or overflow
      const radius = 70 + Math.sqrt(idx + 1) * 62;
      const angle = idx * goldenAngle + (idx % 2 === 0 ? 0.1 : -0.1);
      
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      // Color scheme
      let color = '#8b5cf6'; // Violet default
      if (tx.is_refund) color = '#10b981'; // Emerald
      else if (tx.card_member.includes('JESUS')) color = '#06b6d4'; // Cyan
      else if (tx.expense_type === 'Lifestyle & Luxury') color = '#ec4899'; // Pink

      const pctOfCat = totalSpent > 0 ? ((tx.amount / totalSpent) * 100).toFixed(1) : 0;
      const displayLabel = getCleanBrandLabel(tx);
      const initials = getSmartInitials(tx);

      return {
        ...tx,
        x,
        y,
        size,
        color,
        pctOfCat,
        displayLabel,
        initials,
        orbitRadius: radius
      };
    });
  }, [categoryTxs, totalSpent]);

  // Mouse Drag to Pan canvas
  const handleMouseDown = (e) => {
    if (e.target.closest('.node-element')) return; // Ignore drag if clicking a star node
    setIsDragging(true);
    setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setPanOffset({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Wheel Zoom
  const handleWheel = (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
    setZoomLevel(prev => Math.max(0.4, Math.min(3.0, prev * zoomFactor)));
  };

  const resetView = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
    setSearchTerm('');
  };

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center ${isFullscreen ? 'p-0' : 'p-3 md:p-6'} bg-slate-950/90 backdrop-blur-2xl animate-fadeIn`}>
      {/* Background galaxy ambient universe */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-950/30 via-slate-950 to-slate-950 pointer-events-none" />

      {/* Main Galaxy Window */}
      <div className={`relative w-full ${isFullscreen ? 'h-full rounded-none' : 'max-w-6xl h-[820px] rounded-3xl'} bg-slate-900/90 border border-slate-800 shadow-2xl flex flex-col overflow-hidden backdrop-blur-2xl transition-all duration-300`}>
        
        {/* Header HUD */}
        <div className="p-4 md:p-5 border-b border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-950/60 z-30">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-2xl bg-gradient-to-tr from-violet-600 via-indigo-500 to-cyan-400 text-white shadow-lg shadow-violet-500/20 animate-pulse">
              <Orbit className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">Spend Galaxy Constellation Explorer</span>
                <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-violet-500/10 text-violet-300 border border-violet-500/20">
                  {galaxyNodes.length} Planets Visible
                </span>
              </div>
              <h2 className="text-xl font-extrabold text-white tracking-tight">{categoryName} Constellation</h2>
            </div>
          </div>

          {/* Galaxy Controls: Search, View Mode, Zoom & Fullscreen */}
          <div className="flex flex-wrap items-center gap-2">
            
            {/* Search Planet Bar */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="🔍 Search planet..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-slate-950 text-xs text-slate-200 pl-8 pr-3 py-1.5 rounded-xl border border-slate-800 focus:outline-none focus:border-indigo-500/50 w-36 md:w-44"
              />
            </div>

            {/* Label Mode Switcher */}
            <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
              <button
                onClick={() => setLabelMode('FULL')}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
                  labelMode === 'FULL' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                🏷️ Full Names
              </button>
              <button
                onClick={() => setLabelMode('AMOUNTS')}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
                  labelMode === 'AMOUNTS' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                💰 Amounts
              </button>
              <button
                onClick={() => setLabelMode('MINIMAL')}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
                  labelMode === 'MINIMAL' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                ✨ Stars Only
              </button>
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setZoomLevel(prev => Math.min(3.0, prev + 0.2))}
                className="p-1.5 text-slate-300 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
                title="Zoom In (+)"
              >
                <ZoomIn className="w-4 h-4" />
              </button>
              <span className="text-[10px] font-mono text-slate-400 px-1 font-bold">{Math.round(zoomLevel * 100)}%</span>
              <button
                onClick={() => setZoomLevel(prev => Math.max(0.4, prev - 0.2))}
                className="p-1.5 text-slate-300 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
                title="Zoom Out (-)"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
              <button
                onClick={resetView}
                className="p-1.5 text-slate-300 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
                title="Recenter Canvas"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Fullscreen Toggle */}
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 rounded-xl bg-slate-950 border border-slate-800 hover:bg-slate-800 text-slate-300 transition-colors cursor-pointer"
              title={isFullscreen ? "Exit Fullscreen" : "Fullscreen Galaxy View"}
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Subcategory Solar System Cluster Filter Pills */}
        <div className="px-6 py-2 bg-slate-950/40 border-b border-slate-800/60 flex items-center gap-2 overflow-x-auto z-20">
          <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1 shrink-0">
            <Sun className="w-3.5 h-3.5 text-amber-400" /> Solar Clusters:
          </span>
          {subcategories.map(sub => (
            <button
              key={sub}
              onClick={() => setActiveSubcatFilter(sub)}
              className={`text-[11px] px-3 py-1 rounded-xl font-medium whitespace-nowrap transition-all cursor-pointer ${
                activeSubcatFilter === sub
                  ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 font-bold'
                  : 'bg-slate-950/80 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {sub === 'ALL' ? `🌌 All Constellation (${transactions.length})` : `🪐 ${sub}`}
            </button>
          ))}
        </div>

        {/* Galaxy Body: Interactive PanZoom Universe */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 relative overflow-hidden">
          
          {/* Constellation Canvas Interactive Area */}
          <div
            ref={canvasRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onWheel={handleWheel}
            className={`lg:col-span-2 relative h-full flex items-center justify-center p-4 overflow-hidden select-none ${
              isDragging ? 'cursor-grabbing' : 'cursor-grab'
            }`}
          >
            {/* Pan/Zoom Workspace Wrapper */}
            <div
              style={{
                transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
                transformOrigin: 'center center',
                transition: isDragging ? 'none' : 'transform 0.15s ease-out',
              }}
              className="relative w-[900px] h-[720px] flex items-center justify-center"
            >
              {/* Central Sun / Nucleus */}
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 rounded-full bg-gradient-to-tr from-violet-600/30 via-indigo-600/20 to-cyan-500/30 border border-indigo-500/40 blur-md pointer-events-none animate-pulse" />
              
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none z-10">
                <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Total Galaxy Spend</p>
                <p className="text-2xl font-black text-white font-mono">${totalSpent.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
              </div>

              {/* Orbital System Rings */}
              <div className="absolute w-[240px] h-[240px] rounded-full border border-slate-800/70 pointer-events-none" />
              <div className="absolute w-[420px] h-[420px] rounded-full border border-slate-800/50 pointer-events-none animate-spin-slow" />
              <div className="absolute w-[600px] h-[600px] rounded-full border border-slate-800/30 pointer-events-none" />
              <div className="absolute w-[780px] h-[780px] rounded-full border border-slate-800/15 pointer-events-none" />

              {/* Render All Planets / Floating Star Nodes */}
              {galaxyNodes.map((node) => {
                const isSelected = activeStar?.id === node.id;
                const isMatchSearch = searchTerm && (
                  node.displayLabel.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  node.raw_description.toLowerCase().includes(searchTerm.toLowerCase())
                );

                return (
                  <div
                    key={node.id}
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveStar(node);
                    }}
                    onMouseEnter={() => setActiveStar(node)}
                    style={{
                      left: `${node.x}px`,
                      top: `${node.y}px`,
                      width: `${node.size}px`,
                      height: `${node.size}px`,
                      backgroundColor: node.color,
                      boxShadow: isSelected || isMatchSearch
                        ? `0 0 45px ${node.color}, 0 0 20px #fff`
                        : `0 0 20px ${node.color}aa`,
                      transform: isSelected || isMatchSearch ? 'scale(1.4)' : 'scale(1)',
                    }}
                    className={`node-element absolute rounded-full -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300 flex items-center justify-center border border-white/40 group z-20`}
                  >
                    {/* Pulsing halo */}
                    <div
                      style={{ backgroundColor: node.color }}
                      className="absolute inset-0 rounded-full animate-ping opacity-25 pointer-events-none"
                    />
                    
                    {/* Initials inside Node Circle */}
                    <span className="text-[10px] font-black text-white drop-shadow-md select-none truncate px-0.5 pointer-events-none">
                      {node.initials}
                    </span>

                    {/* ALWAYS-ON FLOATING BRAND NAME / AMOUNT BADGES */}
                    {labelMode === 'FULL' && (
                      <div className="absolute top-full mt-1.5 left-1/2 -translate-x-1/2 bg-slate-950/95 text-slate-100 px-2.5 py-1 rounded-full border border-slate-700/80 text-[10px] font-bold whitespace-nowrap shadow-2xl pointer-events-none flex items-center gap-1.5 z-30">
                        <span className="truncate max-w-[110px]">{node.displayLabel}</span>
                        <span className="text-indigo-300 font-mono font-bold border-l border-slate-800 pl-1.5">${node.amount.toFixed(0)}</span>
                      </div>
                    )}

                    {labelMode === 'AMOUNTS' && (
                      <div className="absolute top-full mt-1.5 left-1/2 -translate-x-1/2 bg-slate-950/95 text-indigo-300 font-mono px-2 py-0.5 rounded-full border border-slate-700/80 text-[10px] font-bold whitespace-nowrap shadow-2xl pointer-events-none z-30">
                        ${node.amount.toFixed(0)}
                      </div>
                    )}

                    {/* Rich Hover Popup Card */}
                    <div className="absolute bottom-full mb-2.5 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-40 bg-slate-950/95 text-white p-3.5 rounded-2xl border border-slate-700 text-xs whitespace-nowrap shadow-2xl space-y-1.5 min-w-[200px]">
                      <div className="flex justify-between items-center gap-2">
                        <p className="font-bold text-white truncate max-w-[140px]">{node.clean_merchant}</p>
                        <span className="text-[10px] font-bold text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">
                          {node.pctOfCat}%
                        </span>
                      </div>
                      <p className="text-indigo-300 font-mono font-black text-base">${node.amount.toFixed(2)}</p>
                      <div className="text-[10px] text-slate-400 flex justify-between pt-1 border-t border-slate-800">
                        <span>{node.card_member.split(' ')[0]}</span>
                        <span>{node.date}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Canvas Navigation Hint Overlay */}
            <div className="absolute bottom-4 left-4 bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-1.5 text-[11px] text-slate-400 flex items-center gap-2 pointer-events-none z-20">
              <Compass className="w-3.5 h-3.5 text-indigo-400" />
              <span>Drag to Pan • Scroll to Zoom ({Math.round(zoomLevel * 100)}%)</span>
            </div>
          </div>

          {/* Right Sidebar: Analytical Deep Dive */}
          <div className="p-6 bg-slate-950/70 border-l border-slate-800/80 flex flex-col justify-between overflow-y-auto space-y-6 z-20">
            
            {/* Active Star Inspector */}
            {activeStar ? (
              <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/40 space-y-4 animate-fadeIn shadow-xl">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" /> Selected Star Node
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                    activeStar.is_refund ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20'
                  }`}>
                    {activeStar.pctOfCat}% of {categoryName}
                  </span>
                </div>

                <div>
                  <h3 className="text-lg font-bold text-white leading-snug">{activeStar.clean_merchant}</h3>
                  <p className="text-xs text-slate-400 truncate">{activeStar.raw_description}</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Amount</span>
                    <p className={`text-base font-bold font-mono ${activeStar.is_refund ? 'text-emerald-400' : 'text-white'}`}>
                      ${activeStar.amount.toFixed(2)}
                    </p>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Date</span>
                    <p className="text-xs font-semibold text-slate-200">{activeStar.date}</p>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-slate-400">Card Member:</span>
                    <span className="font-semibold text-slate-200">{activeStar.card_member}</span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-slate-400">Necessity Rating:</span>
                    <div className="flex items-center gap-0.5">
                      {[1, 2, 3, 4, 5].map(s => (
                        <Star key={s} className={`w-3 h-3 ${s <= activeStar.necessity_score ? 'text-amber-400 fill-amber-400' : 'text-slate-700'}`} />
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {activeStar.tags?.map((t, i) => (
                    <span key={i} className="text-[10px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2 py-0.5 rounded-full font-medium">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 text-center space-y-2">
                <Sparkles className="w-6 h-6 text-indigo-400 mx-auto animate-bounce" />
                <p className="text-xs font-semibold text-slate-200">Hover or click any planet in the constellation</p>
                <p className="text-[11px] text-slate-400">Drag canvas to pan around • Scroll mouse wheel to zoom in & out.</p>
              </div>
            )}

            {/* Constellation Summary Metrics */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Category Galaxy Analytics</h4>

              {/* Cardholder Split */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-300">Household Split Ratio</span>
                  <span className="text-slate-400">${totalSpent.toLocaleString()}</span>
                </div>
                <div className="h-2.5 w-full bg-slate-950 rounded-full overflow-hidden flex border border-slate-800">
                  <div style={{ width: `${cardholderSplit.dinorahPct}%` }} className="bg-indigo-500 h-full" />
                  <div style={{ width: `${cardholderSplit.jesusPct}%` }} className="bg-cyan-400 h-full" />
                </div>
                <div className="flex justify-between text-[11px]">
                  <span className="text-indigo-400 font-semibold">Dinorah: {cardholderSplit.dinorahPct}% (${cardholderSplit.dinorahAmt.toLocaleString()})</span>
                  <span className="text-cyan-400 font-semibold">Jesus: {cardholderSplit.jesusPct}% (${cardholderSplit.jesusAmt.toLocaleString()})</span>
                </div>
              </div>

              {/* Top 3 Stars in this Galaxy */}
              <div className="space-y-2">
                <span className="text-[11px] font-semibold text-slate-400 uppercase">Top Spent Stars</span>
                {galaxyNodes.slice(0, 3).map((node, i) => (
                  <div key={node.id} className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2 truncate">
                      <span className="w-5 h-5 rounded-md bg-indigo-500/10 text-indigo-400 font-bold text-[10px] flex items-center justify-center border border-indigo-500/20">
                        #{i+1}
                      </span>
                      <span className="font-semibold text-slate-200 truncate">{node.displayLabel}</span>
                    </div>
                    <span className="font-mono font-bold text-indigo-300 ml-2">${node.amount.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-colors cursor-pointer"
            >
              Exit Galaxy View
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
