import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jetski_indexer import generate_index, INDEX_OUTPUT, scan_projects

PORT = int(os.environ.get("ANTIGRAVITY_SIDECAR_WEB_PORT", 8099))

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8b5cf6"/>
      <stop offset="50%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>
  </defs>
  <rect width="100" height="100" rx="26" fill="url(#bg)"/>
  <circle cx="50" cy="50" r="32" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="4" stroke-dasharray="10 5"/>
  <polygon points="50,18 62,44 50,82 38,44" fill="#ffffff"/>
  <polygon points="50,18 62,44 50,50" fill="#e0e7ff"/>
  <polygon points="50,82 38,44 50,50" fill="#a5b4fc"/>
  <circle cx="50" cy="50" r="7" fill="#020617"/>
  <circle cx="50" cy="50" r="3" fill="#ffffff"/>
</svg>"""

HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jetski Nav: Deployments & Context Hub</title>
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="alternate icon" type="image/svg+xml" href="/favicon.ico">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #020617; color: #f8fafc; font-family: ui-sans-serif, system-ui, sans-serif; }}
        .glass {{ background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(16px); border: 1px solid rgba(30, 41, 59, 0.8); }}
    </style>
</head>
<body class="p-6 min-h-screen">
    <div class="max-w-6xl mx-auto space-y-6">
        <!-- Header -->
        <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl glass">
            <div class="flex items-center gap-3">
                <div class="p-3 rounded-xl bg-gradient-to-tr from-violet-600 via-indigo-500 to-cyan-400 text-white shadow-lg">
                    🧭
                </div>
                <div>
                    <h1 class="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                        Jetski Nav: Deployment & Session Context Hub
                    </h1>
                    <p class="text-xs text-slate-400">Indexed Autonomous Deployments, Active Ports & Session History</p>
                </div>
            </div>
            
            <div class="flex items-center gap-3">
                <input type="text" id="searchInput" onkeyup="filterProjects()" placeholder="🔍 Search deployment..." class="bg-slate-950 text-xs text-slate-200 px-3 py-2 rounded-xl border border-slate-800 focus:outline-none w-48 md:w-64" />
                <button onclick="refreshIndex()" class="px-3.5 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white transition-all">
                    🔄 Refresh Index
                </button>
            </div>
        </header>

        <!-- KPI Stats -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="p-4 rounded-2xl glass flex items-center justify-between">
                <div>
                    <span class="text-xs text-slate-400 font-semibold uppercase">Total Projects</span>
                    <p id="totalCount" class="text-2xl font-black text-white font-mono">0</p>
                </div>
                <span class="text-2xl">📦</span>
            </div>
            <div class="p-4 rounded-2xl glass flex items-center justify-between">
                <div>
                    <span class="text-xs text-slate-400 font-semibold uppercase">Active Daemons</span>
                    <p id="runningCount" class="text-2xl font-black text-emerald-400 font-mono">0</p>
                </div>
                <span class="text-2xl">🟢</span>
            </div>
            <div class="p-4 rounded-2xl glass flex items-center justify-between">
                <div>
                    <span class="text-xs text-slate-400 font-semibold uppercase">SKILL Blueprints</span>
                    <p id="skillCount" class="text-2xl font-black text-cyan-400 font-mono">0</p>
                </div>
                <span class="text-2xl">🛠️</span>
            </div>
        </div>

        <!-- Projects Grid -->
        <div id="projectsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Dynamic project cards inserted via JS -->
        </div>
    </div>

    <!-- Modal for Context Prompt -->
    <div id="contextModal" class="fixed inset-0 z-50 hidden items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full max-h-[80vh] flex flex-col overflow-hidden shadow-2xl">
            <div class="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950">
                <h3 id="modalTitle" class="text-sm font-bold text-slate-200">Loaded Context Bundle</h3>
                <button onclick="closeModal()" class="text-slate-400 hover:text-white text-lg">✕</button>
            </div>
            <pre id="modalContent" class="p-4 flex-1 overflow-y-auto text-xs font-mono text-slate-300 bg-slate-950/60 whitespace-pre-wrap select-all"></pre>
            <div class="p-3 border-t border-slate-800 flex justify-end gap-2 bg-slate-950">
                <button onclick="copyModalContent()" class="px-4 py-2 text-xs font-bold rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white">
                    📋 Copy Context Bundle
                </button>
                <button onclick="closeModal()" class="px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 text-slate-300">
                    Close
                </button>
            </div>
        </div>
    </div>

    <script>
        let globalData = null;

        async function loadIndexData() {{
            try {{
                const res = await fetch('/api/index');
                globalData = await res.json();
                renderDashboard(globalData);
            }} catch (err) {{
                console.error("Failed to load index:", err);
            }}
        }}

        async function refreshIndex() {{
            try {{
                const res = await fetch('/api/refresh', {{ method: 'POST' }});
                globalData = await res.json();
                renderDashboard(globalData);
            }} catch (err) {{
                console.error("Failed to refresh index:", err);
            }}
        }}

        function renderDashboard(data) {{
            document.getElementById('totalCount').innerText = data.total_projects;
            document.getElementById('runningCount').innerText = data.running_projects;
            
            const skillCount = data.projects.filter(p => p.has_skill).length;
            document.getElementById('skillCount').innerText = skillCount;

            const grid = document.getElementById('projectsGrid');
            grid.innerHTML = '';

            data.projects.forEach(p => {{
                const isRunning = p.is_running;
                const card = document.createElement('div');
                card.className = `p-4 rounded-2xl glass space-y-3 project-card hover:border-indigo-500/40 transition-all ${{isRunning ? 'border-emerald-500/40 bg-slate-900/90' : ''}}`;
                card.setAttribute('data-search', `${{p.id}} ${{p.title}} ${{p.description}}`.toLowerCase());

                const portsBadge = isRunning 
                    ? Object.keys(p.running_ports).map(port => `<span class="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">🟢 ${{port}}</span>`).join(' ')
                    : `<span class="px-2 py-0.5 text-[10px] text-slate-500 bg-slate-950 rounded">Idle</span>`;

                card.innerHTML = `
                    <div class="flex justify-between items-start">
                        <span class="text-xs font-bold font-mono text-indigo-300 truncate max-w-[180px]">${{p.id}}</span>
                        <div>${{portsBadge}}</div>
                    </div>
                    <div>
                        <h4 class="text-sm font-bold text-white line-clamp-1">${{p.title}}</h4>
                        <p class="text-xs text-slate-400 line-clamp-2 mt-1">${{p.description}}</p>
                    </div>
                    <div class="flex flex-wrap gap-1 text-[10px]">
                        ${{p.has_skill ? '<span class="px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">🛠️ SKILL</span>' : ''}}
                        ${{p.has_start_script ? '<span class="px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/20">🚀 ./start.sh</span>' : ''}}
                    </div>
                    <div class="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                        <a href="${{p.github_url}}" target="_blank" class="text-slate-400 hover:text-white transition-colors">GitHub ↗</a>
                        <button onclick="fetchContextBundle('${{p.id}}')" class="px-3 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border border-indigo-500/30 text-[11px] font-bold transition-all">
                            📋 Load Context
                        </button>
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}

        function filterProjects() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.project-card');
            cards.forEach(card => {{
                const text = card.getAttribute('data-search');
                card.style.display = text.includes(query) ? 'block' : 'none';
            }});
        }}

        async function fetchContextBundle(projectId) {{
            try {{
                const res = await fetch(`/api/context?id=${{encodeURIComponent(projectId)}}`);
                const bundleText = await res.text();
                document.getElementById('modalTitle').innerText = `Loaded Context Bundle: ${{projectId}}`;
                document.getElementById('modalContent').innerText = bundleText;
                document.getElementById('contextModal').classList.remove('hidden');
                document.getElementById('contextModal').classList.add('flex');
            }} catch (err) {{
                alert("Failed to fetch context bundle");
            }}
        }}

        function closeModal() {{
            document.getElementById('contextModal').classList.add('hidden');
            document.getElementById('contextModal').classList.remove('flex');
        }}

        function copyModalContent() {{
            const text = document.getElementById('modalContent').innerText;
            navigator.clipboard.writeText(text);
            alert("✅ Copied project context bundle to clipboard!");
        }}

        loadIndexData();
    </script>
</body>
</html>
"""

class NavRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif path in ["/favicon.ico", "/favicon.svg"]:
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            self.wfile.write(FAVICON_SVG.encode("utf-8"))
        elif path == "/api/index":
            if not os.path.exists(INDEX_OUTPUT):
                data = generate_index()
            else:
                with open(INDEX_OUTPUT, "r") as f:
                    data = json.load(f)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        elif path == "/api/context":
            params = urllib.parse.parse_qs(parsed.query)
            pid = params.get("id", [""])[0]
            from jetski_indexer import scan_projects
            from jetski_nav import build_context_bundle
            
            projects = scan_projects()
            matched = next((p for p in projects if p["id"].lower() == pid.lower()), None)
            if matched:
                bundle = build_context_bundle(matched)
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(bundle.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/refresh":
            data = generate_index()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print(f"🚀 Starting Jetski Nav Web Server on port {PORT}...")
    server = HTTPServer(("0.0.0.0", PORT), NavRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
