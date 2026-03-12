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

## Gemini Enterprise vs Agent Engine Deployment (CRITICAL)
- **Agent Engine** is the backend infrastructure (Reasoning Engine) where the code runs. Deploying to Agent Engine only exposes an API endpoint via Vertex AI.
- **Gemini Enterprise** is the consumer-facing user interface (agent builder/discovery engine). 
- **RULE:** If you are asked to deploy and register an agent, deploying to Agent Engine is NOT enough. You MUST also register the Reasoning Engine in the Gemini Enterprise App. If you cannot do this automatically, you MUST explicitly tell the user that they must go to the Gemini Enterprise Console to link the Reasoning Engine ID to complete the registration.

## Avoid
Under any circumstances use old models in your code develop and deploy like gemini-2.0* gemini-1.5* text-bison* or any other old model. NEVER.
- Allowed models to use: gemini-2.5-flash, gemini-2.5-pro, gemini-3-flash-preview and gemini-3-pro-preview in ANY of your develops or troubleshooting.