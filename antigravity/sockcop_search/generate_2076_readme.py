import os
import re

ASSET_DIR = "public/assets"
SCREEN_DIR = "public/screenshots"
os.makedirs(ASSET_DIR, exist_ok=True)

# 1. GENERATE ANIMATED HEADERS

def create_header_svg(filename, title, width=800, height=60):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="grad_{filename}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="1" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0" />
    </linearGradient>
    <filter id="glow_{filename}" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
  
  <rect x="0" y="5" width="{width}" height="50" fill="url(#grad_{filename})" />
  
  <!-- Pulsing Neon Indicator -->
  <rect x="0" y="5" width="5" height="50" fill="#38bdf8" filter="url(#glow_{filename})">
    <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite" />
  </rect>
  
  <!-- Title Text -->
  <text x="30" y="40" font-family="'Courier New', monospace" font-size="28" font-weight="bold" fill="#ffffff" letter-spacing="4">
    {title}
  </text>
  
  <!-- Blinking Cursor -->
  <rect x="{40 + len(title)*20.8}" y="15" width="15" height="28" fill="#38bdf8">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" />
  </rect>

  <!-- Base Grid Line -->
  <line x1="0" y1="58" x2="{width}" y2="58" stroke="#38bdf8" stroke-width="1" opacity="0.3" />
  
  <!-- Scanning Laser Line -->
  <rect x="0" y="57" width="100" height="3" fill="#38bdf8" filter="url(#glow_{filename})">
    <animate attributeName="x" values="0;{width};0" dur="4s" repeatCount="indefinite" />
  </rect>
</svg>"""
    with open(os.path.join(ASSET_DIR, filename), 'w') as f:
        f.write(svg)

create_header_svg("header_setup.svg", "SYSTEM_DEPLOY_PROTOCOL")
create_header_svg("header_config.svg", "ENTERPRISE_AUTHENTICATION_PIPELINE")
create_header_svg("header_topologies.svg", "INTERFACE_TOPOLOGIES")


# 2. GENERATE ANIMATED STEP ICONS

def create_step_svg(step_num):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <filter id="glow_step_{step_num}">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Static Hexagon Base -->
  <polygon points="50,5 89,27 89,72 50,95 11,72 11,27" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5" opacity="0.8"/>
  
  <!-- Number -->
  <text x="50" y="62" font-family="'Courier New', monospace" font-size="36" font-weight="bold" fill="#38bdf8" text-anchor="middle" filter="url(#glow_step_{step_num})">0{step_num}</text>
  
  <!-- Spinning Outer Ring -->
  <circle cx="50" cy="50" r="45" fill="none" stroke="#8b5cf6" stroke-width="1.5" stroke-dasharray="10 5 2 5" opacity="0.8">
     <animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="15s" repeatCount="indefinite"/>
  </circle>
  
  <!-- Counter-Spinning Inner Ring -->
  <circle cx="50" cy="50" r="38" fill="none" stroke="#38bdf8" stroke-width="0.5" stroke-dasharray="4 4" opacity="0.5">
     <animateTransform attributeName="transform" type="rotate" from="360 50 50" to="0 50 50" dur="8s" repeatCount="indefinite"/>
  </circle>
</svg>"""
    with open(os.path.join(ASSET_DIR, f"step_{step_num}.svg"), 'w') as f:
        f.write(svg)

for i in range(1, 7):
    create_step_svg(i)


# 3. UPGRADE HERO BANNER WITH ANIMATIONS

