import React, { useState, useMemo, useRef, useEffect } from 'react';
import { X, Sparkles, Orbit, UserCheck, Star, ZoomIn, ZoomOut, Maximize2, Minimize2, Search, RotateCcw, Compass, Sun, RotateCcw as ReturnIcon, ShieldCheck, Receipt, Database, CheckCircle2, Cpu } from 'lucide-react';
import DeepReceiptModal from './DeepReceiptModal';

// Official multi-color Google Gmail Icon SVG
export function GmailLogo({ className = "w-3 h-3" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M22 6C22 4.9 21.1 4 20 4H4C2.9 4 2 4.9 2 6V18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6Z" fill="#F8F9FA"/>
      <path d="M22 6L12 13L2 6V6C2 4.9 2.9 4 4 4H20C21.1 4 22 4.9 22 6Z" fill="#EA4335"/>
      <path d="M2 6V18C2 19.1 2.9 20 4 20H7V10L2 6Z" fill="#4285F4"/>
      <path d="M22 6V18C22 19.1 21.1 20 20 20H17V10L22 6Z" fill="#34A853"/>
      <path d="M7 20H17V10L12 13.5L7 10V20Z" fill="#FBBC04"/>
    </svg>
  );
}

const GMAIL_GROUNDED_KEYWORDS = ['amazon', 'alo yoga', 'delta', 'whole foods', 'sephora', 'grubhub', 'doordash', 'target', 'google', 'macy'];

const isGmailGroundedMerchant = (merchantName = '', desc = '') => {
  const m = (merchantName + ' ' + desc).toLowerCase();
  return GMAIL_GROUNDED_KEYWORDS.some(k => m.includes(k));
};

