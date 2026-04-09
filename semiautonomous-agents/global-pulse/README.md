# Global Pulse — International News Intelligence

An agentic news research platform that searches 15+ international sources across multiple languages, computes veracity scores, detects signals, and generates intelligence reports.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                     │
│  SearchBar → ConciseAnswer + VeracityGauge + SourceMap      │
│  SourceCards (15+) + SignalBadges + ReportPanel              │
└──────────────────────────┬──────────────────────────────────┘
                           │ POST /api/investigate
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (:8888)                     │
│  Veracity Engine: source tiers, cross-ref, bias balance      │
│  Diversity Radar: 5-dimension analysis scoring               │
└──────────────┬────────────────────────────┬──────────────────┘
               │                            │
               ▼                            ▼
┌──────────────────────────┐  ┌────────────────────────────────┐
│  News Research Agent     │  │  Veracity Engine               │
│  Gemini 2.5 Flash        │  │  Source tier classification     │
│  + Google Search          │  │  Cross-reference scoring       │
│  grounding               │  │  Bias balance analysis         │
│                          │  │  Signal detection              │
│  3-phase search:         │  │  Diversity radar               │
│  1. Broad international  │  │                                │
│  2. Regional deep-dives  │  └────────────────────────────────┘
│  3. Synthesis            │
└──────────────────────────┘
```

## The Veracity Algorithm

Like vibes_nyc's "underground score" — but for news truthfulness:

| Factor | Max Points | How |
|---|---|---|
| Source Tier | +20 | Tier 1 (Reuters, AP, BBC) score highest |
| Cross-Reference | +25 | More independent sources = higher score |
| Geographic Diversity | +15 | Sources from more countries = higher |
| Language Diversity | +12 | Multi-language coverage = higher |
| Bias Balance | +10 / -15 | Diverse bias spectrum = bonus; monoculture = penalty |
| Signal Consistency | +10 / -15 | Agreement on story status boosts score |
| State Media Penalty | -20 | State-controlled sources reduce score |

Source tiers classify 50+ outlets into T1 (wire services, public broadcasters), T2 (major newspapers), T3 (state media, tabloids, partisan outlets).

## Quick Start

### Backend

```bash
cd global-pulse

# Copy env and configure
cp .env.example .env
# Edit .env: set PROJECT_ID, optionally set USE_MOCK_DATA=true

# Install and run
uv venv && source .venv/bin/activate
uv pip install fastapi uvicorn google-genai pydantic
python -m backend.main
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Features

- **Impartial Analysis**: Searches sources from 5+ countries and 3+ languages per query
- **Veracity Score**: 0-100 score based on source quality, cross-referencing, and bias balance
- **Signal Detection**: Classifies news as BREAKING, DEVELOPING, CONFIRMED, DISPUTED, or ANALYSIS
- **Source Map**: Interactive world map showing where each source originates
- **Intelligence Report**: Detailed markdown report with regional perspectives and consensus analysis
- **50+ Source Database**: Pre-classified international outlets with trust scores and bias ratings
- **Mock Mode**: Full demo data for development without API keys

## Tech Stack

- **Agent**: Gemini 2.5 Flash + Google Search grounding (Vertex AI)
- **Backend**: FastAPI (async Python)
- **Frontend**: React 19 + TypeScript + Vite
- **Map**: Leaflet + CartoDB dark tiles
- **Icons**: Lucide React