hero_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#020617" />
      <stop offset="50%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
    
    <filter id="neon" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="8" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#334155" stroke-width="0.5" opacity="0.3"/>
    </pattern>
  </defs>

  <rect width="100%" height="100%" fill="url(#bgGrad)" />
  <rect width="100%" height="100%" fill="url(#grid)">
    <animate attributeName="opacity" values="0.3;0.6;0.3" dur="5s" repeatCount="indefinite" />
  </rect>

  <!-- Abstract Geometric Accents -->
  <path d="M 0 0 L 200 0 L 150 300 L 0 300 Z" fill="#1e293b" opacity="0.4" />
  <path d="M 1200 0 L 1000 0 L 1050 300 L 1200 300 Z" fill="#38bdf8" opacity="0.05" />
  
  <!-- Glowing Nodes with animations -->
  <line x1="50" y1="50" x2="150" y2="50" stroke="#38bdf8" stroke-width="2" filter="url(#neon)"/>
  <circle cx="50" cy="50" r="4" fill="#38bdf8">
    <animate attributeName="r" values="4;8;4" dur="2s" repeatCount="indefinite" />
  </circle>
  <circle cx="150" cy="50" r="4" fill="#38bdf8">
    <animate attributeName="r" values="4;8;4" dur="2.5s" repeatCount="indefinite" />
  </circle>

  <line x1="1050" y1="250" x2="1150" y2="250" stroke="#8b5cf6" stroke-width="2" filter="url(#neon)"/>
  <circle cx="1050" cy="250" r="4" fill="#8b5cf6">
    <animate attributeName="r" values="4;8;4" dur="2s" repeatCount="indefinite" />
  </circle>
  <circle cx="1150" cy="250" r="4" fill="#8b5cf6">
    <animate attributeName="r" values="4;8;4" dur="1.5s" repeatCount="indefinite" />
  </circle>

  <!-- Data points -->
  <text x="1100" y="30" font-family="'Courier New', monospace" font-size="10" fill="#64748b" opacity="0.7">STATUS: <tspan fill="#10b981">ONLINE</tspan></text>
  <text x="1100" y="45" font-family="'Courier New', monospace" font-size="10" fill="#64748b" opacity="0.7">VERSION: 2076.2</text>
  <text x="1100" y="60" font-family="'Courier New', monospace" font-size="10" fill="#38bdf8" opacity="0.7">FEDERATION: ACTIVE</text>

  <!-- Core Typography -->
  <g transform="translate(600, 140)" text-anchor="middle">
    <!-- Drop Shadow Layer -->
    <text x="0" y="0" font-family="'Arial Black', 'Inter', sans-serif" font-weight="900" font-size="64" letter-spacing="12" fill="#000000" opacity="0.5">SOCKCOP SEARCH</text>
    <text x="0" y="-3" font-family="'Arial Black', 'Inter', sans-serif" font-weight="900" font-size="64" letter-spacing="12" fill="#f8fafc">SOCKCOP SEARCH</text>
    <text x="0" y="40" font-family="'Courier New', monospace" font-size="20" letter-spacing="6" fill="#94a3b8">ENTERPRISE FEDERATED INDEXING</text>
  </g>

  <!-- Scanning Vertical Line -->
  <rect x="0" y="0" width="1200" height="2" fill="#8b5cf6" opacity="0.3" filter="url(#neon)">
    <animate attributeName="y" values="0;280;0" dur="8s" repeatCount="indefinite" />
  </rect>

  <!-- Bottom Data Bar -->
  <rect x="0" y="280" width="1200" height="20" fill="#0f172a" opacity="0.8"/>
  <text x="20" y="294" font-family="'Courier New', monospace" font-size="10" fill="#38bdf8">ENTRA ID OIDC HANDSHAKE COMPLETED</text>
  <text x="600" y="294" font-family="'Courier New', monospace" font-size="10" fill="#8b5cf6" text-anchor="middle">VERTEX AI GROUNDING ENABLED</text>
  <text x="1180" y="294" font-family="'Courier New', monospace" font-size="10" fill="#10b981" text-anchor="end">WIF IDENTITY POOL: SECURE</text>
