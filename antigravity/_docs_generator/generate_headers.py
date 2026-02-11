import os

def generate_header(filename, title, subtitle, code_snippet, theme_color="#22d3ee"):
    width = 1000
    height = 180
    
    # Escape code snippet for XML
    code_lines = code_snippet.strip().split('\n')
    escaped_code_lines = []
    for line in code_lines:
        escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        escaped_code_lines.append(escaped_line)
    
    # Duplicate code for scrolling effect
    full_code_lines = escaped_code_lines + escaped_code_lines
    
    # Generate SVG Text Lines
    svg_text_elements = ""
    for i, line in enumerate(full_code_lines):
        y_pos = 20 + i * 14
        svg_text_elements += f'<text x="20" y="{y_pos}" class="code-bg">{line}</text>\n'

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#020617" stop-opacity="1" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="1" />
    </linearGradient>
    <linearGradient id="scanGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="black" stop-opacity="0" />
      <stop offset="50%" stop-color="{theme_color}" stop-opacity="0.1" />
      <stop offset="100%" stop-color="black" stop-opacity="0" />
    </linearGradient>
    <style>
      /* @import removed for GitHub compatibility */
      .bg {{ fill: url(#bgGrad); }}
      .text-main {{ font-family: 'Courier New', Courier, monospace; fill: {theme_color}; font-weight: 700; font-size: 48px; letter-spacing: 4px; text-transform: uppercase; filter: drop-shadow(0 0 5px {theme_color}); }}
      .text-sub {{ font-family: 'Courier New', Courier, monospace; fill: #94a3b8; font-weight: 400; font-size: 16px; letter-spacing: 2px; text-transform: uppercase; }}
      .code-bg {{ font-family: 'Courier New', Courier, monospace; fill: #1e293b; font-size: 10px; opacity: 0.3; }}
      
      /* Animations */
      @keyframes scrollCode {{ 0% {{ transform: translateY(0); }} 100% {{ transform: translateY(-50%); }} }}
      .scrolling-code {{ animation: scrollCode 20s linear infinite; }}
      
      @keyframes pulseGlow {{ 0%, 100% {{ opacity: 0.8; }} 50% {{ opacity: 1; filter: drop-shadow(0 0 15px {theme_color}); }} }}
      .glow-text {{ animation: pulseGlow 3s ease-in-out infinite; }}
      
      @keyframes scanline {{ 0% {{ transform: translateY(-100%); }} 100% {{ transform: translateY(200%); }} }}
      .scan-bar {{ animation: scanline 4s linear infinite; fill: url(#scanGrad); }}
    </style>
  </defs>

  <!-- Background -->
  <rect x="0" y="0" width="{width}" height="{height}" class="bg" />

  <!-- Scrolling Code -->
  <g class="scrolling-code">
    {svg_text_elements}
  </g>

  <!-- Main Content -->
  <text x="50" y="80" class="text-main glow-text">{title}</text>
  <text x="52" y="110" class="text-sub">// {subtitle} ... ONLINE</text>

  <!-- Tech Decor -->
  <path d="M 0 40 L 0 0 L 40 0" stroke="{theme_color}" stroke-width="2" fill="none" />
  <path d="M {width} 40 L {width} 0 L {width-40} 0" stroke="{theme_color}" stroke-width="2" fill="none" />
  <path d="M 0 {height-40} L 0 {height} L 40 {height}" stroke="{theme_color}" stroke-width="2" fill="none" />
  <path d="M {width} {height-40} L {width} {height} L {width-40} {height}" stroke="{theme_color}" stroke-width="2" fill="none" />
  
  <rect x="0" y="0" width="{width}" height="40" class="scan-bar" />
</svg>'''

    # Ensure assets dir exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "w") as f:
        f.write(svg_content)
    print(f"Generated {filename}")

# --- CONFIGURATION ---

common_code = """
import antigravity
from gravity_sdk import OmniModel

class VoidWalker(OmniModel):
    def __init__(self, mode='NEO_MONOLITH'):
        self.connect(protocol='WIF_V2')
        self.matrix.load_shard('0x99')
        
    async def render_future(self):
        await self.inject_styles(theme='DARK_SLATE')
        return "SYSTEM_READY"
"""

headers = [
    ("assets/header_hub.svg", "ANTIGRAVITY_HUB", "NEXUS_ROOT", common_code, "#22d3ee"), # Cyan
    ("assets/header_search.svg", "SEARCH_OPS", "SOCKCOP_SEARCH", """
    const Search = () => {
      const { data } = useVertex('sockcop');
      return <NeoGrid results={data} mode="brutal" />;
    }
    """, "#fda4af"), # Rose
    ("assets/header_finance.svg", "FINANCIAL_INTEL", "STOCK_TERMINAL", """
    def analyze_ticker(symbol: str):
        report = swarms.finance.generate(symbol)
        display(report.charts, theme='terminal')
    """, "#22c55e"), # Green
    ("assets/header_bio.svg", "ARCHITECT_CORE", "BIO_GENERATOR", """
    .monolith-container {
      scroll-snap-type: y mandatory;
      background: #0f172a;
      mix-blend-mode: exclusion;
    }
    """, "#fcd34d"), # Amber
    ("assets/header_mcp.svg", "METADATA_BRIDGE", "SHAREPOINT_MCP", """
    class SharePointConnector(MCP):
        def extract(self, drive_id):
            return self.graph_api.delta_query(drive_id)
    """, "#a855f7"), # Purple
    ("assets/header_adk.svg", "ADK_LABS", "AGENT_DEV_KIT", """
    agent = LlmAgent(model='gemini-2.5-pro')
    agent.add_tool(search_tool)
    agent.run("Build me a world")
    """, "#38bdf8") # Sky
]

for filename, title, sub, code, color in headers:
    generate_header(filename, title, sub, code, color)
