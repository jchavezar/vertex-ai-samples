# 🛡️ SharePoint Sentinel: AI-Powered Sensitivity Classifier

> **Next-Gen Enterprise Data Security powered by Google Agent Development Kit (ADK) & Vertex AI**

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-Vertex_AI-red?style=for-the-badge&logo=googlecloud)
![SharePoint](https://img.shields.io/badge/Microsoft-SharePoint-0078D4?style=for-the-badge&logo=microsoftsharepoint)
![GenAI](https://img.shields.io/badge/Model-Gemini_3_Flash_Preview-purple?style=for-the-badge)

---

## 🚀 Overview

**SharePoint Sentinel** is an intelligent agent that autonomously monitors your corporate SharePoint document libraries. It detects new or modified files and uses the advanced reasoning capabilities of **Gemini 3 Flash Preview** (via Google ADK) to analyze, classify, and tag documents based on their sensitivity.

It's not just a script; it's a **Compliance Officer in a Box**.

### key Features
*   **🧠 Agentic Architecture**: Built on **Google ADK**, using `LlmAgent` and `Runner` for robust, stateful execution.
*   **⚡ Delta Query Polling**: Efficiently fetches *only* changed files using Microsoft Graph Delta Query.
*   **📄 Universal Ingestion**: Automatically converts Office docs (PPTX, DOCX, XLSX) to text using `MarkItDown`.
*   **🔒 Zero-Leak Output**: Generates strictly structured JSON reports suitable for automated DLP pipeline integration.
*   **🌍 Global Scale**: Configured for `global` location to access the latest experimental models.

---

## 🏗️ Architecture

The agent follows an event-driven pipeline, transforming raw SharePoint data into structured intelligence.

```mermaid
graph TD
    subgraph SharePoint ["Microsoft 365 Environment"]
        DL[Document Library]
        API[Graph API Delta Query]
    end

    subgraph AgentRuntime ["ADK Agent Runtime"]
        Con[SharePoint Connector]
        Conv[MarkItDown Converter]
        Runner[ADK Runner]
        Agent[LlmAgent (Gemini 3)]
    end

    subgraph Output ["Intelligence Layer"]
        Report[classification_report.json]
        State[sync_state.json]
    end

    DL -->|Change Event| API
    API -->|JSON Metadata| Con
    Con -->|Download File| Conv
    Conv -->|Text Content| Runner
    Runner -->|Prompt + Content| Agent
    Agent -->|Structured Classification| Runner
    Runner -->|Append| Report
    Con -->|Update Token| State

    style Agent fill:#f9f,stroke:#333,stroke-width:2px
    style Report fill:#bbf,stroke:#333,stroke-width:2px
```

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following:

1.  **Python 3.12+**: Managed preferably by `uv`.
2.  **Microsoft Entra ID App**:
    *   **Permissions**: `Files.Read.All`, `Sites.Read.All` (Application permissions).
    *   **Secrets**: Client ID, Tenant ID, Client Secret.
3.  **Google Cloud Project**:
    *   **APIs Enabled**: Vertex AI API.
    *   **Quota**: Access to `gemini-3-flash-preview`.

---

## ⚡ Getting Started

### 1. Installation

Clone the repository and install dependencies using `uv` (the lightning-fast Python package manager).

```bash
# Install dependencies
uv sync
```

### 2. Configuration {.tabset}

Create a `.env` file in the root directory. This is **CRITICAL** for authentication.

```env
# Microsoft 365 Auth
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
SITE_ID=your-sharepoint-site-id
DRIVE_ID=your-drive-id

# Google Cloud Auth
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_LOCATION=global  # Force global for Gemini 3
```

> **Tip:** Don't know your Site ID? Run the helper script: `uv run sharepoint_discovery.py`

### 3. Run the Agent

Execute the agent. It will verify your credentials, sync changes, and start classifying.

```bash
uv run python classifier_agent.py
```

---

## 📊 Output Data Model

The agent produces a **strict JSON schema** (`classification_report.json`). No parsing required.

```json
[
  {
    "file_uid": "01Y...XA",
    "filename": "Quarterly_Financials.xlsx",
    "sensitivity_level": "High",
    "contains_pii": true,
    "classification_tags": ["Financial", "Confidential", "Internal"],
    "summary": "Detailed revenue breakdown for Q3 2025 including employee payroll data.",
    "reasoning": "Contains explicit salary information and non-public revenue figures.",
    "recommended_action": "Encrypt and restrict access to Finance group."
  }
]
```

### Sensitivity Levels
| Level | Description |
| :--- | :--- |
| **High** | PII, Credentials, Financial Data. Requires encryption. |
| **Medium** | Internal memos, project plans, non-public info. |
| **Low** | Public marketing materials, generic templates. |

---

## 🔧 Troubleshooting

### Common Issues

| Error | Cause | Fix |
| :--- | :--- | :--- |
| `404 Publisher Model Not Found` | Wrong Location | Ensure `GOOGLE_CLOUD_LOCATION=global` in `.env`. |
| `429 Too Many Requests` | SharePoint Throttling | The script automatically backs off. Wait a few minutes. |
| `KeyError: 'file'` | Invalid processing | The script skips folders automatically, but check if user permissions changed. |
| `ImportError: google.adk` | Missing dependency | Run `uv sync` or `uv add google-adk`. |

---
*Built with ❤️ by the Google Cloud AI Team.*
