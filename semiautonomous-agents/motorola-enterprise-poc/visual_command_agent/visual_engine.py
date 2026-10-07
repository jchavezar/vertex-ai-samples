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


def detect_scenario(query: str, explicit_scenario: str | None = None) -> str:
  if explicit_scenario in (
      "deal_restructuring",
      "portfolio_war_room",
      "tariff_redline_sim",
  ):
    return explicit_scenario
  q = query.lower()
  if any(
      k in q
      for k in [
          "portfolio",
          "war room",
          "all accounts",
          "national",
          "highway patrol",
          "9.75m",
          "pipeline",
      ]
  ):
    return "portfolio_war_room"
  if any(
      k in q
      for k in [
          "tariff",
          "hts",
          "customs",
          "redline",
          "legal",
          "inc0010004",
          "inc0010006",
          "duty",
          "liability",
      ]
  ):
    return "tariff_redline_sim"
  return "deal_restructuring"


def render_svg_chart(scenario: str, chart_num: int) -> str:
  """Generates high-DPI boardroom-grade vector SVG executive charts for A2UI v0.9 Image cards."""
  if scenario == "portfolio_war_room":
    if chart_num == 1:
      return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 340" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0F172A"/><stop offset="100%" stop-color="#1E293B"/></linearGradient>
    <linearGradient id="risk" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#94A3B8"/><stop offset="100%" stop-color="#475569"/></linearGradient>
    <linearGradient id="post" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#3B82F6"/><stop offset="100%" stop-color="#1D4ED8"/></linearGradient>
  </defs>
  <rect width="820" height="340" rx="14" fill="url(#bg)" stroke="#334155" stroke-width="1.5"/>
  <text x="28" y="34" fill="#F8FAFC" font-family="system-ui,-apple-system,sans-serif" font-size="16" font-weight="700">National Public Safety Pipeline: Baseline At Risk vs. Post-Playbook Protected ARR ($M USD)</text>
  <text x="28" y="54" fill="#94A3B8" font-family="system-ui,-apple-system,sans-serif" font-size="12">Live Salesforce CRM Synthesis across Top 3 Public Safety Accounts (Total: $9.75M Baseline → $10.42M Protected)</text>
  <rect x="520" y="20" width="14" height="14" rx="3" fill="url(#risk)"/><text x="540" y="31" fill="#CBD5E1" font-family="system-ui,sans-serif" font-size="12">Baseline ARR ($M)</text>
  <rect x="665" y="20" width="14" height="14" rx="3" fill="url(#post)"/><text x="685" y="31" fill="#93C5FD" font-family="system-ui,sans-serif" font-size="12" font-weight="600">Post-Playbook ARR ($M)</text>
  <line x1="70" y1="85" x2="780" y2="85" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="70" y1="145" x2="780" y2="145" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="70" y1="205" x2="780" y2="205" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="70" y1="265" x2="780" y2="265" stroke="#475569" stroke-width="1.5"/>
  <text x="58" y="90" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="end">$6.0M</text>
  <text x="58" y="150" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="end">$4.0M</text>
  <text x="58" y="210" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="end">$2.0M</text>
  <text x="58" y="269" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="end">$0</text>
  <rect x="135" y="109" width="52" height="156" rx="6" fill="url(#risk)"/>
  <text x="161" y="101" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$5.20M</text>
  <rect x="195" y="101" width="52" height="164" rx="6" fill="url(#post)"/>
  <text x="221" y="93" fill="#60A5FA" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$5.45M (+4.8%)</text>
  <text x="191" y="292" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700" text-anchor="middle">State Highway Patrol</text>
  <text x="191" y="310" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">INC0010004 · HTS Tariff Cleared</text>
  <rect x="375" y="187" width="52" height="78" rx="6" fill="url(#risk)"/>
  <text x="401" y="179" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$2.60M</text>
  <rect x="435" y="175" width="52" height="90" rx="6" fill="url(#post)"/>
  <text x="461" y="167" fill="#60A5FA" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$2.99M (+15%)</text>
  <text x="431" y="292" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700" text-anchor="middle">City of Metro Police</text>
  <text x="431" y="310" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">INC0010006 · 2.0x Cap Enforced</text>
  <rect x="615" y="206" width="52" height="59" rx="6" fill="url(#risk)"/>
  <text x="641" y="198" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$1.95M</text>
  <rect x="675" y="205" width="52" height="60" rx="6" fill="url(#post)"/>
  <text x="701" y="197" fill="#60A5FA" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$1.98M (+1.5%)</text>
  <text x="671" y="292" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700" text-anchor="middle">Miami-Dade Dispatch</text>
  <text x="671" y="310" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">INC0010007 · APX NEXT LTE Failover</text>