</svg>"""
with open(os.path.join(ASSET_DIR, "hero_banner.svg"), 'w') as f:
    f.write(hero_svg)


# 4. UPGRADE ARCH DIAGRAM WITH DATA PULSES

arch_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 400">
  <defs>
    <style>
      .bg { fill: #0f172a; }
      .text-title { font-family: 'Courier New', monospace; font-size: 24px; font-weight: 700; fill: #f8fafc; letter-spacing: 2px; }
      .text-body { font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; fill: #f8fafc; }
      .text-small { font-family: 'Courier New', monospace; font-size: 11px; font-weight: 500; fill: #94a3b8; }
      
      .line-main { stroke: #38bdf8; stroke-width: 2; fill: none; }
      .line-glow { stroke: rgba(56, 189, 248, 0.4); stroke-width: 6; fill: none; filter: blur(3px); }
      .line-dash { stroke: #64748b; stroke-width: 1.5; stroke-dasharray: 6 6; fill: none; }
      
      .box-entra { fill: rgba(139, 92, 246, 0.1); stroke: #8b5cf6; stroke-width: 2; rx: 8; ry: 8; }
      .box-gcp { fill: rgba(16, 185, 129, 0.1); stroke: #10b981; stroke-width: 2; rx: 8; ry: 8; }
      .box-vertex { fill: rgba(245, 158, 11, 0.1); stroke: #f59e0b; stroke-width: 2; rx: 8; ry: 8; }
      .box-sharepoint { fill: #1e293b; stroke: #475569; stroke-width: 1; rx: 4; ry: 4; }
    </style>
    
    <filter id="glow">
      <feGaussianBlur stdDeviation="5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
    </marker>
    <marker id="arrow-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
    </marker>
  </defs>

  <rect class="bg" width="1000" height="400" />
  
  <g opacity="0.1">
    <path class="line-dash" d="M0,50 L1000,50 M0,100 L1000,100 M0,150 L1000,150 M0,200 L1000,200 M0,250 L1000,250 M0,300 L1000,300 M0,350 L1000,350" />
    <path class="line-dash" d="M100,0 L100,400 M200,0 L200,400 M300,0 L300,400 M400,0 L400,400 M500,0 L500,400 M600,0 L600,400 M700,0 L700,400 M800,0 L800,400 M900,0 L900,400" />
  </g>

  <!-- Title with animated cursor -->
  <text x="40" y="45" class="text-title">FEDERATION_ARCHITECTURE<tspan fill="#38bdf8"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" />_</tspan></text>

  <!-- Animated Data Packets (Circles moving along paths) -->
  <!-- Auth Flow -->
  <circle r="4" fill="#ffffff" filter="url(#glow)">
    <animateMotion dur="2s" repeatCount="indefinite" path="M 260 130 L 360 130" />
  </circle>
  <circle r="4" fill="#ffffff" filter="url(#glow)">
    <animateMotion dur="2s" repeatCount="indefinite" path="M 580 130 L 680 130" />
  </circle>

  <!-- Sync Flow -->
  <circle r="4" fill="#f59e0b" filter="url(#glow)">
    <animateMotion dur="3s" repeatCount="indefinite" path="M 260 270 L 360 270" />
  </circle>
  <circle r="4" fill="#f59e0b" filter="url(#glow)">
    <animateMotion dur="3s" repeatCount="indefinite" path="M 580 270 L 680 270" />
  </circle>

  <!-- Cross-phase Flow -->
  <circle r="4" fill="#10b981" filter="url(#glow)">
    <animateMotion dur="4s" repeatCount="indefinite" path="M 750 170 C 750 200, 500 200, 430 230" />
  </circle>

  <g transform="translate(40, 90)">
    <!-- Nodes Phase 1 -->
    <rect class="box-entra" width="220" height="80" />
    <text x="20" y="30" class="text-body">Entra ID UI App</text>
    <text x="20" y="50" class="text-small">deloitte-entraid</text>
    <text x="20" y="65" class="text-small" fill="#8b5cf6">Primary Identity Provider</text>

    <rect class="box-gcp" x="320" y="0" width="220" height="80" />
    <text x="340" y="30" class="text-body">WF Identity Federation</text>
    <text x="340" y="50" class="text-small">entra-id-pool-d</text>
    <text x="340" y="65" class="text-small" fill="#10b981">Google Cloud Boundary</text>

    <rect class="box-gcp" x="640" y="0" width="220" height="80" />
    <text x="660" y="30" class="text-body">GCP IAM Bindings</text>
    <text x="660" y="50" class="text-small">principalSet://...</text>
    <text x="660" y="65" class="text-small" fill="#10b981">Vertex AI User Roles</text>

    <!-- Phase 1 Lines -->
    <path class="line-glow" d="M 220 40 L 320 40" />
    <path class="line-main" d="M 220 40 L 320 40" marker-end="url(#arrow-blue)" />
    <text x="230" y="30" class="text-small">Issuer &amp; Token</text>

    <path class="line-glow" d="M 540 40 L 640 40" />
    <path class="line-main" d="M 540 40 L 640 40" marker-end="url(#arrow-blue)" />
    <text x="560" y="30" class="text-small">Federates</text>
  </g>

  <g transform="translate(40, 230)">
    <!-- Nodes Phase 2 -->
    <rect class="box-entra" width="220" height="80" />
    <text x="20" y="30" class="text-body">Entra ID Sync App</text>
    <text x="20" y="50" class="text-small">sharepoint-store</text>
    <text x="20" y="65" class="text-small" fill="#8b5cf6">Service Principal</text>

    <rect class="box-vertex" x="320" y="0" width="220" height="80" />
    <text x="340" y="30" class="text-body">Vertex AI Search</text>
    <text x="340" y="50" class="text-small">deloitte-demo engine</text>
    <text x="340" y="65" class="text-small" fill="#f59e0b">SharePoint Connector</text>
    
    <rect class="box-sharepoint" x="640" y="0" width="220" height="80" />
    <text x="660" y="45" class="text-body">Microsoft SharePoint</text>

    <!-- Phase 2 Lines -->
    <path class="line-glow" d="M 220 40 L 320 40" />
    <path class="line-main" d="M 220 40 L 320 40" marker-end="url(#arrow-blue)" />
    <text x="230" y="30" class="text-small">Client Secret</text>

    <path class="line-dash" d="M 540 40 L 640 40" marker-start="url(#arrow-gray)" marker-end="url(#arrow-gray)" />
    <text x="550" y="30" class="text-small">Background Sync</text>
  </g>

  <!-- Cross-phase Line -->
  <path class="line-glow" d="M 750 170 C 750 200, 500 200, 430 230" />
  <path class="line-main" d="M 750 170 C 750 200, 500 200, 430 230" marker-end="url(#arrow-blue)" />
  <text x="580" y="195" class="text-small">Permits Query Execution</text>

</svg>"""
with open(os.path.join(ASSET_DIR, "arch_diagram.svg"), 'w') as f:
    f.write(arch_svg)

