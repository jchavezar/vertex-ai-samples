# -*- coding: utf-8 -*-
"""Square M.3: Project Babel: Multicultural Hispanic Homebuyer Studio (Familia Morales)
Visual Design: Warm Sunlit Terracotta & Artisanal Community Homeownership Portal
(#FFFBF5 warm sunlit stucco cream, #C2410C warm terracotta, #047857 emerald trust green,
#1E293B warm charcoal, Fraunces expressive serif + Plus Jakarta Sans + IBM Plex Mono).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_m_3(auth_token: str) -> str:
    code = "M.3"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[M.3] Project Babel: Multicultural Hispanic Homebuyer Studio | Familia Morales Concierge</title>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;0,9..144,800;1,9..144,500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --stucco-cream: #FFFBF5;
      --sand-panel: #FBF3E8;
      --terracotta: #C2410C;
      --terracotta-soft: #FFEDD5;
      --emerald-trust: #047857;
      --emerald-soft: #ECFDF5;
      --warm-charcoal: #1E293B;
      --warm-muted: #64748B;
      --clay-border: #E7D8C5;
      --card-white: #FFFFFF;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--stucco-cream);
      color: var(--warm-charcoal);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 96px;
    }}
    .serif-warm {{ font-family: 'Fraunces', Georgia, serif; }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Warm Sunlit Terracotta Community Portal Header */
    .babel-header {{
      background: var(--sand-panel);
      border-top: 4px solid var(--terracotta);
      border-bottom: 1.5px solid var(--clay-border);
      padding: 18px 28px;
    }}
    .babel-header-inner {{
      max-width: 1540px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .community-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--terracotta-soft);
      border: 1px solid #FDBA74;
      color: var(--terracotta);
      font-size: 11.5px;
      font-weight: 800;
      padding: 4px 12px;
      border-radius: 999px;
    }}
    .babel-select-box {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--card-white);
      border: 1.5px solid var(--clay-border);
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }}
    .babel-select-box select {{
      background: transparent;
      color: var(--terracotta);
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}

    /* Main Community Studio Grid */
    .babel-grid {{
      max-width: 1540px;
      margin: 24px auto;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 430px 1fr;
      gap: 24px;
      align-items: start;
    }}
    @media (max-width: 1120px) {{
      .babel-grid {{ grid-template-columns: 1fr; }}
    }}

    .portal-card {{
      background: var(--card-white);
      border: 1.5px solid var(--clay-border);
      border-radius: 20px;
      padding: 24px;
      box-shadow: 0 10px 28px rgba(194, 65, 12, 0.05);
    }}

    /* Family Co-Borrower Sliders */
    .slider-group {{
      background: var(--stucco-cream);
      border: 1px solid var(--clay-border);
      border-radius: 14px;
      padding: 13px 15px;
      margin-bottom: 12px;
    }}
    .slider-label-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12.5px;
      font-weight: 700;
      margin-bottom: 6px;
    }}
    input[type="range"] {{
      width: 100%;
      accent-color: var(--terracotta);
      cursor: pointer;
    }}

    /* Spanish Audio Button */
    .es-audio-btn {{
      width: 100%;
      background: var(--terracotta);
      color: #FFFFFF;
      border: none;
      border-radius: 14px;
      padding: 14px 16px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 13.5px;
      font-weight: 800;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 6px 18px rgba(194, 65, 12, 0.24);
      transition: transform 0.1s, opacity 0.15s;
    }}
    .es-audio-btn:hover {{ opacity: 0.95; }}

    /* Side-by-Side Cultural Glossary Cards */
    .glossary-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin-top: 14px;
    }}
    @media (max-width: 960px) {{
      .glossary-grid {{ grid-template-columns: 1fr; }}
    }}
    .glossary-card {{
      background: var(--stucco-cream);
      border: 1.5px solid var(--clay-border);
      border-top: 4px solid var(--terracotta);
      border-radius: 14px;
      padding: 16px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .glossary-card:hover, .glossary-card.active {{
      background: var(--terracotta-soft);
      border-color: var(--terracotta);
      box-shadow: 0 6px 16px rgba(194, 65, 12, 0.10);
    }}

    /* Qualification Summary Strip */
    .qual-strip {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 20px;
    }}
    @media (max-width: 900px) {{
      .qual-strip {{ grid-template-columns: 1fr 1fr; }}
    }}
    .qual-tile {{
      background: var(--stucco-cream);
      border: 1px solid var(--clay-border);
      border-radius: 14px;
      padding: 14px;
    }}
  </style>
</head>
<body>

  <!-- WARM SUNLIT TERRACOTTA & ARTISANAL COMMUNITY HOMEOWNERSHIP HEADER -->
  <header class="babel-header">
    <div class="babel-header-inner">
      <div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap;">
          <span class="community-pill">🏡 BIENVENIDOS A CASA • USE CASE M.3</span>
          <span class="mono" style="font-size:11px;color:var(--emerald-trust);font-weight:700;">
            FANNIE MAE HOMEREADY + ITIN &amp; MULTI-GENERATIONAL INCOME STUDIO
          </span>
        </div>
        <h1 class="serif-warm" style="font-size:25px;font-weight:800;color:var(--warm-charcoal);">
          Project Babel: Multicultural Hispanic Homebuyer Studio — Familia Morales
        </h1>
      </div>

      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
        <div class="babel-select-box">
          <span style="color:var(--warm-muted);">Model:</span>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" aria-label="Select Gemini Model">
            <option value="gemini-4-argon">gemini-4-argon (Frontier Cultural Transcreation)</option>
            <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Low-Latency Bilingual Concierge)</option>
          </select>
        </div>
        <button onclick="window.runLiveVertexAI()" style="background:var(--emerald-trust);color:#FFFFFF;border:none;padding:9px 16px;border-radius:999px;font-size:12.5px;font-weight:700;cursor:pointer;">
          Actualizar Pre-Aprobación Familiar
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN BILINGUAL CONCIERGE WORKSPACE -->
  <main class="babel-grid">

    <!-- LEFT COLUMN: FAMILIA MORALES MULTI-GENERATIONAL INCOME & DOWN PAYMENT CALCULATOR -->
    <aside class="portal-card">
      <div style="border-bottom:1px solid var(--clay-border);padding-bottom:12px;margin-bottom:14px;">
        <span class="mono" style="font-size:11px;font-weight:700;color:var(--terracotta);text-transform:uppercase;">
          PERFIL FAMILIAR • SAN ANTONIO, TX
        </span>
        <h2 class="serif-warm" style="font-size:20px;font-weight:700;margin-top:2px;">
          Familia Morales Multi-Generational Qualification
        </h2>
        <p style="font-size:12.5px;color:var(--warm-muted);margin-top:4px;">
          Combines W-2 income, 1099/ITIN family business cash flow, and multi-generational co-borrower contributions under Fannie Mae HomeReady.
        </p>
      </div>

      <div class="slider-group">
        <div class="slider-label-row">
          <span>Target Home Price (Precio de la Casa)</span>
          <span class="mono" id="lbl-babel-price" style="color:var(--warm-charcoal);font-weight:700;">$365,000</span>
        </div>
        <input type="range" id="sld-babel-price" min="240000" max="550000" step="5000" value="365000" oninput="window.updateFamiliaMoralesMath()">
      </div>

      <div class="slider-group">
        <div class="slider-label-row">
          <span>Carlos &amp; Elena Primary Income (W-2 + 1099/ITIN)</span>
          <span class="mono" id="lbl-babel-prim" style="color:var(--terracotta);font-weight:700;">$7,400 / mes</span>
        </div>
        <input type="range" id="sld-babel-prim" min="4500" max="12500" step="200" value="7400" oninput="window.updateFamiliaMoralesMath()">
      </div>

      <div class="slider-group">
        <div class="slider-label-row">
          <span>Abuela Rosa &amp; Co-Borrower Income (Multi-Generational)</span>
          <span class="mono" id="lbl-babel-cobor" style="color:var(--emerald-trust);font-weight:700;">+$2,600 / mes</span>
        </div>
        <input type="range" id="sld-babel-cobor" min="0" max="5500" step="200" value="2600" oninput="window.updateFamiliaMoralesMath()">
      </div>

      <div class="slider-group">
        <div class="slider-label-row">
          <span>Family Down Payment &amp; Gift (Enganche + Regalo Familiar)</span>
          <span class="mono" id="lbl-babel-down" style="color:var(--warm-charcoal);font-weight:700;">5.0% ($18,250)</span>
        </div>
        <input type="range" id="sld-babel-down" min="3" max="20" step="1" value="5" oninput="window.updateFamiliaMoralesMath()">
      </div>

      <!-- Warm Spanish Audio Explanation Button -->
      <div style="display:flex;flex-direction:column;gap:8px;margin-top:14px;">
        <button id="btn-babel-es-audio" class="es-audio-btn" onclick="window.playBabelSpanishExplanation(this)">
          🔊 Escuchar Explicación en Español (Gemini 3.8 Live · Aoede HD)
        </button>
        <button onclick="window.stopAllLiveAudio && window.stopAllLiveAudio()" style="background:transparent;border:1px solid var(--clay-border);color:var(--warm-muted);padding:7px;border-radius:10px;font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;cursor:pointer;">
          ✋ Detener / Interrumpir Audio (0ms Barge-In)
        </button>
      </div>
    </aside>

    <!-- RIGHT COLUMN: BILINGUAL PRE-APPROVAL BREAKDOWN & SIDE-BY-SIDE CULTURAL GLOSSARY -->
    <section style="display:flex;flex-direction:column;gap:20px;">
      <div class="portal-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:18px;padding-bottom:14px;border-bottom:1px solid var(--clay-border);">
          <div>
            <span class="mono" style="font-size:11px;font-weight:700;color:var(--terracotta);text-transform:uppercase;">
              RESUMEN DE CALIFICACIÓN • BILINGUAL TRANSPARENCY SHEET
            </span>
            <h2 class="serif-warm" style="font-size:22px;font-weight:800;color:var(--warm-charcoal);margin-top:2px;">
              Pre-Aprobación Hipotecaria para la Familia Morales
            </h2>
          </div>
          <div id="babel-status-pill" style="background:var(--emerald-soft);border:1.5px solid var(--emerald-trust);color:var(--emerald-trust);padding:6px 14px;border-radius:999px;font-size:12px;font-weight:800;">
            ✓ APROBADO • HomeReady 6.125% (Sin LLPA Penalty)
          </div>
        </div>

        <!-- 4 Qualification KPI Tiles -->
        <div class="qual-strip">
          <div class="qual-tile">
            <div class="mono" style="font-size:10.5px;color:var(--warm-muted);">INGRESO FAMILIAR TOTAL</div>
            <div class="serif-warm" id="kpi-babel-inc" style="font-size:22px;font-weight:800;color:var(--warm-charcoal);margin-top:3px;">$10,000 / mes</div>
            <div style="font-size:11.5px;color:var(--emerald-trust);font-weight:600;margin-top:2px;">Incluye Co-Deudor Familiar</div>
          </div>
          <div class="qual-tile" style="background:var(--terracotta-soft);border-color:#FDBA74;">
            <div class="mono" style="font-size:10.5px;color:var(--terracotta);">PAGO MENSUAL TOTAL (PITI)</div>
            <div class="serif-warm" id="kpi-babel-piti" style="font-size:22px;font-weight:800;color:var(--terracotta);margin-top:3px;">$2,684 / mes</div>
            <div style="font-size:11.5px;color:var(--warm-charcoal);font-weight:600;margin-top:2px;">Capital, Interés, Impuestos y Seguro</div>
          </div>
          <div class="qual-tile" style="background:var(--emerald-soft);border-color:#6EE7B7;">
            <div class="mono" style="font-size:10.5px;color:var(--emerald-trust);">RELACIÓN DEUDA-INGRESO (DTI)</div>
            <div class="serif-warm" id="kpi-babel-dti" style="font-size:22px;font-weight:800;color:var(--emerald-trust);margin-top:3px;">31.4% DTI</div>
            <div style="font-size:11.5px;color:var(--emerald-trust);font-weight:600;margin-top:2px;">Muy por debajo del límite 45%</div>
          </div>
          <div class="qual-tile">
            <div class="mono" style="font-size:10.5px;color:var(--warm-muted);">EFECTIVO PARA EL CIERRE</div>
            <div class="serif-warm" id="kpi-babel-cash" style="font-size:22px;font-weight:800;color:var(--warm-charcoal);margin-top:3px;">$20,450</div>
            <div style="font-size:11.5px;color:var(--warm-muted);margin-top:2px;">Incluye Crédito HomeReady $2,500</div>
          </div>
        </div>

        <!-- Side-by-Side Cultural Glossary (Not Literal Machine Translation) -->
        <div>
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <h3 class="serif-warm" style="font-size:18px;font-weight:700;color:var(--warm-charcoal);">
              Glosario Cultural Hipotecario (Side-by-Side English &amp; Natural Family Spanish)
            </h3>
            <span class="mono" style="font-size:11px;color:var(--terracotta);font-weight:700;">
              Haz clic en cualquier término para escucharlo en voz alta
            </span>
          </div>

          <div class="glossary-grid">
            <div class="glossary-card active" onclick="window.selectGlossaryTerm('escrow', this)">
              <div class="mono" style="font-size:10.5px;color:var(--terracotta);font-weight:700;">TERM 01 • TAX &amp; INSURANCE PROTECTION</div>
              <div class="serif-warm" style="font-size:16px;font-weight:700;margin-top:4px;color:var(--warm-charcoal);">
                Escrow / Cuenta de Depósito en Garantía
              </div>
              <p style="font-size:12px;color:var(--warm-muted);margin-top:6px;line-height:1.45;">
                <strong>English:</strong> Dedicated reserve account that collects 1/12th of property taxes and hazard insurance monthly.
              </p>
              <p style="font-size:12px;color:var(--warm-charcoal);margin-top:6px;line-height:1.45;">
                <strong>Español Natural:</strong> Su "alcancía protegida" dentro de la hipoteca para que los impuestos del condado y el seguro de su casa se paguen solos y sin sorpresas a fin de año.
              </p>
            </div>

            <div class="glossary-card" onclick="window.selectGlossaryTerm('cash', this)">
              <div class="mono" style="font-size:10.5px;color:var(--terracotta);font-weight:700;">TERM 02 • CLOSING TABLE FUNDS</div>
              <div class="serif-warm" style="font-size:16px;font-weight:700;margin-top:4px;color:var(--warm-charcoal);">
                Cash to Close / Efectivo para el Cierre
              </div>
              <p style="font-size:12px;color:var(--warm-muted);margin-top:6px;line-height:1.45;">
                <strong>English:</strong> Total net wire due on signing day (down payment + closing costs minus earnest money &amp; lender credits).
              </p>
              <p style="font-size:12px;color:var(--warm-charcoal);margin-top:6px;line-height:1.45;">
                <strong>Español Natural:</strong> El monto exacto que la familia lleva el día de la firma para recibir las llaves—sumando su enganche y gastos de escritura, menos su depósito inicial y el crédito de $2,500 de Rocket.
              </p>
            </div>

            <div class="glossary-card" onclick="window.selectGlossaryTerm('pmi', this)">
              <div class="mono" style="font-size:10.5px;color:var(--terracotta);font-weight:700;">TERM 03 • LOW DOWN PAYMENT INSURANCE</div>
              <div class="serif-warm" style="font-size:16px;font-weight:700;margin-top:4px;color:var(--warm-charcoal);">
                PMI / Seguro Hipotecario Privado
              </div>
              <p style="font-size:12px;color:var(--warm-muted);margin-top:6px;line-height:1.45;">
                <strong>English:</strong> Reduced HomeReady mortgage insurance required above 80% LTV; automatically drops off at 78% LTV.
              </p>
              <p style="font-size:12px;color:var(--warm-charcoal);margin-top:6px;line-height:1.45;">
                <strong>Español Natural:</strong> El seguro temporal que les permite comprar hoy con solo 3% o 5% de enganche, y que se elimina automáticamente cuando su casa alcanza el 22% de plusvalía.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Bilingual Family Concierge Advisory Note -->
      <div class="portal-card" style="background:var(--sand-panel);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:8px;">
          <span class="mono" style="font-size:11.5px;font-weight:700;color:var(--terracotta);">
            CONSEJERO FAMILIAR BILINGÜE • GEMINI 3.8 LIVE (AOEDE HD)
          </span>
          <span class="mono" style="font-size:11px;color:var(--emerald-trust);font-weight:700;">
            ECOA Regulation B Compliant • Cultural Transcreation Active
          </span>
        </div>
        <div id="babel-spoken-box" class="serif-warm" style="font-size:15.5px;line-height:1.65;color:var(--warm-charcoal);">
          "¡Felicidades, Familia Morales! Al combinar el ingreso de Carlos y Elena ($7,400 al mes) con el aporte familiar de Abuela Rosa ($2,600 al mes), su ingreso calificado sube a $10,000 mensuales. Eso reduce su relación deuda-ingreso a un saludable 31.4% y activa el crédito HomeReady de $2,500 para cubrir sus gastos de cierre."
        </div>
      </div>
    </section>

  </main>

  <script>
    let activeGlossaryKey = 'escrow';

    const GLOSSARY_SPEECH = {{
      escrow: "¡Felicidades, Familia Morales! La Cuenta de Depósito en Garantía, o Escrow, funciona como una alcancía protegida dentro de su pago mensual. Cada mes guardamos una doceava parte de los impuestos de propiedad y del seguro de su hogar, para que Rocket los pague puntualmente por ustedes sin sorpresas a fin de año.",
      cash: "El Efectivo para el Cierre es el monto final que necesitan el día de la firma para recibir las llaves de su casa. Incluye su enganche del cinco por ciento más los gastos de cierre, pero le restamos automáticamente el crédito familiar de dos mil quinientos dólares del programa HomeReady.",
      pmi: "El Seguro Hipotecario Privado, o P-M-I, es lo que les permite mudarse a su casa hoy mismo con solo cinco por ciento de enganche en lugar de esperar años para ahorrar el veinte por ciento. Además, por ley federal, este seguro se cancela automáticamente cuando acumulan veintidós por ciento de capital en su hogar."
    }};

    function calcMonthlyPI(principal, annualRatePct, months) {{
      const r = (annualRatePct / 100.0) / 12.0;
      return principal * (r * Math.pow(1 + r, months)) / (Math.pow(1 + r, months) - 1);
    }}

    window.updateFamiliaMoralesMath = async function() {{
      const price = parseFloat(document.getElementById('sld-babel-price').value || 365000);
      const primInc = parseFloat(document.getElementById('sld-babel-prim').value || 7400);
      const coborInc = parseFloat(document.getElementById('sld-babel-cobor').value || 2600);
      const downPct = parseFloat(document.getElementById('sld-babel-down').value || 5);

      const totalInc = primInc + coborInc;
      const downUsd = Math.round(price * (downPct / 100.0));
      const loan = price - downUsd;
      const pi = calcMonthlyPI(loan, 6.125, 360);
      const taxIns = Math.round((price * 0.0155) / 12.0 + 135);
      const pmi = downPct < 20 ? Math.round((loan * 0.0042) / 12.0) : 0;
      const piti = Math.round(pi + taxIns + pmi);
      const dti = ((piti + 455) / totalInc * 100).toFixed(1);
      const cashClose = Math.max(0, downUsd + 4700 - 2500);

      document.getElementById('lbl-babel-price').innerText = '$' + price.toLocaleString();
      document.getElementById('lbl-babel-prim').innerText = '$' + primInc.toLocaleString() + ' / mes';
      document.getElementById('lbl-babel-cobor').innerText = '+$' + coborInc.toLocaleString() + ' / mes';
      document.getElementById('lbl-babel-down').innerText = `${{downPct.toFixed(1)}}% ($${{downUsd.toLocaleString()}})`;

      document.getElementById('kpi-babel-inc').innerText = '$' + totalInc.toLocaleString() + ' / mes';
      document.getElementById('kpi-babel-piti').innerText = '$' + piti.toLocaleString() + ' / mes';
      document.getElementById('kpi-babel-dti').innerText = dti + '% DTI';
      document.getElementById('kpi-babel-cash').innerText = '$' + cashClose.toLocaleString();

      try {{
        await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.3',
            action: 'calc_fha_vs_conv',
            params: {{ price: price }}
          }})
        }});
      }} catch (e) {{}}
    }};

    window.selectGlossaryTerm = function(key, cardEl) {{
      activeGlossaryKey = key;
      document.querySelectorAll('.glossary-card').forEach(c => c.classList.remove('active'));
      if (cardEl) cardEl.classList.add('active');
      const txt = GLOSSARY_SPEECH[key] || GLOSSARY_SPEECH.escrow;
      document.getElementById('babel-spoken-box').innerText = '"' + txt + '"';
      const btn = document.getElementById('btn-babel-es-audio');
      if (window.playLiveCallClip) {{
        window.playLiveCallClip(txt, "Aoede", "Consejera Hipotecaria Bilingüe (Project Babel)", btn);
      }}
    }};

    window.playBabelSpanishExplanation = function(btnEl) {{
      const price = parseFloat(document.getElementById('sld-babel-price').value || 365000);
      const totalInc = document.getElementById('kpi-babel-inc').innerText;
      const piti = document.getElementById('kpi-babel-piti').innerText;
      const cash = document.getElementById('kpi-babel-cash').innerText;
      const speech =
        `¡Hola, Familia Morales! Con su ingreso familiar combinado de ${{totalInc}} para su casa de $${{price.toLocaleString()}} dólares, su pago mensual total queda en ${{piti}}, incluyendo impuestos y seguro en su Cuenta de Depósito en Garantía. Además, con el crédito de dos mil quinientos dólares de HomeReady, su efectivo para el cierre es de solo ${{cash}}.`;
      document.getElementById('babel-spoken-box').innerText = '"' + speech + '"';
      if (window.playLiveCallClip) {{
        window.playLiveCallClip(speech, "Aoede", "Consejera Hipotecaria Bilingüe (Project Babel)", btnEl);
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const price = document.getElementById('sld-babel-price').value || 365000;
      const inc = document.getElementById('kpi-babel-inc').innerText;
      const piti = document.getElementById('kpi-babel-piti').innerText;
      const box = document.getElementById('babel-spoken-box');
      box.innerHTML = `<em>Generando explicación cultural bilingüe con <strong>${{model}}</strong>...</em>`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.3',
            model: model,
            user_input: `Provide a warm bilingual English and natural Family Spanish mortgage qualification summary for Familia Morales buying a $${{price}} home with ${{inc}} multi-generational income and ${{piti}} PITI payment.`,
            params: {{ price: price }}
          }})
        }});
        const data = await res.json();
        const textOut = (data.vertex && data.vertex.response_markdown) || data.output || GLOSSARY_SPEECH[activeGlossaryKey];
        box.innerHTML = `<strong>[${{data.model_used || model}}]:</strong> ${{textOut}}`;
      }} catch (e) {{
        box.innerText = "Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.updateFamiliaMoralesMath();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