export default function SpendGalaxyModal({ categoryName, transactions = [], onClose, onOpenGmailAuth, onOpenTraceConsole }) {
  const [selectedStar, setSelectedStar] = useState(null);
  const [hoveredStar, setHoveredStar] = useState(null);
  const [selectedReceiptTx, setSelectedReceiptTx] = useState(null);
  const [filterCardholder, setFilterCardholder] = useState('ALL');
  const [showReturnsOnly, setShowReturnsOnly] = useState(false);
  const [showGmailOnly, setShowGmailOnly] = useState(false);
  const [showAllLabels, setShowAllLabels] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Semantic Vector Search match state
  const [semanticMatches, setSemanticMatches] = useState({});
  const [isSearching, setIsSearching] = useState(false);

  // Active star for inspector panel
  const activeStar = hoveredStar || selectedStar;

  // Pan & Zoom physics
  const [zoomLevel, setZoomLevel] = useState(1.0);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [isFullscreen, setIsFullscreen] = useState(false);

  const canvasRef = useRef(null);

  // Filter transactions for this modal
  const modalTransactions = useMemo(() => {
    return transactions.filter(t => {
      if (filterCardholder !== 'ALL' && !t.card_member.toLowerCase().includes(filterCardholder.toLowerCase())) {
        return false;
      }
      if (showReturnsOnly && !t.has_return && !t.is_refund) {
        return false;
      }
      if (showGmailOnly && !isGmailGroundedMerchant(t.clean_merchant, t.raw_description)) {
        return false;
      }
      return true;
    });
  }, [transactions, filterCardholder, showReturnsOnly, showGmailOnly]);

  // Aggregate stats
  const totalGrossSpent = useMemo(() => {
    return modalTransactions.reduce((acc, t) => acc + (t.is_refund ? 0 : t.amount), 0);
  }, [modalTransactions]);

  const totalReturnedAmount = useMemo(() => {
    return modalTransactions.reduce((acc, t) => acc + (t.has_return ? (t.return_amount || 0) : t.is_refund ? Math.abs(t.amount) : 0), 0);
  }, [modalTransactions]);

  const totalNetSpent = Math.max(0, totalGrossSpent - totalReturnedAmount);

  // Available cardholders in this category
  const availableMembers = useMemo(() => {
    const set = new Set(transactions.map(t => t.card_member));
    return ['ALL', ...Array.from(set)];
  }, [transactions]);

  // Household split percentage
  const cardholderSplit = useMemo(() => {
    const map = {};
    modalTransactions.forEach(t => {
      const name = t.card_member;
      if (!map[name]) map[name] = { gross: 0, net: 0, count: 0 };
      if (!t.is_refund) map[name].gross += t.amount;
      map[name].net += (t.net_amount !== undefined ? t.net_amount : (t.is_refund ? 0 : t.amount));
      map[name].count += 1;
    });
    return Object.entries(map).map(([name, data]) => ({
      name,
      shortName: name.toUpperCase().includes('DINORAH') ? 'Dinorah' : name.toUpperCase().includes('JESUS') ? 'Jesus' : name.split(' ')[0],
      gross: data.gross,
      net: data.net,
      count: data.count,
      pct: totalGrossSpent > 0 ? Math.round((data.gross / totalGrossSpent) * 100) : 0
    }));
  }, [modalTransactions, totalGrossSpent]);

  // Debounced Semantic Search Hook (calls Vertex AI text-embedding-004 + local dot product)
  useEffect(() => {
    const query = searchTerm.trim();
    if (!query) {
      setSemanticMatches({});
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/search/semantic?q=${encodeURIComponent(query)}&top_k=80&threshold=0.25`);
        if (res.ok) {
          const results = await res.json();
          const matchMap = {};
          results.forEach(r => {
            matchMap[r.id] = r.score;
          });
          setSemanticMatches(matchMap);
        }
      } catch (err) {
        console.error("Semantic search failed:", err);
      } finally {
        setIsSearching(false);
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Gravitational Multi-Cluster Constellation Layout: True 2D Star Clusters & Solar Systems
  const { galaxyNodes, constellationLines, macroClusters } = useMemo(() => {
    if (!modalTransactions.length) return { galaxyNodes: [], constellationLines: [], macroClusters: [] };

    // 1. Consolidate into 4 - 6 High-Level Cohesive Macro Constellations
    const clusterMap = {};

    modalTransactions.forEach(tx => {
      const sub = (tx.cluster_subcategory || tx.subcategory || '').toLowerCase();
      const grp = (tx.cluster_group || tx.primary_category || '').toLowerCase();
      const cleanM = (tx.clean_merchant || '').toLowerCase();
      
      let clusterKey = "Shopping & Retail";
      let clusterIcon = "🛍️";
      let clusterColor = "#ec4899"; // Pink

      if (sub.includes('activewear') || sub.includes('fitness') || sub.includes('yoga') || cleanM.includes('alo') || cleanM.includes('skims') || cleanM.includes('bala') || cleanM.includes('nike')) {
        clusterKey = "Activewear & Fitness";
        clusterIcon = "🧘";
        clusterColor = "#06b6d4"; // Cyan
      } else if (sub.includes('coffee') || sub.includes('cafe') || cleanM.includes('blue bottle') || cleanM.includes('maman') || cleanM.includes('bluestone')) {
        clusterKey = "Cafes & Specialty Coffee";
        clusterIcon = "☕";
        clusterColor = "#f59e0b"; // Amber
      } else if (sub.includes('restaurant') || sub.includes('dining') || sub.includes('taqueria') || sub.includes('delivery') || sub.includes('tacos') || cleanM.includes('grubhub') || cleanM.includes('taco')) {
        clusterKey = "Dining & Delivery";
        clusterIcon = "🌮";
        clusterColor = "#f43f5e"; // Rose
      } else if (sub.includes('luxury') || sub.includes('fashion') || sub.includes('boutique') || cleanM.includes('saks') || cleanM.includes('mango') || cleanM.includes('tory burch') || cleanM.includes('edikted') || cleanM.includes('bloomingdale')) {
        clusterKey = "Fashion & Luxury";
        clusterIcon = "👗";
        clusterColor = "#a855f7"; // Purple
      } else if (sub.includes('e-commerce') || sub.includes('online retail') || sub.includes('tipping') || cleanM.includes('amazon') || cleanM.includes('target')) {
        clusterKey = "E-Commerce & Digital";
        clusterIcon = "📦";
        clusterColor = "#3b82f6"; // Blue
      } else if (sub.includes('flight') || sub.includes('transit') || sub.includes('travel') || cleanM.includes('delta') || cleanM.includes('uber') || cleanM.includes('mta')) {
        clusterKey = "Travel & Transit";
        clusterIcon = "✈️";
        clusterColor = "#10b981"; // Emerald
      }

      if (!clusterMap[clusterKey]) {
        clusterMap[clusterKey] = {
          name: clusterKey,
          icon: clusterIcon,
          color: clusterColor,
          totalSpend: 0,
          items: []
        };
      }
      clusterMap[clusterKey].totalSpend += Math.abs(tx.amount);
      clusterMap[clusterKey].items.push(tx);
    });

    const activeClusters = Object.values(clusterMap).sort((a, b) => b.totalSpend - a.totalSpend);
    const numClusters = activeClusters.length;

    // 2. Position Cluster Sun Centers around the Central Spend Sun
    const clusterOrbitRadius = numClusters <= 3 ? 190 : numClusters <= 5 ? 235 : 270;
    const nodes = [];
    const clusterCentroids = [];

    activeClusters.forEach((cluster, cIdx) => {
      // Symmetrical Angular Distribution for Cluster Centroids
      const clusterAngle = (cIdx / numClusters) * 2 * Math.PI - Math.PI / 2;
      const clusterCenterX = clusterOrbitRadius * Math.cos(clusterAngle);
      const clusterCenterY = clusterOrbitRadius * Math.sin(clusterAngle);

      // Sort items within cluster: largest spend sits at the core of this cluster
      const sortedItems = [...cluster.items].sort((a, b) => Math.abs(b.amount) - Math.abs(a.amount));
      const clusterNodeIds = [];

      sortedItems.forEach((tx, itemIdx) => {
        const absAmt = Math.abs(tx.amount);
        const isDinorah = tx.card_member?.toUpperCase().includes('DINORAH');
        const isJesus = tx.card_member?.toUpperCase().includes('JESUS');
        const isGmailGrounded = isGmailGroundedMerchant(tx.clean_merchant, tx.raw_description);

        // Planet Size: Scaled nicely between 20px and 44px
        const size = Math.max(20, Math.min(44, Math.sqrt(absAmt) * 1.95));

        // 2D Organic Phyllotaxis Spiral Distribution inside the Cluster
        let nodeX = clusterCenterX;
        let nodeY = clusterCenterY;

        if (itemIdx > 0) {
          const goldenAngle = 2.399963229728653; // Golden angle in radians
          const spiralDist = 28 + Math.sqrt(itemIdx) * 19;
          const nodeTheta = itemIdx * goldenAngle;
          nodeX = clusterCenterX + spiralDist * Math.cos(nodeTheta);
          nodeY = clusterCenterY + spiralDist * Math.sin(nodeTheta);
        }

        // Color Coding
        let color;
        if (tx.is_refund || tx.has_return) {
          color = tx.is_fully_returned ? '#10b981' : '#f59e0b';
        } else if (isDinorah) {
          color = absAmt > 250 ? '#ec4899' : '#f472b6';
        } else if (isJesus) {
          color = absAmt > 250 ? '#06b6d4' : '#38bdf8';
        } else {
          color = cluster.color;
        }

        const memberTag = isDinorah ? 'DG' : isJesus ? 'JC' : (tx.card_member || 'AMEX').split(' ').map(w => w[0]).join('').slice(0, 2);
        const initials = (tx.clean_merchant || 'M').split(' ').map(w => w[0]).join('').slice(0, 3).toUpperCase();
        const pctOfCat = totalGrossSpent > 0 ? ((absAmt / totalGrossSpent) * 100).toFixed(1) : '0.0';

        const nodeObj = {
          ...tx,
          x: nodeX,
          y: nodeY,
          size,
          color,
          clusterColor: cluster.color,
          clusterName: cluster.name,
          clusterIcon: cluster.icon,
          initials,
          memberTag,
          isDinorah,
          isJesus,
          isGmailGrounded,
          pctOfCat,
          isClusterCore: itemIdx === 0,
          isTopSpend: absAmt >= 300,
          displayLabel: tx.clean_merchant.length > 15 ? tx.clean_merchant.slice(0, 14) + '...' : tx.clean_merchant
        };

        nodes.push(nodeObj);
        clusterNodeIds.push(nodeObj);
      });

      clusterCentroids.push({
        name: cluster.name,
        icon: cluster.icon,
        totalSpend: cluster.totalSpend,
        count: cluster.items.length,
        color: cluster.color,
        x: clusterCenterX,
        y: clusterCenterY,
        nodes: clusterNodeIds
      });
    });

    // 3. Starlight Constellation Filaments: Connect neighboring stars in the same constellation
    const lines = [];
    clusterCentroids.forEach(cluster => {
      const cNodes = cluster.nodes;
      for (let i = 0; i < cNodes.length; i++) {
        for (let j = i + 1; j < cNodes.length; j++) {
          const dx = cNodes[i].x - cNodes[j].x;
          const dy = cNodes[i].y - cNodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 85) {
            lines.push({
              id: `${cNodes[i].id}-${cNodes[j].id}`,
              x1: cNodes[i].x,
              y1: cNodes[i].y,
              x2: cNodes[j].x,
              y2: cNodes[j].y,
              color: cluster.color,
              sourceNode: cNodes[i],
              targetNode: cNodes[j]
            });
          }
        }
      }
    });

    return { 
      galaxyNodes: nodes, 
      constellationLines: lines, 
      macroClusters: clusterCentroids 
    };
  }, [modalTransactions, totalGrossSpent]);

  // Adjust zoom dynamically on filter changes
  useEffect(() => {
    setZoomLevel(1.0);
    setPanOffset({ x: 0, y: 0 });
  }, [filterCardholder, showReturnsOnly, showGmailOnly, modalTransactions.length]);

  // Pan & Zoom Event Handlers
  const handleMouseDown = (e) => {
    if (e.target.closest('.node-element') || e.target.closest('.control-button')) return;
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

  const handleMouseUp = () => setIsDragging(false);

  const handleWheel = (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
    setZoomLevel(prev => Math.max(0.4, Math.min(2.5, prev * zoomFactor)));
  };

  const resetView = () => {
    setZoomLevel(1.0);
    setPanOffset({ x: 0, y: 0 });
    setSelectedStar(null);
    setHoveredStar(null);
  };

  // Matched star count for search summary
  const hasActiveSearch = Boolean(searchTerm.trim());
  const matchedStarsCount = useMemo(() => {
    if (!hasActiveSearch) return 0;
    const qLower = searchTerm.toLowerCase();
    return galaxyNodes.filter(node => {
      const semScore = semanticMatches[node.id];
      const textMatch = node.clean_merchant.toLowerCase().includes(qLower) || node.raw_description.toLowerCase().includes(qLower);
      return (semScore && semScore >= 0.38) || textMatch;
    }).length;
  }, [galaxyNodes, hasActiveSearch, searchTerm, semanticMatches]);

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center p-2 md:p-6 bg-slate-950/90 backdrop-blur-2xl animate-fadeIn ${isFullscreen ? 'p-0' : ''}`}>
      <div className={`relative w-full h-full max-w-7xl max-h-[92vh] bg-slate-950 border border-slate-800 rounded-3xl shadow-2xl flex flex-col overflow-hidden ${isFullscreen ? 'max-h-screen rounded-none border-none' : ''}`}>
        
        {/* Top Control Header HUD */}
        <div className="p-4 sm:p-5 border-b border-slate-800/80 flex flex-col md:flex-row items-center justify-between gap-3 bg-slate-950/80 z-30">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-violet-600 via-indigo-500 to-cyan-400 text-white shadow-lg shadow-indigo-500/25">
              <Orbit className="w-5 h-5 animate-spin-slow" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">Spend Galaxy Constellation</span>
                <span className="px-2 py-0.2 text-[10px] font-bold rounded-full bg-violet-500/10 text-violet-300 border border-violet-500/20 flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-violet-400" /> Gemini 3.7 Flash
                </span>
                <span className="px-2 py-0.2 text-[10px] font-bold rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                  {galaxyNodes.length} Visible Stars
                </span>
                {hasActiveSearch && (
                  <span className="px-2 py-0.2 text-[10px] font-bold rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/40 flex items-center gap-1 animate-pulse">
                    <Cpu className="w-2.5 h-2.5" /> {matchedStarsCount} Focus Stars
                  </span>
                )}
              </div>
              <h2 className="text-lg font-extrabold text-white">{categoryName} Orbit System</h2>
            </div>
          </div>

          {/* Quick HUD Filters */}
          <div className="flex items-center gap-2 flex-wrap">
            {/* CONTEXTUAL SEMANTIC AI SEARCH BAR */}
            <div className="relative">
              <Search className={`w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 ${isSearching ? 'text-amber-400 animate-spin' : 'text-slate-400'}`} />
              <input
                type="text"
                placeholder="Search semantic keywords (e.g. skim, yoga, flights)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className={`bg-slate-900 text-xs text-slate-100 pl-8 pr-7 py-1.5 rounded-xl border focus:outline-none transition-all w-48 sm:w-64 ${
                  hasActiveSearch
                    ? 'border-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.35)]'
                    : 'border-slate-800 focus:border-indigo-500/50'
                }`}
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-200 text-xs font-bold"
                >
                  ×
                </button>
              )}
            </div>

            {/* REAL COLOR GMAIL GROUNDED ONLY TOGGLE */}
            <button
              onClick={() => setShowGmailOnly(!showGmailOnly)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                showGmailOnly
                  ? 'bg-red-500/20 text-red-200 border border-red-500/60 shadow-md shadow-red-500/20'
                  : 'bg-slate-900 text-slate-300 border border-slate-800 hover:text-white'
              }`}
              title="Show only transactions verified via Gmail Grounding"
            >
              <GmailLogo className="w-3.5 h-3.5 shrink-0" />
              <span>Gmail Grounded {showGmailOnly ? 'Active' : ''}</span>
            </button>

            {/* Returns Only Filter Toggle */}
            <button
              onClick={() => setShowReturnsOnly(!showReturnsOnly)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                showReturnsOnly
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 shadow-md shadow-emerald-500/20'
                  : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200'
              }`}
              title="Show only returned and refunded items"
            >
              <ReturnIcon className="w-3.5 h-3.5" />
              <span>↩️ Returns</span>
            </button>

            {/* Toggle All Labels Button */}
            <button
              onClick={() => setShowAllLabels(!showAllLabels)}
              className={`px-2.5 py-1.5 rounded-xl text-xs font-semibold transition-all border ${
                showAllLabels
                  ? 'bg-indigo-600 text-white border-indigo-500 shadow-sm'
                  : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
              }`}
              title="Toggle full text labels on all stars"
            >
              {showAllLabels ? '🏷️ All Labels' : '✨ Clean View'}
            </button>

            {/* Cardholder Pill Toggle */}
            <div className="flex items-center bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
              {availableMembers.map(m => (
                <button
                  key={m}
                  onClick={() => setFilterCardholder(m)}
                  className={`px-2.5 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                    filterCardholder === m
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {m === 'ALL' ? '👥 All' : m.toUpperCase().includes('DINORAH') ? '🟣 Dinorah' : m.toUpperCase().includes('JESUS') ? '🔵 Jesus' : m.split(' ')[0]}
                </button>
              ))}
            </div>

            {/* Pan/Zoom Controls */}
            <div className="flex items-center bg-slate-900 p-1 rounded-xl border border-slate-800 gap-1">
              <button
                onClick={() => setZoomLevel(prev => Math.min(2.5, prev + 0.15))}
                className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 transition-colors"
                title="Zoom In"
              >
                <ZoomIn className="w-4 h-4" />
              </button>
              <button
                onClick={() => setZoomLevel(prev => Math.max(0.4, prev - 0.15))}
                className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 transition-colors"
                title="Zoom Out"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
              <button
                onClick={resetView}
                className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 transition-colors"
                title="Reset View"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 transition-colors"
                title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
              >
                {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Galaxy Body: Spacious Interactive Universe */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 relative overflow-hidden">
          
          {/* Constellation Canvas Interactive Area */}
          <div
            ref={canvasRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onWheel={handleWheel}
            onClick={() => setSelectedStar(null)}
            className={`lg:col-span-2 relative h-full w-full overflow-hidden select-none bg-slate-950/40 ${
              isDragging ? 'cursor-grabbing' : 'cursor-grab'
            }`}
          >
            {/* Absolute Centered Pan/Zoom Stage (Origin 0,0 is Dead Center of Viewport) */}
            <div
              style={{
                position: 'absolute',
                left: '50%',
                top: '50%',
                width: '0px',
                height: '0px',
                transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
                transformOrigin: '0 0',
                transition: isDragging ? 'none' : 'transform 0.15s ease-out',
              }}
            >
              {/* Central Radiant Sun Core Glow Corona */}
              <div className={`absolute left-0 top-0 -translate-x-1/2 -translate-y-1/2 w-48 h-48 rounded-full bg-gradient-to-tr from-violet-600/25 via-indigo-500/20 to-amber-400/30 blur-2xl pointer-events-none transition-opacity duration-500 ${hasActiveSearch ? 'opacity-40' : 'opacity-100 animate-pulse'} z-10`} />
              <div className="absolute left-0 top-0 -translate-x-1/2 -translate-y-1/2 w-36 h-36 rounded-full border border-amber-400/30 pointer-events-none animate-spin-slow z-10" />
              
              {/* Center Celestial Spend Orb Card (Dead Center at 0, 0) */}
              <div className={`absolute left-0 top-0 -translate-x-1/2 -translate-y-1/2 w-32 h-32 rounded-full bg-slate-950/98 border-2 border-amber-400/80 shadow-[0_0_35px_rgba(251,191,36,0.35),inset_0_0_15px_rgba(99,102,241,0.3)] flex flex-col items-center justify-center p-2 text-center z-25 backdrop-blur-3xl pointer-events-none transition-all duration-500 ${hasActiveSearch ? 'scale-95 opacity-80' : 'scale-100 opacity-100'}`}>
                <span className="px-1.5 py-0.2 rounded-full text-[7.5px] font-black uppercase tracking-widest text-amber-300 bg-amber-950/90 border border-amber-500/60 shadow-sm flex items-center gap-0.5 mb-0.5">
                  <Sparkles className="w-2 h-2 text-amber-400" /> Total Spend
                </span>
                
                <p className="text-base font-black text-white font-mono tracking-tight drop-shadow-[0_2px_8px_rgba(255,255,255,0.6)]">
                  ${totalGrossSpent.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
                
                {totalReturnedAmount > 0 && (
                  <div className="mt-0.5 px-1 py-0.2 rounded bg-emerald-950/90 border border-emerald-500/40 text-[7.5px] font-mono font-bold text-emerald-400">
                    ↩️ -${totalReturnedAmount.toFixed(2)}
                  </div>
                )}

                <span className="text-[7.5px] text-slate-400 font-medium mt-0.5 flex items-center gap-0.5">
                  🪐 {galaxyNodes.length} Stars
                </span>
              </div>

              {/* Main Galactic Macro Orbit Ring */}
              <div
                style={{ width: '480px', height: '480px' }}
                className={`absolute left-0 top-0 -translate-x-1/2 -translate-y-1/2 rounded-full border border-slate-800/30 border-dashed pointer-events-none z-10`}
              />

              {/* Macro Constellation Nebula Glow Clouds & Star Web */}
              {macroClusters.map((cluster, cIdx) => (
                <React.Fragment key={cIdx}>
                  {/* Glowing Cosmic Nebula Cloud */}
                  <div
                    style={{
                      left: `${cluster.x}px`,
                      top: `${cluster.y}px`,
                      backgroundColor: cluster.color,
                    }}
                    className="absolute -translate-x-1/2 -translate-y-1/2 w-44 h-44 rounded-full blur-3xl opacity-15 pointer-events-none z-12 animate-pulse"
                  />
                  {/* Orbit Boundary Circle */}
                  <div
                    style={{
                      left: `${cluster.x}px`,
                      top: `${cluster.y}px`,
                      borderColor: `${cluster.color}35`,
                    }}
                    className="absolute -translate-x-1/2 -translate-y-1/2 w-36 h-36 rounded-full border border-dashed pointer-events-none z-12"
                  />
                  {/* Floating Nebula Cluster Badge */}
                  <div
                    style={{
                      left: `${cluster.x}px`,
                      top: `${cluster.y - 75}px`,
                    }}
                    className="absolute -translate-x-1/2 -translate-y-1/2 pointer-events-none z-22 text-center"
                  >
                    <span 
                      style={{ borderColor: `${cluster.color}60`, color: cluster.color, backgroundColor: 'rgba(15, 23, 42, 0.92)' }}
                      className="px-2.5 py-1 rounded-xl text-[9px] font-black uppercase tracking-wider border shadow-xl backdrop-blur-xl whitespace-nowrap inline-flex items-center gap-1"
                    >
                      <span>{cluster.icon}</span>
                      <span>{cluster.name}</span>
                    </span>
                    <span className="text-[8px] font-mono text-slate-400 block mt-0.5 font-bold">
                      ${cluster.totalSpend.toLocaleString(undefined, { maximumFractionDigits: 0 })} • {cluster.count} stars
                    </span>
                  </div>
                </React.Fragment>
              ))}

              {/* Starlight Filaments (Inter-star SVG vector connections) */}
              <svg className="absolute -left-[600px] -top-[600px] w-[1200px] h-[1200px] pointer-events-none z-15 overflow-visible">
                {constellationLines.map((line) => {
                  const isHoverRelated = (hoveredStar && (hoveredStar.id === line.sourceNode.id || hoveredStar.id === line.targetNode.id));
                  const isSelectRelated = (selectedStar && (selectedStar.id === line.sourceNode.id || selectedStar.id === line.targetNode.id));
                  const strokeOpacity = isHoverRelated || isSelectRelated ? 0.9 : hasActiveSearch ? 0.08 : 0.25;
                  const strokeWidth = isHoverRelated || isSelectRelated ? 2 : 1;

                  return (
                    <line
                      key={line.id}
                      x1={600 + line.x1}
                      y1={600 + line.y1}
                      x2={600 + line.x2}
                      y2={600 + line.y2}
                      stroke={line.color}
                      strokeWidth={strokeWidth}
                      strokeOpacity={strokeOpacity}
                      strokeDasharray={isHoverRelated || isSelectRelated ? "none" : "2,3"}
                      className="transition-all duration-300"
                    />
                  );
                })}
              </svg>

              {/* Render All Planets with Spotlight Focus & Deep-Space Dimming */}
              {galaxyNodes.map((node) => {
                const isSelected = selectedStar?.id === node.id;
                const isHovered = hoveredStar?.id === node.id;

                // Check text match + semantic vector match
                const qLower = searchTerm.toLowerCase();
                const textMatch = hasActiveSearch && (
                  node.clean_merchant.toLowerCase().includes(qLower) ||
                  node.raw_description.toLowerCase().includes(qLower) ||
                  node.primary_category.toLowerCase().includes(qLower)
                );
                const semanticScore = semanticMatches[node.id];
                const isSemMatch = semanticScore !== undefined && semanticScore >= 0.25;

                const isMatchSearch = hasActiveSearch && (textMatch || isSemMatch);
                const matchScoreDisplay = semanticScore ? Math.round(semanticScore * 100) : textMatch ? 100 : null;

                const hasReturn = node.has_return || node.is_refund;
                const shouldShowPill = showAllLabels || isSelected || isHovered || isMatchSearch;

                // Deep-Space Obscurity & Spotlight Scale physics
                const opacity = hasActiveSearch ? (isMatchSearch ? 1 : 0.12) : 1;
                const filterStyle = hasActiveSearch && !isMatchSearch ? 'blur(1.5px) grayscale(90%)' : 'none';
                const scaleTransform = isSelected
                  ? 'scale(1.7)'
                  : isHovered
                  ? 'scale(1.5)'
                  : isMatchSearch
                  ? 'scale(1.45)'
                  : hasActiveSearch
                  ? 'scale(0.82)'
                  : 'scale(1)';

                return (
                  <div
                    key={node.id}
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedStar(node);
                    }}
                    onMouseEnter={() => setHoveredStar(node)}
                    onMouseLeave={() => setHoveredStar(null)}
                    style={{
                      left: `${node.x}px`,
                      top: `${node.y}px`,
                      width: `${node.size}px`,
                      height: `${node.size}px`,
                      backgroundColor: node.color,
                      opacity,
                      filter: filterStyle,
                      boxShadow: isMatchSearch || isSelected
                        ? `0 0 50px ${node.color}, 0 0 25px #ffffff, 0 0 60px ${node.color}cc`
                        : hasReturn
                        ? `0 0 25px #10b981, 0 0 10px ${node.color}`
                        : `0 0 15px ${node.color}99`,
                      transform: scaleTransform,
                      zIndex: isSelected || isHovered ? 60 : isMatchSearch ? 50 : 20,
                      pointerEvents: hasActiveSearch && !isMatchSearch ? 'none' : 'auto'
                    }}
                    className={`node-element absolute rounded-full -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300 flex items-center justify-center border border-white/40 group`}
                  >
                    {/* SUPERNOVA SPOTLIGHT RING FOR SEMANTIC MATCHES */}
                    {isMatchSearch && (
                      <div
                        style={{ width: `${node.size + 24}px`, height: `${node.size + 24}px` }}
                        className="absolute rounded-full border-2 border-amber-300 animate-pulse pointer-events-none shadow-[0_0_25px_rgba(251,191,36,0.9)]"
                      />
                    )}

                    {/* LOCKED SELECTION HIGHLIGHT RING */}
                    {isSelected && (
                      <div
                        style={{ width: `${node.size + 16}px`, height: `${node.size + 16}px` }}
                        className="absolute rounded-full border-2 border-cyan-400 animate-pulse pointer-events-none shadow-[0_0_15px_rgba(6,182,212,0.8)]"
                      />
                    )}

                    {/* HOLOGRAPHIC RETURN / REFUND ROTATING DASHED RING */}
                    {hasReturn && (
                      <div
                        style={{ width: `${node.size + 12}px`, height: `${node.size + 12}px` }}
                        className="absolute rounded-full border-2 border-dashed border-emerald-400 animate-spin-slow pointer-events-none shadow-[0_0_12px_rgba(16,185,129,0.5)]"
                      />
                    )}

                    {/* AUTHENTIC MULTI-COLOR GMAIL ICON BADGE (TOP-LEFT OF PLANET) */}
                    {node.isGmailGrounded ? (
                      <div
                        className="absolute -top-1 -left-1 p-0.5 rounded-full bg-slate-950 border border-slate-700 shadow-md z-30 pointer-events-none flex items-center justify-center"
                        title="Verified with Gmail MCP Grounding"
                      >
                        <GmailLogo className="w-2 h-2" />
                      </div>
                    ) : (
                      <div
                        className="absolute -top-1 -left-1 p-0.5 rounded-full bg-slate-950 text-violet-400 border border-violet-500/40 shadow-sm z-30 pointer-events-none opacity-70"
                        title="Synthesized by Google ADK LLM"
                      >
                        <Sparkles className="w-1.5 h-1.5 text-violet-400" />
                      </div>
                    )}

                    {/* Pulsing halo */}
                    <div
                      style={{ backgroundColor: node.color }}
                      className={`absolute inset-0 rounded-full pointer-events-none ${hasActiveSearch && !isMatchSearch ? 'hidden' : 'animate-ping opacity-25'}`}
                    />
                    
                    {/* Initials inside Node Circle */}
                    <span className="text-[8px] sm:text-[9px] font-black text-white drop-shadow-md select-none truncate px-0.5 pointer-events-none">
                      {node.initials}
                    </span>

                    {/* CARDHOLDER BADGE TAG (TOP RIGHT OF PLANET) */}
                    <div
                      className={`absolute -top-1 -right-1 px-1 py-0.2 rounded-full text-[6.5px] font-black tracking-tighter border shadow-md pointer-events-none z-30 ${
                        node.isDinorah
                          ? 'bg-pink-950/90 text-pink-300 border-pink-500/50'
                          : node.isJesus
                          ? 'bg-cyan-950/90 text-cyan-300 border-cyan-500/50'
                          : 'bg-slate-950/90 text-slate-300 border-slate-700'
                      }`}
                    >
                      {node.memberTag}
                    </div>

                    {/* RETURN OVERLAY BADGE PILL (IF RETURNED/REFUNDED) */}
                    {hasReturn && (
                      <div className="absolute -bottom-1.5 -left-1 bg-emerald-950/95 text-emerald-300 border border-emerald-500/70 text-[6.5px] font-black px-1 py-0.2 rounded-full shadow-lg pointer-events-none flex items-center gap-0.5 z-30">
                        <span>↩️</span>
                      </div>
                    )}

                    {/* Clean Floating HUD Pill Label with Match Precision */}
                    {shouldShowPill && (
                      <div className={`absolute top-full mt-1 left-1/2 -translate-x-1/2 whitespace-nowrap text-[8.5px] font-bold px-2 py-0.5 rounded-md border pointer-events-none shadow-xl flex items-center gap-1 z-40 ${
                        isMatchSearch
                          ? 'bg-amber-950/95 text-amber-200 border-amber-400/80 shadow-[0_0_15px_rgba(251,191,36,0.4)] animate-bounce-short'
                          : 'bg-slate-950/90 text-slate-200 border-slate-800'
                      }`}>
                        <span>{node.displayLabel}</span>
                        <span className="text-indigo-300 font-mono">${node.amount.toFixed(0)}</span>
                        {isMatchSearch && matchScoreDisplay && (
                          <span className="px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[7.5px] font-mono">
                            {matchScoreDisplay}% Match
                          </span>
                        )}
                      </div>
                    )}

                    {/* RICH HOVER POPUP CARD (IN FRONT OF ALL NODES) */}
                    {(isHovered || isSelected) && (
                      <div className="absolute bottom-full mb-2.5 left-1/2 -translate-x-1/2 pointer-events-none z-50 bg-slate-950/98 text-white p-3 rounded-2xl border-2 border-indigo-500 text-xs whitespace-nowrap shadow-[0_0_30px_rgba(0,0,0,0.9)] space-y-1.5 min-w-[230px] backdrop-blur-3xl animate-fadeIn">
                        <div className="flex justify-between items-center gap-2">
                          <p className="font-extrabold text-white text-xs truncate max-w-[140px]">{node.clean_merchant}</p>
                          {node.isGmailGrounded ? (
                            <span className="text-[8.5px] font-black text-emerald-300 bg-emerald-950/90 px-2 py-0.5 rounded-full border border-emerald-500/40 flex items-center gap-1">
                              <GmailLogo className="w-2.5 h-2.5" /> Gmail Grounded
                            </span>
                          ) : (
                            <span className="text-[8.5px] font-bold text-violet-300 bg-violet-950/90 px-2 py-0.5 rounded-full border border-violet-500/40 flex items-center gap-1">
                              <Sparkles className="w-2 h-2 text-violet-400" /> ADK LLM
                            </span>
                          )}
                        </div>
                        <div className="flex items-baseline justify-between">
                          <p className="text-indigo-300 font-mono font-black text-base">${node.amount.toFixed(2)}</p>
                          {node.has_return && (
                            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/80 px-1.5 py-0.2 rounded border border-emerald-500/40">
                              ↩️ Returned -${node.return_amount.toFixed(2)}
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-slate-300 flex justify-between pt-1 border-t border-slate-800">
                          <span className={`font-bold ${node.isDinorah ? 'text-pink-400' : node.isJesus ? 'text-cyan-400' : 'text-slate-200'}`}>
                            {node.card_member}
                          </span>
                          <span className="font-mono text-slate-400">{node.date}</span>
                        </div>
                        {isMatchSearch && matchScoreDisplay && (
                          <div className="text-[9px] text-amber-300 font-semibold text-center pt-0.5 bg-amber-950/40 rounded py-0.5">
                            ⚡ Vector Semantic Relevance: {matchScoreDisplay}%
                          </div>
                        )}
                        <p className="text-[8.5px] text-indigo-400/80 italic text-center pt-0.5">Click planet to lock inspector</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Canvas Navigation & Engine Status Overlay */}
            <div className="absolute bottom-4 left-4 bg-slate-950/85 border border-slate-800 rounded-xl px-3 py-1.5 text-[11px] text-slate-400 flex items-center gap-3 pointer-events-none z-20 backdrop-blur-md">
              <div className="flex items-center gap-1.5 text-slate-300 font-semibold">
                <GmailLogo className="w-3.5 h-3.5" />
                <span>Gmail Grounded</span>
              </div>
              <div className="flex items-center gap-1 text-slate-400">
                <Sparkles className="w-3 h-3 text-violet-400" />
                <span>Vertex AI text-embedding-004</span>
              </div>
              {hasActiveSearch && (
                <div className="flex items-center gap-1 text-amber-300 font-bold border-l border-slate-800 pl-3">
                  <Cpu className="w-3 h-3 text-amber-400 animate-spin" />
                  <span>Spotlight Active ({matchedStarsCount} Stars)</span>
                </div>
              )}
            </div>
          </div>

          {/* Right Sidebar: Analytical Deep Dive */}
          <div className="p-5 bg-slate-950/70 border-l border-slate-800/80 flex flex-col justify-between overflow-y-auto space-y-4 z-20">
            
            {/* Active Star Inspector */}
            {activeStar ? (
              <div className="p-4 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/40 space-y-3 animate-fadeIn shadow-xl">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5" /> {selectedStar?.id === activeStar.id ? '📌 Selected Star (Locked)' : '👁 Hovered Preview'}
                  </span>
                  
                  {activeStar.isGmailGrounded ? (
                    <span className="text-[9px] font-black px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5">
                      <GmailLogo className="w-3 h-3" /> Gmail Grounded
                    </span>
                  ) : (
                    <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-300 border border-violet-500/20 flex items-center gap-1">
                      <Sparkles className="w-2.5 h-2.5 text-violet-400" /> ADK LLM
                    </span>
                  )}
                </div>

                <div>
                  <h3 className="text-base font-bold text-white leading-snug">{activeStar.clean_merchant}</h3>
                  <p className="text-xs text-slate-400 truncate">{activeStar.raw_description}</p>
                </div>

                <div className="flex items-baseline justify-between">
                  <span className="text-xl font-mono font-black text-indigo-300">${activeStar.amount.toFixed(2)}</span>
                  <span className="text-xs font-mono text-slate-400">{activeStar.date}</span>
                </div>

                {/* RETURN / REFUND STATUS BADGE */}
                {activeStar.has_return && (
                  <div className="p-2.5 rounded-xl bg-emerald-950/30 border border-emerald-500/40 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-emerald-300 flex items-center gap-1">
                        <ReturnIcon className="w-3 h-3" /> Returned / Refunded
                      </span>
                      <span className="font-mono font-bold text-emerald-400">-${activeStar.return_amount.toFixed(2)}</span>
                    </div>
                  </div>
                )}

                <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Card Member:</span>
                    <span className="font-semibold text-slate-200">{activeStar.card_member}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Category:</span>
                    <span className="font-semibold text-slate-200">{activeStar.primary_category}</span>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedReceiptTx(activeStar)}
                  className="w-full py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-xs shadow-md shadow-violet-600/20 flex items-center justify-center gap-2 cursor-pointer transition-all"
                >
                  <Receipt className="w-3.5 h-3.5" /> 🧾 View Deep Receipt & Line Items
                </button>
              </div>
            ) : (
              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 text-center space-y-1.5">
                <Sparkles className="w-5 h-5 text-indigo-400 mx-auto animate-bounce" />
                <p className="text-xs font-semibold text-slate-200">
                  {hasActiveSearch ? `Spotlight focused on ${matchedStarsCount} matching stars` : 'Click any planet in the constellation'}
                </p>
                <p className="text-[10px] text-slate-400">Type any merchant, product, or semantic category to illuminate relevant stars.</p>
              </div>
            )}

            {/* Constellation Summary Metrics */}
            <div className="space-y-3">
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Category Galaxy Analytics</h4>

              {/* Household Split */}
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-300">Household Split Breakdown</span>
                  <span className="text-slate-400">${totalGrossSpent.toLocaleString()}</span>
                </div>
                <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden flex border border-slate-800">
                  {cardholderSplit.map((member, idx) => (
                    <div
                      key={member.name}
                      style={{ width: `${member.pct}%` }}
                      className={idx === 0 ? 'bg-pink-500 h-full' : idx === 1 ? 'bg-cyan-400 h-full' : 'bg-violet-500 h-full'}
                    />
                  ))}
                </div>
              </div>

              {/* Top 3 Stars in this Galaxy */}
              <div className="space-y-1.5">
                <span className="text-[10px] font-semibold text-slate-400 uppercase">Top Spent Stars</span>
                {galaxyNodes.slice(0, 3).map((node, i) => (
                  <div key={node.id} className="p-2 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1.5 truncate">
                      {node.isGmailGrounded ? (
                        <GmailLogo className="w-3.5 h-3.5 shrink-0" />
                      ) : (
                        <Sparkles className="w-3.5 h-3.5 text-violet-400 shrink-0" />
                      )}
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
              className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-colors cursor-pointer"
            >
              Exit Galaxy View
            </button>
          </div>
        </div>
      </div>

      {/* Deep Receipt Intelligence Modal */}
      {selectedReceiptTx && (
        <DeepReceiptModal
          transaction={selectedReceiptTx}
          onClose={() => setSelectedReceiptTx(null)}
          onOpenGmailAuth={onOpenGmailAuth}
          onOpenTraceConsole={onOpenTraceConsole}
        />
      )}
    </div>
  );
}