print("Generated all animated SVG assets.")

# 5. GENERATE THE NEW README.MD 

readme_content = """<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./public/assets/hero_banner.svg">
    <source media="(prefers-color-scheme: light)" srcset="./public/assets/hero_banner.svg">
    <img alt="Sockcop Search Neo-Monolith Hero" src="./public/assets/hero_banner.svg" width="100%">
  </picture>
</p>

<div align="center">

[![License](https://img.shields.io/badge/License-Apache_2.0-0F172A?style=for-the-badge&logoColor=38BDF8&labelColor=1E293B)](https://opensource.org/licenses/Apache-2.0)
[![React](https://img.shields.io/badge/React-19.0-0F172A?style=for-the-badge&logo=react&logoColor=3B82F6&labelColor=1E293B)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-0F172A?style=for-the-badge&logo=tailwind-css&logoColor=06B6D4&labelColor=1E293B)](https://tailwindcss.com/)
[![Google Cloud](https://img.shields.io/badge/Vertex_AI-Search-0F172A?style=for-the-badge&logo=googlecloud&logoColor=F59E0B&labelColor=1E293B)](https://cloud.google.com/enterprise-search)
[![Microsoft Entra](https://img.shields.io/badge/Entra_ID-Federation-0F172A?style=for-the-badge&logo=microsoft&logoColor=8B5CF6&labelColor=1E293B)](https://entra.microsoft.com/)

</div>

<blockquote>
  <p><b>SYSTEM LOG:</b> Sockcop Search transcends basic retrieval. It is a high-fidelity, brutalist neo-monolith acting as a secure gateway to your enterprise intelligence. It federates Microsoft Entra ID authentication signals directly into the heart of Google Cloud's Vertex AI Search (Gemini Enterprise) engine without a traditional backend.</p>
</blockquote>

<br/>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./public/assets/arch_diagram.svg">
    <source media="(prefers-color-scheme: light)" srcset="./public/assets/arch_diagram.svg">
    <img alt="Next Gen Architecture Pathway" src="./public/assets/arch_diagram.svg" width="100%">
  </picture>
</p>

<br/>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./public/assets/header_topologies.svg">
    <source media="(prefers-color-scheme: light)" srcset="./public/assets/header_topologies.svg">
    <img alt="Interface Topologies Header" src="./public/assets/header_topologies.svg" width="100%">
  </picture>
</p>

<blockquote>
  <p><b>ARCHITECTURE DUALITY:</b> The Vertex AI Search backend can be consumed via two distinct presentation layers. Choose your methodology.</p>
</blockquote>

<details open>
<summary><kbd>TOPOLOGY A</kbd> <b>Native Gemini Enterprise Interface (Zero-Code)</b></summary>
<br/>
<table>
  <tr>
    <td valign="top">
      <kbd>EXECUTE</kbd> Navigate to <b>GCP Console</b> &gt; <b>Agent Builder</b> &gt; <b>deloitte-demo</b>.<br/><br/>
      <kbd>DEFINE</kbd> Ensure the SharePoint datastore is connected and fully synced.<br/><br/>
      <kbd>OPERATE</kbd> Click <b>Preview</b> to utilize the out-of-the-box Gemini UI.<br/><br/>
      <kbd>RESULT</kbd> Instantly chat, search, and retrieve grounded financial data directly from Microsoft SharePoint without deploying any custom React code.
    </td>
    <td width="400" valign="top">
      <img src="./public/screenshots/native_datastore_status.png" width="400" style="border-radius: 8px;" />
      <br/><br/>
      <img src="./public/screenshots/native_search_results.png" width="400" style="border-radius: 8px;" />
    </td>
  </tr>
</table>
</details>

<br/>

<details open>
<summary><kbd>TOPOLOGY B</kbd> <b>Custom React Neo-Monolith (WIF Required)</b></summary>
<br/>
<table>
  <tr>
    <td valign="top">
      <kbd>EXECUTE</kbd> Utilize this repository's precise brutalist UI.<br/><br/>
      <kbd>DEFINE</kbd> This methodology bypasses the preview interface and calls the Discovery Engine API directly using <b>Workforce Identity Federation (WIF)</b> coupled with Entra ID.<br/><br/>
      <kbd>OPERATE</kbd> Follow the rigorous 6-Phase Pipeline below to orchestrate the auth handshake.
    </td>
    <td width="400" valign="top">
      <img src="./public/screenshots/search_results.png" width="400" style="border-radius: 8px;" />
    </td>
  </tr>
</table>
</details>

<br/>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./public/assets/header_config.svg">

    <source media="(prefers-color-scheme: light)" srcset="./public/assets/header_config.svg">
    <img alt="Configuration Pipeline Header" src="./public/assets/header_config.svg" width="100%">
  </picture>
</p>

<blockquote>
  <p><b>SECURITY PROTOCOL:</b> Follow this specific initialization chronological order. Crucially, no credentials must be leaked or stored in your frontend.</p>
</blockquote>

###

<details open>
<summary><kbd>PHASE 1</kbd> <b>Initial Azure AD (Entra ID) App Setup</b></summary>
<br/>

<table>
  <tr>
    <td width="100" align="center" valign="top"><img src="./public/assets/step_1.svg" width="60"></td>
    <td valign="top">
      <kbd>EXECUTE</kbd> Navigate to <b>Entra ID</b> &gt; <b>App registrations</b>.<br/><br/>
      <kbd>INPUT</kbd> Create the app <code>deloitte-entraid</code>.<br/><br/>
      <kbd>DEFINE</kbd> Under Authentication, add Single-page application and set redirect URI to <code>http://localhost:5173</code>.<br/><br/>
      <kbd>CONFIG</kbd> Under API Permissions, grant <code>User.Read</code>, <code>profile</code>, <code>openid</code>, and <code>email</code>.<br/><br/>
      <kbd>EXTRACT</kbd> Recover your exact payloads shown below.
      <br/><br/>
      <code>TENANT_ID: "YOUR_TENANT_ID"</code><br/>
      <code>MS_APP_ID: "YOUR_CLIENT_ID"</code><br/>
      <code>ISSUER: "https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0"</code>
    </td>
    <td width="400" valign="top">
      <img src="./public/screenshots/deloitte-entraid_Authentication.png" width="400" style="border-radius: 8px;" />
      <br/><br/>
      <img src="./public/screenshots/deloitte-entraid_API_permissions.png" width="400" style="border-radius: 8px;" />
    </td>
  </tr>
</table>

</details>

<br/>

<details open>
<summary><kbd>PHASE 2</kbd> <b>Google Cloud Workforce Identity Federation (WIF)</b></summary>
<br/>

<table>
  <tr>
    <td width="100" align="center" valign="top"><img src="./public/assets/step_2.svg" width="60"></td>
    <td valign="top">
      <kbd>EXECUTE</kbd> Navigate to <b>GCP Console</b> &gt; <b>IAM &amp; Admin</b>.<br/><br/>
      <kbd>INPUT</kbd> Create pool named <code>entra-id-oidc-pool-d</code>.<br/><br/>
      <kbd>DEFINE</kbd> Add OIDC Provider. Set <b>Issuer URI</b> and <b>Client ID</b> from Phase 1.<br/><br/>
      <kbd>CONFIG</kbd> Map <code>google.subject</code> to <code>assertion.sub</code>.<br/><br/>
      <kbd>EXTRACT</kbd> Recover the <code>WIF Pool ID</code> and <code>WIF Provider ID</code>.
    </td>
    <td width="400" valign="top">
      <img src="./public/screenshots/WIF_pool_overview.png" width="400" style="border-radius: 8px;" />
      <br/><br/>
      <img src="./public/screenshots/WIF_provider_config.png" width="400" style="border-radius: 8px;" />
    </td>
  </tr>
</table>

</details>

<br/>

<details open>
<summary><kbd>PHASE 3</kbd> <b>Google Cloud IAM WIF Binding</b></summary>
<br/>

<table>
  <tr>
    <td width="100" align="center" valign="top"><img src="./public/assets/step_3.svg" width="60"></td>
    <td valign="top">
      <kbd>EXECUTE</kbd> Navigate to <b>GCP Console</b> &gt; <b>IAM &amp; Admin</b>.<br/><br/>
      <kbd>DEFINE</kbd> Bind permissions directly to the WIF-authenticated identities.<br/><br/>
      <kbd>INPUT</kbd> Enter the <code>principalSet://</code> identifier for the WIF pool.<br/><br/>
      <kbd>CONFIG</kbd> Assign <code>Discovery Engine Viewer</code> and <code>Vertex AI User</code> roles.
    </td>
    <td width="400" valign="top">
      <img src="./public/screenshots/gcp_iam_wif_bindings.png" width="400" style="border-radius: 8px;" />
    </td>
  </tr>
</table>

</details>

<br/>

<details open>
<summary><kbd>PHASE 4</kbd> <b>SharePoint Connector App (Background Sync)</b></summary>
<br/>

<table>
  <tr>
    <td width="100" align="center" valign="top"><img src="./public/assets/step_4.svg" width="60"></td>
    <td valign="top">
      <kbd>EXECUTE</kbd> Return to <b>Entra ID</b> &gt; <b>App registrations</b>.<br/><br/>
      <kbd>DEFINE</kbd> Create Service App: <code>sharepoint-datastore</code>.<br/><br/>
      <kbd>CONFIG</kbd> Under API permissions, add Application permissions for Microsoft Graph (<code>Sites.Read.All</code>, <code>Sites.Search.All</code>). <b>Grant Admin Consent</b>.<br/><br/>
      <kbd>INPUT</kbd> Generate a new <b>Client Secret</b>.<br/><br/>
      <kbd>EXTRACT</kbd> Save the <code>Client Secret</code>.
    </td>
    <td width="400" valign="top">
      <img src="./public/screenshots/deloitte-sharepoint-datastore_Authentication.png" width="400" style="border-radius: 8px;" />
      <br/><br/>
      <img src="./public/screenshots/deloitte-sharepoint-datastore_API_permissions.png" width="400" style="border-radius: 8px;" />
    </td>
  </tr>
</table>

</details>

<br/>

<details open>
<summary><kbd>PHASE 5</kbd> <b>Gemini Enterprise Agent Builder Configuration</b></summary>
<br/>

<table>
  <tr>
    <td width="100" align="center" valign="top"><img src="./public/assets/step_5.svg" width="60"></td>
    <td valign="top">
      <kbd>EXECUTE</kbd> Navigate to <b>GCP Console</b> &gt; <b>Agent Builder</b>.<br/><br/>
      <kbd>DEFINE</kbd> Connect the Entra ID Service App pipeline into the Google Cloud search indexer.<br/><br/>
      <kbd>INPUT</kbd> Create Data Store &gt; SharePoint. Provide Client ID (Phase 4), Tenant ID, and Client Secret.<br/><br/>
      <kbd>CONFIG</kbd> Define the SharePoint Site URLs to index and initiate the sync.<br/><br/>
      <kbd>EXTRACT</kbd> Recover the <code>Datastore ID</code> and <code>Engine ID</code>.
    </td>
    <td width="400" valign="top">
      <img src="./public/screenshots/gcp_agent_builder_datastores.png" width="400" style="border-radius: 8px;" />
    </td>
  </tr>
</table>

</details>

<br/>

<details open>
<summary><kbd>PHASE 6</kbd> <b>Frontend Integration (React App)</b></summary>
<br/>

<table>
  <tr>
    <td width="100" align="center" valign="top"><img src="./public/assets/step_6.svg" width="60"></td>
    <td valign="top">
      <kbd>EXECUTE</kbd> Inject all accumulated identifiers into the Codebase.<br/><br/>
      <kbd>DEFINE</kbd> Update your <code>src/api/config.js</code> file.
      <br/><br/>
<pre><code>export const CONFIG = {
  // GCP Configuration
  LOCATION: "global",
  
  // WIF Configuration (Phase 2)
  WIF_POOL: "&lt;YOUR_POOL_ID&gt;",
  WIF_PROVIDER: "&lt;YOUR_PROVIDER_ID&gt;",
  
  // Vertex AI (Phase 5)
  DATA_STORE_ID: "&lt;YOUR_DATA_STORE_ID&gt;",
  ENGINE_ID: "deloitte-demo",
  
  // Entra ID (Phase 1)
  TENANT_ID: "&lt;YOUR_TENANT_ID&gt;",
  MS_APP_ID: "&lt;YOUR_ENTRA_CLIENT_ID&gt;", 
  ISSUER: "https://login.microsoft..."
};</code></pre>
    </td>
    <td width="400" valign="top">
    </td>
  </tr>
</table>

</details>

<br/>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./public/assets/header_setup.svg">
    <source media="(prefers-color-scheme: light)" srcset="./public/assets/header_setup.svg">
    <img alt="Setup Protocol Header" src="./public/assets/header_setup.svg" width="100%">
  </picture>
</p>

<blockquote>
  <p><b>OPERATION:</b> Initialize the monolith terminal sequence.</p>
</blockquote>

<table>
  <tr>
    <td>
      <kbd>EXECUTE</kbd> Install dependencies: <br/><code>npm install</code><br/><br/>
      <kbd>EXECUTE</kbd> Start the serverless React client: <br/><code>npm run dev</code>
    </td>
  </tr>
</table>

"""

with open("README.md", "w") as f:
    f.write(readme_content)

print("Generated full completely new 2076 Markdown structure")
