#!/usr/bin/env python3
"""
inject_feature.py
Feature injection tool for Jetski demos on Libertad Financiera portal.
Allows real-time injection of new business features into predefined semantic slots.
"""

import sys
import argparse
from pathlib import Path

SITE_DIR = Path(__file__).parent / "site"
INDEX_FILE = SITE_DIR / "index.html"
BACKUP_FILE = SITE_DIR / "index.html.original"

MODERN_HERO_AND_SIMULATOR_HTML = r"""
<!-- Modern Fintech Hero Section & Live Simulator -->
<div id="jetski-modern-hero" style="background: linear-gradient(135deg, #001f52 0%, #002c72 55%, #00439c 100%); color: white; padding: 56px 24px 64px 24px; position: relative; overflow: hidden; font-family: 'defaultFont', sans-serif; box-shadow: 0 10px 30px rgba(0, 44, 114, 0.15);">
  <!-- Decorative Glows -->
  <div style="position: absolute; top: -120px; right: -80px; width: 450px; height: 450px; background: radial-gradient(circle, rgba(251,186,0,0.18) 0%, rgba(0,0,0,0) 70%); border-radius: 50%; pointer-events: none;"></div>
  <div style="position: absolute; bottom: -100px; left: 10%; width: 400px; height: 400px; background: radial-gradient(circle, rgba(0,163,255,0.18) 0%, rgba(0,0,0,0) 70%); border-radius: 50%; pointer-events: none;"></div>

  <div style="max-width: 1350px; margin: 0 auto; display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 48px; align-items: center; position: relative; z-index: 2;">
    
    <!-- Left Column: Value Proposition & Highlights -->
    <div>
      <!-- Pill Badge -->
      <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.12); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.22); padding: 7px 16px; border-radius: 9999px; margin-bottom: 22px;">
        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #fbba00; box-shadow: 0 0 10px #fbba00;"></span>
        <span style="font-size: 12px; font-weight: 800; letter-spacing: 0.6px; color: #fbba00; text-transform: uppercase;">Experiencia Digital 2026</span>
        <span style="font-size: 12px; color: #e2e8f0;">• 100% en Línea y Transparente</span>
      </div>

      <!-- Main Headline -->
      <h1 style="font-size: 48px; font-weight: 800; line-height: 1.15; margin: 0 0 18px 0; letter-spacing: -0.8px; color: #ffffff;">
        Tu dinero crece con <br/><span style="background: linear-gradient(90deg, #fbba00 0%, #ffe082 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">certeza, rapidez y libertad</span>.
      </h1>

      <p style="font-size: 18px; line-height: 1.6; color: #cbd5e1; margin: 0 0 32px 0; max-width: 580px;">
        Evolucionamos la banca tradicional hacia una experiencia digital ágil. Invierte con hasta <b>14.00% de rendimiento anual garantizado</b> o accede a créditos preaprobados sin trámites engorrosos.
      </p>

      <!-- Trust Pillars / Metrics Grid -->
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px; padding-top: 22px; border-top: 1px solid rgba(255,255,255,0.15);">
        <div>
          <div style="font-size: 28px; font-weight: 800; color: #fbba00; line-height: 1;">14.00%</div>
          <div style="font-size: 12.5px; color: #94a3b8; margin-top: 6px;">Rendimiento Anual Fijo</div>
        </div>
        <div>
          <div style="font-size: 28px; font-weight: 800; color: #38bdf8; line-height: 1;">&lt; 24 hrs</div>
          <div style="font-size: 12.5px; color: #94a3b8; margin-top: 6px;">Aprobación Digital</div>
        </div>
        <div>
          <div style="font-size: 28px; font-weight: 800; color: #4ade80; line-height: 1;">65 Años</div>
          <div style="font-size: 12.5px; color: #94a3b8; margin-top: 6px;">Solidez Financiera</div>
        </div>
      </div>

      <!-- Regulatory Badges -->
      <div style="display: flex; align-items: center; gap: 24px; font-size: 12.5px; color: rgba(255,255,255,0.7);">
        <span style="display: flex; align-items: center; gap: 8px;">
          <svg width="16" height="16" fill="#fbba00" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/></svg>
          Regulado por CNBV y CONDUSEF
        </span>
        <span style="display: flex; align-items: center; gap: 8px;">
          <svg width="16" height="16" fill="#38bdf8" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          Calificación HR Ratings AA+
        </span>
      </div>
    </div>

    <!-- Right Column: Interactive Financial Simulator Card (Glassmorphism) -->
    <div style="background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.7); border-radius: 24px; padding: 32px; box-shadow: 0 25px 60px -10px rgba(0, 20, 60, 0.5); color: #0f172a;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px;">
        <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.6px; color: #0033a0; background: #e0f2fe; padding: 4px 10px; border-radius: 6px;">Simulador Interactivo</span>
        <div style="display: flex; gap: 4px; background: #f1f5f9; padding: 4px; border-radius: 12px; border: 1px solid #e2e8f0;">
          <button type="button" id="sim-btn-inv" onclick="setSimulatorMode('inv')" style="background: #002c72; color: white; border: none; font-size: 12px; font-weight: 700; padding: 7px 16px; border-radius: 8px; cursor: pointer; transition: all 0.2s;">Inversión</button>
          <button type="button" id="sim-btn-cred" onclick="setSimulatorMode('cred')" style="background: transparent; color: #64748b; border: none; font-size: 12px; font-weight: 700; padding: 7px 16px; border-radius: 8px; cursor: pointer; transition: all 0.2s;">Crédito</button>
        </div>
      </div>

      <!-- Amount Slider -->
      <div style="margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px;">
          <label id="sim-label-amount" style="font-size: 13.5px; font-weight: 700; color: #475569;">¿Cuánto deseas invertir?</label>
          <span id="sim-display-amount" style="font-size: 28px; font-weight: 800; color: #002c72; letter-spacing: -0.5px;">$50,000 MXN</span>
        </div>
        <input type="range" id="sim-slider" min="5000" max="300000" step="5000" value="50000" oninput="updateSimulator(this.value)" style="width: 100%; height: 8px; border-radius: 4px; accent-color: #0033a0; cursor: pointer; background: #cbd5e1;" />
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; margin-top: 8px; font-weight: 600;">
          <span>$5,000</span>
          <span>$150,000</span>
          <span>$300,000</span>
        </div>
      </div>

      <!-- Result Card -->
      <div style="background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%); border: 1.5px solid #e2e8f0; border-radius: 18px; padding: 22px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0;">
          <span style="font-size: 12.5px; color: #64748b;" id="sim-metric-1-label">Tasa Anual Fija Garantizada</span>
          <span style="font-size: 16px; font-weight: 800; color: #16a34a;" id="sim-metric-1-val">14.00%</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0;">
          <span style="font-size: 12.5px; color: #64748b;" id="sim-metric-2-label">Plazo sugerido</span>
          <span style="font-size: 14px; font-weight: 700; color: #002c72;" id="sim-metric-2-val">360 días</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 14px; font-weight: 700; color: #002c72;" id="sim-metric-total-label">Tu Ganancia Neta Estimada:</span>
          <span style="font-size: 24px; font-weight: 900; color: #0033a0;" id="sim-metric-total-val">+$7,000 MXN</span>
        </div>
      </div>

      <!-- CTA Button -->
      <button type="button" id="sim-cta-btn" onclick="alert('¡Iniciando solicitud digital inmediata en Libertad Financiera!')" style="width: 100%; background: #fbba00; color: #002c72; font-size: 15px; font-weight: 800; border: none; padding: 15px 20px; border-radius: 12px; cursor: pointer; box-shadow: 0 6px 18px rgba(251,186,0,0.45); transition: transform 0.15s ease, background 0.15s ease; display: flex; align-items: center; justify-content: center; gap: 8px;">
        <span id="sim-cta-text">Abrir Inversión Digital en 3 Minutos</span> <span style="font-size: 18px;">➔</span>
      </button>
      <div style="text-align: center; font-size: 11px; color: #94a3b8; margin-top: 12px;">
        Sin papeleo físico • Apertura 100% digital desde tu celular
      </div>
    </div>

  </div>
</div>

<!-- Modern Quick Products Bar -->
<div id="jetski-modern-products" style="background: #ffffff; padding: 28px 24px 36px 24px; border-bottom: 1px solid #e2e8f0; font-family: 'defaultFont', sans-serif;">
  <div style="max-width: 1350px; margin: 0 auto;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <div>
        <span style="font-size: 11px; font-weight: 800; color: #0033a0; text-transform: uppercase; letter-spacing: 0.6px;">Accesos Directos</span>
        <h2 style="font-size: 22px; font-weight: 800; color: #002c72; margin: 4px 0 0 0;">Soluciones Financieras Destacadas</h2>
      </div>
      <span style="font-size: 13px; color: #64748b;">Selecciona el producto ideal para ti</span>
    </div>

    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px;">
      <!-- Card 1 -->
      <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 22px; transition: all 0.2s; cursor: pointer;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 12px 24px rgba(0,44,114,0.08)';" onmouseout="this.style.transform='none';this.style.boxShadow='none';">
        <div style="width: 44px; height: 44px; background: #e0f2fe; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; margin-bottom: 14px;">💰</div>
        <div style="font-weight: 800; color: #002c72; font-size: 16px; margin-bottom: 6px;">Inversión Plazo Fijo</div>
        <div style="font-size: 12.5px; color: #64748b; line-height: 1.5; margin-bottom: 14px;">Crece tu patrimonio seguro con hasta 14.00% de rendimiento anual.</div>
        <div style="font-size: 12.5px; font-weight: 700; color: #0033a0;">Ver detalles ➔</div>
      </div>

      <!-- Card 2 -->
      <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 22px; transition: all 0.2s; cursor: pointer;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 12px 24px rgba(0,44,114,0.08)';" onmouseout="this.style.transform='none';this.style.boxShadow='none';">
        <div style="width: 44px; height: 44px; background: #fef3c7; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; margin-bottom: 14px;">⚡</div>
        <div style="font-weight: 800; color: #002c72; font-size: 16px; margin-bottom: 6px;">Crédito Personal</div>
        <div style="font-size: 12.5px; color: #64748b; line-height: 1.5; margin-bottom: 14px;">Préstamos desde $5,000 hasta $300,000 con respuesta en menos de 24h.</div>
        <div style="font-size: 12.5px; font-weight: 700; color: #0033a0;">Simular crédito ➔</div>
      </div>

      <!-- Card 3 -->
      <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 22px; transition: all 0.2s; cursor: pointer;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 12px 24px rgba(0,44,114,0.08)';" onmouseout="this.style.transform='none';this.style.boxShadow='none';">
        <div style="width: 44px; height: 44px; background: #dcfce7; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; margin-bottom: 14px;">💳</div>
        <div style="font-weight: 800; color: #002c72; font-size: 16px; margin-bottom: 6px;">CuentaYa Digital</div>
        <div style="font-size: 12.5px; color: #64748b; line-height: 1.5; margin-bottom: 14px;">Cuenta de débito 100% digital sin saldo mínimo ni comisiones ocultas.</div>
        <div style="font-size: 12.5px; font-weight: 700; color: #0033a0;">Abrir cuenta ➔</div>
      </div>

      <!-- Card 4 -->
      <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 22px; transition: all 0.2s; cursor: pointer;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 12px 24px rgba(0,44,114,0.08)';" onmouseout="this.style.transform='none';this.style.boxShadow='none';">
        <div style="width: 44px; height: 44px; background: #ede9fe; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; margin-bottom: 14px;">🛡️</div>
        <div style="font-weight: 800; color: #002c72; font-size: 16px; margin-bottom: 6px;">Libertad Segura</div>
        <div style="font-size: 12.5px; color: #64748b; line-height: 1.5; margin-bottom: 14px;">Protección médica y de vida para ti y tu familia desde $150 al mes.</div>
        <div style="font-size: 12.5px; font-weight: 700; color: #0033a0;">Conoce planes ➔</div>
      </div>
    </div>
  </div>
</div>

<script>
let simMode = 'inv';
function setSimulatorMode(mode) {
  simMode = mode;
  const btnInv = document.getElementById('sim-btn-inv');
  const btnCred = document.getElementById('sim-btn-cred');
  const lblAmount = document.getElementById('sim-label-amount');
  const slider = document.getElementById('sim-slider');
  const metric1Lbl = document.getElementById('sim-metric-1-label');
  const metric1Val = document.getElementById('sim-metric-1-val');
  const metric2Lbl = document.getElementById('sim-metric-2-label');
  const metric2Val = document.getElementById('sim-metric-2-val');
  const totalLbl = document.getElementById('sim-metric-total-label');
  const ctaText = document.getElementById('sim-cta-text');

  if (mode === 'inv') {
    if(btnInv) { btnInv.style.background = '#002c72'; btnInv.style.color = '#ffffff'; }
    if(btnCred) { btnCred.style.background = 'transparent'; btnCred.style.color = '#64748b'; }
    if(lblAmount) lblAmount.innerText = '¿Cuánto deseas invertir?';
    if(metric1Lbl) metric1Lbl.innerText = 'Tasa Anual Fija Garantizada';
    if(metric1Val) { metric1Val.innerText = '14.00%'; metric1Val.style.color = '#16a34a'; }
    if(metric2Lbl) metric2Lbl.innerText = 'Plazo sugerido';
    if(metric2Val) metric2Val.innerText = '360 días';
    if(totalLbl) totalLbl.innerText = 'Tu Ganancia Neta Estimada:';
    if(ctaText) ctaText.innerText = 'Abrir Inversión Digital en 3 Minutos';
  } else {
    if(btnCred) { btnCred.style.background = '#002c72'; btnCred.style.color = '#ffffff'; }
    if(btnInv) { btnInv.style.background = 'transparent'; btnInv.style.color = '#64748b'; }
    if(lblAmount) lblAmount.innerText = '¿Cuánto crédito necesitas?';
    if(metric1Lbl) metric1Lbl.innerText = 'Tasa Anual Preferencial';
    if(metric1Val) { metric1Val.innerText = 'Desde 18.5%'; metric1Val.style.color = '#0284c7'; }
    if(metric2Lbl) metric2Lbl.innerText = 'Plazo de pago';
    if(metric2Val) metric2Val.innerText = '24 meses fijos';
    if(totalLbl) totalLbl.innerText = 'Tu Pago Mensual Estimado:';
    if(ctaText) ctaText.innerText = 'Solicitar Crédito Preaprobado';
  }
  if(slider) updateSimulator(slider.value);
}

function handleSimulatorCTA() {
  if (simMode === 'cred') {
    if (typeof openMultimodalModal === 'function') {
      openMultimodalModal();
    } else {
      alert('⚡ Para activar la Precalificación Multimodal con Visión AI, ejecuta el Paso 5 en la terminal.');
    }
  } else {
    alert('¡Iniciando apertura de Inversión Digital al 14% en Libertad Financiera!');
  }
}

function updateSimulator(val) {
  const num = parseInt(val, 10);
  const disp = document.getElementById('sim-display-amount');
  const totalVal = document.getElementById('sim-metric-total-val');
  if(disp) disp.innerText = '$' + num.toLocaleString('es-MX') + ' MXN';

  if (simMode === 'inv') {
    const ganancia = Math.round(num * 0.14);
    if(totalVal) {
      totalVal.innerText = '+$' + ganancia.toLocaleString('es-MX') + ' MXN';
      totalVal.style.color = '#0033a0';
    }
  } else {
    const pagoMensual = Math.round((num * 1.25) / 24);
    if(totalVal) {
      totalVal.innerText = '$' + pagoMensual.toLocaleString('es-MX') + ' MXN / mes';
      totalVal.style.color = '#002c72';
    }
  }
}
</script>
"""


