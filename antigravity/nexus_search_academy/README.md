# 🌌 Nexus Search Academy (Year 3050 Edition)

<div align="center">

![Nexus Academy Header](./assets/nexus_search_academy_header_1773929912159.png)

[![Security: WIF](https://img.shields.io/badge/Security-Workload%20Identity%20(WIF)-00f3ff?style=for-the-badge&logo=google-cloud&logoColor=white)](#)
[![Model: Gemini](https://img.shields.io/badge/AI%20Model-Gemini%202.5-00ff66?style=for-the-badge&logo=google-gemini&logoColor=white)](#)
[![Framework](https://img.shields.io/badge/Stack-Vite%20%2B%20FastAPI-ab00ff?style=for-the-badge&logo=fastapi&logoColor=white)](#)

</div>

---

## 🛰️ Overview

Welcome to the **Nexus Search Academy**, a futuristic holographic dashboard designed to strip away the black box of enterprise security and RAG operations. Guide operations through **Secure Workload Identity Federation (WIF)** translates and triggers strictly trimmed flows back down into sub-indexed frames dynamically.

To communicate with the Discovery Engine without maintaining static long-lived keys, we utilize transparent Token Exchange translation pipelines binding securely to targeted indices.

---

## 🛰️ Dashboard Dashboard Previews

### 🔬 Inner Auditing View (Step 5)
Monitor exactly which DataStores (e.g., SharePoint Online Federated Indices) are executing background queries along with raw layout configurations frames transparently.

![Dashboard Preview Step 5](./assets/nexus_search_academy_step5_1773931181078.png)

### 🤖 Live Agent Smith stream assist
Trigger live AI prompts executing strictly isolated streaming pipelines maintaining visual audit streams collapsibly above clean narrative replies.

![Agent Smith View Screen](./assets/nexus_search_academy_with_agent_smith_1773931216260.png)

---

## 🛠️ Core Upgrades Layered

*   **🧠 Dynamic Reasoning Tracking Box:** Transparently separates AI intermediate "Thinking" logs (`Assessing Database...`, `Formulating Query...`) inside styled collapsible Panel overlays above Markdown descriptive layouts buffers directly!
*   **🛰️ Transparent SharePoint diagnostics Specs:** Explicit payload structures layout accurately inside debug logs fully describing direct workspace index target addresses securely without rendering dead-ends layout templates or ambiguity lists.

---

## 🧠 The Authentication Cycle

Below is the sequential architectural flowchart demonstrating how we translate corporate Identities (Microsoft Entra ID) securely into a transparent Google Cloud access credential bind.

```mermaid
%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'primaryColor': '#00f3ff',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#00f3ff',
    'lineColor': '#ab00ff',
    'secondaryColor': '#0a0e17',
    'tertiaryColor': '#00ff66',
    'mainBkg': '#030712',
    'nodeBorder': '#00f3ff',
    'clusterBkg': '#0f172a',
    'clusterBorder': '#1e293b'
  }
}}%%
graph LR
    subgraph UI [Browser Layout]
        direction TB
        User([User 👤])
        FE[Frontend App 🖥️]
        User -->|1. Clicks Login| FE
        FE -.->|4. Render telemetry| FE
    end

    subgraph Entra [Azure Workspace]
        MS[Microsoft Entra ID 🔐]
    end

    subgraph Host [FastAPI Gateway]
        direction TB
        BE[Backend API ⚙️]
        STS[Google STS 🔑]
    end

    subgraph Vertex [Discovery Engine]
        DE[Discovery Engine 🧠]
    end

    %% Client authentication trigger
    FE -->|2. Redirect| MS
    MS -->|3. Return id_token| FE
    FE -->|5. Forward id_token| BE

    %% Exchange & Groundings
    BE -->|6. POST /sts/token| STS
    STS -->|7. Return Access_Token| BE
    BE -->|8. executeStreamAssist| DE
    DE -->|9. SSE Streams responses| BE
    BE -->|10. Push UI Stream| FE

    classDef chrome fill:#0b1120,stroke:#00f3ff,stroke-width:2px;
    classDef server fill:#0b1120,stroke:#ab00ff,stroke-width:2px;
    classDef provider fill:#040914,stroke:#00ff66,stroke-width:2px;
    
    class FE chrome;
    class BE server;
    class MS,STS,DE provider;
```

---

## 📖 Essential references

For concrete Python execution guidelines covering how the backend swaps security frameworks endpoints dynamically before triggerings:

*   🛰️ **[`SHAREPOINT_STS_SPEC.md`](./SHAREPOINT_STS_SPEC.md)**: Full configuration spec template mapping indices to backend pipelines correctly!

---

## ⚙️ Configuration & Environment Setup

To allow other users to load their own Microsoft Entra ID and Google Cloud Workload Identity Federation specs into this tool, follow these environment variable setup guides.

### 1. 🖥️ Frontend setup
Navigate to the `frontend` directory and copy the template:
```bash
cd frontend
cp .env.example .env
```
Open `.env` and configure your **Microsoft Entra ID Application Dashboard** bindings:
*   `VITE_MS_APP_ID`: Your client Application (App Registrations) ID
*   `VITE_TENANT_ID`: Your corporate Azure Tenant ID
*   `VITE_WIF_POOL`: Google Cloud IAM Workload Identity Pool ID
*   `VITE_WIF_PROVIDER`: Google Cloud IAM Workload Identity Pool Provider ID

### 2. ⚙️ Backend Setup
Navigate to the `backend` directory and copy the template:
```bash
cd backend
cp .env.example .env
```
Open `.env` and configure your **Google Cloud Vertex AI Search index targets**:
*   `PROJECT_NUMBER`: Your Google Cloud numeric Project Number (not project-id string)
*   `ENGINE_ID`: Vertex AI App/Engine Identifier
*   `DATA_STORE_ID`: Primary DataStore Bucket target ID

---

## 🚀 Launch Procedure

To ignite the subsystem, use the absolute controller:

```bash
# Navigate to Scratch Control
cd /usr/local/google/home/jesusarguelles/.gemini/jetski/scratch

# Fire default thrusters
./restart_academy.sh
```

*The Academy is officially online.*
