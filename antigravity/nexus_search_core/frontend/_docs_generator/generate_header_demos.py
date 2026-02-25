import os

ASSET_DIR = "public/assets"
os.makedirs(ASSET_DIR, exist_ok=True)

title = "INTERFACE_TOPOLOGIES"
width = 800
height = 60

# Option 1: Monolithic Tab (Angular, Dark Slate, Cyan glowing edge)
opt1 = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <defs>
    <filter id="glow1" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
  <!-- Angled dark background -->
  <polygon points="0,5 720,5 750,55 0,55" fill="#0f172a" />
  
  <!-- Glowing neon top edge -->
  <polygon points="0,5 720,5 725,12 0,12" fill="#38bdf8" filter="url(#glow1)"/>
  
  <!-- Accent triangle -->
  <polygon points="730,5 740,5 765,45 755,45" fill="#8b5cf6" />
  
  <text x="30" y="40" font-family="'Courier New', monospace" font-size="24" font-weight="bold" fill="#f8fafc" letter-spacing="4">
    {title}
  </text>
  
  <!-- Pulsing Square -->
  <rect x="{40 + len(title)*18}" y="20" width="16" height="22" fill="#38bdf8">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" />
  </rect>
</svg>"""

# Option 2: Digital Hologram (Wireframe, glowing brackets, dotted grid)
opt2 = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <defs>
    <pattern id="dotGrid" width="10" height="10" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#475569" opacity="0.4"/>
    </pattern>
    <filter id="glow2" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
  
  <rect x="0" y="5" width="{width}" height="50" fill="url(#dotGrid)" />
  
  <!-- Holographic Brackets -->
  <path d="M 25 15 L 10 15 L 10 45 L 25 45" fill="none" stroke="#8b5cf6" stroke-width="3" filter="url(#glow2)"/>
  <path d="M {60 + len(title)*18} 15 L {75 + len(title)*18} 15 L {75 + len(title)*18} 45 L {60 + len(title)*18} 45" fill="none" stroke="#8b5cf6" stroke-width="3" filter="url(#glow2)"/>
  
  <text x="40" y="38" font-family="'Courier New', monospace" font-size="24" font-weight="bold" fill="#38bdf8" letter-spacing="4">
    {title}
  </text>
  
  <!-- Scanning Data Line -->
  <rect x="0" y="55" width="{width}" height="1" fill="#38bdf8" opacity="0.3"/>
  <rect x="0" y="54" width="100" height="3" fill="#38bdf8" filter="url(#glow2)">
    <animate attributeName="x" values="-100;{width};-100" dur="4s" repeatCount="indefinite" />
  </rect>
</svg>"""

# Option 3: Cyber-Terminal (Mac/Linux window dots, CLI prompt style)
opt3 = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <defs>
    <filter id="glow3" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
  
  <!-- Solid Terminal Body -->
  <rect x="0" y="0" width="{width}" height="60" fill="#050505" rx="6" stroke="#1e293b" stroke-width="2"/>
  
  <!-- Window Controls -->
  <circle cx="20" cy="30" r="6" fill="#ef4444" />
  <circle cx="40" cy="30" r="6" fill="#eab308" />
  <circle cx="60" cy="30" r="6" fill="#22c55e" />
  
  <text x="90" y="38" font-family="'Courier New', monospace" font-size="22" font-weight="bold" fill="#22c55e">
    root@sockcop:~$<tspan fill="#38bdf8"> ./{title}.sh</tspan>
  </text>
  
  <!-- Block Cursor -->
  <rect x="{300 + len(title)*14}" y="18" width="12" height="24" fill="#f8fafc" filter="url(#glow3)">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" />
  </rect>
</svg>"""

with open(os.path.join(ASSET_DIR, "opt1_monolithic.svg"), 'w') as f:
    f.write(opt1)
with open(os.path.join(ASSET_DIR, "opt2_holographic.svg"), 'w') as f:
    f.write(opt2)
with open(os.path.join(ASSET_DIR, "opt3_terminal.svg"), 'w') as f:
    f.write(opt3)

print("Options generated.")
