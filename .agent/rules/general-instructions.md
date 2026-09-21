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
Under any circumstances use old or obsolete models in your code develop and deploy like gemini-2.5*, gemini-2.0*, gemini-1.5*, text-bison* or any other old model. NEVER.
- Allowed models to use: gemini-3.7-flash, gemini-3.8-flash, gemini-3-flash-preview and gemini-3-pro-preview in ANY of your develops or troubleshooting.

## Think first before testing/publish
Because you are in a ssh session (jetski is running locally on my macbook and the resource is connecto through ssh to jchavezar.c.googlers.com) if you are gonna test "browsing" using or depending a specific port, you ALWAYS have to ask the user first to forward those ports, otherwise you wont be able to use them.


## Clean is important
After you do testings, creating new files, scripts etc and I ask for github pushes or "clean in general" besides the zero leak and other rules you already have I need you to keep the files and scripts in temporary folders out of the github (I dont need to backup unnecesary files).

## Python Backend & Environment Handling
- **Dotenv Overrides**: When loading `.env` files in Python servers/scripts, you MUST set `override=True` inside `load_dotenv(override=True)` to prevent system shell environment variables from hijacking your local configurations.
- **Port Conflict Management**: Before starting any local server or static web server on ports like `8000`, `8001`, or `5173`, you MUST verify if the port is currently in use. If it is in use, try to terminate the active listener using `kill -9 $(lsof -t -i:PORT)`. If the listener cannot/should not be terminated, you must locate another free port and dynamically configure the application and frontend variables to use that free port.
- **Proactive Port Allocation**: Before starting construction of any new application or pipeline, you MUST verify which ports are currently free. Dynamically configure and assign these free ports in the code and environment scripts *before* writing or compiling code, ensuring zero token waste on post-build port re-modifications.
- **Explicit GenAI Target**: Initialize Google GenAI clients explicitly specifying `vertexai=True`, target project ID, and region (e.g., `us-central1` or `us-east4`) rather than relying on default credentials, avoiding project quota mismatches.

## A2A Routing for "claude-code"
- **Automatic A2A Routing**: When a user's request begins with `claude-code`, the agent MUST automatically route the request through the deployed Vertex AI Reasoning Engine on GCP (Resource ID: `projects/254356041555/locations/us-central1/reasoningEngines/4299946434406383616`) using the A2A delegation protocol.
- **Output Presentation**: Stream the results, capture the complete text response, and display it back to the user in a clean, formatted Markdown layout.

## Universal LLM Chat Input Mechanics (Zero-Glitch Auto-Expanding Textarea)
- **Zero Scrollbar Defect**: Textareas in chat interfaces MUST NOT show premature vertical scrollbars on single lines or multiline placeholders. Apply `overflow-hidden` by default.
- **Reactive Height Sync**: Whenever creating or editing a chat prompt box in React, Vue, Svelte, or Vanilla JS, the textarea height MUST be dynamically recalculated via a reactive effect listening to the prompt state (`textarea.style.height = 'auto'; textarea.style.height = Math.min(textarea.scrollHeight, maxHeight) + 'px'`).
- **Dynamic Growth on Newlines**: Support seamless expansion when entering newlines (`\n` or `Shift+Enter`) up to `maxHeight` (e.g. 180px-200px), enabling scrolling only after exceeding the maximum height.
- **Reset on Submit**: After a message is submitted, the textarea height MUST immediately reset to its initial single-line `minHeight` (`style.height = 'auto'`).
- **Typography & No Resize**: Always set `resize: none` (`resize-none`), `line-height: 1.5` (`leading-relaxed`), and balanced padding to prevent glyph clipping.

## Autonomous Terminal Diagram & Visual Rendering (iTerm2 / CLI Protocol)
- **Zero Raw Mermaid Code Dumps**: NEVER output raw, unrendered ````mermaid` codeblocks in the terminal response text. In iTerm2 and terminal CLIs, raw Mermaid syntax prints as unreadable code lines.
- **Autonomous Visual Execution**: Whenever an architecture, flowchart, or diagram is needed, the agent MUST autonomously run `show-diagram` via `run_command` during the turn. This compiles the dark-themed visual graphic and executes macOS `open` so it pops onto the user's screen automatically.
- **Native In-Terminal Unicode Box Art**: Inside the terminal chat response itself, ALWAYS represent the topology using clean, high-contrast Unicode / ASCII box-drawing characters (`┌─┐`, `│ │`, `└─┘`, `──►`). This ensures the user gets instant, crystal-clear readability directly inside iTerm2 without context switching.
- **Autonomous Image/Artifact Display**: When generating or referencing images or HTML dashboards, autonomously trigger their display using macOS `open` so they are immediately visible.

## Zero "Copilot" Protocol (Institutional Branding)
- Under any circumstance NEVER use the word "copilot" (Microsoft trademark) in any code, UI, comments, scripts, or presentation materials for Weil or Google Cloud partner demos.
- Permitted branding: "Weil Deal & Regulatory AI Advisor", "Weil Deal Advisor 24/7", "Autonomous Legal Agent", or "Deal Advisor".

## UI/UX Container Spacing & Zero-Overlap Mandate
- In any web application or dashboard, strictly prevent overlapping containers, touching cards, or colliding boxes.
- Always use explicit flex/grid gaps (`gap-4 lg:gap-6`), `shrink-0` header elements, and clean divider borders (`border-slate-200/80 pl-4 ml-4`).
- Provide an "Inspect Code" overlay modal for live code review during presentations and a "100\" Display" toggle for auditorium/boardroom scaling.

## Presenter Representation for Weil
- The sole Google Cloud AI lead and speaker is Jesus Chavez (CE, AI). Ensure zero references to prior co-speaker names in slide decks, scripts, and documentation.