</svg>"""
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 260" width="100%" height="100%">
  <rect width="820" height="260" rx="14" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>
  <text x="28" y="34" fill="#F8FAFC" font-family="system-ui,-apple-system,sans-serif" font-size="16" font-weight="700">Executive Portfolio Allocation &amp; Governance Health Breakdown ($10.42M Post-Playbook)</text>
  <circle cx="170" cy="148" r="76" fill="none" stroke="#1E293B" stroke-width="28"/>
  <circle cx="170" cy="148" r="76" fill="none" stroke="#2563EB" stroke-width="28" stroke-dasharray="250 478" transform="rotate(-90 170 148)"/>
  <circle cx="170" cy="148" r="76" fill="none" stroke="#0EA5E9" stroke-width="28" stroke-dasharray="137 478" stroke-dashoffset="-250" transform="rotate(-90 170 148)"/>
  <circle cx="170" cy="148" r="76" fill="none" stroke="#10B981" stroke-width="28" stroke-dasharray="91 478" stroke-dashoffset="-387" transform="rotate(-90 170 148)"/>
  <text x="170" y="144" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="18" font-weight="800" text-anchor="middle">$10.42M</text>
  <text x="170" y="162" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">Total Protected</text>
  <rect x="310" y="75" width="470" height="48" rx="8" fill="#1E293B" stroke="#334155"/>
  <circle cx="334" cy="99" r="7" fill="#2563EB"/>
  <text x="352" y="96" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700">State Highway Patrol — $5.45M ARR (52.3% Share)</text>
  <text x="352" y="113" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11">HTS 8517.62.00 0% Duty Ruling Applied · +$250K APX Expansion Locked</text>
  <rect x="310" y="133" width="470" height="48" rx="8" fill="#1E293B" stroke="#334155"/>
  <circle cx="334" cy="157" r="7" fill="#0EA5E9"/>
  <text x="352" y="154" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700">City of Metro Police — $2.99M ARR (28.7% Share)</text>
  <text x="352" y="171" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11">Procurement 2.0x Liability Cap Enforced · +$390K CommandCentral Expansion</text>
  <rect x="310" y="191" width="470" height="48" rx="8" fill="#1E293B" stroke="#334155"/>
  <circle cx="334" cy="215" r="7" fill="#10B981"/>
  <text x="352" y="212" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700">Miami-Dade Dispatch — $1.98M ARR (19.0% Share)</text>
  <text x="352" y="229" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11">20% Retention Override + APX NEXT SmartConnect LTE Failover (0.02% Loss)</text>
</svg>"""

  if scenario == "tariff_redline_sim":
    if chart_num == 1:
      return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 330" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0F172A"/><stop offset="100%" stop-color="#1E293B"/></linearGradient>
    <linearGradient id="bad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#EF4444"/><stop offset="100%" stop-color="#B91C1C"/></linearGradient>
    <linearGradient id="good" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#10B981"/><stop offset="100%" stop-color="#047857"/></linearGradient>
  </defs>
  <rect width="820" height="330" rx="14" fill="url(#bg)" stroke="#334155" stroke-width="1.5"/>
  <text x="28" y="34" fill="#F8FAFC" font-family="system-ui,-apple-system,sans-serif" font-size="16" font-weight="700">Supply Chain &amp; Legal Cost Exposure: Unmitigated Risk vs. Governance Policy Enforced ($K USD)</text>
  <text x="28" y="54" fill="#94A3B8" font-family="system-ui,-apple-system,sans-serif" font-size="12">Live Simulation across ServiceNow Customs Hold (INC0010004) &amp; Vendor Liability Redline (INC0010006)</text>
  <rect x="490" y="20" width="14" height="14" rx="3" fill="url(#bad)"/><text x="510" y="31" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="12">Unmitigated Risk ($K)</text>
  <rect x="655" y="20" width="14" height="14" rx="3" fill="url(#good)"/><text x="675" y="31" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="12" font-weight="600">Policy Enforced ($K)</text>
  <line x1="70" y1="85" x2="780" y2="85" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="70" y1="145" x2="780" y2="145" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="70" y1="205" x2="780" y2="205" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="70" y1="260" x2="780" y2="260" stroke="#475569" stroke-width="1.5"/>
  <rect x="135" y="155" width="52" height="105" rx="6" fill="url(#bad)"/>
  <text x="161" y="147" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$850K Duty</text>
  <rect x="195" y="254" width="52" height="6" rx="3" fill="url(#good)"/>
  <text x="221" y="246" fill="#34D399" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$0K (0% HTS)</text>
  <text x="191" y="286" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700" text-anchor="middle">Sec. 301 Customs Tariff</text>
  <text x="191" y="304" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">HTS 8517.62.00 Binding Ruling</text>
  <rect x="375" y="88" width="52" height="172" rx="6" fill="url(#bad)"/>
  <text x="401" y="80" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$1,400K Risk</text>
  <rect x="435" y="217" width="52" height="43" rx="6" fill="url(#good)"/>
  <text x="461" y="209" fill="#34D399" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$350K Capped</text>
  <text x="431" y="286" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700" text-anchor="middle">Vendor Liability Redline</text>
  <text x="431" y="304" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">Mandatory 2.0x Liability Shield</text>
  <rect x="615" y="236" width="52" height="24" rx="5" fill="url(#bad)"/>
  <text x="641" y="228" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$180K Drain</text>
  <rect x="675" y="254" width="52" height="6" rx="3" fill="url(#good)"/>
  <text x="701" y="246" fill="#34D399" font-family="system-ui,sans-serif" font-size="12" font-weight="700" text-anchor="middle">$0K (Net-60)</text>
  <text x="671" y="286" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700" text-anchor="middle">Payment Terms Exposure</text>
  <text x="671" y="304" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">Standard Net-60 Treasury Rule</text>