AI_ADVISOR_HTML = r"""
<!-- INJECTED_FEATURE: AI_ADVISOR -->
<div id="jetski-advisor-container" style="font-family: 'defaultFont', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <!-- Floating Launcher Button -->
  <div id="jetski-advisor-launcher" onclick="toggleAdvisorChat()" style="position: fixed; bottom: 26px; right: 26px; z-index: 999990; display: flex; align-items: center; gap: 12px; background: linear-gradient(135deg, #001f52 0%, #0033a0 100%); color: #ffffff; padding: 12px 22px; border-radius: 9999px; box-shadow: 0 10px 30px rgba(0, 31, 82, 0.38), 0 0 0 2px rgba(251, 186, 0, 0.45); cursor: pointer; transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1); user-select: none;" onmouseover="this.style.transform='translateY(-3px) scale(1.02)';" onmouseout="this.style.transform='none';">
    <div style="position: relative; width: 32px; height: 32px; background: #fbba00; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 17px; color: #002c72; font-weight: 900; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
      ✦
      <span style="position: absolute; top: -1px; right: -1px; width: 9px; height: 9px; background: #22c55e; border: 2px solid #001f52; border-radius: 50%;"></span>
    </div>
    <div style="text-align: left;">
      <div style="font-size: 13.5px; font-weight: 800; letter-spacing: -0.2px; line-height: 1.2;">Libertad AI Advisor</div>
      <div style="font-size: 10.5px; color: #fbba00; font-weight: 700; letter-spacing: 0.2px;">⚡ Asesor en Vivo • Gemini 3.7 Flash</div>
    </div>
  </div>

  <!-- Floating Chat Window / Drawer -->
  <div id="jetski-advisor-window" style="display: none; position: fixed; bottom: 84px; right: 26px; z-index: 999995; width: 430px; max-width: calc(100vw - 32px); height: 580px; max-height: calc(100vh - 120px); background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(20px); border-radius: 22px; box-shadow: 0 25px 60px -10px rgba(0, 20, 60, 0.45), 0 0 0 1px rgba(226, 232, 240, 0.8); border: 1px solid rgba(255, 255, 255, 0.9); overflow: hidden; flex-direction: column;">
    
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #001f52 0%, #002c72 70%, #00439c 100%); color: white; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.15);">
      <div style="display: flex; align-items: center; gap: 12px;">
        <div style="width: 36px; height: 36px; background: #fbba00; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #002c72; font-weight: 900;">
          ✦
        </div>
        <div>
          <div style="font-weight: 800; font-size: 15px; letter-spacing: -0.2px;">Libertad AI Advisor</div>
          <div style="font-size: 11px; color: #cbd5e1; display: flex; align-items: center; gap: 6px;">
            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #4ade80;"></span>
            <span>Gemini 3.7 Flash • Asesor Financiero</span>
          </div>
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 6px;">
        <button onclick="clearAdvisorChat()" title="Reiniciar chat" style="background: rgba(255,255,255,0.12); border: none; border-radius: 8px; width: 28px; height: 28px; color: white; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 13px;">↺</button>
        <button onclick="toggleAdvisorChat()" title="Cerrar" style="background: rgba(255,255,255,0.12); border: none; border-radius: 8px; width: 28px; height: 28px; color: white; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 18px; line-height: 1;">&times;</button>
      </div>
    </div>

    <!-- Quick Prompt Chips -->
    <div style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; padding: 10px 14px; display: flex; gap: 6px; overflow-x: auto; white-space: nowrap; scrollbar-width: none;">
      <button onclick="sendQuickAdvisorPrompt('¿Cómo funciona la inversión a plazo fijo con 14% de rendimiento?')" style="background: #ffffff; border: 1px solid #cbd5e1; color: #0033a0; font-size: 11px; font-weight: 700; padding: 5px 12px; border-radius: 9999px; cursor: pointer; flex-shrink: 0; transition: all 0.15s ease;">💰 Inversión 14%</button>
      <button onclick="sendQuickAdvisorPrompt('¿Qué necesito para un crédito personal de $50,000 MXN?')" style="background: #ffffff; border: 1px solid #cbd5e1; color: #0033a0; font-size: 11px; font-weight: 700; padding: 5px 12px; border-radius: 9999px; cursor: pointer; flex-shrink: 0; transition: all 0.15s ease;">⚡ Crédito $50,000</button>
      <button onclick="sendQuickAdvisorPrompt('¿Qué requisitos y comisiones tiene CuentaYa Digital?')" style="background: #ffffff; border: 1px solid #cbd5e1; color: #0033a0; font-size: 11px; font-weight: 700; padding: 5px 12px; border-radius: 9999px; cursor: pointer; flex-shrink: 0; transition: all 0.15s ease;">💳 CuentaYa Digital</button>
    </div>

    <!-- Chat Messages Container -->
    <div id="jetski-advisor-messages" style="flex: 1; padding: 16px; overflow-y: auto; background: #ffffff; display: flex; flex-direction: column; gap: 12px; font-size: 13.5px; line-height: 1.55;">
      <!-- Welcome Message -->
      <div style="display: flex; gap: 10px; align-items: flex-start;">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: #002c72; color: #fbba00; font-size: 13px; font-weight: 900; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;">✦</div>
        <div style="background: #f1f5f9; color: #0f172a; padding: 12px 16px; border-radius: 16px 16px 16px 4px; max-width: 86%; border: 1px solid #e2e8f0;">
          ¡Hola! Soy tu <b>Libertad AI Advisor</b> impulsado por <b>Gemini 3.7 Flash</b>. 🤝<br/><br/>
          Estoy listo para asesorarte en tiempo real sobre <b>inversiones garantizadas hasta al 14%</b>, <b>créditos preaprobados</b> o apertura de cuentas digitales. ¿En qué te puedo apoyar hoy?
        </div>
      </div>
    </div>

    <!-- Dynamic Zero-Glitch Auto-Expanding Textarea Input Dock -->
    <div style="padding: 12px 16px; background: #ffffff; border-top: 1px solid #e2e8f0;">
      <div style="display: flex; align-items: flex-end; gap: 8px; background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 16px; padding: 8px 12px; transition: border-color 0.2s ease;" id="advisor-input-container">
        <textarea id="jetski-advisor-input" 
                  rows="1" 
                  placeholder="Escribe tu consulta o pide una simulación..." 
                  style="flex: 1; border: none; background: transparent; outline: none; font-size: 13px; font-family: inherit; resize: none; overflow: hidden; line-height: 1.5; max-height: 140px; padding: 2px 0; color: #0f172a;"
                  oninput="adjustAdvisorHeight(this)"
                  onkeydown="handleAdvisorKey(event)"></textarea>
        <button id="jetski-advisor-send" onclick="sendAdvisorMessage()" style="background: #002c72; color: white; border: none; border-radius: 10px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; transition: background 0.15s ease;">
          ➔
        </button>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px; padding: 0 4px; font-size: 10.5px; color: #94a3b8;">
        <span>Presiona Enter para enviar • Shift+Enter para salto de línea</span>
        <span id="jetski-advisor-latency"></span>
      </div>
    </div>

  </div>
</div>

<script>
function toggleAdvisorChat() {
  const win = document.getElementById('jetski-advisor-window');
  if (!win) return;
  const isHidden = win.style.display === 'none' || !win.style.display;
  win.style.display = isHidden ? 'flex' : 'none';
  if (isHidden) {
    setTimeout(() => {
      const input = document.getElementById('jetski-advisor-input');
      if (input) input.focus();
    }, 100);
  }
}

function clearAdvisorChat() {
  const msgs = document.getElementById('jetski-advisor-messages');
  if (!msgs) return;
  msgs.innerHTML = `
    <div style="display: flex; gap: 10px; align-items: flex-start;">
      <div style="width: 28px; height: 28px; border-radius: 50%; background: #002c72; color: #fbba00; font-size: 13px; font-weight: 900; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;">✦</div>
      <div style="background: #f1f5f9; color: #0f172a; padding: 12px 16px; border-radius: 16px 16px 16px 4px; max-width: 86%; border: 1px solid #e2e8f0;">
        ¡Hola! Soy tu <b>Libertad AI Advisor</b> impulsado por <b>Gemini 3.7 Flash</b>. 🤝<br/><br/>
        ¿En qué tipo de crédito o inversión te gustaría cotizar hoy?
      </div>
    </div>
  `;
}

function sendQuickAdvisorPrompt(text) {
  const input = document.getElementById('jetski-advisor-input');
  if (input) {
    input.value = text;
    sendAdvisorMessage();
  }
}

function adjustAdvisorHeight(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 140) + 'px';
  el.style.overflowY = el.scrollHeight > 140 ? 'auto' : 'hidden';
}

function handleAdvisorKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendAdvisorMessage();
  }
}

async function sendAdvisorMessage() {
  const input = document.getElementById('jetski-advisor-input');
  const msgs = document.getElementById('jetski-advisor-messages');
  const latencyBadge = document.getElementById('jetski-advisor-latency');
  if (!input || !msgs) return;
  const text = input.value.trim();
  if (!text) return;

  // Append user bubble
  msgs.innerHTML += `
    <div style="display: flex; justify-content: flex-end;">
      <div style="background: #002c72; color: #ffffff; padding: 12px 16px; border-radius: 16px 16px 4px 16px; max-width: 80%; box-shadow: 0 4px 12px rgba(0,44,114,0.15);">
        ${escapeAdvisorHtml(text)}
      </div>
    </div>
  `;

  input.value = '';
  input.style.height = 'auto';
  msgs.scrollTop = msgs.scrollHeight;

  // Typing indicator
  const loadId = 'advisor-load-' + Date.now();
  msgs.innerHTML += `
    <div id="${loadId}" style="display: flex; gap: 10px; align-items: flex-start;">
      <div style="width: 28px; height: 28px; border-radius: 50%; background: #002c72; color: #fbba00; font-size: 13px; font-weight: 900; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;">✦</div>
      <div style="background: #f1f5f9; color: #64748b; padding: 12px 16px; border-radius: 16px 16px 16px 4px; max-width: 86%; border: 1px solid #e2e8f0; display: flex; align-items: center; gap: 8px;">
        <span>Pensando con Gemini 3.7 Flash</span>
        <span style="display: inline-flex; gap: 3px;">
          <span style="width: 4px; height: 4px; border-radius: 50%; background: #0033a0; animation: advisorBounce 1s infinite alternate;"></span>
          <span style="width: 4px; height: 4px; border-radius: 50%; background: #0033a0; animation: advisorBounce 1s infinite alternate 0.2s;"></span>
          <span style="width: 4px; height: 4px; border-radius: 50%; background: #0033a0; animation: advisorBounce 1s infinite alternate 0.4s;"></span>
        </span>
      </div>
    </div>
  `;
  msgs.scrollTop = msgs.scrollHeight;

  const t0 = Date.now();
  try {
    const res = await fetch('/api/advisor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    const loadEl = document.getElementById(loadId);
    if (loadEl) loadEl.remove();

    const tTotal = Date.now() - t0;
    if (latencyBadge) {
      latencyBadge.innerText = `⚡ ${data.latency_ms || tTotal}ms (Gemini 3.7 Flash)`;
    }

    const formatted = formatAdvisorReply(data.reply || '');
    msgs.innerHTML += `
      <div style="display: flex; gap: 10px; align-items: flex-start;">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: #002c72; color: #fbba00; font-size: 13px; font-weight: 900; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;">✦</div>
        <div style="background: #f8fafc; color: #0f172a; padding: 14px 18px; border-radius: 16px 16px 16px 4px; max-width: 86%; border: 1.5px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
          ${formatted}
        </div>
      </div>
    `;
    msgs.scrollTop = msgs.scrollHeight;
  } catch(err) {
    const loadEl = document.getElementById(loadId);
    if (loadEl) loadEl.remove();
    msgs.innerHTML += `
      <div style="display: flex; gap: 10px; align-items: flex-start;">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: #ef4444; color: white; font-size: 13px; font-weight: 900; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;">!</div>
        <div style="background: #fef2f2; color: #991b1b; padding: 12px 16px; border-radius: 16px 16px 16px 4px; max-width: 86%; border: 1px solid #fecaca;">
          Lo siento, hubo un problema de conexión temporal con el asesor. Por favor intenta de nuevo.
        </div>
      </div>
    `;
    msgs.scrollTop = msgs.scrollHeight;
  }
}

function escapeAdvisorHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br/>');
}

function formatAdvisorReply(text) {
  let res = text
    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
    .replace(/\*(.*?)\*/g, '<i>$1</i>')
    .replace(/•\s*(.*?)(?=\n|$)/g, '<li style="margin-left: 16px; margin-bottom: 4px;">$1</li>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');
  return res;
}
</script>

<style>
@keyframes advisorBounce {
  0% { transform: translateY(0); }
  100% { transform: translateY(-4px); }
}
</style>
<!-- /INJECTED_FEATURE: AI_ADVISOR -->
"""

