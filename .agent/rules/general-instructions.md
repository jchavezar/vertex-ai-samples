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


## Avoid
Under any circumstances use old models in your code develop and deploy like gemini-2.0* gemini-1.5* text-bison* or any other old model. NEVER.
- Allowed models to use: gemini-2.5-flash, gemini-2.5-pro, gemini-3-flash-preview and gemini-3-pro-preview in ANY of your develops or troubleshooting.

## Think first before testing/publish
Because you are in a ssh session (jetski is running locally on my macbook and the resource is connecto through ssh to jchavezar.c.googlers.com) if you are gonna test "browsing" using or depending a specific port, you ALWAYS have to ask the user first to forward those ports, otherwise you wont be able to use them.


## Clean is important
After you do testings, creating new files, scripts etc and I ask for github pushes or "clean in general" besides the zero leak and other rules you already have I need you to keep the files and scripts in temporary folders out of the github (I dont need to backup unnecesary files).

## Python Backend & Environment Handling
- **Dotenv Overrides**: When loading `.env` files in Python servers/scripts, you MUST set `override=True` inside `load_dotenv(override=True)` to prevent system shell environment variables from hijacking your local configurations.
- **Port Conflict Management**: Before starting any local server or static web server on ports like `8000`, `8001`, or `5173`, you MUST verify if the port is currently in use. If it is in use, try to terminate the active listener using `kill -9 $(lsof -t -i:PORT)`. If the listener cannot/should not be terminated, you must locate another free port and dynamically configure the application and frontend variables to use that free port.
- **Proactive Port Allocation**: Before starting construction of any new application or pipeline, you MUST verify which ports are currently free. Dynamically configure and assign these free ports in the code and environment scripts *before* writing or compiling code, ensuring zero token waste on post-build port re-modifications.
- **Explicit GenAI Target**: Initialize Google GenAI clients explicitly specifying `vertexai=True`, target project ID, and region (e.g., `us-central1` or `us-east4`) rather than relying on default credentials, avoiding project quota mismatches.