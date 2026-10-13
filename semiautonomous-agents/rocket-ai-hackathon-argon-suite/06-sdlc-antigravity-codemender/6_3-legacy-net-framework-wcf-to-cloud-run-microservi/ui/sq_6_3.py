# -*- coding: utf-8 -*-
"""Square 6.3: Legacy .NET Framework / WCF to Cloud Run Modernizer — Standalone UI Design File.
Visual Archetype: Dual-Pane Legacy Visual Studio 2008 WCF SOAP XML (#1B1429) vs.
Modern Google Cloud Run .NET 9 Minimal API Transpiler Studio (#0B192C + #38BDF8)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_6_3(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("6.3", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Legacy .NET 4.8 WCF -> Cloud Run .NET 9 Transpiler Studio</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Space Grotesk', sans-serif;
      background: #070E1A;
      color: #F8FAFC;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    .transpiler-bar {{
      background: linear-gradient(90deg, #2E1065 0%, #0F172A 50%, #0369A1 100%);
      border-bottom: 1px solid #334155;
      padding: 14px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .transpile-btn {{
      background: linear-gradient(135deg, #38BDF8, #10B981);
      color: #020617;
      border: none;
      padding: 10px 20px;
      border-radius: 8px;
      font-weight: 800;
      font-size: 13px;
      cursor: pointer;
    }}

    .dual-studio {{
      display: grid;
      grid-template-columns: 1fr 280px 1fr;
      flex: 1;
      min-height: calc(100vh - 64px);
    }}
    @media (max-width: 1100px) {{
      .dual-studio {{ grid-template-columns: 1fr; }}
    }}

    /* Left Pane: Legacy Visual Studio WCF */
    .legacy-pane {{
      background: #171124;
      border-right: 1px solid #3B2854;
      padding: 24px;
    }}
    /* Center Bridge: AST Transpiler Telemetry */
    .bridge-pane {{
      background: #0B1220;
      border-right: 1px solid #1E293B;
      padding: 22px 18px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    /* Right Pane: Cloud Run .NET 9 */
    .modern-pane {{
      background: #081526;
      padding: 24px 24px 80px 24px;
    }}
    .method-pill {{
      width: 100%;
      padding: 10px 12px;
      background: #131D31;
      border: 1px solid #263859;
      color: #E2E8F0;
      border-radius: 8px;
      text-align: left;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      cursor: pointer;
      margin-bottom: 6px;
    }}
    .method-pill.active {{
      border-color: #38BDF8;
      background: rgba(56, 189, 248, 0.14);
      color: #38BDF8;
      font-weight: 700;
    }}
  </style>
</head>
<body>

  <header class="transpiler-bar">
    <div style="display:flex;align-items:center;gap:14px;">
      <span class="mono" style="background:#581C87;color:#E9D5FF;padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;">LEGACY WCF .NET 4.8</span>
      <span style="font-size:18px;">⚡➔</span>
      <span class="mono" style="background:#0284C7;color:#E0F2FE;padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;">CLOUD RUN .NET 9 AOT</span>
      <h1 style="font-size:18px;font-weight:700;margin-left:6px;">Antigravity AST Transpiler & Windows License Eliminator</h1>
    </div>

    <div style="display:flex;align-items:center;gap:10px;">
      <div class="mono" style="background:rgba(0,0,0,0.4);padding:5px 10px;border-radius:6px;border:1px solid #475569;font-size:11px;">
        Model:
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" class="mono" style="background:transparent;color:#38BDF8;font-weight:700;border:none;outline:none;font-size:11px;cursor:pointer;">
          <option value="gemini-4-argon" style="background:#0F172A;">gemini-4-argon</option>
          <option value="gemini-3.8-flash" style="background:#0F172A;">gemini-3.8-flash</option>
        </select>
      </div>
      <button class="transpile-btn" onclick="window.runLiveVertexAI()" id="transpile-btn">🚀 Transpile WCF Service to .NET 9</button>
    </div>
  </header>

  <div class="dual-studio">
    <!-- LEFT: LEGACY WCF MONOLITH -->
    <section class="legacy-pane">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <span class="mono" style="font-size:12px;font-weight:700;color:#C084FC;">🏛️ Legacy Windows Server 2016 IIS / WCF `.svc`</span>
        <span class="mono" style="font-size:10px;background:#4C1D95;color:#DDD6FE;padding:3px 8px;border-radius:4px;">Cold Start: 14.2s</span>
      </div>
      <pre id="wcf-source" class="mono" style="background:#0F0A19;border:1px solid #3B2854;border-radius:10px;padding:16px;font-size:11.5px;line-height:1.65;color:#E9D5FF;overflow-x:auto;">using System.ServiceModel;
using System.Runtime.Serialization;

namespace Rocket.Legacy.Servicing.Wcf
{{
    [ServiceContract(Namespace = "http://rocket.com/wcf/2011")]
    public interface IEscrowPayoffService
    {{
        [OperationContract]
        [FaultContract(typeof(SoapEscrowFault))]
        PayoffXmlResult ComputePerDiemPayoff(string loanNumber, int days);
    }}

    // Requires Windows IIS + Web.config basicHttpBinding SOAP Envelope
}}</pre>
    </section>

    <!-- CENTER: AST BRIDGE & ROI SLIDERS -->
    <aside class="bridge-pane">
      <div>
        <div class="mono" style="font-size:11px;color:#38BDF8;text-transform:uppercase;margin-bottom:8px;">Select WCF Contract Method:</div>
        <button class="method-pill active" onclick="selectWcfMethod(0, this)">ComputePerDiemPayoff()</button>
        <button class="method-pill" onclick="selectWcfMethod(1, this)">ValidateMersLienRelease()</button>
        <button class="method-pill" onclick="selectWcfMethod(2, this)">RecalculateEscrowShortage()</button>
      </div>

      <div style="background:#111C2D;border:1px solid #1E293B;border-radius:10px;padding:14px;">
        <div class="mono" style="font-size:10.5px;color:#10B981;margin-bottom:8px;">🎛️ Fleet Migration Scale</div>
        <div class="mono" style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px;">
          <span>WCF Endpoints:</span>
          <strong id="lbl-eps" style="color:#38BDF8;">24</strong>
        </div>
        <input type="range" id="sl-eps" min="5" max="100" step="1" value="24" style="width:100%;accent-color:#38BDF8;" oninput="recalcWcf()">
        <div class="mono" style="font-size:11px;color:#94A3B8;margin-top:10px;line-height:1.55;" id="wcf-metrics-box">
          • Cold Start: 14.2s ➔ 0.38s<br>
          • Windows License Saved: $148,800/yr<br>
          • Parity Tests: 100% Match
        </div>
      </div>

      <div style="background:#111C2D;border:1px solid #1E293B;border-radius:10px;padding:14px;font-size:12px;line-height:1.55;color:#CBD5E1;" id="wcf-ai-notes">
        <strong>AST Modernization Verdict:</strong> Stripped `System.ServiceModel` SOAP envelopes and compiled into Linux `mcr.microsoft.com/dotnet/aspnet:9.0-alpine` containers on Google Cloud Run.
      </div>
    </aside>

    <!-- RIGHT: CLOUD RUN .NET 9 MINIMAL API -->
    <section class="modern-pane">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <span class="mono" style="font-size:12px;font-weight:700;color:#38BDF8;">☁️ Google Cloud Run `.NET 9 Minimal API` + OpenTelemetry</span>
        <span class="mono" id="modern-model-badge" style="font-size:10px;background:#0369A1;color:#E0F2FE;padding:3px 8px;border-radius:4px;">Cold Start: 0.38s • gemini-4-argon</span>
      </div>
      <pre id="dotnet9-source" class="mono" style="background:#040B14;border:1px solid #1E3A5F;border-radius:10px;padding:16px;font-size:11.5px;line-height:1.65;color:#7DD3FC;overflow-x:auto;">using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http.HttpResults;

var builder = WebApplication.CreateSlimBuilder(args);
builder.Services.AddOpenTelemetry().WithTracing();
var app = builder.Build();

app.MapPost("/v1/payoff/per-diem", Results&lt;Ok&lt;PayoffDto&gt;, BadRequest&gt; (PayoffRequest req) =>
{{
    decimal dailyInterest = Math.Round((req.Principal * (req.NoteRate / 100m)) / 365m, 2);
    decimal totalPayoff = req.Principal + (dailyInterest * req.Days) + req.RecordingFee;
    return TypedResults.Ok(new PayoffDto(req.LoanNumber, dailyInterest, totalPayoff));
}});

app.Run(); // Runs rootless on Google Cloud Run Gen2 Linux</pre>
    </section>
  </div>

  {controls}

  <script>
    function selectWcfMethod(idx, btn) {{
      document.querySelectorAll('.method-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }}

    async function recalcWcf() {{
      const eps = parseInt(document.getElementById('sl-eps').value);
      document.getElementById('lbl-eps').innerText = eps;
      const res = await fetch('/api/sandbox', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{code: '6.3', action: 'transpile_wcf_to_dotnet8', params: {{wcf_endpoints: eps}}}})
      }});
      const data = await res.json();
      if (data.ok && data.metrics) {{
        document.getElementById('wcf-metrics-box').innerHTML =
          Object.values(data.metrics).map(v => '• ' + v).join('<br>');
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('transpile-btn');
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Transpiling on ' + model + '...';
      const eps = parseInt(document.getElementById('sl-eps').value);
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{code: '6.3', model: model, params: {{wcf_endpoints: eps}}}})
        }});
        const data = await res.json();
        document.getElementById('modern-model-badge').innerText = 'Cold Start: 0.38s • ' + (data.model_used || model);
        if (data.structured_data && (data.structured_data.migration_summary || data.structured_data.executive_summary)) {{
          document.getElementById('wcf-ai-notes').innerHTML = data.structured_data.migration_summary || data.structured_data.executive_summary;
        }} else if (data.output) {{
          document.getElementById('wcf-ai-notes').innerText = data.output;
        }}
      }} catch (e) {{}}
      finally {{
        btn.innerText = '🚀 Transpile WCF Service to .NET 9';
      }}
    }};
  </script>
</body>
</html>"""
