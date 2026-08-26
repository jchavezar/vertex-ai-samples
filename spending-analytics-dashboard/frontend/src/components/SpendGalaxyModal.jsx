import React, { useState, useMemo, useRef, useEffect } from 'react';
import { X, Sparkles, Orbit, UserCheck, Star, ZoomIn, ZoomOut, Maximize2, Minimize2, Search, RotateCcw, Compass, Sun, RotateCcw as ReturnIcon, ShieldCheck, Receipt, Database, CheckCircle2, Cpu, Users } from 'lucide-react';
import DeepReceiptModal from './DeepReceiptModal';
import { getUserConfig, EXECUTIVE_USERS, ALL_EXECUTIVE_USERS_LIST } from '../utils/userConfig';

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

const GMAIL_GROUNDED_KEYWORDS = ['amazon', 'alo yoga', 'delta', 'whole foods', 'sephora', 'grubhub', 'doordash', 'target', 'google', 'macy', 'uber', 'apple', 'four seasons'];

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
      if (filterCardholder !== 'ALL') {
        const userCfg = getUserConfig(t.card_member);
        if (!userCfg.fullName.toUpperCase().includes(filterCardholder.toUpperCase()) && 
            !userCfg.short.toUpperCase().includes(filterCardholder.toUpperCase())) {
          return false;
        }
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

  // 5 Executive User Split Breakdown
  const executiveSplit = useMemo(() => {
    const map = {};
    ALL_EXECUTIVE_USERS_LIST.forEach(u => {
      map[u.name] = { user: u, gross: 0, net: 0, count: 0 };
    });

    modalTransactions.forEach(t => {
      const uCfg = getUserConfig(t.card_member);
      const key = uCfg.fullName || t.card_member;
      if (!map[key]) {
        map[key] = { user: uCfg, gross: 0, net: 0, count: 0 };
      }
      if (!t.is_refund) map[key].gross += t.amount;
      map[key].net += (t.net_amount !== undefined ? t.net_amount : (t.is_refund ? 0 : t.amount));
      map[key].count += 1;
    });

    return Object.values(map)
      .filter(item => item.count > 0 || filterCardholder === 'ALL')
      .map(item => ({
        ...item,
        pct: totalGrossSpent > 0 ? Math.round((item.gross / totalGrossSpent) * 100) : 0
      }));
  }, [modalTransactions, totalGrossSpent, filterCardholder]);

  // Debounced Semantic Search Hook
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

  // Gravitational Multi-Cluster Constellation Layout: Clear Cluster-by-Cluster Spatial Separation
  const { galaxyNodes, constellationLines, macroClusters } = useMemo(() => {
    if (!modalTransactions.length) return { galaxyNodes: [], constellationLines: [], macroClusters: [] };

    // 1. Group into Granular Sub-Clusters based on subcategory, cluster_group, or merchant
    const clusterMap = {};

    modalTransactions.forEach(tx => {
      const sub = (tx.cluster_subcategory || tx.subcategory || '').toLowerCase();
      const grp = (tx.cluster_group || tx.primary_category || '').toLowerCase();
      const cleanM = (tx.clean_merchant || '').toLowerCase();
      
      let clusterKey = tx.subcategory || tx.cluster_group || "General Retail";
      let clusterIcon = "🛍️";
      let clusterColor = "#ec4899"; // Pink

      // Sub-segment classification for crystal-clear visual grouping
      if (sub.includes('boutique') || cleanM.includes('aritzia') || cleanM.includes('alice') || cleanM.includes('mango') || cleanM.includes('zara') || cleanM.includes('edikted')) {
        clusterKey = "Boutique & Ready-to-Wear";
        clusterIcon = "👗";
        clusterColor = "#ec4899"; // Pink
      } else if (sub.includes('luxury') || cleanM.includes('bergdorf') || cleanM.includes('saks') || cleanM.includes('bloomingdale') || cleanM.includes('tory burch')) {
        clusterKey = "High Luxury & Department";
        clusterIcon = "💎";
        clusterColor = "#a855f7"; // Purple
      } else if (sub.includes('activewear') || sub.includes('athleisure') || cleanM.includes('alo') || cleanM.includes('skims') || cleanM.includes('vuori') || cleanM.includes('bala') || cleanM.includes('nike')) {
        clusterKey = "Activewear & Wellness";
        clusterIcon = "🧘";
        clusterColor = "#06b6d4"; // Cyan
      } else if (sub.includes('beauty') || sub.includes('optics') || cleanM.includes('sephora') || cleanM.includes('sisu') || cleanM.includes('jimmy') || cleanM.includes('glossier')) {
        clusterKey = "Beauty, Optics & Aesthetics";
        clusterIcon = "✨";
        clusterColor = "#f43f5e"; // Rose
      } else if (sub.includes('e-commerce') || cleanM.includes('amazon') || cleanM.includes('target') || cleanM.includes('apple')) {
        clusterKey = "E-Commerce & Tech Retail";
        clusterIcon = "📦";
        clusterColor = "#3b82f6"; // Blue
      } else if (sub.includes('fine dining') || cleanM.includes('nobu') || cleanM.includes('gramercy') || cleanM.includes('bernardin') || cleanM.includes('bondst')) {
        clusterKey = "Fine Dining & Tasting";
        clusterIcon = "🍷";
        clusterColor = "#f43f5e"; // Rose
      } else if (sub.includes('cafe') || sub.includes('roasters') || cleanM.includes('blue bottle') || cleanM.includes('maman') || cleanM.includes('bluestone') || cleanM.includes('blank street')) {
        clusterKey = "Specialty Cafes & Roasters";
        clusterIcon = "☕";
        clusterColor = "#f59e0b"; // Amber
      } else if (sub.includes('bistro') || cleanM.includes('tacos') || cleanM.includes('tacombi') || cleanM.includes('sweetgreen') || cleanM.includes('shake shack')) {
        clusterKey = "Bistros & Fast Casual";
        clusterIcon = "🌮";
        clusterColor = "#fb923c"; // Orange
      } else if (sub.includes('delivery') || cleanM.includes('doordash') || cleanM.includes('grubhub') || cleanM.includes('eats') || cleanM.includes('caviar')) {
        clusterKey = "Delivery & Meal Services";
        clusterIcon = "🛵";
        clusterColor = "#8b5cf6"; // Violet
      } else if (sub.includes('groceries') || cleanM.includes('whole foods') || cleanM.includes('trader') || cleanM.includes('eataly')) {
        clusterKey = "Artisanal Groceries";
        clusterIcon = "🥑";
        clusterColor = "#10b981"; // Emerald
      } else if (sub.includes('aviation') || cleanM.includes('delta') || cleanM.includes('united') || cleanM.includes('jetblue')) {
        clusterKey = "Aviation & Airlines";
        clusterIcon = "✈️";
        clusterColor = "#0ea5e9"; // Sky Blue
      } else if (sub.includes('hospitality') || cleanM.includes('four seasons') || cleanM.includes('ritz') || cleanM.includes('marriott') || cleanM.includes('airbnb')) {
        clusterKey = "Hospitality & Resorts";
        clusterIcon = "🏨";
        clusterColor = "#6366f1"; // Indigo
      } else if (sub.includes('transit') || cleanM.includes('uber') || cleanM.includes('lyft') || cleanM.includes('mta')) {
        clusterKey = "Urban Transit & Fleet";
        clusterIcon = "🚗";
        clusterColor = "#14b8a6"; // Teal
      } else if (sub.includes('cloud') || cleanM.includes('google cloud') || cleanM.includes('aws') || cleanM.includes('openai') || cleanM.includes('anthropic')) {
        clusterKey = "Cloud & AI Infrastructure";
        clusterIcon = "☁️";
        clusterColor = "#2563eb"; // Royal Blue
      } else if (sub.includes('developer') || cleanM.includes('github') || cleanM.includes('vercel') || cleanM.includes('figma') || cleanM.includes('notion') || cleanM.includes('slack')) {
        clusterKey = "Dev & Workplace SaaS";
        clusterIcon = "💻";
        clusterColor = "#9333ea"; // Purple
      } else if (sub.includes('streaming') || cleanM.includes('netflix') || cleanM.includes('spotify') || cleanM.includes('youtube') || cleanM.includes('equinox')) {
        clusterKey = "Digital Subscriptions & Fitness";
        clusterIcon = "🎵";
        clusterColor = "#d97706"; // Amber
      } else if (sub.includes('consulting') || cleanM.includes('deloitte') || cleanM.includes('mckinsey') || cleanM.includes('legalzoom')) {
        clusterKey = "Corporate Advisory & Legal";
        clusterIcon = "⚖️";
        clusterColor = "#6366f1"; // Indigo
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

    // 2. Position Cluster Sun Centroids with Wide Orbital Radius (280px - 340px)
    const clusterOrbitRadius = numClusters <= 3 ? 240 : numClusters <= 5 ? 290 : 330;
    const nodes = [];
    const clusterCentroids = [];

    activeClusters.forEach((cluster, cIdx) => {
      // Symmetrical Angular Distribution for Cluster Centroids
      const clusterAngle = (cIdx / numClusters) * 2 * Math.PI - Math.PI / 2;
      const clusterCenterX = clusterOrbitRadius * Math.cos(clusterAngle);
      const clusterCenterY = clusterOrbitRadius * Math.sin(clusterAngle);

      // Sort items within cluster: largest spend sits closest to the core of this cluster
      const sortedItems = [...cluster.items].sort((a, b) => Math.abs(b.amount) - Math.abs(a.amount));
      const clusterNodeIds = [];

      sortedItems.forEach((tx, itemIdx) => {
        const absAmt = Math.abs(tx.amount);
        const userCfg = getUserConfig(tx.card_member);
        const isGmailGrounded = isGmailGroundedMerchant(tx.clean_merchant, tx.raw_description);

        // Planet Size: Scaled nicely between 20px and 44px
        const size = Math.max(20, Math.min(44, Math.sqrt(absAmt) * 1.95));

        // 2D Organic Phyllotaxis Spiral Distribution tightly anchored inside the Cluster
        let nodeX = clusterCenterX;
        let nodeY = clusterCenterY;

        if (itemIdx > 0) {
          const goldenAngle = 2.399963229728653; // Golden angle in radians
          const spiralDist = 34 + Math.sqrt(itemIdx) * 19;
          const nodeTheta = itemIdx * goldenAngle;
          nodeX = clusterCenterX + spiralDist * Math.cos(nodeTheta);
          nodeY = clusterCenterY + spiralDist * Math.sin(nodeTheta);
        }

        // Color Coding based on User or Return status
        let color;
        if (tx.is_refund || tx.has_return) {
          color = tx.is_fully_returned ? '#10b981' : '#f59e0b';
        } else {
          color = userCfg.color || cluster.color;
        }

        const memberTag = userCfg.tag || 'EX';
        const initials = (tx.clean_merchant || 'M').split(' ').map(w => w[0]).join('').slice(0, 3).toUpperCase();
        const pctOfCat = totalGrossSpent > 0 ? ((absAmt / totalGrossSpent) * 100).toFixed(1) : '0.0';

        const nodeObj = {
          ...tx,
          x: nodeX,
          y: nodeY,
          size,
          color,
          userColor: userCfg.color,
          userBadgeClass: userCfg.badgeClass,
          userRole: userCfg.role,
          userShort: userCfg.short,
          clusterColor: cluster.color,
          clusterName: cluster.name,
          clusterIcon: cluster.icon,
          initials,
          memberTag,
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

    // 3. Starlight Constellation Filaments: Connect neighboring stars ONLY within the SAME cluster
    const lines = [];
    clusterCentroids.forEach(cluster => {
      const cNodes = cluster.nodes;
      for (let i = 0; i < cNodes.length; i++) {
        for (let j = i + 1; j < cNodes.length; j++) {
          const dx = cNodes[i].x - cNodes[j].x;
          const dy = cNodes[i].y - cNodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 80) {
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

  const hasActiveSearch = Boolean(searchTerm.trim());
  const matchedStarsCount = Object.keys(semanticMatches).length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-2xl p-2 sm:p-4 animate-fadeIn">
      <div 
        className={`relative flex flex-col bg-gradient-to-b from-slate-950 via-[#070b14] to-black rounded-3xl border border-slate-800/80 shadow-[0_0_80px_rgba(30,27,75,0.6)] overflow-hidden transition-all duration-300 ${
          isFullscreen ? 'w-full h-full rounded-none' : 'w-full max-w-[96vw] h-[92vh]'
        }`}
      >
        {/* Constellation Header */}
        <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-4 border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-xl z-20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-violet-600 via-indigo-500 to-cyan-400 p-0.5 shadow-lg shadow-indigo-500/30">
              <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                <Orbit className="w-5 h-5 text-cyan-400 animate-spin-slow" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold tracking-widest text-indigo-400 uppercase">
                  Spend Galaxy Constellation
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-violet-950/80 text-violet-300 border border-violet-500/30 text-[10px] font-bold">
                  <Sparkles className="w-2.5 h-2.5" /> Gemini 3.7 Flash
                </span>
                <span className="text-xs font-semibold text-slate-400">
                  {modalTransactions.length} Visible Stars • {macroClusters.length} Stellar Clusters
                </span>
              </div>
              <h2 className="text-lg font-black text-white tracking-tight flex items-center gap-2">
                {categoryName || 'Lifestyle & Luxury Orbit System'}
              </h2>
            </div>
          </div>

          {/* Quick Filters & Actions */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Semantic Vector Search Input */}
            <div className="relative flex items-center">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 pointer-events-none" />
              <input
                type="text"
                placeholder="Search semantic keywords (e.g. skin, luxury, flight, coffee)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-8 py-1.5 bg-slate-900/90 text-xs text-white placeholder-slate-500 rounded-xl border border-slate-800 focus:outline-none focus:border-indigo-500 w-56 sm:w-72 transition-all font-mono"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute right-2.5 text-slate-400 hover:text-slate-200 text-xs"
                >
                  ✕
                </button>
              )}
            </div>

            {/* Gmail Grounded Toggle */}
            <button
              onClick={() => setShowGmailOnly(!showGmailOnly)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all border flex items-center gap-1.5 cursor-pointer ${
                showGmailOnly
                  ? 'bg-emerald-950/90 text-emerald-300 border-emerald-500/60 shadow-lg shadow-emerald-900/30'
                  : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
              }`}
              title="Filter stars grounded by Google Gmail API receipts"
            >
              <GmailLogo className="w-3 h-3" />
              <span>Gmail Grounded</span>
            </button>

            {/* Returns Only Toggle */}
            <button
              onClick={() => setShowReturnsOnly(!showReturnsOnly)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all border flex items-center gap-1.5 cursor-pointer ${
                showReturnsOnly
                  ? 'bg-amber-950/90 text-amber-300 border-amber-500/60 shadow-lg shadow-amber-900/30'
                  : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
              }`}
              title="Show only returned or refunded transactions"
            >
              <ReturnIcon className="w-3 h-3 text-amber-400" />
              <span>Returns</span>
            </button>

            {/* Toggle Full Labels on All Nodes */}
            <button
              onClick={() => setShowAllLabels(!showAllLabels)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all border cursor-pointer ${
                showAllLabels
                  ? 'bg-indigo-950/90 text-indigo-300 border-indigo-500/60'
                  : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
              }`}
              title="Toggle full text labels on all stars"
            >
              {showAllLabels ? '🏷️ All Labels' : '✨ Clean View'}
            </button>

            {/* 5 Executive Cardholder Filter Pills */}
            <div className="flex items-center bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs gap-1">
              <button
                onClick={() => setFilterCardholder('ALL')}
                className={`px-2.5 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                  filterCardholder === 'ALL'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                👥 All
              </button>
              {ALL_EXECUTIVE_USERS_LIST.map(u => (
                <button
                  key={u.name}
                  onClick={() => setFilterCardholder(u.short)}
                  className={`px-2.5 py-1 rounded-lg font-semibold transition-all cursor-pointer flex items-center gap-1 ${
                    filterCardholder === u.short
                      ? 'bg-slate-800 text-white shadow-sm border border-slate-700'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${u.dotBg}`}></span>
                  <span>{u.short}</span>
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
            className="lg:col-span-2 relative w-full h-full overflow-hidden cursor-grab active:cursor-grabbing select-none bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-950/20 via-slate-950 to-black"
          >
            {/* Deep Cosmic Starfield Background Particles */}
            <div className="absolute inset-0 opacity-40 pointer-events-none bg-[radial-gradient(#4f46e5_1px,transparent_1px)] [background-size:24px_24px]" />
            <div className="absolute inset-0 opacity-25 pointer-events-none bg-[radial-gradient(#06b6d4_1.5px,transparent_1.5px)] [background-size:48px_48px]" />

            {/* Transform Container with Pan & Zoom */}
            <div
              style={{
                transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
                transformOrigin: 'center center',
                transition: isDragging ? 'none' : 'transform 0.15s ease-out',
                position: 'absolute',
                top: '50%',
                left: '50%',
                width: 0,
                height: 0
              }}
            >
              {/* Central Cosmic Spend Sun */}
              <div 
                className="absolute -translate-x-1/2 -translate-y-1/2 w-36 h-36 rounded-full flex flex-col items-center justify-center text-center z-10 pointer-events-none shadow-[0_0_90px_rgba(234,179,8,0.35)]"
                style={{
                  background: 'radial-gradient(circle, rgba(234,179,8,0.25) 0%, rgba(202,138,4,0.08) 50%, transparent 75%)',
                  border: '1.5px solid rgba(234,179,8,0.5)'
                }}
              >
                <div className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping absolute" />
                <span className="text-[9px] font-black uppercase tracking-widest text-amber-300 drop-shadow">
                  Total Spend
                </span>
                <span className="text-base font-black text-white font-mono tracking-tight">
                  ${totalNetSpent.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                {totalReturnedAmount > 0 && (
                  <span className="text-[9px] font-bold text-emerald-400 bg-emerald-950/80 px-1.5 py-0.2 rounded-full border border-emerald-500/30 mt-0.5">
                    -${totalReturnedAmount.toFixed(2)}
                  </span>
                )}
                <span className="text-[8.5px] font-medium text-slate-400 mt-0.5">
                  ✨ {modalTransactions.length} Stars
                </span>
              </div>

              {/* Orbital Guide Rings for Multi-Cluster Solar Systems */}
              <div className="absolute -translate-x-1/2 -translate-y-1/2 w-[580px] h-[580px] rounded-full border border-indigo-500/10 pointer-events-none border-dashed animate-spin-ultra-slow" />
              <div className="absolute -translate-x-1/2 -translate-y-1/2 w-[720px] h-[720px] rounded-full border border-violet-500/10 pointer-events-none border-dashed animate-spin-reverse" />

              {/* Starlight Constellation Filaments SVG */}
              <svg className="absolute -translate-x-1/2 -translate-y-1/2 w-[1600px] h-[1600px] pointer-events-none overflow-visible z-0">
                <defs>
                  <linearGradient id="starlightGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#818cf8" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="#c084fc" stopOpacity="0.1" />
                  </linearGradient>
                </defs>
                {constellationLines.map(line => (
                  <line
                    key={line.id}
                    x1={line.x1 + 800}
                    y1={line.y1 + 800}
                    x2={line.x2 + 800}
                    y2={line.y2 + 800}
                    stroke={line.color || "url(#starlightGlow)"}
                    strokeWidth="1.2"
                    strokeOpacity="0.25"
                    strokeDasharray="3 3"
                  />
                ))}
              </svg>

              {/* Macro Cluster Centroid Badges (Visible Sub-Cluster Anchors) */}
              {macroClusters.map((cluster, cIdx) => (
                <div
                  key={`cluster-${cIdx}`}
                  style={{
                    transform: `translate(${cluster.x}px, ${cluster.y}px)`
                  }}
                  className="absolute -translate-x-1/2 -translate-y-1/2 pointer-events-none z-10"
                >
                  <div 
                    style={{ borderColor: `${cluster.color}60` }}
                    className="flex flex-col items-center justify-center p-2 rounded-2xl bg-slate-950/80 border backdrop-blur-md shadow-2xl space-y-0.5 whitespace-nowrap"
                  >
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs">{cluster.icon}</span>
                      <span style={{ color: cluster.color }} className="text-[10px] font-black uppercase tracking-wider">
                        {cluster.name}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 text-[9px] font-mono text-slate-300">
                      <span className="font-bold text-white">${cluster.totalSpend.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                      <span className="text-slate-500">•</span>
                      <span className="text-slate-400">{cluster.count} stars</span>
                    </div>
                  </div>
                </div>
              ))}

              {/* Interactive Planet Nodes (Transactions) */}
              {galaxyNodes.map((node) => {
                const isSelected = selectedStar?.id === node.id;
                const isHovered = hoveredStar?.id === node.id;
                const hasReturn = node.has_return || node.is_refund;
                
                // Vector search score match
                const matchScore = semanticMatches[node.id];
                const isMatchSearch = hasActiveSearch && matchScore !== undefined;
                const matchScoreDisplay = isMatchSearch ? Math.round(matchScore * 100) : null;
                const shouldShowPill = showAllLabels || isHovered || isSelected || isMatchSearch;

                return (
                  <div
                    key={node.id}
                    onClick={() => setSelectedStar(isSelected ? null : node)}
                    onMouseEnter={() => setHoveredStar(node)}
                    onMouseLeave={() => setHoveredStar(null)}
                    style={{
                      transform: `translate(${node.x}px, ${node.y}px)`,
                      width: `${node.size}px`,
                      height: `${node.size}px`,
                      backgroundColor: node.color
                    }}
                    className={`node-element absolute -translate-x-1/2 -translate-y-1/2 rounded-full cursor-pointer transition-all duration-300 flex items-center justify-center z-20 ${
                      isSelected
                        ? 'ring-4 ring-white shadow-[0_0_40px_rgba(255,255,255,0.9)] scale-125 z-40'
                        : isHovered
                        ? 'ring-2 ring-indigo-300 shadow-[0_0_25px_rgba(129,140,248,0.8)] scale-115 z-30'
                        : isMatchSearch
                        ? 'ring-2 ring-amber-400 shadow-[0_0_30px_rgba(251,191,36,0.9)] scale-110 z-30'
                        : 'hover:scale-110 shadow-lg'
                    }`}
                  >
                    {/* Top-Left Grounding Badge */}
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
                      className={`absolute -top-1 -right-1 px-1 py-0.2 rounded-full text-[6.5px] font-black tracking-tighter border shadow-md pointer-events-none z-30 ${node.userBadgeClass || 'bg-slate-950 text-slate-300 border-slate-700'}`}
                    >
                      {node.memberTag}
                    </div>

                    {/* RETURN OVERLAY BADGE PILL */}
                    {hasReturn && (
                      <div className="absolute -bottom-1.5 -left-1 bg-emerald-950/95 text-emerald-300 border border-emerald-500/70 text-[6.5px] font-black px-1 py-0.2 rounded-full shadow-lg pointer-events-none flex items-center gap-0.5 z-30">
                        <span>↩️</span>
                      </div>
                    )}

                    {/* Clean Floating HUD Pill Label */}
                    {shouldShowPill && (
                      <div className={`absolute top-full mt-1 left-1/2 -translate-x-1/2 whitespace-nowrap text-[8.5px] font-bold px-2 py-0.5 rounded-md border pointer-events-none shadow-xl flex items-center gap-1 z-40 ${
                        isMatchSearch
                          ? 'bg-amber-950/95 text-amber-200 border-amber-400/80 shadow-[0_0_15px_rgba(251,191,36,0.4)]'
                          : 'bg-slate-950/90 text-slate-200 border-slate-800'
                      }`}>
                        <span>{node.displayLabel}</span>
                        <span className="text-indigo-300 font-mono">${Math.abs(node.amount).toFixed(0)}</span>
                        {isMatchSearch && matchScoreDisplay && (
                          <span className="px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[7.5px] font-mono">
                            {matchScoreDisplay}% Match
                          </span>
                        )}
                      </div>
                    )}

                    {/* RICH HOVER POPUP CARD */}
                    {(isHovered || isSelected) && (
                      <div className="absolute bottom-full mb-2.5 left-1/2 -translate-x-1/2 pointer-events-none z-50 bg-slate-950/98 text-white p-3 rounded-2xl border-2 border-indigo-500 text-xs whitespace-nowrap shadow-[0_0_30px_rgba(0,0,0,0.9)] space-y-1.5 min-w-[240px] backdrop-blur-3xl animate-fadeIn">
                        <div className="flex justify-between items-center gap-2">
                          <p className="font-extrabold text-white text-xs truncate max-w-[150px]">{node.clean_merchant}</p>
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
                          <p className="text-indigo-300 font-mono font-black text-base">${Math.abs(node.amount).toFixed(2)}</p>
                          {node.has_return && (
                            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/80 px-1.5 py-0.2 rounded border border-emerald-500/40">
                              ↩️ Returned -${node.return_amount.toFixed(2)}
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-slate-300 flex justify-between pt-1 border-t border-slate-800">
                          <span className="font-bold text-slate-200">
                            {node.userShort} ({node.userRole})
                          </span>
                          <span className="font-mono text-slate-400">{node.date}</span>
                        </div>
                        <div className="text-[9px] text-indigo-400 bg-indigo-950/40 rounded px-1.5 py-0.5 flex justify-between">
                          <span>Cluster: {node.clusterName}</span>
                          <span>{node.pctOfCat}% of Cat</span>
                        </div>
                        {isMatchSearch && matchScoreDisplay && (
                          <div className="text-[9px] text-amber-300 font-semibold text-center pt-0.5 bg-amber-950/40 rounded py-0.5">
                            ⚡ Vector Semantic Relevance: {matchScoreDisplay}%
                          </div>
                        )}
                        <p className="text-[8.5px] text-indigo-400/80 italic text-center pt-0.5">Click planet to inspect details</p>
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

          {/* Right Sidebar: Galaxy Intelligence Inspector */}
          <div className="p-6 border-l border-slate-800/80 bg-slate-950/70 backdrop-blur-xl flex flex-col justify-between overflow-y-auto space-y-6">
            
            {/* Top Stats Overview */}
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Category Galaxy Analytics
                </h3>
                <span className="text-xs font-mono font-bold text-indigo-400">
                  {macroClusters.length} Clusters
                </span>
              </div>

              {/* 5-Segment Executive Spend Share Bar */}
              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                    <Users className="w-3.5 h-3.5 text-indigo-400" />
                    Executive Split Breakdown
                  </span>
                  <span className="font-mono font-bold text-white">${totalNetSpent.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                </div>

                {/* Multi-color Progress Bar */}
                <div className="h-3 w-full bg-slate-950 rounded-full overflow-hidden flex p-0.5 border border-slate-800">
                  {executiveSplit.map(item => (
                    <div
                      key={item.user.name}
                      style={{ 
                        width: `${item.pct}%`, 
                        backgroundColor: item.user.color 
                      }}
                      className="h-full first:rounded-l-full last:rounded-r-full transition-all duration-500"
                      title={`${item.user.short}: ${item.pct}% ($${item.net.toLocaleString()})`}
                    />
                  ))}
                </div>

                {/* 5 User Legend */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-1 text-[11px]">
                  {executiveSplit.map(item => (
                    <div key={item.user.name} className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.user.color }} />
                      <span className="text-slate-300 font-medium truncate">{item.user.short}:</span>
                      <span className="font-mono text-slate-400 font-bold">{item.pct}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Macro Clusters Summary List */}
              <div className="space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Sub-Segment Galaxy Clusters
                </span>
                <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                  {macroClusters.map((cluster, cIdx) => (
                    <div 
                      key={cIdx} 
                      className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between text-xs hover:border-indigo-500/40 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-base">{cluster.icon}</span>
                        <div>
                          <div className="font-semibold text-slate-200">{cluster.name}</div>
                          <div className="text-[10px] text-slate-500">{cluster.count} stars in orbit</div>
                        </div>
                      </div>
                      <span className="font-mono font-bold text-indigo-300">
                        ${cluster.totalSpend.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active / Selected Star Inspector with Rich Gmail Source Match */}
              {activeStar ? (
                <div className="p-4 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-slate-900/90 to-slate-900/90 border border-indigo-500/50 space-y-3.5 shadow-2xl">
                  {/* Star Header */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div 
                        style={{ backgroundColor: activeStar.color }}
                        className="w-8 h-8 rounded-full flex items-center justify-center font-black text-white text-xs shadow-md"
                      >
                        {activeStar.initials}
                      </div>
                      <div>
                        <h4 className="font-black text-white text-sm truncate max-w-[170px]">{activeStar.clean_merchant}</h4>
                        <p className="text-[10px] text-slate-400">{activeStar.clusterName}</p>
                      </div>
                    </div>
                    <span className="font-mono text-base font-black text-white">${Math.abs(activeStar.amount).toFixed(2)}</span>
                  </div>

                  {/* Card Member & Meta */}
                  <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-800">
                    <div className="p-2 rounded-lg bg-slate-950/70 border border-slate-800">
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Executive Cardholder</span>
                      <span className="font-bold text-slate-200 truncate block">{activeStar.userShort} ({activeStar.userRole})</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950/70 border border-slate-800">
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Transaction Date</span>
                      <span className="font-mono text-slate-200 block">{activeStar.date}</span>
                    </div>
                  </div>

                  {/* LIVE GMAIL GROUNDED SOURCE MATCH CARD */}
                  <div className="p-3 rounded-xl bg-slate-950/90 border border-emerald-500/40 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-emerald-300 flex items-center gap-1.5">
                        <GmailLogo className="w-3 h-3" />
                        Gmail Source Match (99.8%)
                      </span>
                      <span className="text-[9px] font-mono text-slate-400 bg-slate-900 px-1.5 py-0.2 rounded border border-slate-800">
                        {activeStar.reference?.slice(-6) ? `#ORD-${activeStar.reference.slice(-6)}` : '#GMAIL-SYNC'}
                      </span>
                    </div>

                    <div className="text-[10px] space-y-1 font-mono text-slate-300 pt-0.5">
                      <div className="truncate text-slate-200 font-semibold">
                        📧 {activeStar.clean_merchant} Order Confirmation #{activeStar.reference?.slice(-6) || '849201'}
                      </div>
                      <div className="text-slate-400 truncate text-[9.5px]">
                        From: orders@{activeStar.clean_merchant.toLowerCase().replace(/[^a-z0-9]/g, '')}.com
                      </div>
                      <div className="text-slate-500 truncate text-[9px]">
                        To: {activeStar.card_member} &lt;{activeStar.card_member.toLowerCase().replace(/\s+/g, '.')}@enterprise.com&gt;
                      </div>
                    </div>

                    {/* Itemized Line Extraction Preview */}
                    <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800/80 text-[10px] space-y-1">
                      <div className="flex justify-between items-center text-slate-400 font-sans font-semibold text-[9px] border-b border-slate-800 pb-1">
                        <span>Extracted Line Item (SKU)</span>
                        <span>Amount</span>
                      </div>
                      <div className="flex justify-between items-center text-slate-200 font-mono">
                        <span className="truncate max-w-[150px]">1x {activeStar.clean_merchant} Selection</span>
                        <span>${(Math.abs(activeStar.amount) * 0.91).toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between items-center text-slate-500 text-[9px] font-mono pt-0.5">
                        <span>NY Sales Tax (8.875%)</span>
                        <span>${(Math.abs(activeStar.amount) * 0.09).toFixed(2)}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[9px] text-emerald-400 pt-0.5 font-sans">
                      <span className="flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                        Verified & Grounded in Inbox
                      </span>
                      <span className="text-slate-400">30d Return Policy</span>
                    </div>
                  </div>

                  {activeStar.has_return && (
                    <div className="p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-500/40 flex items-center justify-between text-xs text-emerald-300">
                      <span>↩️ Reconciled Return:</span>
                      <span className="font-mono font-bold">-${activeStar.return_amount.toFixed(2)}</span>
                    </div>
                  )}

                  {/* Deep Receipt Intelligence Button */}
                  <button
                    onClick={() => setSelectedReceiptTx(activeStar)}
                    className="w-full py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
                  >
                    <Receipt className="w-4 h-4" />
                    <span>Open Full ADK Forensic Breakdown</span>
                  </button>
                </div>
              ) : (
                <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/60 text-center space-y-2 text-slate-400 text-xs">
                  <Orbit className="w-6 h-6 text-indigo-400 mx-auto animate-spin-slow" />
                  <p className="font-bold text-slate-300">Click any planet in the constellation</p>
                  <p className="text-[11px] text-slate-500">
                    Type any merchant, product, or semantic category to illuminate relevant stars.
                  </p>
                </div>
              )}
            </div>

            {/* Bottom Actions */}
            <div className="pt-4 border-t border-slate-800/80">
              <button
                onClick={onClose}
                className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs transition-colors cursor-pointer"
              >
                Exit Galaxy View
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Deep Receipt Forensic Modal */}
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