AI_MULTIMODAL_CREDIT_HTML = r"""
<!-- INJECTED_FEATURE: MULTIMODAL_CREDIT -->
<div id="jetski-multimodal-container" style="font-family: 'defaultFont', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  
  <!-- Floating Launch Banner / Badge (Bottom Left) -->
  <div id="jetski-multimodal-banner" onclick="openMultimodalModal()" style="position: fixed; bottom: 26px; left: 26px; z-index: 999980; display: flex; align-items: center; gap: 12px; background: linear-gradient(135deg, #001f52 0%, #002c72 100%); color: #ffffff; padding: 12px 20px; border-radius: 9999px; box-shadow: 0 12px 30px rgba(0, 31, 82, 0.4), 0 0 0 2px rgba(56, 189, 248, 0.5); cursor: pointer; transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1); user-select: none;" onmouseover="this.style.transform='translateY(-3px) scale(1.02)';" onmouseout="this.style.transform='none';">
    <div style="width: 32px; height: 32px; background: #38bdf8; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; color: #001f52; font-weight: 900; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
      📄
    </div>
    <div style="text-align: left;">
      <div style="font-size: 13px; font-weight: 800; letter-spacing: -0.2px; line-height: 1.2;">Precalificación Visión AI</div>
      <div style="font-size: 10px; color: #38bdf8; font-weight: 700;">✦ Recibo CFDI 4.0 • Gemini 3.7 Flash</div>
    </div>
    <span style="background: rgba(255,255,255,0.15); padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 800; color: #fbba00;">Preaprobar ➔</span>
  </div>

  <!-- Fullscreen Modal Overlay -->
  <div id="jetski-multimodal-modal" style="display: none; position: fixed; inset: 0; z-index: 999999; background: rgba(0, 15, 40, 0.82); backdrop-filter: blur(14px); align-items: center; justify-content: center; padding: 20px;">
    
    <div style="position: relative; width: 1020px; max-width: 96vw; max-height: 92vh; background: #ffffff; border-radius: 24px; box-shadow: 0 25px 80px rgba(0,0,0,0.5); overflow: hidden; display: flex; flex-direction: column; border: 1px solid rgba(255,255,255,0.2);">
      
      <!-- Modal Header -->
      <div style="background: linear-gradient(135deg, #001f52 0%, #002c72 60%, #00439c 100%); color: white; padding: 20px 28px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.15);">
        <div style="display: flex; align-items: center; gap: 14px;">
          <div style="width: 44px; height: 44px; background: #fbba00; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; color: #002c72; font-weight: 900;">
            ✦
          </div>
          <div>
            <div style="font-size: 19px; font-weight: 800; letter-spacing: -0.4px;">Precalificación Instantánea con Visión AI</div>
            <div style="font-size: 12px; color: #93c5fd; display: flex; align-items: center; gap: 8px; margin-top: 2px;">
              <span style="background: rgba(255,255,255,0.12); padding: 2px 8px; border-radius: 6px; font-weight: 700; color: #fbba00;">CFDI 4.0 SAT</span>
              <span>•</span>
              <span>Regulación CNBV (Tope 30% Capacidad de Pago)</span>
              <span>•</span>
              <span style="color: #4ade80;">⚡ Gemini 3.7 Flash</span>
            </div>
          </div>
        </div>
        <button onclick="closeMultimodalModal()" style="background: rgba(255,255,255,0.12); border: none; border-radius: 10px; width: 36px; height: 36px; color: white; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 24px; line-height: 1; transition: background 0.15s ease;">&times;</button>
      </div>

      <!-- Modal Body (2 Columns) -->
      <div style="display: grid; grid-template-columns: 1.15fr 1fr; gap: 24px; padding: 24px 28px; overflow-y: auto; background: #f8fafc; flex: 1;">
        
        <!-- Left Column: Document Viewer & Laser Scanner -->
        <div style="display: flex; flex-direction: column; gap: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 12px; font-weight: 800; color: #002c72; text-transform: uppercase; letter-spacing: 0.6px;">1. Comprobante de Ingresos (Nómina SAT)</span>
            <button type="button" onclick="triggerSampleScan()" style="background: #002c72; color: #fbba00; border: none; font-size: 12px; font-weight: 800; padding: 8px 16px; border-radius: 8px; cursor: pointer; transition: all 0.15s ease; box-shadow: 0 4px 12px rgba(0,44,114,0.2);">
              ⚡ Probar con Recibo Ejemplo ($18,450/qna)
            </button>
          </div>

          <!-- Document Canvas with Laser Effect -->
          <div id="cfdi-canvas" style="position: relative; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); min-height: 380px; overflow: hidden;">
            
            <!-- Laser Scan Line -->
            <div id="laser-scanner-line" style="display: none; position: absolute; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, rgba(56,189,248,0) 0%, #38bdf8 50%, rgba(56,189,248,0) 100%); box-shadow: 0 0 15px #38bdf8, 0 0 30px #0284c7; z-index: 10; animation: laserMove 1.8s ease-in-out infinite alternate;"></div>
            
            <!-- Simulated Mexican SAT CFDI 4.0 Receipt -->
            <div id="cfdi-preview" style="font-family: 'Courier New', Courier, monospace; font-size: 11px; color: #1e293b; line-height: 1.45;">
              <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #002c72; padding-bottom: 8px; margin-bottom: 12px;">
                <div>
                  <div style="font-weight: 800; font-size: 13px; color: #002c72; font-family: sans-serif;">GRUPO INDUSTRIAL QUERÉTARO S.A. DE C.V.</div>
                  <div>RFC: GIQ040815-9K2 • Régimen Personas Morales</div>
                  <div>Lugar Expedición: C.P. 76000, Querétaro, Qro.</div>
                </div>
                <div style="text-align: right;">
                  <div style="font-weight: 800; color: #0033a0;">CFDI DE NÓMINA 4.0</div>
                  <div>Folio Fiscal: 9F8A2C11-4E81-49B3-AA87</div>
                  <div>Fecha: 2026-02-15T12:30:00</div>
                </div>
              </div>

              <!-- Employee Data -->
              <div style="background: #f1f5f9; padding: 10px 12px; border-radius: 8px; margin-bottom: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <div><b>Empleado:</b> JUAN CARLOS RAMÍREZ MONTES</div>
                <div><b>RFC:</b> RAMJ850412-HX8</div>
                <div><b>NSS:</b> 01088523419 • <b>CURP:</b> RAMJ850412HDFMNN02</div>
                <div><b>Periodicidad:</b> Quincenal (01/Feb/2026 - 15/Feb/2026)</div>
              </div>

              <!-- Breakdown Grid -->
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                <!-- Percepciones -->
                <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 10px;">
                  <div style="font-weight: 800; color: #16a34a; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-bottom: 6px;">+ PERCEPCIONES</div>
                  <div style="display: flex; justify-content: space-between;"><span>001 Sueldo Base</span><span>$20,000.00</span></div>
                  <div style="display: flex; justify-content: space-between;"><span>038 Bono Desempeño</span><span>$2,500.00</span></div>
                  <div style="display: flex; justify-content: space-between; font-weight: 800; margin-top: 6px; border-top: 1px dashed #cbd5e1; padding-top: 4px;">
                    <span>Total Percepciones:</span><span>$22,500.00</span>
                  </div>
                </div>
                <!-- Deducciones -->
                <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 10px;">
                  <div style="font-weight: 800; color: #dc2626; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-bottom: 6px;">- DEDUCCIONES</div>
                  <div style="display: flex; justify-content: space-between;"><span>002 Retención ISR</span><span>$2,850.00</span></div>
                  <div style="display: flex; justify-content: space-between;"><span>001 Seguridad Social (IMSS)</span><span>$1,200.00</span></div>
                  <div style="display: flex; justify-content: space-between; font-weight: 800; margin-top: 6px; border-top: 1px dashed #cbd5e1; padding-top: 4px;">
                    <span>Total Retenciones:</span><span>$4,050.00</span>
                  </div>
                </div>
              </div>

              <!-- Net Total Callout -->
              <div style="background: #e6fffa; border: 1.5px solid #38bdf8; border-radius: 10px; padding: 10px 16px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; color: #002c72; font-size: 13px; font-family: sans-serif;">NETO RECIBIDO EN CUENTA:</span>
                <span style="font-size: 20px; font-weight: 900; color: #0284c7; font-family: sans-serif;">$18,450.00 MXN</span>
              </div>

              <div style="font-size: 9px; color: #94a3b8; margin-top: 10px; word-break: break-all;">
                Sello Digital SAT: 9FA82...BB02A4== | Cadena Original Timbre SAT | Certificado No. 00001000000504465028
              </div>
            </div>

          </div>

          <!-- File Upload input fallback -->
          <div style="display: flex; gap: 8px; align-items: center;">
            <input type="file" id="cfdi-file-input" accept="image/*" style="display: none;" onchange="handleFileInput(event)" />
            <button type="button" onclick="document.getElementById('cfdi-file-input').click()" style="background: #ffffff; border: 1.5px dashed #cbd5e1; border-radius: 10px; padding: 8px 14px; font-size: 12px; font-weight: 700; color: #475569; cursor: pointer; flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;">
              📁 O sube una fotografía de tu nómina (.jpg, .png)
            </button>
          </div>
        </div>

        <!-- Right Column: Real-time Analysis & Pre-Approved Certificate -->
        <div style="display: flex; flex-direction: column; gap: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 12px; font-weight: 800; color: #002c72; text-transform: uppercase; letter-spacing: 0.6px;">2. Dictamen Regulatorio CNBV & Oferta</span>
            <span id="multimodal-status-badge" style="font-size: 11px; font-weight: 700; color: #0369a1; background: #e0f2fe; padding: 3px 10px; border-radius: 9999px; border: 1px solid #bae6fd;">
              Esperando comprobante...
            </span>
          </div>

          <!-- Analysis Progression Tracker -->
          <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 18px;">
            <div style="display: flex; flex-direction: column; gap: 12px;">
              <div id="step-ocr" style="display: flex; align-items: center; gap: 10px; font-size: 12.5px; color: #94a3b8; font-weight: 700;">
                <span id="step-ocr-icon">⏳</span> <span id="step-ocr-text">1. Lectura OCR & Timbre Fiscal SAT (Pendiente)</span>
              </div>
              <div id="step-income" style="display: flex; align-items: center; gap: 10px; font-size: 12.5px; color: #94a3b8; font-weight: 700;">
                <span id="step-income-icon">⏳</span> <span id="step-income-text">2. Cálculo de Ingreso Mensual Neto (Pendiente)</span>
              </div>
              <div id="step-cnbv" style="display: flex; align-items: center; gap: 10px; font-size: 12.5px; color: #94a3b8; font-weight: 700;">
                <span id="step-cnbv-icon">⏳</span> <span id="step-cnbv-text">3. Capacidad Máxima de Pago (30% CNBV) (Pendiente)</span>
              </div>
            </div>
          </div>

          <!-- Empty State Box before scanning -->
          <div id="cert-empty-box" style="background: #ffffff; border: 1.5px dashed #cbd5e1; border-radius: 20px; padding: 36px 20px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 240px;">
            <div style="width: 52px; height: 52px; background: #f1f5f9; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 12px;">
              🤖
            </div>
            <div style="font-weight: 800; font-size: 15px; color: #002c72; margin-bottom: 6px;">
              Listo para Evaluar con Gemini 3.7 Flash
            </div>
            <div style="font-size: 12.5px; color: #64748b; line-height: 1.5; max-width: 290px; margin-bottom: 18px;">
              Haz clic en <b>"Probar con Recibo Ejemplo"</b> para ejecutar el escaneo láser y calcular tu línea de crédito en tiempo real.
            </div>
            <button type="button" onclick="triggerSampleScan()" style="background: linear-gradient(135deg, #0033a0, #0056b3); color: white; border: none; font-weight: 800; font-size: 13px; padding: 11px 22px; border-radius: 10px; cursor: pointer; box-shadow: 0 4px 14px rgba(0,51,160,0.25);">
              ⚡ Iniciar Análisis Multimodal
            </button>
          </div>

          <!-- Pre-Approved Loan Certificate Card (Hidden initially) -->
          <div id="approved-cert-card" style="display: none; background: linear-gradient(135deg, #001f52 0%, #002c72 100%); color: white; border-radius: 20px; padding: 24px; box-shadow: 0 15px 35px rgba(0, 31, 82, 0.35); border: 2px solid #fbba00; position: relative; overflow: hidden; animation: certReveal 0.4s cubic-bezier(0.16, 1, 0.3, 1);">
            <div style="position: absolute; top: -50px; right: -50px; width: 150px; height: 150px; background: radial-gradient(circle, rgba(251,186,0,0.3) 0%, rgba(0,0,0,0) 70%); border-radius: 50%;"></div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
              <span style="background: #fbba00; color: #002c72; font-weight: 900; font-size: 11px; padding: 4px 10px; border-radius: 6px; letter-spacing: 0.5px; text-transform: uppercase;">
                Crédito Preaprobado
              </span>
              <span style="font-size: 11px; color: #cbd5e1; font-family: monospace;" id="cert-folio">Folio: LIB-PRE-2026-9842</span>
            </div>

            <div style="font-size: 38px; font-weight: 900; color: #fbba00; letter-spacing: -1px; margin-bottom: 4px;" id="cert-amount">
              $85,000 MXN
            </div>
            <div style="font-size: 13px; color: #e2e8f0; margin-bottom: 18px;">
              Línea de crédito personal autorizada con desembolso en 24h.
            </div>

            <!-- Parameters Grid -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: rgba(255,255,255,0.1); backdrop-filter: blur(8px); border-radius: 12px; padding: 12px 14px; margin-bottom: 18px; border: 1px solid rgba(255,255,255,0.15);">
              <div>
                <div style="font-size: 11px; color: #94a3b8;">Mensualidad fija:</div>
                <div style="font-size: 16px; font-weight: 800; color: #38bdf8;" id="cert-payment">$4,427 MXN / mes</div>
                <div style="font-size: 10px; color: #4ade80;">(Solo 12% de tu ingreso)</div>
              </div>
              <div>
                <div style="font-size: 11px; color: #94a3b8;">Plazo y Tasa:</div>
                <div style="font-size: 15px; font-weight: 800; color: #ffffff;" id="cert-terms">24 meses • 16.5% fija</div>
                <div style="font-size: 10px; color: #cbd5e1;">Sin penalización prepago</div>
              </div>
            </div>

            <!-- Official Statement -->
            <div style="font-size: 11.5px; color: #cbd5e1; line-height: 1.45; border-left: 2px solid #fbba00; padding-left: 10px; margin-bottom: 20px;" id="cert-dictamen">
              "Aprobado con Calificación A1. La cuota mensual estimada representa únicamente el 12.0% de su ingreso comprobable, cumpliendo holgadamente el límite legal de 30% emitido por la CNBV."
            </div>

            <!-- CTA Actions -->
            <div style="display: flex; gap: 10px;">
              <button type="button" onclick="acceptApprovedCredit()" style="flex: 1; background: #fbba00; color: #002c72; border: none; font-size: 13.5px; font-weight: 800; padding: 13px 18px; border-radius: 10px; cursor: pointer; transition: transform 0.15s ease;">
                Aceptar Crédito en Línea ➔
              </button>
              <button type="button" onclick="downloadCertificateJSON()" style="background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.3); color: white; border-radius: 10px; padding: 13px 16px; font-size: 12.5px; font-weight: 700; cursor: pointer;">
                Descargar Certificado 📥
              </button>
            </div>

          </div>

        </div>

      </div>

    </div>

  </div>
</div>

<script>
let lastMultimodalResult = null;

function openMultimodalModal() {
  const modal = document.getElementById('jetski-multimodal-modal');
  if (modal) modal.style.display = 'flex';
}

function closeMultimodalModal() {
  const modal = document.getElementById('jetski-multimodal-modal');
  if (modal) modal.style.display = 'none';
}

async function triggerSampleScan() {
  const laser = document.getElementById('laser-scanner-line');
  const emptyBox = document.getElementById('cert-empty-box');
  const certCard = document.getElementById('approved-cert-card');
  const statusBadge = document.getElementById('multimodal-status-badge');
  const stepOcr = document.getElementById('step-ocr');
  const stepIncome = document.getElementById('step-income');
  const stepCnbv = document.getElementById('step-cnbv');

  if (emptyBox) emptyBox.style.display = 'none';
  if (certCard) certCard.style.display = 'none';
  if (laser) laser.style.display = 'block';

  if (statusBadge) {
    statusBadge.innerText = '⚡ Escaneando con Gemini 3.7 Flash...';
    statusBadge.style.background = '#fef3c7';
    statusBadge.style.color = '#b45309';
    statusBadge.style.borderColor = '#fde68a';
  }

  if (stepOcr) stepOcr.innerHTML = '<span style="color: #0284c7;">🔄</span> <span style="color: #0284c7; font-weight: 700;">1. Analizando Timbre Fiscal SAT y RFC...</span>';
  if (stepIncome) stepIncome.innerHTML = '<span style="color: #94a3b8;">⏳</span> <span style="color: #94a3b8;">2. Cálculo de Ingreso Mensual Neto</span>';
  if (stepCnbv) stepCnbv.innerHTML = '<span style="color: #94a3b8;">⏳</span> <span style="color: #94a3b8;">3. Validación Capacidad CNBV (30%)</span>';

  try {
    const res = await fetch('/api/multimodal-credit');
    const data = await res.json();
    lastMultimodalResult = data;

    setTimeout(() => {
      if (stepOcr) stepOcr.innerHTML = `<span style="color: #16a34a;">✅</span> <span style="color: #16a34a; font-weight: 700;">1. Timbre SAT & RFC: <b>${data.rfc}</b> (${data.empleado})</span>`;
      if (stepIncome) stepIncome.innerHTML = '<span style="color: #0284c7;">🔄</span> <span style="color: #0284c7; font-weight: 700;">2. Calculando percepciones y deducciones...</span>';
    }, 400);

    setTimeout(() => {
      if (stepIncome) stepIncome.innerHTML = `<span style="color: #16a34a;">✅</span> <span style="color: #16a34a; font-weight: 700;">2. Ingreso Neto: <b>$${Number(data.ingreso_mensual_neto).toLocaleString('es-MX', {minimumFractionDigits:2})} MXN</b></span>`;
      if (stepCnbv) stepCnbv.innerHTML = '<span style="color: #0284c7;">🔄</span> <span style="color: #0284c7; font-weight: 700;">3. Evaluando límite regulatorio CNBV (máx 30%)...</span>';
    }, 900);

    setTimeout(() => {
      if (laser) laser.style.display = 'none';
      if (stepCnbv) stepCnbv.innerHTML = `<span style="color: #16a34a;">✅</span> <span style="color: #16a34a; font-weight: 700;">3. Capacidad Máxima CNBV: <b>$${Number(data.capacidad_pago_maxima_mensual).toLocaleString('es-MX', {minimumFractionDigits:2})}/mes</b></span>`;
      
      if (statusBadge) {
        statusBadge.innerText = '✅ Dictamen Aprobado (A1)';
        statusBadge.style.background = '#dcfce7';
        statusBadge.style.color = '#15803d';
        statusBadge.style.borderColor = '#bbf7d0';
      }

      updateCertUI(data);
      if (certCard) certCard.style.display = 'block';
    }, 1400);

  } catch(e) {
    if (laser) laser.style.display = 'none';
    if (emptyBox) emptyBox.style.display = 'flex';
    if (statusBadge) {
      statusBadge.innerText = '❌ Error de lectura';
      statusBadge.style.background = '#fee2e2';
      statusBadge.style.color = '#991b1b';
    }
    alert('Error al procesar el comprobante de nómina.');
  }
}

async function handleFileInput(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async function(evt) {
    const base64 = evt.target.result;
    const laser = document.getElementById('laser-scanner-line');
    const emptyBox = document.getElementById('cert-empty-box');
    const certCard = document.getElementById('approved-cert-card');
    if (emptyBox) emptyBox.style.display = 'none';
    if (certCard) certCard.style.display = 'none';
    if (laser) laser.style.display = 'block';

    try {
      const res = await fetch('/api/multimodal-credit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: base64 })
      });
      const data = await res.json();
      lastMultimodalResult = data;
      if (laser) laser.style.display = 'none';
      updateCertUI(data);
      if (certCard) certCard.style.display = 'block';
    } catch(err) {
      if (laser) laser.style.display = 'none';
      if (emptyBox) emptyBox.style.display = 'flex';
      alert('Error al escanear archivo.');
    }
  };
  reader.readAsDataURL(file);
}

function updateCertUI(data) {
  const certAmount = document.getElementById('cert-amount');
  const certPayment = document.getElementById('cert-payment');
  const certTerms = document.getElementById('cert-terms');
  const certFolio = document.getElementById('cert-folio');
  const certDictamen = document.getElementById('cert-dictamen');

  if (certAmount) certAmount.innerText = '$' + Number(data.credito_preaprobado_monto).toLocaleString('es-MX') + ' MXN';
  if (certPayment) certPayment.innerText = '$' + Number(data.pago_mensual_estimado).toLocaleString('es-MX') + ' MXN / mes';
  if (certTerms) certTerms.innerText = `${data.plazo_meses} meses • ${data.tasa_fija_anual}`;
  if (certFolio) certFolio.innerText = `Folio: ${data.folio_autorizacion}`;
  if (certDictamen) certDictamen.innerText = `"${data.dictamen}"`;
}

function acceptApprovedCredit() {
  const certCard = document.getElementById('approved-cert-card');
  if (!certCard) return;
  certCard.innerHTML = `
    <div style="text-align: center; padding: 16px 8px;">
      <div style="font-size: 48px; margin-bottom: 8px;">🎉</div>
      <div style="font-size: 22px; font-weight: 900; color: #fbba00; margin-bottom: 6px;">
        ¡Línea de Crédito Otorgada!
      </div>
      <div style="font-size: 13.5px; color: #e2e8f0; margin-bottom: 18px; line-height: 1.5;">
        Tu crédito por <b>$85,000 MXN</b> ha sido formalizado digitalmente bajo el folio <b>LIB-PRE-2026-9842</b>.<br/>
        Los fondos se dispersarán a tu cuenta en menos de 24 horas.
      </div>
      <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 12px; margin-bottom: 18px; font-size: 12px; text-align: left;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;"><span>Titular:</span><b>JUAN CARLOS RAMÍREZ MONTES</b></div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;"><span>Mensualidad fija:</span><b>$4,427.00 MXN</b></div>
        <div style="display: flex; justify-content: space-between;"><span>Primer pago:</span><b>15 de Marzo, 2026</b></div>
      </div>
      <div style="display: flex; gap: 8px;">
        <button onclick="downloadCertificateJSON()" style="flex: 1; background: #fbba00; color: #002c72; border: none; font-size: 12.5px; font-weight: 800; padding: 11px; border-radius: 10px; cursor: pointer;">
          Descargar Contrato 📥
        </button>
        <button onclick="closeMultimodalModal()" style="background: rgba(255,255,255,0.15); color: white; border: none; font-size: 12.5px; font-weight: 700; padding: 11px 16px; border-radius: 10px; cursor: pointer;">
          Cerrar
        </button>
      </div>
    </div>
  `;
}

function downloadCertificateJSON() {
  const payload = lastMultimodalResult || {
    folio: "LIB-PRE-2026-9842",
    monto_autorizado: "$85,000 MXN",
    plazo: "24 meses",
    pago_mensual: "$4,427 MXN",
    regulacion: "CNBV 30% capacidad comprobable",
    validez: "15 dias naturales"
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `Certificado_Preaprobacion_${payload.folio_autorizacion || 'Libertad'}.json`;
  a.click();
}
</script>

<style>
@keyframes laserMove {
  0% { top: 0%; }
  100% { top: 96%; }
}
@keyframes certReveal {
  0% { opacity: 0; transform: scale(0.95) translateY(10px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
<!-- /INJECTED_FEATURE: MULTIMODAL_CREDIT -->
"""

