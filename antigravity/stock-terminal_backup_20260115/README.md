# Stock Terminal Project

This project contains a financial stock terminal application with a Python FastAPI backend and a React (Vite) frontend.

## Project Structure

- `backend/`: Python FastAPI application using `uv` for dependency management.
- `frontend/`: React application using Vite.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (for Python backend)
- [Node.js](https://nodejs.org/) & npm (for Frontend)

## Getting Started

You need to run both the backend and frontend terminals simultaneously.

### 1. Backend Setup

Navigate to the backend directory and run the server:

```bash
cd backend
uv sync
uv run main.py
```

The backend API will start at `http://localhost:8001`.

### 2. Frontend Setup

Open a new terminal, navigate to the frontend directory, and start the development server:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start at `http://localhost:5173` (or similar) and connect to the backend at port 8001.

## Features

- **Real-time Stock Data**: Fetches data using `yfinance`.
- **AI Summaries**: Uses Google Gemini to summarize dashboard data.
- **FactSet Integration**: Optional integration with FactSet for professional data (requires auth).
- **Interactive Chat**: AI-powered chat assistant for financial questions.
