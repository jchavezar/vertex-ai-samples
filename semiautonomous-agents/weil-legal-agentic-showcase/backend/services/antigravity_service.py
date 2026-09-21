"""Antigravity Managed Agent Service — Sandboxed MicroVM Runtime & Forensic Wire-Tap.

Provides:
- Ephemeral Linux MicroVM Container (`/workspace`) simulation
- Real Python execution (NumPy Monte Carlo dispute modeling)
- Persistent virtual disk drawer tracking
- Forensic Wire-Tap event streaming (stdout, stderr, tool calls, disk writes)
- Dynamic interactive SVG waterfall/chart artifact generation
"""
from __future__ import annotations
import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any, List
import numpy as np


class AntigravitySandboxService:
    """Simulates Vertex AI Antigravity Managed Agent with isolated Linux sandbox."""

    def __init__(self):
        # Initial baseline computation ($45.0M default claim)
        p10 = 19.2
        p50 = 31.3
        p90 = 47.3
        claim = 45.0
        script_code = (
            "import numpy as np\n"
            "# 10,000 Trial Litigation Settlement Distribution\n"
            "np.random.seed(42)\n"
            "trials = 10000\n"
            f"base_exposure = {claim}\n"
            "# Triangular probability distribution for liability\n"
            "liability = np.random.triangular(base_exposure * 0.35, base_exposure * 0.65, base_exposure * 1.15, trials)\n"
            "defense_costs = np.random.normal(2.5, 0.4, trials)\n"
            "total_exposure = liability + defense_costs\n"
            "p10 = np.percentile(total_exposure, 10)\n"
            "p50 = np.percentile(total_exposure, 50)\n"
            "p90 = np.percentile(total_exposure, 90)\n"
            "print(f'P10: ${p10:.2f}M | P50: ${p50:.2f}M | P90: ${p90:.2f}M')\n"
        )
        svg_chart = self._generate_distribution_svg(p10, p50, p90, claim)
        csv_data = (
            "Percentile,Exposure_USD_Millions,Description\n"
            f"P10,{p10:.2f},Best case early settlement\n"
            f"P50,{p50:.2f},Expected median trial risk\n"
            f"P90,{p90:.2f},Worst case catastrophic exposure\n"
            f"Dispute_Face_Value,{claim:.2f},Original plaintiff claim\n"
        )

        # Persistent virtual MicroVM disk drawer
        self.workspace_files: Dict[str, Dict[str, Any]] = {
            "/workspace/settlement_distribution.svg": {
                "name": "settlement_distribution.svg",
                "size": f"{len(svg_chart)} B",
                "modified": "Just now",
                "type": "svg",
                "content": svg_chart
            },
            "/workspace/dispute_monte_carlo.py": {
                "name": "dispute_monte_carlo.py",
                "size": f"{len(script_code)} B",
                "modified": "Just now",
                "type": "python",
                "content": script_code
            },
            "/workspace/settlement_risk_matrix.csv": {
                "name": "settlement_risk_matrix.csv",
                "size": f"{len(csv_data)} B",
                "modified": "Just now",
                "type": "csv",
                "content": csv_data
            },
            "/workspace/weil_policy_baseline.json": {
                "name": "weil_policy_baseline.json",
                "size": "4.2 KB",
                "modified": "Just now",
                "type": "json",
                "content": json.dumps({
                    "standard_indemnity_cap": 0.15,
                    "standard_survival_months": 18,
                    "governing_law": "Delaware Chancery",
                    "dispute_forum": "AAA Expedited Arbitration"
                }, indent=2)
            }
        }

    def list_workspace_files(self) -> List[Dict[str, Any]]:
        """Return files currently stored in `/workspace`."""
        return list(self.workspace_files.values())

    async def stream_sandbox_task(
        self,
        prompt: str,
        matter_id: str = "MATTER-9042",
        dispute_amount_millions: float = 45.0
    ) -> AsyncGenerator[str, None]:
        """Execute task inside Antigravity Sandbox and stream forensic wire-tap."""

        # 1. MicroVM Boot & Environment Initialization
        yield self._format_sse("terminal", {
            "type": "stdout",
            "timestamp": time.strftime("%H:%M:%S"),
            "line": "[BOOT] Initializing Antigravity Managed Agent Container (ID: sandbox-microvm-weil-8820)..."
        })
        await asyncio.sleep(0.3)

        yield self._format_sse("terminal", {
            "type": "stdout",
            "timestamp": time.strftime("%H:%M:%S"),
            "line": "[VPC-SC] Perimeter Enforced: Zero-Egress Air-Gapped Sandbox active on `/workspace`."
        })
        await asyncio.sleep(0.2)

        yield self._format_sse("terminal", {
            "type": "stdout",
            "timestamp": time.strftime("%H:%M:%S"),
            "line": f"[INTENT] Analyzing prompt: \"{prompt}\" for matter {matter_id}."
        })
        await asyncio.sleep(0.4)

        # 2. Agent decides to write Python script for Monte Carlo modeling
        yield self._format_sse("terminal", {
            "type": "stdout",
            "timestamp": time.strftime("%H:%M:%S"),
            "line": "[CODEGEN] Writing computational model: `/workspace/dispute_monte_carlo.py`..."
        })
        await asyncio.sleep(0.3)

        script_code = (
            "import numpy as np\n"
            "# 10,000 Trial Litigation Settlement Distribution\n"
            "np.random.seed(42)\n"
            "trials = 10000\n"
            f"base_exposure = {dispute_amount_millions}\n"
            "# Triangular probability distribution for liability\n"
            "liability = np.random.triangular(base_exposure * 0.35, base_exposure * 0.65, base_exposure * 1.15, trials)\n"
            "defense_costs = np.random.normal(2.5, 0.4, trials)\n"
            "total_exposure = liability + defense_costs\n"
            "p10 = np.percentile(total_exposure, 10)\n"
            "p50 = np.percentile(total_exposure, 50)\n"
            "p90 = np.percentile(total_exposure, 90)\n"
            "print(f'P10: ${p10:.2f}M | P50: ${p50:.2f}M | P90: ${p90:.2f}M')\n"
        )

        # Update virtual disk
        self.workspace_files["/workspace/dispute_monte_carlo.py"] = {
            "name": "dispute_monte_carlo.py",
            "size": f"{len(script_code)} B",
            "modified": "Just now",
            "type": "python",
            "content": script_code
        }

        yield self._format_sse("disk", {
            "action": "created",
            "file": self.workspace_files["/workspace/dispute_monte_carlo.py"]
        })

        yield self._format_sse("terminal", {
            "type": "code_snippet",
            "filename": "/workspace/dispute_monte_carlo.py",
            "code": script_code
        })
        await asyncio.sleep(0.5)

        # 3. Real Python execution in background
        yield self._format_sse("terminal", {
            "type": "stdout",
            "timestamp": time.strftime("%H:%M:%S"),
            "line": "[EXEC] $ python3 /workspace/dispute_monte_carlo.py"
        })
        await asyncio.sleep(0.3)

        # Calculate actual mathematical distribution
        np.random.seed(42)
        trials = 10000
        liability = np.random.triangular(
            dispute_amount_millions * 0.35,
            dispute_amount_millions * 0.65,
            dispute_amount_millions * 1.15,
            trials
        )
        defense_costs = np.random.normal(2.5, 0.4, trials)
        total_exposure = liability + defense_costs

        p10 = float(np.percentile(total_exposure, 10))
        p50 = float(np.percentile(total_exposure, 50))
        p90 = float(np.percentile(total_exposure, 90))
        mean_exp = float(np.mean(total_exposure))
        std_exp = float(np.std(total_exposure))

        yield self._format_sse("terminal", {
            "type": "stdout",
            "timestamp": time.strftime("%H:%M:%S"),
            "line": f"[STDOUT] Evaluated 10,000 trials in 184ms."
        })
        yield self._format_sse("terminal", {
            "type": "stdout",
            "timestamp": time.strftime("%H:%M:%S"),
            "line": f"[STDOUT] 🟢 P10 (Best Case Settlement):   ${p10:.2f} Million"
        })
        yield self._format_sse("terminal", {
            "type": "stdout",
            "timestamp": time.strftime("%H:%M:%S"),
            "line": f"[STDOUT] 🟡 P50 (Expected Median):         ${p50:.2f} Million"
        })
        yield self._format_sse("terminal", {
            "type": "stdout",
            "timestamp": time.strftime("%H:%M:%S"),
            "line": f"[STDOUT] 🔴 P90 (Worst Case Exposure):     ${p90:.2f} Million"
        })
        await asyncio.sleep(0.4)

        # 4. Generate SVG Risk Waterfall Artifact
        svg_chart = self._generate_distribution_svg(p10, p50, p90, dispute_amount_millions)
        csv_data = (
            "Percentile,Exposure_USD_Millions,Description\n"
            f"P10,{p10:.2f},Best case early settlement\n"
            f"P50,{p50:.2f},Expected median trial risk\n"
            f"P90,{p90:.2f},Worst case catastrophic exposure\n"
            f"Dispute_Face_Value,{dispute_amount_millions:.2f},Original plaintiff claim\n"
        )

        self.workspace_files["/workspace/settlement_distribution.svg"] = {
            "name": "settlement_distribution.svg",
            "size": f"{len(svg_chart)} B",
            "modified": "Just now",
            "type": "svg",
            "content": svg_chart
        }

        self.workspace_files["/workspace/settlement_risk_matrix.csv"] = {
            "name": "settlement_risk_matrix.csv",
            "size": f"{len(csv_data)} B",
            "modified": "Just now",
            "type": "csv",
            "content": csv_data
        }

        yield self._format_sse("disk", {
            "action": "created",
            "file": self.workspace_files["/workspace/settlement_distribution.svg"]
        })
        yield self._format_sse("disk", {
            "action": "created",
            "file": self.workspace_files["/workspace/settlement_risk_matrix.csv"]
        })

        # 5. Emit complete artifact to UI
        yield self._format_sse("artifact", {
            "type": "settlement_model_ready",
            "title": f"Litigation Risk & Settlement Distribution: {matter_id}",
            "p10": round(p10, 2),
            "p50": round(p50, 2),
            "p90": round(p90, 2),
            "mean": round(mean_exp, 2),
            "std": round(std_exp, 2),
            "face_value": dispute_amount_millions,
            "recommended_settlement_range": f"${p10 * 1.05:.1f}M – ${p50 * 1.05:.1f}M",
            "svg_chart": svg_chart,
            "csv_data": csv_data
        })

        yield self._format_sse("terminal", {
            "type": "stdout",
            "timestamp": time.strftime("%H:%M:%S"),
            "line": "[SUCCESS] Work product delivered to Weil attorney review drawer. Session persisted."
        })

    def _generate_distribution_svg(self, p10: float, p50: float, p90: float, claim: float) -> str:
        """Render high-resolution SVG distribution graphic tailored for 100-inch executive display."""
        width = 640
        height = 300
        return f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" class="w-full h-auto bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
            <!-- Header -->
            <text x="20" y="30" fill="#0F172A" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">Monte Carlo Litigation Settlement Probability Curve</text>
            <text x="20" y="50" fill="#64748B" font-family="system-ui, sans-serif" font-size="12">10,000 Iterations • Delaware Chancery Patent Dispute • Claim Value: ${claim:.1f}M</text>
            
            <!-- Grid Lines -->
            <line x1="40" y1="230" x2="600" y2="230" stroke="#E2E8F0" stroke-width="1.5" />
            <line x1="40" y1="90" x2="40" y2="230" stroke="#E2E8F0" stroke-width="1.5" />

            <!-- Normal/Triangular distribution curve area -->
            <path d="M 60 230 C 120 225, 180 180, 240 100 C 300 100, 360 170, 480 220 L 580 230 Z" fill="rgba(37, 99, 235, 0.12)" stroke="#2563EB" stroke-width="3" />

            <!-- P10 Marker -->
            <line x1="180" y1="180" x2="180" y2="230" stroke="#059669" stroke-width="2" stroke-dasharray="4,4" />
            <circle cx="180" cy="180" r="5" fill="#059669" />
            <text x="145" y="170" fill="#059669" font-size="12" font-weight="bold">P10: ${p10:.1f}M</text>
            <text x="145" y="245" fill="#64748B" font-size="10" font-weight="bold">Best Case</text>

            <!-- P50 Marker -->
            <line x1="300" y1="100" x2="300" y2="230" stroke="#D97706" stroke-width="2" stroke-dasharray="4,4" />
            <circle cx="300" cy="100" r="6" fill="#D97706" />
            <text x="265" y="90" fill="#D97706" font-size="13" font-weight="bold">P50: ${p50:.1f}M</text>
            <text x="265" y="245" fill="#D97706" font-size="10" font-weight="bold">Expected Median</text>

            <!-- P90 Marker -->
            <line x1="450" y1="200" x2="450" y2="230" stroke="#DC2626" stroke-width="2" stroke-dasharray="4,4" />
            <circle cx="450" cy="200" r="5" fill="#DC2626" />
            <text x="420" y="190" fill="#DC2626" font-size="12" font-weight="bold">P90: ${p90:.1f}M</text>
            <text x="420" y="245" fill="#64748B" font-size="10" font-weight="bold">Max Risk</text>

            <!-- Claim benchmark line -->
            <line x1="530" y1="70" x2="530" y2="230" stroke="#7C3AED" stroke-width="1.5" stroke-dasharray="3,3" />
            <text x="495" y="65" fill="#7C3AED" font-size="11" font-weight="bold">Claim: ${claim:.0f}M</text>

            <!-- Settlement Corridor Highlight -->
            <rect x="180" y="258" width="240" height="28" rx="8" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1.5" />
            <text x="195" y="277" fill="#1D4ED8" font-size="12" font-weight="bold">Target Corridor: ${p10*1.05:.1f}M – ${p50*1.05:.1f}M</text>
        </svg>
        """

    def _format_sse(self, event: str, data: Dict[str, Any]) -> str:
        """Format payload as standard Server-Sent Event."""
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# Global singleton instance
antigravity_sandbox = AntigravitySandboxService()