BUILTIN_FEATURES = {
    "modern_header": {
        "slot": "TOP_BAR",
        "description": "Modern uncluttered Header with Dropdown Mega-Menu and Vertex AI Search Navigator",
        "content": r"""
<!-- INJECTED_FEATURE: MODERN_HEADER -->
<div id="jetski-modern-header" style="position: sticky; top: 0; z-index: 99999; background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(12px); border-bottom: 1px solid #e2e8f0; font-family: 'defaultFont', sans-serif; box-shadow: 0 4px 20px rgba(0, 44, 114, 0.06);">
  <div style="max-width: 1400px; margin: 0 auto; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; gap: 24px;">
    
    <!-- Logo -->
    <a href="./index.html" style="display: flex; align-items: center; gap: 10px; text-decoration: none;">
      <img src="./assets/dam/logo-libertad-financiera-azul.svg" alt="Libertad Financiera" style="height: 38px;" />
    </a>

    <!-- Dropdown Navigation -->
    <nav style="display: flex; align-items: center; gap: 8px;">
      <!-- Dropdown 1: Créditos -->
      <div class="jetski-dropdown" style="position: relative;">
        <button style="background: none; border: none; font-size: 15px; font-weight: 600; color: #002c72; padding: 10px 14px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: background 0.2s ease;">
          Créditos <span style="font-size: 11px; opacity: 0.7;">▼</span>
        </button>
        <div class="jetski-menu" style="display: none; position: absolute; top: 100%; left: 0; width: 260px; background: white; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; padding: 10px; margin-top: 6px;">
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Crédito Personal</div>
            <div style="font-size: 12px; color: #64748b;">Préstamos rápidos desde $5,000</div>
          </a>
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Mi Primer Crédito</div>
            <div style="font-size: 12px; color: #64748b;">Inicia tu historial financiero hoy</div>
          </a>
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Liberauto</div>
            <div style="font-size: 12px; color: #64748b;">Financiamiento para auto nuevo o usado</div>
          </a>
        </div>
      </div>

      <!-- Dropdown 2: Inversión & Cuentas -->
      <div class="jetski-dropdown" style="position: relative;">
        <button style="background: none; border: none; font-size: 15px; font-weight: 600; color: #002c72; padding: 10px 14px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
          Inversión & Cuentas <span style="font-size: 11px; opacity: 0.7;">▼</span>
        </button>
        <div class="jetski-menu" style="display: none; position: absolute; top: 100%; left: 0; width: 270px; background: white; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; padding: 10px; margin-top: 6px;">
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Inversión Plazo Fijo <span style="background: #fbba00; color: #002c72; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: 800;">14% Rendimiento</span></div>
            <div style="font-size: 12px; color: #64748b;">Crece tu patrimonio seguro</div>
          </a>
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">CuentaYa Digital</div>
            <div style="font-size: 12px; color: #64748b;">Apertura 100% digital sin comisiones</div>
          </a>
        </div>
      </div>

      <!-- Dropdown 3: Seguros -->
      <div class="jetski-dropdown" style="position: relative;">
        <button style="background: none; border: none; font-size: 15px; font-weight: 600; color: #002c72; padding: 10px 14px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
          Seguros <span style="font-size: 11px; opacity: 0.7;">▼</span>
        </button>
        <div class="jetski-menu" style="display: none; position: absolute; top: 100%; left: 0; width: 240px; background: white; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; padding: 10px; margin-top: 6px;">
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Libertad Segura</div>
            <div style="font-size: 12px; color: #64748b;">Protección familiar integral</div>
          </a>
        </div>
      </div>

      <!-- Dropdown 4: Empresas -->
      <div class="jetski-dropdown" style="position: relative;">
        <button style="background: none; border: none; font-size: 15px; font-weight: 600; color: #002c72; padding: 10px 14px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
          Empresas <span style="font-size: 11px; opacity: 0.7;">▼</span>
        </button>
        <div class="jetski-menu" style="display: none; position: absolute; top: 100%; left: 0; width: 240px; background: white; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; padding: 10px; margin-top: 6px;">
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Créditos Comerciales</div>
            <div style="font-size: 12px; color: #64748b;">Impulsa el crecimiento de tu negocio</div>
          </a>
        </div>
      </div>
    </nav>

    <!-- Vertex AI Search & Smart Navigator -->
    <div id="jetski-search-container" style="flex: 1; max-width: 440px; position: relative;">
      <div style="display: flex; align-items: center; background: #f1f5f9; border: 1.5px solid #cbd5e1; border-radius: 9999px; padding: 6px 14px; transition: all 0.2s ease; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
        <span style="margin-right: 8px; color: #0033a0; font-size: 14px;">✦</span>
        <input id="jetski-search-input" 
               placeholder="Pregúntale a Vertex AI o busca..." 
               autocomplete="off"
               style="flex: 1; border: none; background: transparent; font-size: 13px; outline: none; color: #0f172a; font-family: inherit;" 
               oninput="handleSearchAsYouType(event)"
               onfocus="handleSearchFocus()"
               onkeydown="handleSearchKeydown(event)" />
        <button onclick="executeVertexSearch(true)" style="background: #0033a0; color: white; border: none; border-radius: 9999px; padding: 5px 14px; font-size: 11px; font-weight: 700; cursor: pointer; transition: all 0.15s ease;">Buscar</button>
      </div>

      <!-- Vertex AI Results Floating Dynamic Modal -->
      <div id="jetski-search-modal" class="jetski-modal-compact jetski-modal-hidden">
        <!-- Dynamic Header -->
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 12px;">
          <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
            <span style="font-weight: 800; font-size: 13px; color: #002c72; letter-spacing: -0.2px;">✦ Navegador Inteligente</span>
            <span style="background: #e0f2fe; color: #0369a1; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px; border: 1px solid #bae6fd;">Vertex AI Search</span>
            <span id="jetski-model-badge" style="background: #f0fdf4; color: #166534; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px; border: 1px solid #bbf7d0;">⚡ Gemini 3.5 Flash Lite</span>
            <span id="jetski-latency-badge" style="display: none; background: #faf5ff; color: #7e22ce; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 6px; border: 1px solid #e9d5ff;"></span>
          </div>
          <div style="display: flex; align-items: center; gap: 4px;">
            <button id="jetski-size-toggle-btn" onclick="toggleModalManualSize()" title="Alternar tamaño de ventana" style="background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 6px; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; font-size: 13px; cursor: pointer; color: #475569; transition: background 0.15s ease;">⤢</button>
            <button onclick="hideModal()" title="Cerrar (Esc)" style="background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 6px; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; font-size: 15px; cursor: pointer; color: #475569; line-height: 1; transition: background 0.15s ease;">&times;</button>
          </div>
        </div>

        <!-- Track A: Instant Suggestions / Fast Typeahead (<10ms) -->
        <div id="jetski-instant-section" style="margin-bottom: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 10.5px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.6px;">✦ Coincidencias Inmediatas (<10ms)</span>
            <span id="jetski-suggest-count" style="font-size: 10px; color: #94a3b8; font-weight: 600;">Escribe para filtrar</span>
          </div>
          <div id="jetski-instant-results" style="display: flex; flex-direction: column; gap: 5px;">
            <div style="font-size: 12px; color: #94a3b8; padding: 4px 0;">Escribe para buscar productos y trámites al instante...</div>
          </div>
        </div>

        <!-- Track B: Parallel AI Synthesis & Vertex AI Search Grounding -->
        <div id="jetski-ai-section">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 10.5px; font-weight: 800; color: #0033a0; text-transform: uppercase; letter-spacing: 0.6px;">✦ Síntesis Cognitiva & Páginas Indexadas</span>
            <span id="jetski-ai-status" style="font-size: 10px; color: #64748b; font-weight: 700;">En espera</span>
          </div>
          <div id="jetski-ai-summary" style="background: #f8fafc; border-left: 3px solid #cbd5e1; padding: 12px 14px; border-radius: 8px; font-size: 12px; color: #475569; line-height: 1.6; transition: all 0.25s ease;">
            Ingresa tu consulta para sintetizar la información con Gemini 3.5 Flash Lite y Vertex AI Search.
          </div>
        </div>

        <!-- Footer Hint -->
        <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; font-size: 10.5px; color: #94a3b8;">
          <span>Tip: Usa <kbd style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 3px; padding: 1px 4px; font-size: 9.5px; color: #475569;">Enter</kbd> para buscar o <kbd style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 3px; padding: 1px 4px; font-size: 9.5px; color: #475569;">Esc</kbd> para cerrar</span>
          <span style="color: #0033a0; font-weight: 600;">Libertad Digital AI</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div style="display: flex; align-items: center; gap: 12px;">
      <a href="#" style="background: #fbba00; color: #002c72; font-weight: 800; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 13px; box-shadow: 0 2px 8px rgba(251,186,0,0.3); transition: transform 0.15s ease;">
        Banca en Línea
      </a>
    </div>

  </div>
</div>
""" + MODERN_HERO_AND_SIMULATOR_HTML + r"""

<style>
/* Dropdowns */
.jetski-dropdown:hover .jetski-menu {
  display: block !important;
}
.jetski-menu a:hover {
  background: #f8fafc;
}
#jetski-modern-header + .lib-header,
.cmp-container-header-aa,
.cmp-carousel_lib_new {
  display: none !important;
}

/* Sleek Apple-style scrollbar */
#jetski-search-modal::-webkit-scrollbar {
  width: 6px;
}
#jetski-search-modal::-webkit-scrollbar-track {
  background: transparent;
}
#jetski-search-modal::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 9999px;
}
#jetski-search-modal::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Dynamic Floating Modal Geometry */
#jetski-search-modal {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(203, 213, 225, 0.85);
  border-radius: 16px;
  box-shadow: 0 24px 60px -12px rgba(0, 44, 114, 0.22), 0 0 1px 1px rgba(0, 44, 114, 0.08);
  padding: 16px;
  z-index: 999999;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
  transform-origin: top right;
  transition: width 0.38s cubic-bezier(0.16, 1, 0.3, 1),
              max-height 0.38s cubic-bezier(0.16, 1, 0.3, 1),
              opacity 0.22s ease,
              transform 0.28s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.3s ease;
}

/* Sizing Modes */
#jetski-search-modal.jetski-modal-compact {
  width: 460px;
  max-height: 420px;
}
#jetski-search-modal.jetski-modal-expanded {
  width: min(740px, calc(100vw - 32px));
  max-height: calc(85vh - 70px);
  box-shadow: 0 32px 80px -12px rgba(0, 44, 114, 0.28), 0 0 0 1px rgba(0, 51, 160, 0.12);
}

/* Visibility Animation */
#jetski-search-modal.jetski-modal-hidden {
  display: none !important;
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
  pointer-events: none;
}
#jetski-search-modal.jetski-modal-visible {
  display: block !important;
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
  animation: jetskiScaleIn 0.24s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes jetskiScaleIn {
  0% {
    opacity: 0;
    transform: translateY(-8px) scale(0.97);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Shimmer Loading Skeleton */
@keyframes shimmerPulse {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.jetski-shimmer-line {
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmerPulse 1.6s infinite ease-in-out;
  border-radius: 4px;
}

/* Interactive Rows & Result Cards */
.jetski-suggest-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 8px;
  text-decoration: none;
  color: #0033a0;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  transition: all 0.15s ease;
}
.jetski-suggest-item:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateX(3px);
}

.jetski-result-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  text-decoration: none;
  color: #0033a0;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}
.jetski-result-card:hover {
  background: #f8fafc;
  border-color: #0033a0;
  box-shadow: 0 6px 16px rgba(0, 44, 114, 0.08);
  transform: translateY(-2px);
}
</style>

<script>
let searchDebounceTimer = null;
let aiAbortController = null;
let suggestAbortController = null;
let isUserExpandedManually = false;

function setModalState(state) {
  const modal = document.getElementById('jetski-search-modal');
  const toggleBtn = document.getElementById('jetski-size-toggle-btn');
  if (!modal) return;

  if (state === 'expanded') {
    modal.classList.remove('jetski-modal-compact');
    modal.classList.add('jetski-modal-expanded');
    if (toggleBtn) {
      toggleBtn.innerHTML = '⤡';
      toggleBtn.title = 'Contraer a vista compacta (460px)';
    }
  } else {
    modal.classList.remove('jetski-modal-expanded');
    modal.classList.add('jetski-modal-compact');
    if (toggleBtn) {
      toggleBtn.innerHTML = '⤢';
      toggleBtn.title = 'Expandir a vista completa (740px)';
    }
  }
}

function toggleModalManualSize() {
  const modal = document.getElementById('jetski-search-modal');
  if (!modal) return;
  if (modal.classList.contains('jetski-modal-expanded')) {
    isUserExpandedManually = false;
    setModalState('compact');
  } else {
    isUserExpandedManually = true;
    setModalState('expanded');
  }
}

function showModal() {
  const modal = document.getElementById('jetski-search-modal');
  if (modal) {
    modal.classList.remove('jetski-modal-hidden');
    modal.classList.add('jetski-modal-visible');
  }
}

function hideModal() {
  const modal = document.getElementById('jetski-search-modal');
  if (modal) {
    modal.classList.remove('jetski-modal-visible');
    modal.classList.add('jetski-modal-hidden');
  }
}

function handleSearchFocus() {
  const input = document.getElementById('jetski-search-input');
  if (input && input.value.trim().length >= 1) {
    showModal();
  }
}

function handleSearchKeydown(event) {
  if (event.key === 'Enter') {
    executeVertexSearch(true);
  } else if (event.key === 'Escape') {
    hideModal();
  }
}

// Global click-outside & escape listeners
document.addEventListener('click', function(e) {
  const container = document.getElementById('jetski-search-container');
  if (container && !container.contains(e.target)) {
    hideModal();
  }
});

function formatMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong style="color: #002c72; font-weight: 700;">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '<div style="margin-bottom: 8px;"></div>')
    .replace(/\n/g, '<br>');
}

function handleSearchAsYouType(event) {
  const q = event.target.value.trim();
  if(!q) {
    hideModal();
    setModalState('compact');
    return;
  }
  showModal();

  // Initially keep modal compact for immediate keystroke results
  if (!isUserExpandedManually) {
    setModalState('compact');
  }

  // Track A: Instant Parallel Suggestion (<10ms)
  fetchInstantSuggestions(q);

  // Track B: Debounced Parallel Gemini 3.5 Flash Lite Synthesis (220ms)
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    executeVertexSearch(false);
  }, 220);
}

async function fetchInstantSuggestions(q) {
  if (suggestAbortController) suggestAbortController.abort();
  suggestAbortController = new AbortController();
  const resContainer = document.getElementById('jetski-instant-results');
  const countBadge = document.getElementById('jetski-suggest-count');

  try {
    const res = await fetch('/api/suggest?q=' + encodeURIComponent(q), { signal: suggestAbortController.signal });
    const data = await res.json();
    if (!data.suggestions || data.suggestions.length === 0) {
      if (countBadge) countBadge.textContent = 'Sin accesos directos';
      resContainer.innerHTML = '<div style="font-size: 12px; color: #94a3b8; padding: 4px 0;">No se encontraron productos directos para "' + q + '". Se sintetizará con Vertex AI.</div>';
      return;
    }
    if (countBadge) countBadge.textContent = data.suggestions.length + ' producto(s)';
    let html = '';
    data.suggestions.forEach(s => {
      html += '<a href="' + s.link + '" target="_blank" rel="noopener noreferrer" class="jetski-suggest-item">' +
              '  <div>' +
              '    <span style="font-weight: 700; font-size: 12.5px; color: #002c72;">' + s.title + '</span>' +
              '    <span style="margin-left: 6px; font-size: 10px; background: #f1f5f9; color: #475569; padding: 2px 6px; border-radius: 4px;">' + s.category + '</span>' +
              '  </div>' +
              '  <span style="font-size: 10px; font-weight: 600; color: #059669; background: #ecfdf5; padding: 2px 8px; border-radius: 4px; border: 1px solid #a7f3d0;">' + s.badge + '</span>' +
              '</a>';
    });
    resContainer.innerHTML = html;
  } catch(e) {
    const isAbort = e.name === 'AbortError' || e.code === 20 || (e.message && e.message.toLowerCase().includes('abort'));
    if (!isAbort) {
      console.warn('Suggest error:', e);
    }
  }
}

async function executeVertexSearch(force = false) {
  const q = document.getElementById('jetski-search-input').value.trim();
  if(!q) return;

  showModal();
  // Automatically expand modal to wider viewport for AI synthesis & grounded cards
  setModalState('expanded');

  const aiSummary = document.getElementById('jetski-ai-summary');
  const aiStatus = document.getElementById('jetski-ai-status');
  const badge = document.getElementById('jetski-latency-badge');

  if (aiAbortController) aiAbortController.abort();
  aiAbortController = new AbortController();

  aiStatus.innerHTML = '<span style="color: #0284c7; font-weight: 700;">⚡ Sintetizando...</span>';
  aiSummary.style.borderLeftColor = '#0284c7';
  aiSummary.style.background = '#f0f9ff';
  aiSummary.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 8px;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #0284c7; box-shadow: 0 0 8px #0284c7;"></span>
        <span style="font-size: 11.5px; font-weight: 700; color: #0369a1;">Consultando Vertex AI Search & Generando síntesis con Gemini 3.5 Flash Lite...</span>
      </div>
      <div class="jetski-shimmer-line" style="width: 90%; height: 11px;"></div>
      <div class="jetski-shimmer-line" style="width: 100%; height: 11px;"></div>
      <div class="jetski-shimmer-line" style="width: 65%; height: 11px;"></div>
    </div>
  `;

  try {
    const t0 = performance.now();
    const res = await fetch('/api/search?q=' + encodeURIComponent(q), { signal: aiAbortController.signal });
    const data = await res.json();
    const clientLatency = Math.round(performance.now() - t0);

    aiStatus.innerHTML = '<span style="color: #059669; font-weight: 700;">✓ Completado</span>';
    if(badge && data.latency_ms) {
      badge.style.display = 'inline-block';
      badge.textContent = '⚡ ' + data.latency_ms + 'ms backend (' + clientLatency + 'ms total)';
    }

    aiSummary.style.borderLeftColor = '#0033a0';
    aiSummary.style.background = '#ffffff';
    aiSummary.style.border = '1px solid #e2e8f0';
    aiSummary.style.borderLeft = '4px solid #0033a0';
    aiSummary.style.boxShadow = '0 4px 12px rgba(0,44,114,0.04)';

    let formattedSummary = formatMarkdown(data.summary);
    let html = `
      <div style="margin-bottom: 14px; color: #1e293b; line-height: 1.6; font-size: 12.5px;">
        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
          <span style="font-size: 13px;">💡</span>
          <span style="font-weight: 800; color: #002c72; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Resumen Ejecutivo de Soluciones:</span>
        </div>
        ${formattedSummary}
      </div>
    `;

    if (data.results && data.results.length > 0) {
      html += `
        <div style="margin-top: 14px; padding-top: 10px; border-top: 1px dashed #cbd5e1;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 800; font-size: 11px; color: #475569; text-transform: uppercase; letter-spacing: 0.5px;">✦ Fuentes Verificadas en Libertad.com.mx (${data.results.length}):</span>
            <span style="font-size: 10px; color: #0284c7; font-weight: 600;">Vertex AI Grounding ↗</span>
          </div>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 8px;">
      `;
      data.results.forEach(r => {
        html += `
          <a href="${r.link}" target="_blank" rel="noopener noreferrer" class="jetski-result-card">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; margin-bottom: 4px;">
              <span style="font-weight: 700; font-size: 12px; color: #002c72; line-height: 1.3;">${r.title}</span>
              <span style="font-size: 11px; color: #64748b; opacity: 0.8;">↗</span>
            </div>
            <div style="font-size: 10.5px; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px;">
              ${r.link}
            </div>
            <div style="font-size: 11px; color: #475569; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
              ${r.snippet || 'Acceso directo a la sección oficial de Libertad Financiera.'}
            </div>
          </a>
        `;
      });
      html += `</div></div>`;
    }
    aiSummary.innerHTML = html;
  } catch(e) {
    const isAbort = e.name === 'AbortError' || e.code === 20 || (e.message && e.message.toLowerCase().includes('abort'));
    if (!isAbort) {
      aiStatus.innerHTML = '<span style="color: #ef4444; font-weight: 700;">Error</span>';
      aiSummary.style.borderLeftColor = '#ef4444';
      aiSummary.style.background = '#fef2f2';
      aiSummary.innerHTML = '<span style="color: #dc2626; font-weight: 600;">Error al consultar la síntesis de IA. Intenta nuevamente.</span>';
    }
  }
}
</script>
<!-- /INJECTED_FEATURE: MODERN_HEADER -->
"""
    },
    "modern_header_ux": {
        "slot": "TOP_BAR",
        "description": "Modern Header with Dropdown Mega-Menu and standard search box (Pure UX/UI, no AI)",
        "content": r"""
<!-- INJECTED_FEATURE: MODERN_HEADER -->
<div id="jetski-modern-header" style="position: sticky; top: 0; z-index: 99999; background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(12px); border-bottom: 1px solid #e2e8f0; font-family: 'defaultFont', sans-serif; box-shadow: 0 4px 20px rgba(0, 44, 114, 0.06);">
  <div style="max-width: 1400px; margin: 0 auto; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; gap: 24px;">
    
    <!-- Logo -->
    <a href="./index.html" style="display: flex; align-items: center; gap: 10px; text-decoration: none;">
      <img src="./assets/dam/logo-libertad-financiera-azul.svg" alt="Libertad Financiera" style="height: 38px;" />
    </a>

    <!-- Dropdown Navigation -->
    <nav style="display: flex; align-items: center; gap: 8px;">
      <!-- Dropdown 1: Créditos -->
      <div class="jetski-dropdown" style="position: relative;">
        <button style="background: none; border: none; font-size: 15px; font-weight: 600; color: #002c72; padding: 10px 14px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: background 0.2s ease;">
          Créditos <span style="font-size: 11px; opacity: 0.7;">▼</span>
        </button>
        <div class="jetski-menu" style="display: none; position: absolute; top: 100%; left: 0; width: 260px; background: white; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; padding: 10px; margin-top: 6px;">
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Crédito Personal</div>
            <div style="font-size: 12px; color: #64748b;">Préstamos rápidos desde $5,000</div>
          </a>
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Mi Primer Crédito</div>
            <div style="font-size: 12px; color: #64748b;">Inicia tu historial financiero hoy</div>
          </a>
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Liberauto</div>
            <div style="font-size: 12px; color: #64748b;">Financiamiento para auto nuevo o usado</div>
          </a>
        </div>
      </div>

      <!-- Dropdown 2: Inversión & Cuentas -->
      <div class="jetski-dropdown" style="position: relative;">
        <button style="background: none; border: none; font-size: 15px; font-weight: 600; color: #002c72; padding: 10px 14px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
          Inversión & Cuentas <span style="font-size: 11px; opacity: 0.7;">▼</span>
        </button>
        <div class="jetski-menu" style="display: none; position: absolute; top: 100%; left: 0; width: 270px; background: white; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; padding: 10px; margin-top: 6px;">
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Inversión Plazo Fijo <span style="background: #fbba00; color: #002c72; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: 800;">14% Rendimiento</span></div>
            <div style="font-size: 12px; color: #64748b;">Crece tu patrimonio seguro</div>
          </a>
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">CuentaYa Digital</div>
            <div style="font-size: 12px; color: #64748b;">Apertura 100% digital sin comisiones</div>
          </a>
        </div>
      </div>

      <!-- Dropdown 3: Seguros -->
      <div class="jetski-dropdown" style="position: relative;">
        <button style="background: none; border: none; font-size: 15px; font-weight: 600; color: #002c72; padding: 10px 14px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
          Seguros <span style="font-size: 11px; opacity: 0.7;">▼</span>
        </button>
        <div class="jetski-menu" style="display: none; position: absolute; top: 100%; left: 0; width: 240px; background: white; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; padding: 10px; margin-top: 6px;">
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Libertad Segura</div>
            <div style="font-size: 12px; color: #64748b;">Protección familiar integral</div>
          </a>
        </div>
      </div>

      <!-- Dropdown 4: Empresas -->
      <div class="jetski-dropdown" style="position: relative;">
        <button style="background: none; border: none; font-size: 15px; font-weight: 600; color: #002c72; padding: 10px 14px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
          Empresas <span style="font-size: 11px; opacity: 0.7;">▼</span>
        </button>
        <div class="jetski-menu" style="display: none; position: absolute; top: 100%; left: 0; width: 240px; background: white; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; padding: 10px; margin-top: 6px;">
          <a href="#" style="display: block; padding: 10px 12px; border-radius: 8px; text-decoration: none; color: #1e293b;">
            <div style="font-weight: 700; color: #0033a0; font-size: 14px;">Créditos Comerciales</div>
            <div style="font-size: 12px; color: #64748b;">Impulsa el crecimiento de tu negocio</div>
          </a>
        </div>
      </div>
    </nav>

    <!-- Clean Sleek Search Input (UX Only) -->
    <div style="flex: 1; max-width: 400px; position: relative;">
      <div style="display: flex; align-items: center; background: #f1f5f9; border: 1.5px solid #cbd5e1; border-radius: 9999px; padding: 6px 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
        <span style="margin-right: 8px; color: #0033a0; font-size: 13px;">🔍</span>
        <input placeholder="Buscar en Libertad Financiera..." 
               style="flex: 1; border: none; background: transparent; font-size: 13px; outline: none; color: #0f172a; font-family: inherit;" />
        <button style="background: #0033a0; color: white; border: none; border-radius: 9999px; padding: 5px 14px; font-size: 11px; font-weight: 700; cursor: pointer;">Buscar</button>
      </div>
    </div>

    <!-- Actions -->
    <div style="display: flex; align-items: center; gap: 12px;">
      <a href="#" style="background: #fbba00; color: #002c72; font-weight: 800; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 13px; box-shadow: 0 2px 8px rgba(251,186,0,0.3);">
        Banca en Línea
      </a>
    </div>

  </div>
</div>
""" + MODERN_HERO_AND_SIMULATOR_HTML + r"""

<style>
/* Dropdowns */
.jetski-dropdown:hover .jetski-menu {
  display: block !important;
}
.jetski-menu a:hover {
  background: #f8fafc;
}
#jetski-modern-header + .lib-header,
.cmp-container-header-aa,
.cmp-carousel_lib_new {
  display: none !important;
}
</style>
<!-- /INJECTED_FEATURE: MODERN_HEADER -->
"""
    },
    "ai_advisor": {
        "slot": "FLOATING_ASSISTANT",
        "description": "Libertad AI Advisor 24/7 (Drawer Flotante Asesor con Gemini 3.7 Flash)",
        "content": AI_ADVISOR_HTML
    },
    "ai_assistant": {
        "slot": "FLOATING_ASSISTANT",
        "description": "Libertad AI Advisor 24/7 (Drawer Flotante Asesor con Gemini 3.7 Flash)",
        "content": AI_ADVISOR_HTML
    },
    "ai_multimodal_credit": {
        "slot": "HERO_OVERLAY",
        "description": "Precalificación Multimodal de Crédito (Visión AI Recibo de Nómina SAT CFDI 4.0)",
        "content": AI_MULTIMODAL_CREDIT_HTML
    }
}
BUILTIN_FEATURES["ai_copilot"] = BUILTIN_FEATURES["ai_advisor"]
BUILTIN_FEATURES["modern_header_ai"] = BUILTIN_FEATURES["modern_header"]
BUILTIN_FEATURES["ai_search"] = BUILTIN_FEATURES["modern_header"]


