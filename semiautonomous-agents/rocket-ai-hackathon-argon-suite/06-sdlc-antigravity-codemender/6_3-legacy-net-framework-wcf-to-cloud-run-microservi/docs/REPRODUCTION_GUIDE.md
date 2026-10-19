# Square `[6.3]`: Legacy .NET Framework / WCF to Cloud Run Microservice Modernizer — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `6.3` |
| **Bespoke Application Title** | **Antigravity Legacy Modernizer // C# .NET 4.8 WCF SOAP -> .NET 9 Cloud Run Transpiler** (`legacy_dotnet_wcf_transpiler`) |
| **Business Domain** | 6. SDLC & AI Software Factory (CodeMender Security, Antigravity Swarm & .NET Modernization) (`rocket-demo-sdlc`) |
| **Complexity Level** | `L200–L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/6.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/6.3) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/6.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/6.3) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Refactor legacy on-prem C# / .NET Framework 4.8 SOAP/WCF loan calculators into cloud-native .NET 9 Minimal APIs & Python FastAPI services on Cloud Run.

**Description:**  
Accelerate Rocket's legacy modernization: paste monolithic C# `.NET 4.8` WCF `ServiceContract` classes with synchronous SQL calls and let Gemini 4 Argon refactor them into async, containerized Cloud Run microservices with OpenTelemetry, Dockerfile, and unit tests.

**Bespoke UI Archetype (`legacy_dotnet_wcf_transpiler`):**  
Rather than displaying a generic text response, Square `[6.3]` renders **Antigravity Legacy Modernizer // C# .NET 4.8 WCF SOAP -> .NET 9 Cloud Run Transpiler** with structured visual artifacts (`Return JSON with keys: modernization_metrics ({cold_start_ms, memory_reduction_pct, sql_injection_fixed}), legacy_issues_removed (list of {anti_pattern, legacy_snippet, modern_fix}), modern_csharp_code (str), and michigan_millage_parity_table (list of {scenario, taxable_value, mills, annual_tax, monthly_escrow}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Gemini Code Assist indexes Rocket's private C#/.NET repositories to preserve internal domain conventions while migrating WCF SOAP services to Cloud Run 3x faster than manual rewrites.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini Code Assist Enterprise` · `Gemini 4 Argon (2M Context)` · `Google Cloud Run`

```text
┌────────────────────────────────────────────────────────────────────────┐
│      6.3 LEGACY .NET 4.8 WCF TO CLOUD RUN MODERNIZER (L200-300)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Legacy C# .NET 4.8 WCF SOAP Class (Blocking SQL + Untyped DataTable)]│
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini 4 Argon + Gemini Code Assist Code Transformation Engine]      │
│  ├─► Eliminates WCF SOAP & `DataTable` -> Typed JSON `record` DTOs     │
│  ├─► Converts Sync `SqlCommand` -> Async Parameterized Dapper/Postgres │
│  └─► Generates Multi-Stage Cloud Run `Dockerfile` + xUnit Test Suite   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Cloud-Native .NET 9 / FastAPI Service Deployed on Cloud Run]         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Open the legacy C# solution in VS Code or Visual Studio with Gemini Code Assist Enterprise connected to your private code repository index.
2. Run the `/modernize` prompt powered by `gemini-4-argon` to generate the `.NET 9` Minimal API, `Dockerfile`, and xUnit tests.
3. Deploy directly to Cloud Run: `gcloud run deploy rocket-escrow-svc --source . --region us-central1`.

### Quick Start (Run Standalone from This Folder)

```bash
# 1. Run the deterministic gVisor sandbox & bespoke artifact builder
python3 ./code/sandbox_tool.py

# 2. Execute the live gemini-4-argon structured agent
python3 ./code/agent.py
```

---

## 5. Verified Deterministic Sandbox & Bespoke Visual Artifact

```json
{
  "archetype": "legacy_dotnet_wcf_transpiler",
  "homestead": "$7,245.00/yr ($603.75/mo Escrow at 34.5 Mills)",
  "non_homestead": "$11,025.00/yr ($918.75/mo Escrow at 52.5 Mills w/ 18-Mill School Tax)",
  "runtime": ".NET 9 Native AOT Minimal API / Python FastAPI (Cold Start < 140ms)",
  "diff_pairs": [
    {
      "legacy": "SqlCommand(\"SELECT MillageRate FROM Counties WHERE Name='\" + county + \"'\")",
      "modern": "await db.QuerySingleAsync<decimal>(\"SELECT millage_rate FROM counties WHERE name = @County\", new { County = county })"
    },
    {
      "legacy": "[ServiceContract] public class EscrowWcfSoapService : IEscrowSoap",
      "modern": "app.MapPost(\"/v2/escrow/michigan-millage\", async (MillageRequest req) => ...)"
    }
  ]
}
```
