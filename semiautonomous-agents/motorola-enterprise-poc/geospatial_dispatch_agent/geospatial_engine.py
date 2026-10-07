import asyncio
import json
import os
import time
from google import genai
from google.genai import types
from mcp_connectors import (
    fetch_gdrive_async,
    fetch_salesforce_async,
    fetch_servicenow_async,
)

MODEL_ID = "gemini-3.8-flash"


def detect_geo_scenario(query: str, explicit_scenario: str | None = None) -> str:
  if explicit_scenario in (
      "miami_rf_outage",
      "metro_lpr_grid",
      "apco_vip_summit",
  ):
    return explicit_scenario
  q = query.lower()
  if any(
      k in q
      for k in [
          "metro",
          "chicago",
          "cook county",
          "district 4",
          "lpr",
          "avigilon",
          "inc0010002",
          "3.85m",
          "congestion",
          "saturation",
      ]
  ):
    return "metro_lpr_grid"
  if any(
      k in q
      for k in [
          "apco",
          "orlando",
          "vip",
          "summit",
          "hospitality",
          "sahil",
          "axon",
          "l3harris",
          "event",
          "row 3",
      ]
  ):
    return "apco_vip_summit"
  return "miami_rf_outage"


def render_geospatial_svg(scenario: str, asset_num: int) -> str:
  """Generates high-DPI vector Geospatial RF Tactical Maps (asset_num=1) and Telemetry/Battlecard Waveforms (asset_num=2)."""
  if scenario == "metro_lpr_grid":
    if asset_num == 1:
      return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 380" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#090D16"/><stop offset="100%" stop-color="#111827"/></linearGradient>
    <radialGradient id="congestion" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#EF4444" stop-opacity="0.55"/><stop offset="65%" stop-color="#F59E0B" stop-opacity="0.22"/><stop offset="100%" stop-color="#EF4444" stop-opacity="0"/></radialGradient>
    <radialGradient id="lprZone" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#06B6D4" stop-opacity="0.45"/><stop offset="100%" stop-color="#06B6D4" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="840" height="380" rx="14" fill="url(#bg)" stroke="#334155" stroke-width="1.5"/>
  <!-- Tactical Urban Street Grid & Lake Michigan Shoreline -->
  <path d="M620,0 L650,90 L690,190 L735,380 L840,380 L840,0 Z" fill="#0C2D48" opacity="0.55"/>
  <text x="735" y="160" fill="#38BDF8" font-family="system-ui,sans-serif" font-size="11" font-weight="700" opacity="0.8">LAKE MICHIGAN</text>
  <g stroke="#1E293B" stroke-width="1">
    <line x1="120" y1="0" x2="120" y2="380"/><line x1="240" y1="0" x2="240" y2="380"/><line x1="360" y1="0" x2="360" y2="380"/><line x1="480" y1="0" x2="480" y2="380"/><line x1="600" y1="0" x2="600" y2="380"/>
    <line x1="0" y1="80" x2="840" y2="80"/><line x1="0" y1="160" x2="840" y2="160"/><line x1="0" y1="240" x2="840" y2="240"/><line x1="0" y1="320" x2="840" y2="320"/>
  </g>
  <!-- Major Highway Corridors (I-90 / I-94 / State Pkwy) -->
  <path d="M90,380 L340,210 L450,80 L510,0" stroke="#475569" stroke-width="3.5" fill="none"/>
  <path d="M0,190 L340,210 L670,210" stroke="#475569" stroke-width="3" fill="none"/>
  <!-- District 4 RF Channel Saturation Hotspot (94.2%) -->
  <circle cx="385" cy="215" r="115" fill="url(#congestion)"/>
  <circle cx="385" cy="215" r="78" fill="none" stroke="#EF4444" stroke-width="1.5" stroke-dasharray="5 4"/>
  <!-- Avigilon Alta LPR Camera Corridors -->
  <circle cx="290" cy="155" r="65" fill="url(#lprZone)"/>
  <circle cx="490" cy="250" r="65" fill="url(#lprZone)"/>
  <!-- ASTRO 25 Trunked Site Pins -->
  <circle cx="385" cy="215" r="9" fill="#EF4444" stroke="#FFF" stroke-width="2"/>
  <text x="402" y="212" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="12" font-weight="800">DISTRICT 4 TRUNKED SITE (INC0010002)</text>
  <text x="402" y="227" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="11">94.2% Channel Saturation · 43.2M PTT Calls</text>
  <!-- Avigilon LPR Nodes -->
  <rect x="278" y="143" width="24" height="24" rx="6" fill="#06B6D4" stroke="#FFF" stroke-width="1.5"/>
  <text x="290" y="159" fill="#0F172A" font-family="system-ui,sans-serif" font-size="11" font-weight="800" text-anchor="middle">LPR</text>
  <text x="250" y="135" fill="#67E8F9" font-family="system-ui,sans-serif" font-size="11" font-weight="700">Avigilon Alta Corridor North (1200 N. State Pkwy)</text>
  <rect x="478" y="238" width="24" height="24" rx="6" fill="#06B6D4" stroke="#FFF" stroke-width="1.5"/>
  <text x="490" y="254" fill="#0F172A" font-family="system-ui,sans-serif" font-size="11" font-weight="800" text-anchor="middle">LPR</text>
  <text x="510" y="254" fill="#67E8F9" font-family="system-ui,sans-serif" font-size="11" font-weight="700">CommandCentral Aware RTCC Feed</text>
  <!-- Top HUD Banner -->
  <rect x="18" y="16" width="560" height="52" rx="10" fill="#0F172A" fill-opacity="0.92" stroke="#3B82F6" stroke-width="1.2"/>
  <text x="32" y="37" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="14" font-weight="800">🗺️ GEOSPATIAL RF &amp; LPR TACTICAL GRID — CITY OF METRO (COOK COUNTY, IL)</text>
  <text x="32" y="55" fill="#93C5FD" font-family="system-ui,sans-serif" font-size="11">Contract MUN-IL-884 ($2.60M Core + $1.25M Avigilon LPR Upsell = $3.85M · 12% Bundle Discount)</text>
  <!-- Bottom Legend Bar -->
  <rect x="18" y="328" width="804" height="36" rx="8" fill="#0F172A" fill-opacity="0.9" stroke="#334155"/>
  <circle cx="38" cy="346" r="6" fill="#EF4444"/><text x="50" y="350" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">P1 RF Congestion Zone (INC0010002 · 94.2%)</text>
  <circle cx="315" cy="346" r="6" fill="#06B6D4"/><text x="327" y="350" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">Avigilon Alta Cloud Video + LPR Overlay</text>
  <circle cx="585" cy="346" r="6" fill="#10B981"/><text x="597" y="350" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">Sponsor: Comm. Marcus Vance (45d Renewal)</text>