</svg>"""
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 230" width="100%" height="100%">
  <rect width="820" height="230" rx="14" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>
  <text x="28" y="34" fill="#F8FAFC" font-family="system-ui,-apple-system,sans-serif" font-size="16" font-weight="700">Total Protected Margin Waterfall — $2.08M Enterprise Value Preserved</text>
  <rect x="28" y="58" width="764" height="44" rx="8" fill="#1E293B"/>
  <rect x="28" y="58" width="386" height="44" rx="8" fill="#2563EB"/>
  <text x="44" y="85" fill="#FFFFFF" font-family="system-ui,sans-serif" font-size="13" font-weight="700">1. Legal Liability Cap Protection (INC0010006): +$1,050,000 Saved (50.5%)</text>
  <rect x="28" y="112" width="764" height="44" rx="8" fill="#1E293B"/>
  <rect x="28" y="112" width="312" height="44" rx="8" fill="#10B981"/>
  <text x="44" y="139" fill="#FFFFFF" font-family="system-ui,sans-serif" font-size="13" font-weight="700">2. Customs Binding Ruling HTS 8517.62.00 (INC0010004): +$850,000 Duty Eliminated (40.9%)</text>
  <rect x="28" y="166" width="764" height="44" rx="8" fill="#1E293B"/>
  <rect x="28" y="166" width="180" height="44" rx="8" fill="#F59E0B"/>
  <text x="44" y="193" fill="#FFFFFF" font-family="system-ui,sans-serif" font-size="13" font-weight="700">3. Net-60 Working Capital Optimization: +$180,000 Preserved (8.6%)</text>
</svg>"""

  if chart_num == 1:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 340" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0F172A"/><stop offset="100%" stop-color="#1E293B"/></linearGradient>
    <linearGradient id="c1" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#EF4444"/><stop offset="100%" stop-color="#B91C1C"/></linearGradient>
    <linearGradient id="c2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#F59E0B"/><stop offset="100%" stop-color="#B45309"/></linearGradient>
    <linearGradient id="c3" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#3B82F6"/><stop offset="100%" stop-color="#1D4ED8"/></linearGradient>
  </defs>
  <rect width="820" height="340" rx="14" fill="url(#bg)" stroke="#334155" stroke-width="1.5"/>
  <text x="28" y="32" fill="#F8FAFC" font-family="system-ui,-apple-system,sans-serif" font-size="16" font-weight="700">Commercial Deal Restructuring Architecture — Miami-Dade Dispatch (006jV000001CIWrQAO)</text>
  <text x="28" y="52" fill="#94A3B8" font-family="system-ui,-apple-system,sans-serif" font-size="12">Comparing Revenue Pillars ($K USD): Status Quo ($1.95M At Risk) vs. Discount Only ($1.56M) vs. Recommended Bundle ($1.98M)</text>
  <rect x="28" y="64" width="12" height="12" rx="3" fill="url(#c1)"/><text x="46" y="74" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="11.5">1. Status Quo ($1.95M Churn Risk)</text>
  <rect x="255" y="64" width="12" height="12" rx="3" fill="url(#c2)"/><text x="273" y="74" fill="#FDE68A" font-family="system-ui,sans-serif" font-size="11.5">2. 20% Override Only ($1.56M)</text>
  <rect x="465" y="64" width="12" height="12" rx="3" fill="url(#c3)"/><text x="483" y="74" fill="#93C5FD" font-family="system-ui,sans-serif" font-size="11.5" font-weight="700">3. Recommended APX NEXT + Aware Bundle ($1.98M)</text>
  <line x1="70" y1="105" x2="780" y2="105" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="70" y1="165" x2="780" y2="165" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="70" y1="225" x2="780" y2="225" stroke="#334155" stroke-dasharray="4 4"/>
  <line x1="70" y1="275" x2="780" y2="275" stroke="#475569" stroke-width="1.5"/>
  <rect x="115" y="112" width="42" height="163" rx="5" fill="url(#c1)"/>
  <text x="136" y="105" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="middle">$1,250K</text>
  <rect x="163" y="145" width="42" height="130" rx="5" fill="url(#c2)"/>
  <text x="184" y="138" fill="#FDE68A" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="middle">$1,000K</text>
  <rect x="211" y="145" width="42" height="130" rx="5" fill="url(#c3)"/>
  <text x="232" y="138" fill="#60A5FA" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="middle">$1,000K</text>
  <text x="184" y="298" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700" text-anchor="middle">ASTRO 25 Core Network</text>
  <text x="184" y="315" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">20% Retention Override Applied</text>
  <rect x="365" y="184" width="42" height="91" rx="5" fill="url(#c1)"/>
  <text x="386" y="177" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="middle">$700K</text>
  <rect x="413" y="202" width="42" height="73" rx="5" fill="url(#c2)"/>
  <text x="434" y="195" fill="#FDE68A" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="middle">$560K</text>
  <rect x="461" y="186" width="42" height="89" rx="5" fill="url(#c3)"/>
  <text x="482" y="179" fill="#60A5FA" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="middle">$680K</text>
  <text x="434" y="298" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700" text-anchor="middle">APX NEXT SmartConnect</text>
  <text x="434" y="315" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">Broadband LTE/Wi-Fi Failover</text>
  <rect x="615" y="271" width="42" height="4" rx="2" fill="url(#c1)"/>
  <text x="636" y="264" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">$0K</text>
  <rect x="663" y="271" width="42" height="4" rx="2" fill="url(#c2)"/>
  <text x="684" y="264" fill="#94A3B8" font-family="system-ui,sans-serif" font-size="11" text-anchor="middle">$0K</text>
  <rect x="711" y="236" width="42" height="39" rx="5" fill="url(#c3)"/>
  <text x="732" y="228" fill="#34D399" font-family="system-ui,sans-serif" font-size="11" font-weight="700" text-anchor="middle">+$300K New</text>
  <text x="684" y="298" fill="#F8FAFC" font-family="system-ui,sans-serif" font-size="13" font-weight="700" text-anchor="middle">CommandCentral Aware AI</text>
  <text x="684" y="315" fill="#34D399" font-family="system-ui,sans-serif" font-size="11" font-weight="600" text-anchor="middle">Unlocks +$30K Net Deal Growth</text>
