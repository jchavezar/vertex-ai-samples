# 🌌 Nexus Search Academy (Year 3050 Edition)

> **Status:** Cybernetically Enhanced & Operational 🚀
> **Location:** `antigravity/nexus_search_academy`

Welcome to the **Nexus Search Academy**, a futuristic, interactive learning environment designed to guide you through the inner workings of **Secure Workload Identity Federation (WIF)** and **Vertex AI Discovery Engine** integrations.

This application isn't just a tool; it's a holographic dashboard that strips away the black box of enterprise security, showing you every token, every hash, and every API packet in real-time.

---

## 🛰️ Application Ports

| Component | Port | Tech Stack |
| :--- | :--- | :--- |
| **Frontend** | `5179` | Vite + React ⚛️ |
| **Backend** | `8010` | FastAPI + UV 🐍 |

---

## 🧠 The Authentication Cycle

To communicate with the Discovery Engine without managing risky static service account keys, we utilize a secure Token Exchange workflow. 

Below is the architectural flowchart demonstrating how we translate a corporate identity (Microsoft Entra ID) into a Google Cloud access token.

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
graph TD
    subgraph "Client Environment (Browser)"
        User([User 👤]) -->|1. Clicks Login| FE[Frontend App 🖥️]
        FE -->|2. Redirect to Auth| MS
        MS -->|3. Return id_token| FE
        FE -->|4. Update Code Visualiszer| FE
        FE -->|5. Send id_token Request| BE[Backend API ⚙️]
    end

    MS[Microsoft Entra ID 🔐]
    STS[Google STS 🔑]
    DE[Discovery Engine 🧠]

    BE -->|6. POST /sts/v1/token| STS
    STS -->|7. Issue Google Token| BE
    BE -->|8. executeStreamAssist| DE
    DE -->|9. SSE Stream Responses| BE
    BE -->|10. Reactive Stream| FE

    classDef chrome fill:#0b1120,stroke:#00f3ff,stroke-width:2px;
    classDef server fill:#0b1120,stroke:#ab00ff,stroke-width:2px;
    classDef provider fill:#040914,stroke:#00ff66,stroke-width:2px;
    
    class FE chrome;
    class BE server;
    class MS,STS,DE provider;
```

---

## 🛠️ Core Features

### 1. Step-by-Step Interactive Walkthrough
Navigate through the lifecycle of a query:
*   **Identity Provider Login:** Direct OAuth redirect.
*   **Hash Fragment Listener:** Real-time extraction.
*   **STS Token Exchange:** Transparent token visualization.
*   **Authenticated StreamAssist:** Live SSE streams.

### 2. Reactive Chat Overlay
An AI-powered assistant is always on standby in the bottom right corner.
*   **Maximized Mode:** Expand to fill the glassmorphic visor view.
*   **Grounding Indicator:** Instant HUD response verification (`Telemetry Grounded`).
*   **Streaming HUD:** Watch responses populate fluidly.

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