</svg>"""
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 250" width="100%" height="100%">
  <rect width="840" height="250" rx="14" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>
  <text x="26" y="32" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="15" font-weight="700">36-Month ASTRO 25 Push-To-Talk Saturation (43.2M Calls) vs. Cloud Video + LPR Offload</text>
  <line x1="65" y1="65" x2="795" y2="65" stroke="#EF4444" stroke-dasharray="4 4"/><text x="790" y="58" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="10" text-anchor="end">90% Critical Congestion Threshold</text>
  <polyline points="70,180 190,162 310,138 430,108 550,74 670,58 780,145" fill="none" stroke="#38BDF8" stroke-width="3.5"/>
  <circle cx="670" cy="58" r="6" fill="#EF4444" stroke="#FFF" stroke-width="1.5"/>
  <text x="665" y="45" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="end">Peak: 94.2% Saturation (INC0010002)</text>
  <circle cx="780" cy="145" r="6" fill="#10B981" stroke="#FFF" stroke-width="1.5"/>
  <text x="775" y="168" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="end">Post-Bundle: 61.4% (Healthy SLA)</text>
  <rect x="26" y="195" width="788" height="38" rx="8" fill="#1E293B"/>
  <text x="42" y="219" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="12" font-weight="600">📊 Commercial Bundle Math: $2.60M ASTRO 25 Core + $1.25M Avigilon Alta &amp; LPR = $3.85M List → $3.39M Net (12% Parent Discount)</text>
</svg>"""

  if scenario == "apco_vip_summit":
    if asset_num == 1:
      return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 380" width="100%" height="100%">
  <defs>
    <linearGradient id="bgApco" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#0B1120"/><stop offset="100%" stop-color="#1E1B4B"/></linearGradient>
  </defs>
  <rect width="840" height="380" rx="14" fill="url(#bgApco)" stroke="#4F46E5" stroke-width="1.5"/>
  <!-- Orlando Convention Center Floor & Hospitality Suites Map -->
  <rect x="40" y="80" width="500" height="230" rx="12" fill="#1E293B" stroke="#475569" stroke-width="1.5"/>
  <text x="60" y="106" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" font-weight="700">ORLANDO ORANGE COUNTY CONVENTION CENTER — APCO 2026 FLOOR MAP</text>
  <!-- Motorola VIP Hospitality Command Suite -->
  <rect x="65" y="122" width="230" height="168" rx="10" fill="#172554" stroke="#3B82F6" stroke-width="2"/>
  <text x="80" y="146" fill="#60A5FA" font-family="system-ui,sans-serif" font-size="13" font-weight="800">⭐ MOTOROLA VIP SUITE #A1</text>
  <circle cx="92" cy="175" r="6" fill="#10B981"/><text x="106" y="179" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="11" font-weight="700">Comm. Marcus Vance ($3.85M)</text>
  <circle cx="92" cy="205" r="6" fill="#10B981"/><text x="106" y="209" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="11" font-weight="700">Col. Elena Rostova ($5.20M)</text>
  <circle cx="92" cy="235" r="6" fill="#F59E0B"/><text x="106" y="239" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="11" font-weight="700">Sheriff Dietrich Keller ($1.95M)</text>
  <circle cx="92" cy="265" r="6" fill="#38BDF8"/><text x="106" y="269" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="11" font-weight="700">Dir. Henrik Lindqvist (VIP)</text>
  <!-- Competitor Booth Threat Zones -->
  <rect x="320" y="122" width="195" height="78" rx="8" fill="#3F1D2E" stroke="#F43F5E" stroke-width="1.5"/>
  <text x="335" y="145" fill="#FDA4AF" font-family="system-ui,sans-serif" font-size="12" font-weight="800">⚠️ AXON BOOTH #412</text>
  <text x="335" y="165" fill="#FFE4E6" font-family="system-ui,sans-serif" font-size="10">Pitching Fleet 3 + BWC SaaS Discount</text>
  <text x="335" y="182" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="10" font-weight="700">Counter: ASTRO 25 + Avigilon Interop</text>
  <rect x="320" y="212" width="195" height="78" rx="8" fill="#3B251E" stroke="#F97316" stroke-width="1.5"/>
  <text x="335" y="235" fill="#FDBA74" font-family="system-ui,sans-serif" font-size="12" font-weight="800">⚠️ L3HARRIS BOOTH #608</text>
  <text x="335" y="255" fill="#FFEDD5" font-family="system-ui,sans-serif" font-size="10">Pitching 15% P25 Radio Hardware Cut</text>
  <text x="335" y="272" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="10" font-weight="700">Counter: FIPS 140-3 Chip Delay Risk</text>
  <!-- Right Executive Pipeline Panel -->
  <rect x="560" y="80" width="245" height="230" rx="12" fill="#0F172A" stroke="#6366F1" stroke-width="1.5"/>
  <text x="580" y="110" fill="#A5B4FC" font-family="system-ui,sans-serif" font-size="12" font-weight="800">VIP DELEGATION PIPELINE</text>
  <text x="580" y="145" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="28" font-weight="800">$11.00M</text>
  <text x="580" y="165" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11">Total Attending Renewal ARR</text>
  <line x1="580" y1="185" x2="785" y2="185" stroke="#334155"/>
  <text x="580" y="210" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">• Host: Sahil Taank (Territory Catalyst)</text>
  <text x="580" y="232" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">• Intel: Jacky Chui (Competitive Dossier)</text>
  <text x="580" y="254" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="11" font-weight="700">• 4 Demo APX NEXT Radios Cleared (TMP)</text>
  <!-- Top HUD Banner -->
  <rect x="40" y="16" width="765" height="48" rx="10" fill="#0F172A" stroke="#6366F1" stroke-width="1.2"/>
  <text x="58" y="37" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="14" font-weight="800">🎯 APCO 2026 ORLANDO SUMMIT — VIP HOSPITALITY &amp; COMPETITIVE COMMAND MAP (ROW 3)</text>
  <text x="58" y="53" fill="#C7D2FE" font-family="system-ui,sans-serif" font-size="11">Live Sync across Google Calendar Reception Invite + Gmail Partner Alert + Drive Competitive Battlecards</text>