def backup_if_needed():
    if not BACKUP_FILE.exists() and INDEX_FILE.exists():
        BACKUP_FILE.write_text(INDEX_FILE.read_text(encoding="utf-8"), encoding="utf-8")


def list_features():
    print("\n📦 Available Builtin Demo Features:")
    for key, feat in BUILTIN_FEATURES.items():
        print(f"  • {key.ljust(18)} -> Slot: {feat['slot']} ({feat['description']})")


def inject(feature_name: str):
    backup_if_needed()
    if feature_name not in BUILTIN_FEATURES:
        print(f"❌ Error: Unknown feature '{feature_name}'. Use 'list' to see available features.")
        sys.exit(1)

    feature = BUILTIN_FEATURES[feature_name]
    slot_tag = f"<!-- FEATURE_SLOT: {feature['slot']} -->"
    content = INDEX_FILE.read_text(encoding="utf-8")

    if slot_tag not in content:
        print(f"❌ Error: Slot tag '{slot_tag}' not found in index.html.")
        sys.exit(1)

    import re
    # If injecting a header variant, remove any previously injected header first
    if "HEADER" in feature['content']:
        content = re.sub(r'<!-- INJECTED_FEATURE: MODERN_HEADER -->.*?<!-- /INJECTED_FEATURE: MODERN_HEADER -->\s*', '', content, flags=re.DOTALL)
    if "AI_ADVISOR" in feature['content']:
        content = re.sub(r'<!-- INJECTED_FEATURE: AI_ADVISOR -->.*?<!-- /INJECTED_FEATURE: AI_ADVISOR -->\s*', '', content, flags=re.DOTALL)
    if "MULTIMODAL_CREDIT" in feature['content']:
        content = re.sub(r'<!-- INJECTED_FEATURE: MULTIMODAL_CREDIT -->.*?<!-- /INJECTED_FEATURE: MULTIMODAL_CREDIT -->\s*', '', content, flags=re.DOTALL)

    # Inject immediately after slot marker
    updated = content.replace(slot_tag, f"{slot_tag}\n{feature['content']}")
    INDEX_FILE.write_text(updated, encoding="utf-8")
    print(f"✅ Injected feature '{feature_name}' into slot '{feature['slot']}' successfully.")


def reset():
    if BACKUP_FILE.exists():
        INDEX_FILE.write_text(BACKUP_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        print("✅ Restored original pristine cloned index.html.")
    else:
        print("ℹ️ No backup found, index.html is already pristine.")


def main():
    parser = argparse.ArgumentParser(description="Jetski Feature Injector for Libertad Financiera")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List available demo features")
    subparsers.add_parser("reset", help="Reset index.html to pristine baseline")

    inj_parser = subparsers.add_parser("inject", help="Inject a feature")
    inj_parser.add_argument("feature", help="Feature name to inject")

    args = parser.parse_args()
    if args.command == "list":
        list_features()
    elif args.command == "inject":
        inject(args.feature)
    elif args.command == "reset":
        reset()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
