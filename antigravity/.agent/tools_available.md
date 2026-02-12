# 🛠️ Available Tools for Antigravity Agent

This document lists the tools available to the AI agent for assisting with coding, research, and development tasks. These tools allow the agent to move beyond text prediction and actually interact with the codebase, the internet, and external services.

## 🌐 Web & Internet (Sensory Tools)
- **`read_url_content`**: Fetches the text or markdown content of a public URL directly.
- **`search_web`**: Performs live web searches (via Brave Search) for the latest documentation, facts, or code fixes.
- **`browser_subagent`**: Dispatches a specialized agent to navigate, click, and interact with complex websites (supporting JavaScript and multistep flows). / **active browser.**

## 📁 File System & Research
- **`view_file`**: Reads the content of a specific file (supports text, images, and videos).
- **`view_file_outline`**: Shows a high-level overview of classes and functions in a file.
- **`list_dir`**: Lists the contents of a directory to understand project structure.
- **`grep_search`**: Powerful text search across the codebase.
- **`find_by_name`**: Finds specific files by name or glob pattern.

## 💻 Execution & Terminal
- **`run_command`**: Executes Linux shell commands (e.g., `npm install`, `pytest`, `uv run`).
- **`send_command_input`**: Interacts with long-running or interactive terminal processes (REPLs).
- **`command_status`**: Monitors the output and health of background tasks.

## ✍️ Code Editing
- **`write_to_file`**: Creates new files and directories from scratch.
- **`replace_file_content`**: Replaces a single contiguous block of code with precision.
- **`multi_replace_file_content`**: Performs multiple separate edits in a single file at once (best for refactoring).

## 🔌 Service Connectors (MCP)
- **Codemind**: Deep integration with internal developer systems:
    - **Critique**: Manage code reviews (CLs).
    - **Buganizer**: Track and update issues/bugs.
    - **Google Drive/Docs**: Create and read documentation.
    - **Sponge/XManager**: Access build logs and compute resources.
- **Glimpse**: AI-powered code graph search for large-scale architectural understanding.

## 🎨 Creative & Media
- **`generate_image`**: Generates custom UI assets, icons, and interface mockups based on descriptions.

---
*Generated: Tuesday, February 10, 2026*