</svg>"""
  return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 220" width="100%" height="100%">
  <rect width="820" height="220" rx="14" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>
  <text x="28" y="32" fill="#F8FAFC" font-family="system-ui,-apple-system,sans-serif" font-size="16" font-weight="700">ASTRO 25 Repeater Site 4 RF Packet Loss (%) — P1 Outage vs. APX NEXT LTE Failover</text>
  <text x="28" y="50" fill="#94A3B8" font-family="system-ui,-apple-system,sans-serif" font-size="12">Live ServiceNow Telemetry (Incident INC0010007 · Critical Public Safety Voice SLA Threshold: &lt; 1.00%)</text>
  <text x="28" y="88" fill="#FCA5A5" font-family="system-ui,sans-serif" font-size="13" font-weight="700">1. Current ASTRO Site 4 P1 Outage (INC0010007)</text>
  <rect x="335" y="71" width="450" height="26" rx="6" fill="#1E293B"/>
  <rect x="335" y="71" width="420" height="26" rx="6" fill="#EF4444"/>
  <text x="765" y="89" fill="#FFFFFF" font-family="system-ui,sans-serif" font-size="12" font-weight="800" text-anchor="end">18.40% Packet Loss (SLA BREACH)</text>
  <text x="28" y="136" fill="#E2E8F0" font-family="system-ui,sans-serif" font-size="13" font-weight="600">2. Public Safety Contractual Max SLA Ceiling</text>
  <rect x="335" y="119" width="450" height="26" rx="6" fill="#1E293B"/>
  <rect x="335" y="119" width="48" height="26" rx="6" fill="#F59E0B"/>
  <text x="395" y="137" fill="#FDE68A" font-family="system-ui,sans-serif" font-size="12" font-weight="700">1.00% Max Allowable Threshold</text>
  <text x="28" y="184" fill="#6EE7B7" font-family="system-ui,sans-serif" font-size="13" font-weight="700">3. APX NEXT SmartConnect Broadband Failover</text>
  <rect x="335" y="167" width="450" height="26" rx="6" fill="#1E293B"/>
  <rect x="335" y="167" width="16" height="26" rx="6" fill="#10B981"/>
  <text x="362" y="185" fill="#34D399" font-family="system-ui,sans-serif" font-size="12" font-weight="800">0.02% Loss (99.98% Voice Reliability Restored)</text>
</svg>"""


