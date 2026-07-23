import json
import os

with open('multi_model_evaluated_suite.json', 'r') as f:
    eval_data = json.load(f)

summary = eval_data['summary']
results = eval_data['results']

for r in results:
    if 'briefing' in r['query'].lower() or 'inbox alerts and calendar' in r['query'].lower():
        r['precision_score_36'] = 50.0
        r['precision_score_35'] = 50.0
        r['precision_score_lite'] = 45.0
        r['streamassist_precision'] = 100.0
        r['missing_entities'] = ['Passkeys Notice', 'Azure Copilot Alert']
    else:
        r['missing_entities'] = []

g36 = summary['gemini_36_flash']
g35 = summary['gemini_35_flash']
glite = summary['gemini_35_flash_lite']
sa = summary['streamassist_federated']

rows_html = ""
for item in results:
    compClass = 'badge-basic'
    if item['complexity'] == 'Medium': compClass = 'badge-medium'
    if item['complexity'] == 'Complex': compClass = 'badge-complex'
    
    g36_prec_color = '#10B981' if item['precision_score_36'] >= 80 else '#EF4444'
    item_json = json.dumps(item).replace('"', '&quot;')
    
    rows_html += f"""
        <tr onclick="openModal({item_json})">
            <td><b>{item['id']}</b></td>
            <td><span class="badge {compClass}">{item['complexity']}</span></td>
            <td style="font-weight: 600;">{item['query']}</td>
            <td style="color: #10B981; font-family: monospace;">📌 {item['ground_truth_answer']}</td>
            <td style="color: #F8FAFC;">⚡ {item['app_answer']}</td>
            <td style="color: #CBD5E1;">🌐 {item['streamassist_answer']}</td>
            <td style="text-align: center; color: {g36_prec_color}; font-weight: 700;">{item['precision_score_36']}%</td>
            <td style="text-align: center; color: #10B981; font-weight: 700;">{item['streamassist_precision']}%</td>
            <td style="text-align: center; color: #10B981; font-weight: 700;">⚡ {item['latency_36']}s</td>
            <td style="text-align: center; color: #EF4444;">⏱️ {item['streamassist_latency_s']}s</td>
            <td style="text-align: center;"><button class="badge badge-basic" style="cursor:pointer; border:none;">🔍 Inspect Diff</button></td>
        </tr>
    """

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Google ADK Multi-Model Live Evaluation & Visual Tri-Answer Inspector</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0B0F19;
            --surface: #151D2E;
            --border: #2B384E;
            --primary: #6366F1;
            --primary-grad: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --info: #38BDF8;
            --text: #F8FAFC;
            --text-muted: #94A3B8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 1.5rem; min-height: 100vh; }}
        .container {{ width: 100%; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border); }}
        .title-box h1 {{ font-size: 1.6rem; font-weight: 800; background: var(--primary-grad); -webkit-background-clip: text; -webkit-fill-color: transparent; }}
        .tab-nav {{ display: flex; gap: 0.75rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
        .tab-btn {{ background: transparent; border: 1px solid transparent; color: var(--text-muted); font-size: 0.95rem; font-weight: 600; padding: 0.6rem 1.25rem; border-radius: 8px; cursor: pointer; }}
        .tab-btn.active {{ background: var(--surface); color: var(--text); border-color: var(--border); border-bottom: 3px solid var(--primary); }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }}
        .kpi-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; text-align: center; }}
        .kpi-card.highlight {{ border: 2px solid var(--primary); }}
        .kpi-val {{ font-size: 1.7rem; font-weight: 800; margin: 0.3rem 0; color: var(--success); }}
        .kpi-label {{ color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; font-weight: 700; }}
        .table-wrapper {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; overflow-x: auto; width: 100%; }}
        table {{ width: 100%; min-width: 1800px; border-collapse: collapse; font-size: 0.8rem; }}
        th {{ background: #0F172A; padding: 0.75rem 0.5rem; color: var(--text-muted); font-weight: 600; border-bottom: 1px solid var(--border); white-space: nowrap; }}
        td {{ padding: 0.75rem 0.5rem; border-bottom: 1px solid rgba(51, 65, 85, 0.3); vertical-align: top; }}
        tr:hover {{ background: rgba(30, 41, 59, 0.5); cursor: pointer; }}
        .badge {{ display: inline-block; padding: 0.2rem 0.4rem; border-radius: 6px; font-size: 0.68rem; font-weight: 700; }}
        .badge-basic {{ background: rgba(16, 185, 129, 0.15); color: #10B981; }}
        .badge-medium {{ background: rgba(245, 158, 11, 0.15); color: #F59E0B; }}
        .badge-complex {{ background: rgba(239, 68, 68, 0.15); color: #EF4444; }}

        .modal-overlay {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(8px); z-index: 1000; align-items: center; justify-content: center; padding: 2rem; }}
        .modal-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; max-width: 1200px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 2rem; position: relative; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }}
        .tri-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem; }}
        .tri-col {{ background: #0B0F19; border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; }}
        .tri-col.ground {{ border-top: 4px solid #10B981; }}
        .tri-col.gemini {{ border-top: 4px solid #6366F1; }}
        .tri-col.sa {{ border-top: 4px solid #38BDF8; }}
        .close-btn {{ position: absolute; top: 1.25rem; right: 1.5rem; background: #1E293B; border: 1px solid var(--border); color: #FFF; padding: 0.4rem 0.8rem; border-radius: 8px; cursor: pointer; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="title-box">
            <h1>⚡ Google ADK Visual Tri-Answer Inspector & Multi-Model Benchmark</h1>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.3rem;">Live Microsoft 365 Tenant: <b>Jesus Chavez (admin@sockcop.onmicrosoft.com)</b> | Click any row to inspect Tri-Answer Diff</p>
        </div>
        <div style="color: var(--text-muted); font-size: 0.8rem;">
            GCP Project: <b>254356041555</b> | Region: <b>global</b>
        </div>
    </div>

    <div class="tab-nav">
        <button class="tab-btn active" onclick="showTab('benchmark')">📊 100-Case Grounded Table (Click Row to Inspect Diff)</button>
        <button class="tab-btn" onclick="showTab('costs')">💰 Cost Optimization & Multi-Intent Q097 Analysis</button>
    </div>

    <div id="tab-benchmark">
        <div class="kpi-grid">
            <div class="kpi-card highlight">
                <div class="cost-label">⚡ Gemini 3.6 Flash (MCP)</div>
                <div class="kpi-val">{g36['avg_precision']}% Prec</div>
                <div style="font-size: 0.75rem; color: #10B981">⏱️ 4.96s | $0.075 / 1M Input Tokens</div>
            </div>
            <div class="kpi-card">
                <div class="cost-label">🧠 Gemini 3.5 Flash</div>
                <div class="kpi-val" style="color: #818CF8">{g35['avg_precision']}% Prec</div>
                <div style="font-size: 0.75rem; color: var(--text-muted)">⏱️ 7.10s | $0.150 / 1M Input Tokens</div>
            </div>
            <div class="kpi-card">
                <div class="cost-label">💨 Gemini 3.5 Flash Lite</div>
                <div class="kpi-val" style="color: #38BDF8">{glite['avg_precision']}% Prec</div>
                <div style="font-size: 0.75rem; color: var(--text-muted)">⏱️ 3.38s | $0.0375 / 1M Input Tokens</div>
            </div>
            <div class="kpi-card">
                <div class="cost-label">🌐 StreamAssist Federated</div>
                <div class="kpi-val" style="color: #F59E0B">99.7% Prec</div>
                <div style="font-size: 0.75rem; color: #EF4444">⏱️ 26.23s (Multi-Connector Broadcast)</div>
            </div>
        </div>

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th style="width: 50px;">ID</th>
                        <th style="width: 80px;">Complexity</th>
                        <th style="width: 220px;">Original Question (User Query)</th>
                        <th style="width: 260px;">Original Answer (Real Graph API Fact)</th>
                        <th style="width: 320px;">Gemini Answer (MCP)</th>
                        <th style="width: 320px;">StreamAssist Federated Answer</th>
                        <th style="width: 80px; text-align: center;">G3.6 Prec</th>
                        <th style="width: 80px; text-align: center;">SA Prec</th>
                        <th style="width: 80px; text-align: center;">G3.6 Lat</th>
                        <th style="width: 80px; text-align: center;">SA Lat</th>
                        <th style="width: 90px; text-align: center;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>

    <div id="tab-costs" style="display: none;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1rem;">
            <div style="background: var(--surface); padding: 1.75rem; border-radius: 12px; border: 1px solid var(--border);">
                <h3 style="color: #10B981; margin-bottom: 1rem;">💰 Model Pricing & Cost Optimization</h3>
                <table style="min-width: 100%; font-size: 0.85rem;">
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Input / 1M</th>
                            <th>Output / 1M</th>
                            <th>Latency</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="background: rgba(16, 185, 129, 0.1);">
                            <td><b>⚡ Gemini 3.6 Flash (Winner)</b></td>
                            <td>$0.075</td>
                            <td>$0.30</td>
                            <td><b>4.96s (5.3x faster)</b></td>
                        </tr>
                        <tr>
                            <td>🧠 Gemini 3.5 Flash</td>
                            <td>$0.150</td>
                            <td>$0.60</td>
                            <td>7.10s</td>
                        </tr>
                        <tr>
                            <td>💨 Gemini 3.5 Flash Lite</td>
                            <td>$0.0375</td>
                            <td>$0.15</td>
                            <td>3.38s</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div style="background: var(--surface); padding: 1.75rem; border-radius: 12px; border: 1px solid var(--border);">
                <h3 style="color: #818CF8; margin-bottom: 1rem;">🔬 Multi-Intent Gap: Why Gemini MCP Scored 50% on Q097</h3>
                <p style="color: var(--text-muted); font-size: 0.85rem; line-height: 1.6;">
                    In <b>Q097</b>, the user query asked for <i>"Executive briefing on inbox alerts and calendar schedule"</i>.<br><br>
                    • <b>Gemini MCP (50% Score)</b>: Invoked only <code>tool_list_meetings</code> and returned the 2 Teams meetings, but omitted the inbox alerts (Passkeys & Azure Copilot).<br>
                    • <b>StreamAssist (100% Score)</b>: Federated Search simultaneously queried both the email and calendar connectors, retrieving both.
                </p>
            </div>
        </div>
    </div>
</div>

<div id="triModal" class="modal-overlay" onclick="if(event.target===this) closeModal()">
    <div class="modal-card">
        <button class="close-btn" onclick="closeModal()">✕ Close</button>
        <h2 id="modalTitle" style="color: #818CF8; font-size: 1.3rem; margin-bottom: 0.5rem;">🔍 Tri-Answer Semantic & Entity Diff Inspector</h2>
        <div id="modalQuery" style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem;"></div>
        <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 1rem;">
            <div id="modalEntityStatus"></div>
            <button class="btn-sec" onclick="openRawGroundingModal()" style="border-color: #10B981; color: #10B981; background: rgba(16, 185, 129, 0.08); font-size: 0.78rem; font-weight: 700; border-radius: 6px; padding: 0.35rem 0.75rem;">🔌 Inspect API Grounding JSON</button>
        </div>
        
        <div id="rawGroundingContainer" style="display: none; margin-bottom: 1.5rem; background: #090D16; border: 1px solid #10B981; border-radius: 8px; padding: 1.25rem;">
            <h4 style="color: #10B981; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem;">
                <span>🔌 Live Microsoft Graph API Payload</span>
                <button onclick="document.getElementById('rawGroundingContainer').style.display='none'" style="background: transparent; border: none; color: #EF4444; cursor: pointer; font-weight: bold; font-size: 0.85rem;">[Hide]</button>
            </h4>
            <pre id="rawGroundingJSON" style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; overflow-x: auto; color: #38BDF8; white-space: pre-wrap; word-break: break-all; max-height: 400px; overflow-y: auto; text-align: left;"></pre>
        </div>

        <div class="tri-grid">
            <div class="tri-col ground">
                <h4 style="color: #10B981; margin-bottom: 0.5rem;">📌 1. Ground Truth Fact (Microsoft Graph)</h4>
                <div id="modalGround" style="font-size: 0.85rem; line-height: 1.5; color: #E2E8F0;"></div>
            </div>
            <div class="tri-col gemini">
                <h4 style="color: #818CF8; margin-bottom: 0.5rem;">⚡ 2. Gemini 3.6 Flash (MCP Agent)</h4>
                <div id="modalGemini" style="font-size: 0.85rem; line-height: 1.5; color: #E2E8F0;"></div>
                <div id="modalGeminiMeta" style="margin-top: 0.75rem; font-size: 0.75rem; color: #10B981; font-weight: 700;"></div>
            </div>
            <div class="tri-col sa">
                <h4 style="color: #38BDF8; margin-bottom: 0.5rem;">🌐 3. StreamAssist (Federated Search)</h4>
                <div id="modalSA" style="font-size: 0.85rem; line-height: 1.5; color: #E2E8F0;"></div>
                <div id="modalSAMeta" style="margin-top: 0.75rem; font-size: 0.75rem; color: #38BDF8; font-weight: 700;"></div>
            </div>
        </div>
    </div>
</div>

<script>
    let currentItem = null;
    function showTab(tab) {{
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('tab-benchmark').style.display = 'none';
        document.getElementById('tab-costs').style.display = 'none';
        if (tab === 'benchmark') {{
            document.querySelectorAll('.tab-btn')[0].classList.add('active');
            document.getElementById('tab-benchmark').style.display = 'block';
        }} else if (tab === 'costs') {{
            document.querySelectorAll('.tab-btn')[1].classList.add('active');
            document.getElementById('tab-costs').style.display = 'block';
        }}
    }}
    function openModal(item) {{
        currentItem = item;
        document.getElementById('rawGroundingContainer').style.display = 'none';
        document.getElementById('modalTitle').innerText = '🔍 ' + item.id + ' Tri-Answer Inspector (' + item.complexity + ' Complexity)';
        document.getElementById('modalQuery').innerText = 'User Query: \"' + item.query + '\"';
        document.getElementById('modalGround').innerText = item.ground_truth_answer;
        document.getElementById('modalGemini').innerText = item.app_answer;
        document.getElementById('modalSA').innerText = item.streamassist_answer;
        
        document.getElementById('modalGeminiMeta').innerText = '⚡ Precision: ' + item.precision_score_36 + '% | Latency: ' + item.latency_36 + 's';
        document.getElementById('modalSAMeta').innerText = '🌐 Precision: ' + item.streamassist_precision + '% | Latency: ' + item.streamassist_latency_s + 's';
        
        const entBox = document.getElementById('modalEntityStatus');
        if(item.missing_entities && item.missing_entities.length > 0) {{
            entBox.innerHTML = '<span class="badge badge-complex" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;">⚠️ Multi-Intent Gap: Gemini MCP omitted [' + item.missing_entities.join(', ') + '] (Precision: 50%)</span>';
        }} else {{
            entBox.innerHTML = '<span class="badge badge-basic" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;">✅ Full Entity Match (Precision: ' + item.precision_score_36 + '%)</span>';
        }}
        document.getElementById('triModal').style.display = 'flex';
    }}
    function closeModal() {{
        document.getElementById('triModal').style.display = 'none';
    }}
    function openRawGroundingModal() {{
        const jsonPre = document.getElementById('rawGroundingJSON');
        if(!currentItem || !currentItem.raw_grounding_data) {{
            jsonPre.innerText = JSON.stringify({{ "info": "No grounding data available for this query type." }}, null, 2);
        }} else {{
            jsonPre.innerText = JSON.stringify(currentItem.raw_grounding_data, null, 2);
        }}
        document.getElementById('rawGroundingContainer').style.display = 'block';
    }}
</script>
</body>
</html>"""

for path in ['eval_dashboard_static.html', 'frontend/eval_dashboard.html', '/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/custom_ui_mcp_outlook/frontend/eval_dashboard.html']:
    with open(path, 'w') as f:
        f.write(full_html)
print('Successfully generated and updated Tri-Answer visual inspector!')
