---
name: replicating-legacy-to-ai-modernization
description: Orchestrates setup, testing, and teardown of the Legacy to AI-Native Modernization Hub (EBC Showcase). Use when the user requests deployment, replication, or testing of the modernization hub.
---

# Replicating Legacy to AI-Native Modernization Hub

This skill provides step-by-step instructions for provisioning, running, and testing the **Antigravity Legacy to AI-Native Modernization Hub**, demonstrating the transformation of a 2015-era monolithic ERP table into a 2026 reactive Agent-Native Generative UI.

---

## 1. Quick Verification & Setup

Run the idempotent setup script to record resource state and verify environment:

```bash
uv run agy-recipes/legacy-to-ai-modernization/scripts/setup.py
```

---

## 2. Launching the Showcase Hub

To launch both backend (FastAPI, port 8008) and frontend (React 19 + Vite, port 5178):

```bash
cd semiautonomous-agents/legacy-to-ai-modernization-hub
./start.sh
```

---

## 3. Automated Endpoint Diagnostics

Run the automated endpoint test suite against the running service:

```bash
uv run agy-recipes/legacy-to-ai-modernization/scripts/test_recipe.py
```

---

## 4. Teardown and Cleanup

To clean up all local processes and remove the state tracker:

```bash
uv run agy-recipes/legacy-to-ai-modernization/scripts/teardown.py
```
