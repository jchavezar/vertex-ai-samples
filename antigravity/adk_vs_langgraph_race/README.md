# AI Framework Race: ADK vs LangGraph

A real-time comparison tool that races Google ADK 2.0 against LangGraph using the same Gemini 2.5 Flash model.

## Features

- **Parallel Execution**: Both frameworks run simultaneously
- **3-Step Workflows**: Analyzer -> Reasoner -> Synthesizer
- **Real-time Visualization**: Watch the race unfold with live latency updates
- **Answer Evaluation**: Automated scoring using Gemini Flash Lite
- **Test Suite**: 8 complex multi-step reasoning questions

## Architecture

```
Query
  │
  ├─────────────────────┬─────────────────────┐
  │                     │                     │
  ▼                     ▼                     │
┌─────────────┐   ┌─────────────┐             │
│  Google ADK │   │  LangGraph  │             │
│    2.0      │   │             │             │
└──────┬──────┘   └──────┬──────┘             │
       │                 │                    │
       │  3-Step Flow    │  3-Step Flow       │
       │  ─────────────  │  ─────────────     │
       │  1. Analyzer    │  1. Analyzer       │
       │  2. Reasoner    │  2. Reasoner       │
       │  3. Synthesizer │  3. Synthesizer    │
       │                 │                    │
       ▼                 ▼                    │
  ┌─────────┐       ┌─────────┐               │
  │ Answer  │       │ Answer  │               │
  └────┬────┘       └────┬────┘               │
       │                 │                    │
       └────────┬────────┘                    │
                │                             │
                ▼                             │
       ┌────────────────┐                     │
       │   Evaluator    │◄────────────────────┘
       │ (Gemini Flash) │
       └───────┬────────┘
               │
               ▼
       ┌────────────────┐
       │    Winner!     │
       │ Speed + Score  │
       └────────────────┘
```

## Quick Start

```bash
# 1. Setup
chmod +x setup.sh
./setup.sh

# 2. Run
cd backend
uv run uvicorn main:app --reload --port 8080

# 3. Open browser
open http://localhost:8080
```

## Test Cases

| # | Name | Description |
|---|------|-------------|
| 1 | Multi-step Math | Train meeting time calculation |
| 2 | Logic Puzzle | 5-house ordering with constraints |
| 3 | Code Analysis | Python list comprehension sum |
| 4 | Science Reasoning | Physics ball drop comparison |
| 5 | Historical Analysis | Timeline calculations |
| 6 | Multi-hop Reasoning | Age algebra problem |
| 7 | Data Transformation | List operations chain |
| 8 | Business Calculation | Profit margin computation |

## Models Used

- **Reasoning**: Gemini 2.5 Flash Preview (both frameworks)
- **Evaluation**: Gemini 2.0 Flash Lite (fast scoring)

## Requirements

- Python 3.12+
- Google Cloud Project with Vertex AI enabled
- ADC configured (`gcloud auth application-default login`)

## Project Structure

```
adk_vs_langgraph_race/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── pyproject.toml       # Dependencies
│   └── workflows/
│       ├── adk_workflow.py      # Google ADK 2.0 implementation
│       ├── langgraph_workflow.py # LangGraph implementation
│       └── evaluator.py         # Answer evaluation
├── frontend/
│   └── index.html           # Race visualization UI
├── evaluation/
│   └── test_cases.md        # Expected answers
├── setup.sh                 # Setup script
└── README.md
```