</svg>"""
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 240" width="100%" height="100%">
  <rect width="840" height="240" rx="14" fill="#0F172A" stroke="#4F46E5" stroke-width="1.5"/>
  <text x="26" y="32" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="15" font-weight="700">APCO 2026 Competitive Counter-Positioning Matrix (Jacky Chui Deep Research Dossier)</text>
  <rect x="26" y="52" width="385" height="165" rx="10" fill="#1E293B" stroke="#3B82F6"/>
  <text x="44" y="78" fill="#60A5FA" font-family="system-ui,sans-serif" font-size="13" font-weight="800">⚔️ VS. AXON ENTERPRISE (FLEET 3 / BWC SAAS)</text>
  <text x="44" y="104" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">• Competitor Trap: Aggressive camera discount tied to proprietary cloud</text>
  <text x="44" y="128" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">• Motorola Counter: Native ASTRO 25 mission-critical voice + Avigilon</text>
  <text x="44" y="148" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">  Alta video + CommandCentral Aware single-pane-of-glass dispatch</text>
  <text x="44" y="182" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="12" font-weight="700">✅ Target VIP: Comm. Marcus Vance ($3.85M City of Metro)</text>
  <rect x="429" y="52" width="385" height="165" rx="10" fill="#1E293B" stroke="#10B981"/>
  <text x="447" y="78" fill="#34D399" font-family="system-ui,sans-serif" font-size="13" font-weight="800">⚔️ VS. L3HARRIS (15% P25 HARDWARE DISCOUNT)</text>
  <text x="447" y="104" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">• Competitor Trap: Upfront 15% cap-ex discount on portable P25 radios</text>
  <text x="447" y="128" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">• Motorola Counter: Highlight L3Harris FIPS 140-3 AES-256 chip delays</text>
  <text x="447" y="148" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">  (9-month lead time) vs. Motorola immediate FIPS 140-3 stock + LTE</text>
  <text x="447" y="182" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="12" font-weight="700">✅ Target VIP: Col. Elena Rostova ($5.20M State Patrol)</text>
</svg>"""

  # Default: miami_rf_outage (Showstopper 2 Geospatial RF Outage & Field Dispatch Map)
  if asset_num == 1:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 390" width="100%" height="100%">
  <defs>
    <linearGradient id="bgMiami" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#070B14"/><stop offset="100%" stop-color="#0F172A"/></linearGradient>
    <radialGradient id="rfDeadZone" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#EF4444" stop-opacity="0.65"/><stop offset="55%" stop-color="#DC2626" stop-opacity="0.28"/><stop offset="100%" stop-color="#EF4444" stop-opacity="0"/></radialGradient>
    <radialGradient id="rfHealthy" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#10B981" stop-opacity="0.32"/><stop offset="100%" stop-color="#10B981" stop-opacity="0"/></radialGradient>
    <radialGradient id="lteMesh" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#3B82F6" stop-opacity="0.45"/><stop offset="100%" stop-color="#3B82F6" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="840" height="390" rx="14" fill="url(#bgMiami)" stroke="#334155" stroke-width="1.5"/>
  <!-- Biscayne Bay & Atlantic Coastline Vector Geometry -->
  <path d="M590,0 L615,110 L585,220 L635,310 L610,390 L840,390 L840,0 Z" fill="#082F49" opacity="0.65"/>
  <path d="M645,95 L665,195 L650,260 L670,255 L680,175 Z" fill="#1E293B" stroke="#475569" stroke-width="1"/>
  <text x="705" y="195" fill="#38BDF8" font-family="system-ui,sans-serif" font-size="11" font-weight="700" opacity="0.85">BISCAYNE BAY / MIAMI BEACH</text>
  <!-- GIS Coordinate Grid -->
  <g stroke="#1E293B" stroke-width="1">
    <line x1="140" y1="0" x2="140" y2="390"/><line x1="280" y1="0" x2="280" y2="390"/><line x1="420" y1="0" x2="420" y2="390"/><line x1="560" y1="0" x2="560" y2="390"/>
    <line x1="0" y1="90" x2="840" y2="90"/><line x1="0" y1="180" x2="840" y2="180"/><line x1="0" y1="270" x2="840" y2="270"/>
  </g>
  <!-- I-95 & Palmetto Expressway Corridors -->
  <path d="M465,0 L455,140 L440,260 L395,390" stroke="#475569" stroke-width="3.5" fill="none"/>
  <path d="M210,80 L455,140 L650,155" stroke="#475569" stroke-width="2.5" fill="none"/>
  <!-- Healthy ASTRO 25 Repeater Coverage Rings (Sites 1, 2, 3) -->
  <circle cx="240" cy="145" r="85" fill="url(#rfHealthy)" stroke="#10B981" stroke-width="1" stroke-dasharray="4 4"/>
  <circle cx="265" cy="295" r="80" fill="url(#rfHealthy)" stroke="#10B981" stroke-width="1" stroke-dasharray="4 4"/>
  <circle cx="510" cy="110" r="75" fill="url(#rfHealthy)" stroke="#10B981" stroke-width="1" stroke-dasharray="4 4"/>
  <!-- P1 Outage Dead Zone on Repeater Site 4 (INC0010007 — 18.4% Packet Loss) -->
  <circle cx="445" cy="235" r="108" fill="url(#rfDeadZone)"/>
  <circle cx="445" cy="235" r="92" fill="none" stroke="#EF4444" stroke-width="2" stroke-dasharray="6 4"/>
  <!-- APX NEXT SmartConnect LTE Failover Mesh Umbrella -->
  <circle cx="495" cy="215" r="70" fill="url(#lteMesh)" stroke="#60A5FA" stroke-width="1.5"/>
  <!-- Live Field Dispatch Vector Route: Unit #RF-104 -> Repeater Site 4 -->
  <path d="M315,175 L375,205 L445,235" stroke="#FBBF24" stroke-width="3" stroke-dasharray="6 4" fill="none"/>
  <!-- Healthy Site Pins -->
  <circle cx="240" cy="145" r="6" fill="#10B981" stroke="#FFF" stroke-width="1.5"/><text x="175" y="133" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="10" font-weight="700">SITE 1 (Doral · 99.99%)</text>
  <circle cx="265" cy="295" r="6" fill="#10B981" stroke="#FFF" stroke-width="1.5"/><text x="195" y="314" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="10" font-weight="700">SITE 2 (Kendall · 99.98%)</text>
  <circle cx="510" cy="110" r="6" fill="#10B981" stroke="#FFF" stroke-width="1.5"/><text x="455" y="96" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="10" font-weight="700">SITE 3 (North Dade · 99.99%)</text>
  <!-- Field Engineering Truck Pin (#RF-104) -->
  <rect x="298" y="162" width="28" height="22" rx="5" fill="#F59E0B" stroke="#FFF" stroke-width="1.5"/>
  <text x="312" y="177" fill="#0F172A" font-family="system-ui,sans-serif" font-size="10" font-weight="800" text-anchor="middle">RF</text>
  <text x="210" y="198" fill="#FDE68A" font-family="system-ui,sans-serif" font-size="11" font-weight="700">🚐 Unit #RF-104 (ETA 11 min · 4.2 mi)</text>
  <!-- P1 Critical Outage Repeater Site 4 Pin -->
  <circle cx="445" cy="235" r="10" fill="#EF4444" stroke="#FFF" stroke-width="2.5"/>
  <text x="462" y="232" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="12" font-weight="800">🚨 REPEATER SITE 4 — P1 OUTAGE (INC0010007)</text>
  <text x="462" y="248" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="11">25.7907° N, 80.1300° W · 18.4% Packet Loss · RSSI -114 dBm</text>
  <text x="462" y="264" fill="#93C5FD" font-family="system-ui,sans-serif" font-size="11" font-weight="700">⚡ APX NEXT SmartConnect LTE Failover Ready (0.02% Loss)</text>
  <!-- Top HUD Command Overlay -->
  <rect x="18" y="14" width="605" height="52" rx="10" fill="#0F172A" fill-opacity="0.92" stroke="#EF4444" stroke-width="1.4"/>
  <text x="32" y="35" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="14" font-weight="800">📡 LIVE GEOSPATIAL RF OUTAGE &amp; FIELD DISPATCH MAP — MIAMI-DADE (INC0010007)</text>
  <text x="32" y="53" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="11">Salesforce Opp 006jV000001CIWrQAO ($1,950,000 Renewal at Risk) · ServiceNow Priority-1 Outage Active</text>
  <!-- Bottom Telemetry Legend Bar -->
  <rect x="18" y="338" width="804" height="36" rx="8" fill="#0F172A" fill-opacity="0.92" stroke="#334155"/>
  <circle cx="38" cy="356" r="6" fill="#EF4444"/><text x="50" y="360" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">P1 RF Packet Loss Zone (18.4%)</text>
  <circle cx="245" cy="356" r="6" fill="#3B82F6"/><text x="257" y="360" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">APX NEXT SmartConnect LTE Mesh</text>
  <circle cx="475" cy="356" r="6" fill="#F59E0B"/><text x="487" y="360" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">Field Unit #RF-104 Dispatch Route</text>
  <circle cx="695" cy="356" r="6" fill="#10B981"/><text x="707" y="360" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="11">Sites 1–3 Healthy</text>
</svg>"""

  return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 250" width="100%" height="100%">
  <rect width="840" height="250" rx="14" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>
  <text x="26" y="32" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="15" font-weight="700">Real-Time ASTRO 25 Repeater Site 4 RF Packet Loss (%) vs. Automatic APX NEXT LTE Failover</text>
  <line x1="65" y1="70" x2="795" y2="70" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="65" y1="125" x2="795" y2="125" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="65" y1="175" x2="795" y2="175" stroke="#475569" stroke-width="1.5"/>
  <text x="55" y="75" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="11" text-anchor="end">20%</text>
  <text x="55" y="130" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="end">10%</text>
  <text x="55" y="179" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="11" text-anchor="end">0%</text>
  <!-- LMR Packet Loss Spike Curve -->
  <polyline points="70,172 170,171 260,169 340,78 430,74 510,79 560,173 680,174 790,174" fill="none" stroke="#EF4444" stroke-width="3.5"/>
  <circle cx="430" cy="74" r="6" fill="#EF4444" stroke="#FFF" stroke-width="1.5"/>
  <text x="430" y="58" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="middle">P1 Outage Spike: 18.4% Loss (INC0010007)</text>
  <circle cx="560" cy="173" r="6" fill="#10B981" stroke="#FFF" stroke-width="1.5"/>
  <text x="675" y="158" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="middle">APX NEXT LTE Failover Triggered (&lt;80ms) → 0.02% Loss</text>
  <rect x="26" y="196" width="788" height="38" rx="8" fill="#1E293B"/>
  <text x="42" y="220" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="12" font-weight="600">⚡ Turnaround Pitch: Dispatch Field Unit #RF-104 + Apply Pre-Approved 20% Executive Retention Discount on $1.95M Renewal</text>
</svg>"""


async def generate_geospatial_flash_brief(
    scenario: str,
    query: str,
    sfdc_data: dict,
    snow_data: dict,
    drive_data: dict,
) -> str:
  """Generates an ultra-crisp 5-line Executive Geospatial & Field Dispatch Flash Brief."""
  sfdc_rec = (sfdc_data.get("records") or [{}])[0]
  snow_rec = (snow_data.get("records") or [{}])[0]
  inc_num = snow_rec.get("number", "INC0010007")
  sfdc_id = sfdc_rec.get("Id", "006jV000001CIWrQAO")

  if scenario == "metro_lpr_grid":
    return (
        "### 🗺️ Executive Geospatial RF & LPR Grid Brief — City of Metro Public Safety\n"
        "- **Live Geospatial Correlation**: District 4 Trunked Site (`Cook County, IL`) is operating at **94.2% channel saturation** (`43.2M` 36-month PTT calls) with active Priority-1 Incident **`INC0010002`**.\n"
        "- **Salesforce Contract Exposure**: Renewal **`MUN-IL-884`** (`001jV000009Im4DQAS`) represents **$2,600,000** in core ASTRO 25 ARR closing in **45 days** (Decision Maker: **Commissioner Marcus Vance**).\n"
        "- **Geospatial Offload Architecture**: Deploying **Avigilon Alta Cloud Video + LPR Corridors** along `1200 N. State Pkwy` + **CommandCentral Aware** offloads routine dispatch voice traffic to drop saturation to **61.4%**.\n"
        "- **Pre-Approved Commercial Offer**: Bundles **$2.60M ASTRO 25 Core + $1.25M Avigilon Video/LPR Upsell ($3.85M Total)** with Motorola's **12% Public Sector Parent Bundle Discount ($3.39M Net)**."
    )

  if scenario == "apco_vip_summit":
    return (
        "### 🎯 APCO 2026 Orlando Summit — VIP Delegation & Competitive Command Brief (Row 3)\n"
        "- **VIP Hospitality Attendance ($11.0M Pipeline)**: Live sync across **Sahil Taank's** Gmail alerts & Google Calendar confirms **Commissioner Marcus Vance ($3.85M)**, **Colonel Elena Rostova ($5.20M)**, **Sheriff Dietrich Keller ($1.95M)**, and **Director Henrik Lindqvist** in **Motorola VIP Suite #A1**.\n"
        "- **Countering Axon Enterprise (Booth #412)**: Neutralize Axon Fleet 3 + BWC SaaS discounting by demonstrating native **ASTRO 25 P25 Voice + Avigilon Alta Cloud Video + CommandCentral Aware** unified dispatch interoperability.\n"
        "- **Countering L3Harris (Booth #608)**: Neutralize L3Harris 15% P25 hardware discounts by exposing their **9-month FIPS 140-3 encryption chip supply chain delay** vs. immediate Motorola APX NEXT delivery.\n"
        "- **Export Compliance Clearance**: **4 AES-256 FIPS 140-3 APX NEXT demo radios** cleared under ServiceNow **`INC0010005` (`License Exception TMP`)** for live VIP suite demonstrations."
    )

  return (
      f"### 📡 Live Geospatial RF Outage & Field Dispatch Brief — Miami-Dade (`{inc_num}`)\n"
      f"- **Geospatial Fault Pinpoint**: **Repeater Site 4 (`25.7907° N, 80.1300° W`)** is experiencing an active Priority-1 RF outage (**`{inc_num}`**) with **18.4% trunked audio packet loss** and `-114 dBm` RSSI floor.\n"
      f"- **Commercial Renewal Exposure**: Directly impacts Salesforce Opportunity **`{sfdc_id}`** (**$1,950,000.00** ASTRO 25 Renewal in `Negotiation/Review`, closing `2026-10-15`).\n"
      "- **Automated Field & LTE Failover Action**: **Field Engineering Unit `#RF-104`** routed to Site 4 (**ETA 11 mins / 4.2 mi**), while **APX NEXT SmartConnect LTE Failover** switches first responders to broadband in `<80ms` (`0.02%` loss).\n"
      "- **Executive Turnaround Playbook**: Authorize pre-approved **20% Executive Retention Discount** on `$1.95M` renewal bundled with **APX NEXT SmartConnect + CommandCentral Aware**."
  )


def build_geospatial_a2ui_messages(
    scenario: str,
    sfdc_rec: dict,
    snow_rec: dict,
    drive_doc: dict,
    base_url: str,
) -> tuple[dict, dict, list[dict]]:
  """Constructs native GA A2UI v0.9 (createSurface -> updateComponents -> updateDataModel) & v0.8 messages."""
  inc_num = snow_rec.get("number", "INC0010007")
  sfdc_id = sfdc_rec.get("Id", "006jV000001CIWrQAO")
  surface_id = f"motorola-geo-surface-{scenario}-{int(time.time())}"

  map_url = f"{base_url}/api/geo/{scenario}/1.svg"
  chart_url = f"{base_url}/api/geo/{scenario}/2.svg"

  if scenario == "metro_lpr_grid":
    title_str = "🗺️ Motorola Geospatial RF & Avigilon LPR Grid — City of Metro (INC0010002)"
    subtitle_str = "Live GIS & Telemetry Overlay: Cook County District 4 (94.2% Saturation) + Contract MUN-IL-884 ($3.85M Bundle)"
    kpi1_title = "📡 94.2% → 61.4%"
    kpi1_sub = "District 4 RF Congestion Offloaded via LPR"
    kpi2_title = "💰 $2.60M → $3.85M"
    kpi2_sub = "+$1.25M Avigilon Video & LPR Upsell (12% Off)"
    kpi3_title = "🏛️ Comm. M. Vance"
    kpi3_sub = "45 Days to Expiration · War Room Scheduled"
    primary_btn_label = "⚡ Authorize $3.85M Avigilon LPR Bundle & Patch ServiceNow (INC0010002)"
    primary_inc = "INC0010002"
    sec1_label = "📡 Switch to Miami-Dade Live RF Outage Map ($1.95M)"
    sec1_target = "miami_rf_outage"
    sec2_label = "🎯 Switch to APCO 2026 Orlando VIP & Competitor Map ($11.0M)"
    sec2_target = "apco_vip_summit"
    map_heading = "🗺️ Geospatial Tactical Grid: District 4 RF Congestion & Avigilon Alta LPR Corridors"
    chart_heading = "📈 36-Month ASTRO 25 PTT Volume (43.2M Calls) & Post-Bundle Offload Trajectory"
    ev_row1 = "🏢 Salesforce Account (001jV000009Im4DQAS): City of Metro Public Safety — $2.60M Core Renewal + $1.25M Cloud Video Upsell"
    ev_row2 = "🚨 ServiceNow Incident (INC0010002): District 4 Trunked RF Channel 4 Packet Loss at 94.2% Peak Capacity"
    ev_row3 = "📜 Google Drive Playbook: Pre-approves 12% Public Sector Parent Bundle Discount when combining ASTRO 25 + Avigilon Alta"
  elif scenario == "apco_vip_summit":
    title_str = "🎯 Motorola APCO 2026 Summit — VIP Hospitality & Competitive Command Deck (Row 3)"
    subtitle_str = "Orlando Convention Center Floor Map: $11.00M Attending VIP Pipeline + Live Axon & L3Harris Counter-Playbooks"
    kpi1_title = "🏆 $11.00M Pipeline"
    kpi1_sub = "4 VIP Delegations Confirmed in Suite #A1"
    kpi2_title = "⚔️ Axon & L3Harris"
    kpi2_sub = "Booth #412 & #608 Counter-Playbooks Armed"
    kpi3_title = "📻 4 APX NEXT Cleared"
    kpi3_sub = "FIPS 140-3 AES-256 License Exception TMP"
    primary_btn_label = "⚡ Dispatch VIP Hospitality Briefing & Log ServiceNow Export Clearance (INC0010005)"
    primary_inc = "INC0010005"
    sec1_label = "📡 Switch to Miami-Dade Live RF Outage Map ($1.95M)"
    sec1_target = "miami_rf_outage"
    sec2_label = "🗺️ Switch to City of Metro District 4 LPR Grid ($3.85M)"
    sec2_target = "metro_lpr_grid"
    map_heading = "🗺️ APCO 2026 Floor Map: Motorola VIP Suite #A1 vs. Competitor Booth Threat Zones"
    chart_heading = "⚔️ Executive Competitive Counter-Matrix (Axon Fleet 3 vs. L3Harris P25)"
    ev_row1 = "📅 Google Calendar & Gmail Sync: Sahil Taank VIP Reception confirmed for Vance ($3.85M), Rostova ($5.2M), Keller ($1.95M)"
    ev_row2 = "🛡️ Jacky Chui Competitive Dossier: Neutralizes Axon SaaS bundle & exposes L3Harris 9-month FIPS 140-3 chip delay"
    ev_row3 = "🛃 ServiceNow Export Clearance (INC0010005): Authorizes hand-carry of 4 AES-256 encrypted APX NEXT radios under TMP"
  else:
    title_str = f"📡 Motorola Geospatial RF Outage & Field Dispatch Command — Miami-Dade ({inc_num})"
    subtitle_str = f"Live GIS Telemetry: Repeater Site 4 Outage ({inc_num}) · Field Unit #RF-104 Dispatch · Salesforce Deal {sfdc_id} ($1.95M)"
    kpi1_title = "🚨 Site 4: 18.4% Loss"
    kpi1_sub = "25.7907° N, 80.1300° W · RSSI -114 dBm"
    kpi2_title = "🚐 Unit #RF-104: 11m"
    kpi2_sub = "Dispatched (4.2 mi) + APX NEXT LTE <80ms"
    kpi3_title = "💰 $1.95M Protected"
    kpi3_sub = "20% Executive Retention Discount Ready"
    primary_btn_label = f"🚀 Dispatch Unit #RF-104, Activate LTE Failover & Patch ServiceNow ({inc_num})"
    primary_inc = inc_num
    sec1_label = "🗺️ Switch to City of Metro District 4 LPR Grid ($3.85M)"
    sec1_target = "metro_lpr_grid"
    sec2_label = "🎯 Switch to APCO 2026 Orlando VIP & Competitor Map ($11.0M)"
    sec2_target = "apco_vip_summit"
    map_heading = "🗺️ Live Geospatial RF Outage Map: Repeater Site 4 Dead Zone, Field Unit #RF-104 & LTE Mesh"
    chart_heading = "📉 Real-Time ASTRO 25 Packet Loss (%) & Sub-80ms APX NEXT LTE Failover Curve"
    ev_row1 = f"🏢 Salesforce Opportunity ({sfdc_id}): Miami-Dade Dispatch Renewal ($1,950,000 · Stage: Negotiation · Close: 2026-10-15)"
    ev_row2 = f"🚨 ServiceNow P1 Incident ({inc_num}): Repeater Site 4 RF Packet Loss (18.4%) — Field Unit #RF-104 routed (ETA 11 min)"
    ev_row3 = "📜 Google Drive Governance Playbook: Authorizes 20% Executive Retention Override + APX NEXT SmartConnect LTE Failover"

  v09_messages = [
      {
          "version": "v0.9",
          "createSurface": {
              "surfaceId": surface_id,
              "catalogId": "https://a2ui.org/specification/v0_9/basic_catalog.json",
          },
      },
      {
          "version": "v0.9",
          "updateComponents": {
              "surfaceId": surface_id,
              "components": [
                  {
                      "id": "root",
                      "component": "Column",
                      "align": "stretch",
                      "children": [
                          "header_card",
                          "kpi_row",
                          "map_card",
                          "chart_card",
                          "evidence_card",
                          "action_card",
                      ],
                  },
                  {"id": "header_card", "component": "Card", "child": "header_col"},
                  {"id": "header_col", "component": "Column", "children": ["deck_title", "deck_subtitle"]},
                  {"id": "deck_title", "component": "Text", "variant": "h2", "text": title_str},
                  {"id": "deck_subtitle", "component": "Text", "variant": "caption", "text": subtitle_str},
                  {
                      "id": "kpi_row",
                      "component": "Row",
                      "justify": "spaceBetween",
                      "children": ["kpi_card_1", "kpi_card_2", "kpi_card_3"],
                  },
                  {"id": "kpi_card_1", "component": "Card", "child": "kpi_col_1"},
                  {"id": "kpi_col_1", "component": "Column", "children": ["kpi1_h", "kpi1_s"]},
                  {"id": "kpi1_h", "component": "Text", "variant": "h3", "text": kpi1_title},
                  {"id": "kpi1_s", "component": "Text", "variant": "caption", "text": kpi1_sub},
                  {"id": "kpi_card_2", "component": "Card", "child": "kpi_col_2"},
                  {"id": "kpi_col_2", "component": "Column", "children": ["kpi2_h", "kpi2_s"]},
                  {"id": "kpi2_h", "component": "Text", "variant": "h3", "text": kpi2_title},
                  {"id": "kpi2_s", "component": "Text", "variant": "caption", "text": kpi2_sub},
                  {"id": "kpi_card_3", "component": "Card", "child": "kpi_col_3"},
                  {"id": "kpi_col_3", "component": "Column", "children": ["kpi3_h", "kpi3_s"]},
                  {"id": "kpi3_h", "component": "Text", "variant": "h3", "text": kpi3_title},
                  {"id": "kpi3_s", "component": "Text", "variant": "caption", "text": kpi3_sub},
                  {"id": "map_card", "component": "Card", "child": "map_col"},
                  {"id": "map_col", "component": "Column", "align": "stretch", "children": ["map_heading", "map_img"]},
                  {"id": "map_heading", "component": "Text", "variant": "h3", "text": map_heading},
                  {"id": "map_img", "component": "Image", "url": map_url, "fit": "contain"},
                  {"id": "chart_card", "component": "Card", "child": "chart_col"},
                  {"id": "chart_col", "component": "Column", "align": "stretch", "children": ["chart_heading", "chart_img"]},
                  {"id": "chart_heading", "component": "Text", "variant": "h3", "text": chart_heading},
                  {"id": "chart_img", "component": "Image", "url": chart_url, "fit": "contain"},
                  {"id": "evidence_card", "component": "Card", "child": "evidence_col"},
                  {
                      "id": "evidence_col",
                      "component": "Column",
                      "children": ["ev_header", "ev_div", "ev_t1", "ev_t2", "ev_t3"],
                  },
                  {
                      "id": "ev_header",
                      "component": "Text",
                      "variant": "h3",
                      "text": "🔍 Live Multi-System MCP Telemetry & Grounded Citations",
                  },
                  {"id": "ev_div", "component": "Divider", "axis": "horizontal"},
                  {"id": "ev_t1", "component": "Text", "variant": "body", "text": ev_row1},
                  {"id": "ev_t2", "component": "Text", "variant": "body", "text": ev_row2},
                  {"id": "ev_t3", "component": "Text", "variant": "body", "text": ev_row3},
                  {"id": "action_card", "component": "Card", "child": "action_col"},
                  {
                      "id": "action_col",
                      "component": "Column",
                      "children": ["action_header", "btn_primary", "btn_sec_row"],
                  },
                  {
                      "id": "action_header",
                      "component": "Text",
                      "variant": "h3",
                      "text": "⚡ Live Field Dispatch, ServiceNow Write-Back & Geospatial View Switcher",
                  },
                  {"id": "btn_label", "component": "Text", "text": primary_btn_label},
                  {
                      "id": "btn_primary",
                      "component": "Button",
                      "child": "btn_label",
                      "variant": "primary",
                      "action": {
                          "event": {
                              "name": "approve_executive_override",
                              "context": {
                                  "incident_number": primary_inc,
                                  "sfdc_id": sfdc_id,
                                  "scenario": scenario,
                              },
                          }
                      },
                  },
                  {
                      "id": "btn_sec_row",
                      "component": "Row",
                      "justify": "spaceBetween",
                      "children": ["btn_sec1", "btn_sec2"],
                  },
                  {"id": "btn_sec1_txt", "component": "Text", "text": sec1_label},
                  {
                      "id": "btn_sec1",
                      "component": "Button",
                      "child": "btn_sec1_txt",
                      "action": {
                          "event": {
                              "name": "switch_scenario",
                              "context": {"scenario": sec1_target},
                          }
                      },
                  },
                  {"id": "btn_sec2_txt", "component": "Text", "text": sec2_label},
                  {
                      "id": "btn_sec2",
                      "component": "Button",
                      "child": "btn_sec2_txt",
                      "action": {
                          "event": {
                              "name": "switch_scenario",
                              "context": {"scenario": sec2_target},
                          }
                      },
                  },
              ],
          },
      },
      {
          "version": "v0.9",
          "updateDataModel": {
              "surfaceId": surface_id,
              "path": "/",
              "value": {
                  "scenario": scenario,
                  "sfdcId": sfdc_id,
                  "incidentNumber": primary_inc,
              },
          },
      },
  ]

  v08_begin = {"beginRendering": {"surfaceId": surface_id, "root": "root"}}
  v08_update = {
      "surfaceUpdate": {
          "surfaceId": surface_id,
          "components": [
              {
                  "id": "root",
                  "component": {
                      "Column": {
                          "children": {
                              "explicitList": [
                                  "deck_header_card",
                                  "kpi_row",
                                  "map_card",
                                  "chart_card",
                                  "action_card",
                              ]
                          },
                          "alignment": "stretch",
                      }
                  },
              },
              {"id": "deck_header_card", "component": {"Card": {"child": "deck_header_col"}}},
              {"id": "deck_header_col", "component": {"Column": {"children": {"explicitList": ["deck_title", "deck_subtitle"]}}}},
              {"id": "deck_title", "component": {"Text": {"text": {"literalString": title_str}, "usageHint": "h2"}}},
              {"id": "deck_subtitle", "component": {"Text": {"text": {"literalString": subtitle_str}, "usageHint": "caption"}}},
              {"id": "kpi_row", "component": {"Row": {"children": {"explicitList": ["kpi_card_1", "kpi_card_2", "kpi_card_3"]}, "distribution": "spaceBetween"}}},
              {"id": "kpi_card_1", "component": {"Card": {"child": "kpi_col_1"}}},
              {"id": "kpi_col_1", "component": {"Column": {"children": {"explicitList": ["kpi1_h", "kpi1_s"]}}}},
              {"id": "kpi1_h", "component": {"Text": {"text": {"literalString": kpi1_title}, "usageHint": "h3"}}},
              {"id": "kpi1_s", "component": {"Text": {"text": {"literalString": kpi1_sub}, "usageHint": "caption"}}},
              {"id": "kpi_card_2", "component": {"Card": {"child": "kpi_col_2"}}},
              {"id": "kpi_col_2", "component": {"Column": {"children": {"explicitList": ["kpi2_h", "kpi2_s"]}}}},
              {"id": "kpi2_h", "component": {"Text": {"text": {"literalString": kpi2_title}, "usageHint": "h3"}}},
              {"id": "kpi2_s", "component": {"Text": {"text": {"literalString": kpi2_sub}, "usageHint": "caption"}}},
              {"id": "kpi_card_3", "component": {"Card": {"child": "kpi_col_3"}}},
              {"id": "kpi_col_3", "component": {"Column": {"children": {"explicitList": ["kpi3_h", "kpi3_s"]}}}},
              {"id": "kpi3_h", "component": {"Text": {"text": {"literalString": kpi3_title}, "usageHint": "h3"}}},
              {"id": "kpi3_s", "component": {"Text": {"text": {"literalString": kpi3_sub}, "usageHint": "caption"}}},
              {"id": "map_card", "component": {"Card": {"child": "map_col"}}},
              {"id": "map_col", "component": {"Column": {"children": {"explicitList": ["map_heading", "map_img"]}}}},
              {"id": "map_heading", "component": {"Text": {"text": {"literalString": map_heading}, "usageHint": "h3"}}},
              {"id": "map_img", "component": {"Image": {"url": {"literalString": map_url}}}},
              {"id": "chart_card", "component": {"Card": {"child": "chart_col"}}},
              {"id": "chart_col", "component": {"Column": {"children": {"explicitList": ["chart_heading", "chart_img"]}}}},
              {"id": "chart_heading", "component": {"Text": {"text": {"literalString": chart_heading}, "usageHint": "h3"}}},
              {"id": "chart_img", "component": {"Image": {"url": {"literalString": chart_url}}}},
              {"id": "action_card", "component": {"Card": {"child": "action_col"}}},
              {"id": "action_col", "component": {"Column": {"children": {"explicitList": ["btn_primary"]}}}},
              {"id": "btn_primary_txt", "component": {"Text": {"text": {"literalString": primary_btn_label}}}},
              {
                  "id": "btn_primary",
                  "component": {
                      "Button": {
                          "child": "btn_primary_txt",
                          "primary": True,
                          "action": {
                              "name": "approve_executive_override",
                              "context": [
                                  {"key": "incident_number", "value": {"literalString": primary_inc}},
                                  {"key": "sfdc_id", "value": {"literalString": sfdc_id}},
                                  {"key": "scenario", "value": {"literalString": scenario}},
                              ],
                          },
                      }
                  },
              },
          ],
      }
  }

  return v08_begin, v08_update, v09_messages


async def run_geospatial_dispatch_agent(
    query: str,
    base_url: str,
    explicit_scenario: str | None = None,
) -> dict:
  t0 = time.monotonic()
  scenario = detect_geo_scenario(query, explicit_scenario)
  sfdc_data, snow_data, drive_data = await asyncio.gather(
      fetch_salesforce_async(query),
      fetch_servicenow_async(query),
      fetch_gdrive_async(query),
  )
  flash_brief = await generate_geospatial_flash_brief(
      scenario, query, sfdc_data, snow_data, drive_data
  )
  sfdc_rec = (sfdc_data.get("records") or [{}])[0]
  snow_rec = (snow_data.get("records") or [{}])[0]
  drive_doc = drive_data.get("document") or {}
  v08_begin, v08_update, v09_messages = build_geospatial_a2ui_messages(
      scenario, sfdc_rec, snow_rec, drive_doc, base_url
  )
  return {
      "scenario": scenario,
      "flash_brief": flash_brief,
      "v08_begin": v08_begin,
      "v08_update": v08_update,
      "v09_messages": v09_messages,
      "latency_ms": int((time.monotonic() - t0) * 1000),
  }
