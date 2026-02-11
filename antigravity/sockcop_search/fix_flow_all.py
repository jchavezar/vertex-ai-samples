with open("public/assets/arch_diagram.svg", "r") as f:
    text = f.read()

start_idx = text.find('<!-- Animated Data Packets (Circles moving along paths) -->')
end_idx = text.find('<g transform="translate(40, 90)">')

if start_idx != -1 and end_idx != -1:
    new_packets = """
  <!-- Auth Flow (Token Exchange Sequence) -->
  
  <!-- Step 1: Microsoft Entra Token to WIF -->
  <circle r="4" fill="#ffffff" filter="url(#glow)">
    <animateMotion dur="3s" repeatCount="indefinite" path="M 260 130 L 360 130" keyPoints="0;1" keyTimes="0;1" calcMode="linear"/>
  </circle>
  
  <!-- Step 2: GCP STS Token to Vertex AI API -->
  <circle r="4" fill="#38bdf8" filter="url(#glow)">
    <animateMotion dur="2s" repeatCount="indefinite" path="M 430 170 L 430 230" begin="2s" keyPoints="0;1" keyTimes="0;1" calcMode="linear" />
  </circle>

  <!-- Step 3: API Query Execution to SharePoint -->
  <circle r="4" fill="#10b981" filter="url(#glow)">
    <animateMotion dur="2s" repeatCount="indefinite" path="M 540 270 L 640 270" begin="4s" keyPoints="0;1" keyTimes="0;1" calcMode="linear" />
  </circle>

  <!-- Background Sync Flow -->
  <circle r="4" fill="#f59e0b" filter="url(#glow)">
    <animateMotion dur="4s" repeatCount="indefinite" path="M 640 270 L 540 270" />
  </circle>
  <circle r="4" fill="#f59e0b" filter="url(#glow)">
    <animateMotion dur="4s" repeatCount="indefinite" path="M 260 270 L 360 270" />
  </circle>
"""
    middle = text[:start_idx] + new_packets + text[end_idx:]
    
    old_cross = """  <!-- Cross-phase Line -->
  <path class="line-glow" d="M 750 170 C 750 200, 500 200, 430 230" />
  <path class="line-main" d="M 750 170 C 750 200, 500 200, 430 230" marker-end="url(#arrow-blue)" />
  <text x="580" y="195" class="text-small">Permits Query Execution</text>"""
    
    new_cross = """  <!-- Discovery Engine API Query Line -->
  <path class="line-glow" d="M 430 80 C 430 200, 430 200, 430 230" />
  <path class="line-main" d="M 430 80 C 430 200, 430 200, 430 230" marker-end="url(#arrow-blue)" />
  <text x="440" y="150" class="text-small">GCP STS Token Handshake</text>
  <text x="440" y="165" class="text-small">Permits DiscoveryEngine API</text>"""
        
    if old_cross in middle:
        middle = middle.replace(old_cross, new_cross)
    
    middle = middle.replace('<text x="560" y="30" class="text-small">Federates</text>', '<text x="560" y="30" class="text-small">STS Token Validated</text>')
    middle = middle.replace('<text x="230" y="30" class="text-small">Issuer &amp; Token</text>', '<text x="230" y="30" class="text-small">Microsoft Entra Token</text>')

    with open("public/assets/arch_diagram.svg", "w") as f:
        f.write(middle)
        
    print("Arch Diagram Modified.")

with open("generate_2076_readme.py", "r") as f:
    text = f.read()

# Fix Gradients
old_grad = """    <linearGradient id="grad_{filename}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0" />
    </linearGradient>"""
    
new_grad = """    <linearGradient id="grad_{filename}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="1" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0" />
    </linearGradient>"""
    
text = text.replace(old_grad, new_grad)

old_cursor = '  <rect x="{50 + len(title)*16.8}" y="15" width="15" height="28" fill="#38bdf8">'
old_cursor2 = '  <rect x="{50 + len(title)*17}" y="15" width="15" height="28" fill="#38bdf8">'
old_cursor3 = '  <rect x="{40 + len(title)*17}" y="15" width="15" height="28" fill="#38bdf8">'
old_cursor4 = '  <rect x="{40 + len(title)*16.8}" y="15" width="15" height="28" fill="#38bdf8">'

new_cursor = '  <rect x="{30 + len(title)*20.8}" y="15" width="15" height="28" fill="#38bdf8">'

if old_cursor in text: text = text.replace(old_cursor, new_cursor)
if old_cursor2 in text: text = text.replace(old_cursor2, new_cursor)
if old_cursor3 in text: text = text.replace(old_cursor3, new_cursor)
if old_cursor4 in text: text = text.replace(old_cursor4, new_cursor)

with open("generate_2076_readme.py", "w") as f:
    f.write(text)

