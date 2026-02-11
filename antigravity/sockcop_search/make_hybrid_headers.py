import re

with open("generate_2076_readme.py", "r") as f:
    text = f.read()

# Replace `create_header_svg` with the hybrid Terminal/Code generator
new_func = """def create_header_svg(filename, title, width=800, height=80):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <defs>
    <filter id="glow_{filename}" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <clipPath id="codeClip_{filename}">
      <rect x="0" y="24" width="{width}" height="{height-24}" rx="0" />
    </clipPath>
    <linearGradient id="fadeEdge_{filename}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0f172a" stop-opacity="0.9" />
      <stop offset="20%" stop-color="#0f172a" stop-opacity="0" />
      <stop offset="80%" stop-color="#0f172a" stop-opacity="0" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0.9" />
    </linearGradient>
  </defs>
  
  <!-- Solid Terminal Body -->
  <rect x="0" y="0" width="{width}" height="{height}" fill="#0f172a" rx="6" stroke="#1e293b" stroke-width="2"/>
  
  <!-- Animated Floating Code Background (Simulating real React code from App.jsx) -->
  <g clip-path="url(#codeClip_{filename})" opacity="0.25" font-family="'Courier New', monospace" font-size="10" fill="#38bdf8">
    <g>
      <animateTransform attributeName="transform" type="translate" from="0,80" to="0,-160" dur="20s" repeatCount="indefinite"/>
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
      <animateTransform attributeName="transform" type="translate" from="0,200" to="0,-40" dur="25s" repeatCount="indefinite"/>
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
  
  <!-- Left/Right Fade Overlay for Code Depth -->
  <rect x="0" y="24" width="{width}" height="{height-24}" fill="url(#fadeEdge_{filename})" />
  
  <!-- Terminal Top Bar -->
  <path d="M 0 6 Q 0 0 6 0 L {width-6} 0 Q {width} 0 {width} 6 L {width} 24 L 0 24 Z" fill="#050505" />
  
  <!-- Window Controls -->
  <circle cx="20" cy="12" r="5" fill="#ef4444" />
  <circle cx="38" cy="12" r="5" fill="#eab308" />
  <circle cx="56" cy="12" r="5" fill="#22c55e" />
  <text x="80" y="16" font-family="'Courier New', monospace" font-size="12" fill="#64748b">bash - root@sockcop_terminal</text>
  
  <!-- The main Text -->
  <text x="30" y="58" font-family="'Courier New', monospace" font-size="22" font-weight="bold" fill="#22c55e">
    root@sockcop:~$<tspan fill="#38bdf8"> ./{title}.sh</tspan>
  </text>
  
  <!-- Blinking Cursor -->
  <rect x="{300 + len(title)*13.2}" y="38" width="12" height="24" fill="#f8fafc" filter="url(#glow_{filename})">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" />
  </rect>
</svg>'''
    with open(f"{ASSET_DIR}/{filename}.svg", "w") as f:
        f.write(svg)
"""

pattern = re.compile(r"def create_header_svg\(.*?\):\n.*?with open.*?f\.write\(svg\)", re.DOTALL)
text = pattern.sub(new_func, text)

with open("generate_2076_readme.py", "w") as f:
    f.write(text)