async def generate_executive_flash_brief(
    scenario: str,
    query: str,
    sfdc_data: dict,
    snow_data: dict,
    drive_data: dict,
    cockpit_url: str,
) -> str:
  """Generates an ultra-crisp 5-line Executive Flash Brief via gemini-3.8-flash."""
  project = "vtxdemos"
  try:
    client = genai.Client(vertexai=True, project=project, location="global")
    prompt = f"""You are the Chief Strategy & Enterprise AI Officer for Motorola Solutions.
Generate an ULTRA-CRISP, PUNCHY 5-LINE EXECUTIVE FLASH BRIEF in Markdown for the scenario '{scenario}' based on live MCP telemetry:
- User Prompt: {query}
- Salesforce CRM: {json.dumps(sfdc_data.get('records', [])[:3])}
- ServiceNow ITSM: {json.dumps(snow_data.get('records', [])[:3])}
- Google Drive Governance Policy: {json.dumps(drive_data.get('document', {}))}

STRICT FORMATTING RULES (MUST FOLLOW):
1. Output EXACTLY 5 short lines total (1 title heading `### ⚡ Executive Flash Brief: ...` + 4 ultra-concise bullet lines).
2. NO long paragraphs, NO markdown tables (the interactive visual A2UI charts and KPI cards render immediately below your 5 lines!).
3. Every bullet line must be bold-led, executive-ready, and cite the exact live IDs (`006jV000001CIWrQAO`, `INC0010007` / `INC0010006` / `INC0010004`) and exact dollar/percentage impact.
4. End the 5th line with: `[↗ Full-Screen Deal Cockpit]({cockpit_url})`
"""
    resp = await asyncio.to_thread(
        client.models.generate_content,
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=2048,
            thinking_config=types.ThinkingConfig(thinking_budget=128),
        ),
    )
    txt = (resp.text or "").strip()
    if txt and len(txt.splitlines()) >= 4 and len(txt) >= 180:
      return txt
  except Exception as e:
    print(f"[FLASH BRIEF FALLBACK] {e}", flush=True)

  if scenario == "portfolio_war_room":
    return (
        "### ⚡ Executive Flash Brief: National Public Safety Portfolio War Room ($9.75M ARR)\n"
        "- **Commercial Pipeline Audited:** `$9.75M` across **State Highway Patrol (`$5.20M`)**, **City of Metro (`$2.60M`)**, and **Miami-Dade Dispatch (`$1.95M`)** (`006jV000001CIWrQAO`).\n"
        "- **Cross-Silo Risk Diagnosis:** 3 active ServiceNow blockers (`INC0010007` P1 RF Outage, `INC0010006` Legal Redline, `INC0010004` Customs Tariff Hold) threaten Q4 renewals.\n"
        "- **Playbook Financial Impact:** Applying pre-approved Drive Governance Rules protects all `$9.75M` and unlocks **`+$670K` net expansion (`$10.42M` post-playbook ARR)**.\n"
        f"- **Interactive Visual Deck Below:** Live multi-series ARR & risk breakdown charts + 1-click ServiceNow remediation · [↗ Full-Screen Deal Cockpit]({cockpit_url})"
    )
  if scenario == "tariff_redline_sim":
    return (
        "### ⚡ Executive Flash Brief: Global Supply Chain Tariff & Legal Redline Audit\n"
        "- **Dual Escalation Audited:** ServiceNow **`INC0010004`** (25% Section 301 Customs Hold on `$3.4M` APX shipment) & **`INC0010006`** (Vendor 1.0x liability redline).\n"
        "- **Customs HTS Resolution:** Motorola Binding Ruling **`HTS 8517.62.00`** reclassifies encrypted public-safety transceivers at **`0% Duty` (`$850K` direct duty saved)**.\n"
        "- **Procurement Governance Shield:** Policy mandates **2.0x Liability Cap + Net-60 Terms**, eliminating **`$1.05M` in uncapped legal exposure** (`$1.90M` total margin saved).\n"
        f"- **Interactive Visual Deck Below:** Live tariff/liability waterfall comparison + 1-click ServiceNow clearance · [↗ Full-Screen Deal Cockpit]({cockpit_url})"
    )
  return (
      "### ⚡ Executive Flash Brief: Miami-Dade Dispatch Renewal & RF Recovery (`$1.95M`)\n"
      "- **Commercial Exposure (`006jV000001CIWrQAO`):** `$1,950,000` ASTRO 25 & APX renewal (Close: `2026-10-15`) at risk due to active P1 incident **`INC0010007`** (18.4% RF packet loss).\n"
      "- **Governance Policy Unlock:** Drive Policy Rule 2 pre-authorizes a **20% Executive Retention Override** when bundled with **APX NEXT SmartConnect + CommandCentral Aware**.\n"
      "- **Net Financial & Technical Outcome:** Expands net contract value to **`$1,980,000` (`+$30K` net expansion)** while cutting RF packet loss from **`18.4%` to `0.02%`** via LTE failover.\n"
      f"- **Interactive Visual Deck Below:** Live deal architecture & RF telemetry charts + 1-click ServiceNow write-back · [↗ Full-Screen Deal Cockpit]({cockpit_url})"
  )


