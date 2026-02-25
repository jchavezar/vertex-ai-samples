import os

ASSET_DIR = "public/assets"
os.makedirs(ASSET_DIR, exist_ok=True)

title = "INTERFACE_TOPOLOGIES"
width = 800
height = 80

# Option 4: Immersive Cyber-Code (Glassmorphic tab over scrolling actual React code)
# Features dark slate + purple/blue glow to match user's previous preference, plus animated code text.
opt4 = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <defs>
    <filter id="glow4" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <clipPath id="codeClip">
      <rect x="0" y="0" width="{width}" height="{height}" />
    </clipPath>
    <linearGradient id="fadeEdge" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0f172a" stop-opacity="1" />
      <stop offset="20%" stop-color="#0f172a" stop-opacity="0" />
      <stop offset="80%" stop-color="#0f172a" stop-opacity="0" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="1" />
    </linearGradient>
  </defs>

  <!-- Background Base -->
  <rect x="0" y="0" width="{width}" height="{height}" fill="#0f172a" />

  <!-- Animated Floating Code Background (Simulating real React code from App.jsx) -->
  <g clip-path="url(#codeClip)" opacity="0.15" font-family="'Courier New', monospace" font-size="10" fill="#38bdf8">
    <g>
      <animateTransform attributeName="transform" type="translate" from="0,80" to="0,-120" dur="15s" repeatCount="indefinite"/>
      <text x="10" y="20">import React, {{ useState, useEffect }} from 'react';</text>
      <text x="10" y="40">import {{ DataStoreSearch }} from '@google-cloud/vertex-ai-search';</text>
      <text x="10" y="60">export const SockcopSearch = () => {{</text>
      <text x="20" y="80">const [query, setQuery] = useState('');</text>
      <text x="20" y="100">const [results, setResults] = useState([]);</text>
      <text x="20" y="120">const handleSearch = async (e) => {{</text>
      <text x="30" y="140">e.preventDefault();</text>
      <text x="30" y="160">const googleToken = await WIF.exchangeToken(entraIdToken);</text>
      <text x="30" y="180">const res = await VertexAPI.search(query, googleToken);</text>
      <text x="30" y="200">setResults(res.data.results);</text>
      <text x="20" y="220">}};</text>
      <text x="20" y="240">return (</text>
    </g>
    <g>
      <animateTransform attributeName="transform" type="translate" from="0,300" to="0,20" dur="20s" repeatCount="indefinite"/>
      <text x="400" y="20">&lt;div className="sockcop-container bg-slate-900"&gt;</text>
      <text x="420" y="40">&lt;header className="border-b border-cyan-500/30"&gt;</text>
      <text x="440" y="60">&lt;h1 className="text-2xl font-bold tracking-widest text-slate-100"&gt;</text>
      <text x="460" y="80">SOCKCOP // DISCOVERY INTELLIGENCE</text>
      <text x="440" y="100">&lt;/h1&gt;</text>
      <text x="420" y="120">&lt;/header&gt;</text>
      <text x="420" y="140">&lt;main className="mt-8"&gt;</text>
      <text x="440" y="160">&lt;SearchInput value={{query}} onChange={{setQuery}} /&gt;</text>
      <text x="440" y="180">&lt;ResultsGrid data={{results}} /&gt;</text>
      <text x="420" y="200">&lt;/main&gt;</text>
      <text x="400" y="220">&lt;/div&gt;</text>
    </g>
  </g>

  <!-- Left/Right Fade Overlay to blend the code edges -->
  <rect x="0" y="0" width="{width}" height="{height}" fill="url(#fadeEdge)" />

  <!-- The Solid Header Block (Glassmorphic look) -->
  <polygon points="20,20 600,20 620,60 20,60" fill="#1e293b" opacity="0.95" stroke="#38bdf8" stroke-width="1" />
  
  <!-- Glowing Neon Accent Edge -->
  <polygon points="20,20 600,20 605,25 20,25" fill="#c4b5fd" filter="url(#glow4)"/>

  <!-- Vertical Cyan Tab -->
  <rect x="20" y="20" width="4" height="40" fill="#38bdf8" filter="url(#glow4)" />
  
  <text x="40" y="48" font-family="'Courier New', monospace" font-size="28" font-weight="bold" fill="#f8fafc" letter-spacing="4">
    {title}
  </text>
  
  <!-- Blinking Terminal Cursor matching text width precisely -->
  <rect x="{50 + len(title)*16.8}" y="28" width="15" height="24" fill="#38bdf8" filter="url(#glow4)">
    <animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite" />
  </rect>
</svg>"""

with open(os.path.join(ASSET_DIR, "opt4_cyber_code.svg"), 'w') as f:
    f.write(opt4)

print("Option 4 generated.")
