---
name: pulse-spend-ai-dashboard
description: Complete blueprint & functional instructions to build the PulseSpend AI Spending Analytics Platform and Spend Galaxy Constellation Explorer from scratch using FastAPI, React, Tailwind CSS, Chart.js, and Vertex AI (Gemini 3.5 Flash).
---

# 🌌 PulseSpend AI: Blueprint & Skill Instructions

This skill provides a comprehensive design, architecture, and functional specification to reproduce **PulseSpend AI** — an executive spending intelligence platform featuring an interactive **Spend Galaxy Constellation Explorer**, automated **Amex CSV Statement Importer**, **Cardholder Household Comparison**, and **Gemini 3.5 Flash Financial Audit Agent**.

---

## 🏗️ 1. Technical Stack & System Architecture

### Backend Stack
- **Framework**: FastAPI (Python 3.9+) with Uvicorn server on port `8001`.
- **AI Model Client**: Vertex AI SDK (`google-genai`) configured for `gemini-2.5-flash` in `us-central1`.
- **Data Engine**: Pandas for CSV parsing, statistical aggregations, and merchant string cleaning.
- **API CORS**: Configured to allow origins `http://localhost:5173` and `http://127.0.0.1:5173`.

### Frontend Stack
- **Framework**: React 19 + Vite 8 on port `5173`.
- **Styling**: Tailwind CSS v4 with custom dark space theme and glassmorphism utilities.
- **Charts**: `react-chartjs-2` + `Chart.js` for Line timeline, Doughnut category splits, and Bar intent charts.
- **Icons**: `lucide-react` for UI icons.
- **Vite Proxy**: Proxy `/api` requests to `http://127.0.0.1:8001` to resolve macOS IPv6 port binding.

---

## 🎨 2. Cosmic Design System & Visual Tokens

### Palette Tokens
- **Canvas Base Background**: Midnight Space Slate (`bg-slate-950` `#020617`).
- **Glassmorphism Panels**: `bg-slate-900/80 border border-slate-800/80 backdrop-blur-xl shadow-2xl rounded-3xl`.
- **Primary Brand Gradient**: `from-violet-600 via-indigo-500 to-cyan-400`.
- **Cardholder Accent Colors**:
  - Card Member 1 (Violet): `#8b5cf6` (Indigo/Violet glow)
  - Card Member 2 (Cyan): `#06b6d4` (Cyan glow)
  - Refund / Credit (Emerald): `#10b981` (Emerald green glow)
  - Luxury / Lifestyle (Pink): `#ec4899` (Hot pink glow)
  - AI Assistant (Amber): `#f59e0b` (Amber gold glow)

---

## 📊 3. Amex CSV Parsing & AI Enrichment Engine

### CSV Input Schema
Accepts standard American Express CSV exports containing columns:
`Date, Description, Card Member, Account #, Amount, Extended Details, Appears On Your Statement As, City/State, Country, Category`

### Merchant String Normalization Algorithm
1. Strip payment gateway noise prefixes using regex:
   `^(AplPay|TST\*|SP\*|BT\*DD \*|DD \*|SP )\s*`
2. Strip city/state location suffixes:
   `\s+(NEW YORK|MANHATTAN|BEVERLY HILLS|LOS ANGELES|ATLANTA|SAN FRANCISCO|BROOKLYN)\b.*`
3. Map cleaned strings to canonical brand names (*Sephora*, *Grubhub*, *Delta Air Lines*, *Whole Foods Market*, *Nordstrom Direct*, *Amazon*, *Target*, *Uber*, *Midjourney AI*).

### Classification Taxonomy
- **Primary Categories**: *Dining & Food Delivery*, *Groceries & Household*, *Fashion, Beauty & Luxury*, *Travel & Transit*, *Digital & Subscriptions*, *Health & Fitness*, *Pet Care*, *Services & General*, *Refund & Credit*.
- **Expense Intent Types**: *Essential*, *Lifestyle & Luxury*, *Food & Dining*, *Subscription*, *Travel & Transit*, *Healthcare*, *Pet Care*, *Refund/Credit*.
- **Necessity Score (1-5 Stars)**:
  - `1`: High luxury apparel, designer fashion, boutique spa.
  - `2`: Food delivery apps, dining out, entertainment.
  - `3`: Subscriptions, software, travel transit.
  - `4`: Fitness memberships, pet supplies, pharmacy.
  - `5`: Essential groceries, utilities, medical clinics.
- **Micro-Tags**: Automatically append 2-3 hashtag labels (`#Groceries`, `#DeliveryApp`, `#Fashion`, `#Travel`).

---

## 🪐 4. Spend Galaxy Constellation Physics Engine

The Spend Galaxy renders category transactions as an interactive 2D orbital planetary system.

### Coordinate & Orbital Physics Specs
1. **Fibonacci / Golden Angle Orbital Placement**:
   For sorted transactions $i = 0, 1, \dots, N-1$:
   $$r_i = R_{\text{base}} + \sqrt{i + 1} \cdot S_{\text{radial}} \quad (R_{\text{base}} = 70\text{px}, S_{\text{radial}} = 62\text{px})$$
   $$\theta_i = i \cdot 137.5^\circ + \text{jitter}$$
   $$x_i = X_{\text{center}} + r_i \cos(\theta_i), \quad y_i = Y_{\text{center}} + r_i \sin(\theta_i)$$
2. **Node Scale Formula**:
   $$D_i = \max\left(20\text{px}, \min\left(56\text{px}, \sqrt{|\text{Amount}_i|} \cdot 1.9 + 14\right)\right)$$
