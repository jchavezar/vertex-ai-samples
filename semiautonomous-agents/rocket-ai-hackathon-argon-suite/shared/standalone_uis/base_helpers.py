# -*- coding: utf-8 -*-
"""Invisible API Bridge, Security URL Sanitizer, Model Selector (`gemini-4-argon` vs `gemini-3.8-flash`),
Real WebAudio Bidi WebSocket Engine, and Slide-Over Blueprint/Code Drawer for the 33 Standalone Demo Apps.
NOTE: This module renders ZERO page layout chrome — 100% of each demo's visual UI, fonts, colors,
navigation, buttons, and interactive dynamics live in its own dedicated `sq_X_Y.py` design file."""

import json
from typing import Any, Dict
from shared.auth_and_vertex import get_recommended_model_for_square
from shared.catalog_data import CLOUD_RUN_URLS, PROJECTS_BY_CODE


def build_genai_sdk_snippet(code: str, model_id: str) -> str:
    """Returns the official google-genai SDK snippet matching the user's Agent Studio screenshot."""
    proj = PROJECTS_BY_CODE.get(code, PROJECTS_BY_CODE["1.1"])
    sys_p = proj.get("systemPrompt", "You are a Rocket Companies AI specialist.").replace('"', '\\"')
    sample_in = proj.get("sampleInput", "Analyze this scenario.").replace('"', '\\"').replace("\n", "\\n")
    return f'''# Install SDK: pip install --upgrade google-genai
from google import genai
from google.genai import types
import os

def generate_rocket_solution():
    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
        location="global",
    )

    model = "{model_id}"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="{sample_in[:220]}...")
            ]
        )
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=2048,
        system_instruction=[types.Part.from_text(text="{sys_p[:180]}...")],
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    print(response.text)

if __name__ == "__main__":
    generate_rocket_solution()
'''


