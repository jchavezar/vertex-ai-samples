# Minimalist Custom UI // Bain Financial Analysis Agent

This directory contains the custom frontend user interface designed for **Bain & Company**, built with React 19, Vite, Tailwind CSS, Zustand, and the Vercel AI SDK.

## 🏛️ Design System: Yazdani Architectural Grid
This interface rigorously enforces the **Yazdani Architectural Grid** design system, mimicking the high-end drafting table precision of Yazdani Studio:
- **Sharp Rectilinear Geometry**: Zero rounded corners (`border-radius: 0 !important`). Every button, input field, and chat block is sharp and structural.
- **Monochrome & Warm Neutrals**: Built on off-white/alabaster (`#faf9f6`) canvas backgrounds, warm sand (`#f4f3ef`) panels, and deep charcoal (`#1a1a19`) text.
- **Ultra-Thin Dividers**: Sections are separated by extremely thin technical borders (`0.5px`, `#d8d6d0`).
- **Solid Black Voids**: Empty containers and placeholders are rendered as solid black boxes (`#111111`) to emphasize contrast.
- **Flat Textual Console**: The chatbot panel functions like a technical command console. Messages are plain text blocks aligned with left accent borders, completely eliminating bubble styles.
- **Scroll Isolation & Flex Bounding Chain**: Follows a strict flexbox height bounding chain (`min-height: 0`, `flex: 1`) to ensure chat histories stay locked inside the side drawer without stretching or breaking page layout dimensions.

## ⚡ Architecture: Zero-Parsing Financial Streaming
Implements the **Zero-Parsing** architecture using the Vercel AI SDK (`useChat`) and Zustand:
- **Data & Text Separation**: Strictly separates streaming text (`0: "content"`) from financial widget data (`2: [{"chart": ...}]`).
- **Global State (`dashboardStore.ts`)**: Uses Zustand to hold active financial positions and chart data, updating the main view dynamically without prop drilling or regex parsing fragility.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
Ensure you have Node.js installed, then run (using `--legacy-peer-deps` to resolve React 19 peer dependencies for `lucide-react`):
```bash
npm install --legacy-peer-deps
```

### 2. Verify Port Availability
We proactively verify and clean port `5185` before starting the development server to prevent port conflicts:
```bash
kill -9 $(lsof -t -i:5185) 2>/dev/null || true
```

### 3. Start the Development Server
```bash
npm run dev
```

Open your browser to `http://localhost:5185`.
