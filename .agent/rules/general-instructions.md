---
trigger: always_on
---

# Global Agent Rules

## Python Project Management
- **ALWAYS use `uv`** for Python project management, environment handling, and execution.
- Initialize new projects with `uv init` and manage dependencies via `uv add`.
- Execute all code using `uv run` to ensure environment isolation.

## Mode Behavior
- When "ro" is called I need the agent to behave like an assistant to answer questions, no to run workflows, depelop, create, etc I just need it to answer questions.

## Documentation Rules
- Every new folder needs to be put in the main index in the antigravity folder every time you push it.