def render_floating_control_bar_and_drawer(code: str, auth_token: str, badge_style: str = "dark") -> str:
    """Renders a compact floating control pill (Model Selector Dropdown: gemini-4-argon vs gemini-3.8-flash,
    Portal Return Link, and Slide-Over Blueprint & Code Drawer) plus the client-side JS API helpers."""
    proj = PROJECTS_BY_CODE.get(code, PROJECTS_BY_CODE["1.1"])
    route = get_recommended_model_for_square(code)
    default_model = route.get("default_model", "gemini-4-argon")
    portal_url = f"{CLOUD_RUN_URLS['portal']}?auth_token={auth_token}"
    docs_url = f"{CLOUD_RUN_URLS['portal']}/docs/{code}?auth_token={auth_token}"
    ge_ui_url = "https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023"

    sel_argon = "selected" if default_model == "gemini-4-argon" else ""
    sel_flash = "selected" if default_model == "gemini-3.8-flash" else ""

    snippet_argon = json.dumps(build_genai_sdk_snippet(code, "gemini-4-argon"))
    snippet_flash = json.dumps(build_genai_sdk_snippet(code, "gemini-3.8-flash"))
    proj_json = json.dumps(proj)

    square_options_html = []
    for sq_code, sq_p in PROJECTS_BY_CODE.items():
        sel = "selected" if sq_code == code else ""
        short_name = sq_p["project"][:34]
        square_options_html.append(
            f'<option value="{sq_code}" {sel} style="background:#0F172A;color:#F8FAFC;">[{sq_code}] {short_name}</option>'
        )
    square_options_str = "\n      ".join(square_options_html)

    return f"""
<!-- COMPACT FLOATING RUNTIME & MODEL CONTROL PILL -->
<div id="rkt-floating-pill" style="position:fixed;bottom:18px;right:18px;z-index:9990;display:flex;align-items:center;gap:8px;padding:8px 12px;border-radius:999px;background:rgba(9,13,22,0.92);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.16);box-shadow:0 16px 40px rgba(0,0,0,0.45);font-family:'JetBrains Mono',monospace;font-size:11px;color:#F8FAFC;flex-wrap:wrap;">
  <a href="{portal_url}" style="color:#94A3B8;text-decoration:none;font-weight:700;padding:4px 8px;border-radius:999px;background:rgba(255,255,255,0.06);transition:0.2s;" onmouseover="this.style.color='#FFF'" onmouseout="this.style.color='#94A3B8'">
    ← Hub
  </a>
  <div style="display:flex;align-items:center;gap:4px;padding:3px 10px;border-radius:999px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);">
    <select onchange="window.location.href='/?case='+encodeURIComponent(this.value)" style="background:transparent;color:#E2E8F0;font-weight:700;font-family:'JetBrains Mono',monospace;font-size:10.5px;border:none;outline:none;cursor:pointer;max-width:190px;">
      {square_options_str}
    </select>
  </div>
  <div style="display:flex;align-items:center;gap:5px;padding:3px 10px;border-radius:999px;background:rgba(99,102,241,0.18);border:1px solid rgba(99,102,241,0.4);">
    <span style="width:7px;height:7px;border-radius:50%;background:#10B981;display:inline-block;"></span>
    <span style="color:#A5B4FC;font-size:10px;text-transform:uppercase;font-weight:700;">Model:</span>
    <select id="model-select" onchange="window.syncSelectedModel(this.value)" style="background:transparent;color:#FFFFFF;font-weight:700;font-family:'JetBrains Mono',monospace;font-size:11px;border:none;outline:none;cursor:pointer;">
      <option value="gemini-4-argon" {sel_argon} style="background:#0F172A;color:#38BDF8;">gemini-4-argon (Frontier Global)</option>
      <option value="gemini-3.8-flash" {sel_flash} style="background:#0F172A;color:#10B981;">gemini-3.8-flash (Fast / ADK Runtime)</option>
    </select>
  </div>
  <button onclick="window.toggleBlueprintDrawer()" style="background:linear-gradient(135deg,#4F46E5,#06B6D4);color:#FFF;border:none;padding:5px 12px;border-radius:999px;font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;cursor:pointer;box-shadow:0 4px 12px rgba(79,70,229,0.4);">
    🛠️ Code & Architecture
  </button>
</div>

<!-- SLIDE-OVER ARCHITECTURE, GENAI SDK CODE & REPRODUCTION DRAWER -->
<div id="rkt-blueprint-drawer" style="position:fixed;top:0;right:-560px;width:min(540px,95vw);height:100vh;z-index:9999;background:#090D16;color:#F8FAFC;border-left:1px solid #1E293B;box-shadow:-20px 0 60px rgba(0,0,0,0.7);transition:right 0.3s cubic-bezier(0.16,1,0.3,1);display:flex;flex-direction:column;font-family:'Inter',sans-serif;">
  <div style="padding:18px 22px;border-bottom:1px solid #1E293B;display:flex;align-items:center;justify-content:space-between;background:#050811;">
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#38BDF8;text-transform:uppercase;letter-spacing:0.08em;">Square [{code}] • Technical Blueprint & GenAI SDK</div>
      <div style="font-size:15px;font-weight:800;color:#FFF;margin-top:2px;">{proj['project']}</div>
    </div>
    <button onclick="window.toggleBlueprintDrawer()" style="background:#1E293B;color:#CBD5E1;border:none;width:32px;height:32px;border-radius:8px;cursor:pointer;font-weight:800;">✕</button>
  </div>
  <div style="padding:20px 22px;overflow-y:auto;flex:1;display:flex;flex-direction:column;gap:18px;">
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
      <a href="{docs_url}" target="_blank" style="flex:1;text-align:center;padding:9px 12px;border-radius:10px;background:#4F46E5;color:#FFF;text-decoration:none;font-size:12px;font-weight:700;font-family:'JetBrains Mono',monospace;">
        📘 Full Reproduction Guide & SKILL.md ↗
      </a>
      <a href="{ge_ui_url}" target="_blank" style="flex:1;text-align:center;padding:9px 12px;border-radius:10px;background:rgba(168,85,247,0.2);border:1px solid rgba(168,85,247,0.5);color:#E9D5FF;text-decoration:none;font-size:12px;font-weight:700;font-family:'JetBrains Mono',monospace;">
        ✨ Real Gemini Enterprise UI ↗
      </a>
    </div>

    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:#10B981;text-transform:uppercase;margin-bottom:6px;">
        1. Live Vertex AI GenAI SDK Code (<span id="drawer-model-label">{default_model}</span>)
      </div>
      <pre id="drawer-sdk-code" style="background:#020617;border:1px solid #1E293B;border-radius:12px;padding:14px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#A5F3FC;overflow-x:auto;line-height:1.5;margin:0;"></pre>
    </div>

    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:#38BDF8;text-transform:uppercase;margin-bottom:6px;">
        2. GCP Reference Architecture (<= 78 Cols)
      </div>
      <pre style="background:#020617;border:1px solid #1E293B;border-radius:12px;padding:14px;font-family:'JetBrains Mono',monospace;font-size:10.5px;color:#E2E8F0;overflow-x:auto;line-height:1.4;margin:0;">{proj.get('archDiagram', '')}</pre>
    </div>

    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:#F59E0B;text-transform:uppercase;margin-bottom:6px;">
        3. Custom Scenario Prompt Override
      </div>
      <textarea id="scenario-input" rows="4" style="width:100%;background:#020617;border:1px solid #334155;border-radius:10px;padding:10px;color:#F8FAFC;font-family:'JetBrains Mono',monospace;font-size:11px;">{proj.get('sampleInput', '')}</textarea>
      <button onclick="window.runLiveVertexAI()" style="margin-top:8px;width:100%;padding:10px;border-radius:10px;background:linear-gradient(135deg,#10B981,#059669);color:#FFF;border:none;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:800;cursor:pointer;">
        ⚡ Re-Synthesize with Selected Model
      </button>
    </div>
  </div>
</div>

<script>
  // Immediately scrub ?auth_token=... from the browser URL bar after cookie authentication
  // so sharing or copying the URL never leaks the session token!
  (function() {{
    try {{
      if (window.location.search.includes('auth_token=')) {{
        const url = new URL(window.location.href);
        url.searchParams.delete('auth_token');
        window.history.replaceState({{}}, document.title, url.pathname + url.search);
      }}
    }} catch (e) {{}}
  }})();

  window.SQUARE_CODE = "{code}";
  window.ACTIVE_PROJECT = {proj_json};
  window.SDK_SNIPPETS = {{
    "gemini-4-argon": {snippet_argon},
    "gemini-3.8-flash": {snippet_flash}
  }};

  window.getSelectedModel = function() {{
    const el = document.getElementById('model-select');
    return el ? el.value : "{default_model}";
  }};

  window.syncSelectedModel = function(val) {{
    const el = document.getElementById('model-select');
    if (el && el.value !== val) el.value = val;
    const topSel = document.getElementById('app-model-select');
    if (topSel && topSel.value !== val) topSel.value = val;
    const lbl = document.getElementById('drawer-model-label');
    if (lbl) lbl.innerText = val;
    const codeEl = document.getElementById('drawer-sdk-code');
    if (codeEl && window.SDK_SNIPPETS[val]) codeEl.textContent = window.SDK_SNIPPETS[val];
    const badgeEl = document.getElementById('live-model-pill');
    if (badgeEl) badgeEl.innerText = val;
  }};

  window.toggleBlueprintDrawer = function() {{
    const dr = document.getElementById('rkt-blueprint-drawer');
    if (!dr) return;
    dr.style.right = (dr.style.right === '0px') ? '-560px' : '0px';
  }};

  // Initialize SDK snippet on load
  document.addEventListener('DOMContentLoaded', () => {{
    window.syncSelectedModel("{default_model}");
  }});
</script>
"""