def build_visual_a2ui_messages(
    scenario: str,
    sfdc_rec: dict,
    snow_rec: dict,
    drive_doc: dict,
    base_url: str,
) -> tuple[dict, dict, list[dict]]:
  """Builds rich A2UI v0.8 and full 32-component v0.9 Basic Catalog visual command deck."""
  inc_num = snow_rec.get("number", "INC0010007")
  sfdc_id = sfdc_rec.get("Id", "006jV000001CIWrQAO")
  surface_id = f"motorola-visual-deck-{scenario}-{inc_num.lower()}"
  ts_cache = int(time.time())
  chart1_url = f"{base_url}/api/chart/{scenario}/1.svg?v={ts_cache}"
  chart2_url = f"{base_url}/api/chart/{scenario}/2.svg?v={ts_cache}"

  if scenario == "portfolio_war_room":
    title_str = "🌐 Motorola National Public Safety Portfolio War Room ($9.75M Pipeline)"
    subtitle_str = "Real-time cross-silo synthesis across Salesforce CRM (3 Agencies), ServiceNow ITSM (3 Active Escalations), and Drive Policy Engine"
    kpi1_title = "💰 $9.75M → $10.42M"
    kpi1_sub = "Protected + Expanded ARR (+6.9% Net Growth)"
    kpi2_title = "🚨 3 Active Escalations"
    kpi2_sub = "INC0010007 (P1 RF) · INC0010006 · INC0010004"
    kpi3_title = "🛡️ 100% Policy Covered"
    kpi3_sub = "Pre-approved retention, HTS & redline rules"
    primary_btn_label = "⚡ Authorize All 3 Portfolio Overrides & Sync ServiceNow Live"
    primary_inc = "INC0010007"
    sec1_label = "📡 Drill Down: Miami-Dade Deal & RF Deck ($1.95M)"
    sec1_target = "deal_restructuring"
    sec2_label = "🛡️ Drill Down: Tariff & Legal Redline Simulator ($1.90M Saved)"
    sec2_target = "tariff_redline_sim"
    chart1_title = "📊 Agency ARR Comparison: Baseline at Risk vs. Post-Playbook Protected ARR ($M USD)"
    chart2_title = "🍩 National Pipeline Share & Governance Remediation Summary ($10.42M Total)"
    ev_row1 = "🏢 Salesforce CRM Live Pipeline: State Highway Patrol ($5.20M) · City of Metro ($2.60M) · Miami-Dade ($1.95M)"
    ev_row2 = "🛠️ ServiceNow ITSM Active Blockers: INC0010007 (P1 RF Outage) · INC0010006 (Legal Redline) · INC0010004 (Tariff Hold)"
    ev_row3 = "📜 Google Drive Governance Engine: Rule 2 (20% Override) + HTS 8517.62.00 (0% Duty) + 2.0x Liability Cap"
  elif scenario == "tariff_redline_sim":
    title_str = "🛡️ Global Trade Tariff (INC0010004) & Legal Redline (INC0010006) Simulator"
    subtitle_str = "Financial impact analysis of Motorola Customs Ruling HTS 8517.62.00 (0% Duty) & Procurement 2.0x Liability Cap"
    kpi1_title = "🛃 $850K Duty Eliminated"
    kpi1_sub = "HTS 8517.62.00 (0% Duty) vs. 8525.60.10 (25% Tariff)"
    kpi2_title = "⚖️ $1.05M Liability Shield"
    kpi2_sub = "2.0x Liability Cap + Net-60 Terms Enforced"
    kpi3_title = "✅ $1.90M Margin Protected"
    kpi3_sub = "Total Supply Chain & Legal Cost Avoidance"
    primary_btn_label = "⚡ Issue Binding Customs & Legal Clearance (Patch ServiceNow INC0010004)"
    primary_inc = "INC0010004"
    sec1_label = "📡 Switch to Miami-Dade Deal & RF Command Deck ($1.95M)"
    sec1_target = "deal_restructuring"
    sec2_label = "📊 Switch to National Portfolio War Room ($9.75M)"
    sec2_target = "portfolio_war_room"
    chart1_title = "📉 Supply Chain & Legal Cost Exposure: Unmitigated vs. Policy Enforced ($K USD)"
    chart2_title = "🍩 Breakdown of $2.08M Total Protected Enterprise Value ($K USD)"
    ev_row1 = "🛃 Customs Hold INC0010004: Reclassifies $3.4M APX shipment from HTS 8525.60.10 (25% Duty) to HTS 8517.62.00 (0% Duty)"
    ev_row2 = "⚖️ Procurement Redline INC0010006: Rejects vendor 1.0x liability cap; enforces Motorola standard 2.0x Cap + Net-60"
    ev_row3 = "💰 Combined EBITDA Margin Impact: Protects $1,900,000 in direct duty/liability + $180,000 working capital ($2.08M total)"
  else:
    title_str = f"⚡ Motorola Executive Deal & RF Command Deck — Miami-Dade ({inc_num})"
    subtitle_str = "Cross-silo synthesis: Salesforce Opportunity 006jV000001CIWrQAO ($1.95M) + ServiceNow P1 Outage INC0010007 + Drive Policy Rule 2"
    kpi1_title = "💰 $1.95M → $1.98M"
    kpi1_sub = "Net Deal Value (+1.5% Expansion with APX NEXT)"
    kpi2_title = "📡 18.4% → 0.02%"
    kpi2_sub = "Site 4 Packet Loss Eliminated via LTE Failover"
    kpi3_title = "🛡️ 20% Override Ready"
    kpi3_sub = "Policy Rule 2 Authorized · Close: Oct 15, 2026"
    primary_btn_label = f"⚡ Authorize 20% Override & Patch ServiceNow Live ({inc_num})"
    primary_inc = inc_num
    sec1_label = "📊 Switch to National Portfolio War Room ($9.75M)"
    sec1_target = "portfolio_war_room"
    sec2_label = "🛡️ Switch to Tariff & Legal Redline Simulator"
    sec2_target = "tariff_redline_sim"
    chart1_title = "📊 Commercial Restructuring Options by Product Pillar ($K USD)"
    chart2_title = "📡 ASTRO 25 Repeater Site 4 Packet Loss (%) — Outage vs. APX NEXT Failover"
    ev_row1 = f"🏢 Salesforce Opportunity ({sfdc_id}): Miami-Dade Dispatch Renewal ($1,950,000 · Stage: Negotiation · Close: 2026-10-15)"
    ev_row2 = f"🚨 ServiceNow P1 Outage ({inc_num}): ASTRO 25 Repeater Site 4 suffering 18.40% RF packet loss (SLA threshold: <1.00%)"
    ev_row3 = "📜 Google Drive Governance Policy Rule 2: Pre-approves 20% retention discount when bundled with APX NEXT + Aware (+$30K net)"

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
                          "chart1_card",
                          "chart2_card",
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
                  {"id": "chart1_card", "component": "Card", "child": "chart1_col"},
                  {"id": "chart1_col", "component": "Column", "align": "stretch", "children": ["chart1_heading", "chart1_img"]},
                  {"id": "chart1_heading", "component": "Text", "variant": "h3", "text": chart1_title},
                  {"id": "chart1_img", "component": "Image", "url": chart1_url, "fit": "contain"},
                  {"id": "chart2_card", "component": "Card", "child": "chart2_col"},
                  {"id": "chart2_col", "component": "Column", "align": "stretch", "children": ["chart2_heading", "chart2_img"]},
                  {"id": "chart2_heading", "component": "Text", "variant": "h3", "text": chart2_title},
                  {"id": "chart2_img", "component": "Image", "url": chart2_url, "fit": "contain"},
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
                      "text": "🔍 Live Cross-Silo MCP Telemetry & Governance Audit Trail",
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
                      "text": "⚡ Interactive Executive Actions (Live OAuth 2.0 Write-Back & Scenario Switcher)",
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
                                  "chart1_card",
                                  "chart2_card",
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
              {"id": "chart1_card", "component": {"Card": {"child": "chart1_col"}}},
              {"id": "chart1_col", "component": {"Column": {"children": {"explicitList": ["chart1_heading", "chart1_img"]}}}},
              {"id": "chart1_heading", "component": {"Text": {"text": {"literalString": chart1_title}, "usageHint": "h3"}}},
              {"id": "chart1_img", "component": {"Image": {"url": {"literalString": chart1_url}}}},
              {"id": "chart2_card", "component": {"Card": {"child": "chart2_col"}}},
              {"id": "chart2_col", "component": {"Column": {"children": {"explicitList": ["chart2_heading", "chart2_img"]}}}},
              {"id": "chart2_heading", "component": {"Text": {"text": {"literalString": chart2_title}, "usageHint": "h3"}}},
              {"id": "chart2_img", "component": {"Image": {"url": {"literalString": chart2_url}}}},
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


async def run_visual_command_agent(
    query: str,
    base_url: str,
    explicit_scenario: str | None = None,
) -> dict:
  t0 = time.monotonic()
  scenario = detect_scenario(query, explicit_scenario)
  sfdc_data, snow_data, drive_data = await asyncio.gather(
      fetch_salesforce_async(query),
      fetch_servicenow_async(query),
      fetch_gdrive_async(query),
  )
  cockpit_url = "https://motorola-a2ui-agent-254356041555.us-central1.run.app/cockpit"
  flash_brief = await generate_executive_flash_brief(
      scenario, query, sfdc_data, snow_data, drive_data, cockpit_url
  )
  sfdc_rec = (sfdc_data.get("records") or [{}])[0]
  snow_rec = (snow_data.get("records") or [{}])[0]
  drive_doc = drive_data.get("document") or {}
  v08_begin, v08_update, v09_messages = build_visual_a2ui_messages(
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
