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
Because you are in a ssh session (jetski is running locally on my macbook and the resource is connecto through ssh to sockcop.c.googlers.com) if you are gonna test "browsing" using or depending a specific port, you ALWAYS have to ask the user first to forward those ports, otherwise you wont be able to use them.


## Clean is important
After you do testings, creating new files, scripts etc and I ask for github pushes or "clean in general" besides the zero leak and other rules you already have I need you to keep the files and scripts in temporary folders out of the github (I dont need to backup unnecesary files).