3. **Orbital Rings**: Render concentric SVG/CSS orbital rings around central total spend nucleus.
4. **Always-On Brand Pill Badges**: Render a glassmorphism pill badge attached to each node showing `[ Clean Merchant Name | $Amount ]`.
5. **Pan & Zoom Navigation**:
   - **Mouse Drag**: Update canvas translation vector $(X_{\text{pan}}, Y_{\text{pan}})$.
   - **Wheel Zoom**: Multiplicative zoom scale factor between $0.4\times$ and $3.0\times$.
6. **Subcategory Solar System Clusters**: Filter buttons isolate and highlight specific subcategory clusters (*Supermarket*, *Air Travel*, *Apparel*).
7. **In-Galaxy Planet Search**: Highlights and scales matching planet nodes ($1.4\times$ scale multiplier with intense glowing beam).
8. **Widescreen Fullscreen Canvas**: Expands modal workspace to 100% viewport dimensions.

---

## 🖥️ 5. Component Breakdown & Layout Architecture

### `Navbar` Component
- Brand badge with pulsing AI icon.
- Date range badge (`07/01/2026 - 07/27/2026`).
- Card Member filter dropdown (*All Members*, *Alex Morgan*, *Jordan Taylor*).
- Hidden file input `<input type="file" accept=".csv" />` triggered by `[ 📥 Import Amex CSV ]` button.
- `[ ✨ AI Audit Report ]` action trigger.
- Navigation tabs: *Dashboard Overview*, *AI Patterns & Anomalies*, *Cardholder Breakdown*, *Spending Ledger*, *Ask AI Assistant*.

### `MetricCard` Component
- Displays KPI metric (*Gross Expenses*, *Refunds & Credits*, *Net Outflow*, *Top Category*).
- Formatted dollar amounts, transaction counts, percentage trends, and glowing icon avatars.

### `SpendTimelineChart` Component
- Chart.js smooth line chart plotting daily Gross Spend (Violet curve), Refunds (Emerald dashed curve), and Net Outflow (Cyan curve).

### `CategoryBreakdownChart` Component
- Chart.js Doughnut chart showing primary category percentage distribution.
- Clicking any category slice opens the Spend Galaxy Constellation for that category.

### `ExpenseTypeChart` Component
- Chart.js Bar chart plotting behavioral expense intents.
- Features prominent **`[ 🪐 Explore Galaxy ]`** launcher button.

### `CardholderComparison` Component
- Side-by-side comparison cards for each card member.
- Visual net spend percentage progress bar, average order value, return count, and top individual merchant.

### `TransactionsTable` Component
- Searchable spending ledger table with cardholder badges, necessity star rating indicator (1-5 stars), category chips, and micro-tags.
- Clicking any row opens a transaction inspector modal.

### `AIAuditDrawer` Component
- Narrative executive report powered by `gemini-2.5-flash`.
- Executive summary narrative, key spending metrics, anomaly highlights, behavioral pattern cards, and savings tips.

### `AskAIAssistant` Component
- Interactive AI Q&A chat drawer sending prompts to `/api/ai/chat`.
- Renders formatted markdown responses and quick suggestion pills (*"Where did I spend the most?"*, *"How much was spent on food delivery?"*).

---

## 🔌 6. Backend API Specification

| Endpoint | Method | Input Params | Response Payload |
| :--- | :--- | :--- | :--- |
| `/api/health` | `GET` | None | `{"status": "healthy", "record_count": N, "ai_ready": true}` |
| `/api/upload-csv` | `POST` | `file: UploadFile` | `{"message": "...", "kpis": {...}}` |
| `/api/kpis` | `GET` | None | `{"total_gross": float, "total_refunds": float, "total_net": float, "total_count": int, "avg_transaction": float, "top_merchant": str, "top_category": str}` |
| `/api/analytics/categories` | `GET` | None | List of `{"category": str, "total_spent": float, "count": int, "percentage": float}` |
| `/api/analytics/expense-types`| `GET` | None | List of `{"expense_type": str, "total_spent": float, "count": int}` |
| `/api/analytics/cardholders` | `GET` | None | Object mapping cardholder names to net spent, gross spent, refunds, and top merchant |
| `/api/analytics/merchants` | `GET` | `top_n: int` | List of top merchants ranked by total gross spending |
| `/api/analytics/timeline` | `GET` | None | List of daily timeline points `{"date": str, "gross": float, "refunds": float, "net": float}` |
| `/api/analytics/tags` | `GET` | None | Tag frequency cloud distribution `{"tag": str, "count": int, "total_spent": float}` |
| `/api/transactions` | `GET` | `card_member`, `category`, `expense_type`, `search` | Filtered list of enriched transaction records |
| `/api/ai/audit-report` | `GET` | `force_refresh: bool` | Gemini 3.5 Flash narrative audit report object |
| `/api/ai/chat` | `POST` | `{"query": str}` | `{"reply": str}` powered by Gemini 3.5 Flash |

---

## 🚀 7. How to Invoke & Use This Skill

Developers or AI agents can activate this skill to construct or verify the PulseSpend AI application:

1. **Read Blueprint Specs**: Use `view_file` to review this `SKILL.md` file.
2. **Setup Stack**: Initialize FastAPI backend and React Vite frontend following the technical stack guidelines in Section 1.
3. **Implement Data Engine**: Implement CSV normalization and classification rules according to Section 3.
4. **Build Spend Galaxy Physics**: Implement the Golden Ratio spiral coordinate formula and Pan/Zoom physics according to Section 4.
5. **Apply Cosmic Theme**: Apply Tailwind CSS slate background `#020617` and glassmorphism styling according to Section 2.
