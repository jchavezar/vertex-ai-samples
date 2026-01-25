# Stock Terminal Next-Gen (Refactor)

This is a modernized version of the Stock Terminal application, refactored to use **Vercel AI SDK Protocol v1** and **React 19** principles.

## Key Architecture Changes
*   **Protocol:** Uses `0:` (Text) and `2:` (Data) stream parts instead of Regex parsing.
*   **State:** Uses **Zustand** for global dashboard state instead of prop drilling.
*   **Chat:** Uses `ai/react` (`useChat` hook) for robust stream handling.
*   **Backend:** Uses **FastAPI** + **Pydantic V2** for type-safe widget generation.

## How to Run

### 1. Backend
```bash
cd backend
# Create venv and install dependencies
uv pip install -r pyproject.toml

# Run server
# Ensure GOOGLE_API_KEY is set in .env or environment
uvicorn src.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Usage
Open `http://localhost:5173`.
*   Ask: "Show me a chart of AAPL" -> Backend streams a `ChartWidget` (Protocol Type 2).
*   Frontend `useTerminalChat` hook catches the data block and updates the Zustand store.
*   Dashboard automatically renders the chart using Recharts.
