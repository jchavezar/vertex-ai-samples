# 🤖 Universal Agent Replication Packs (`agent-replication-packs/`)

This folder provides turnkey, natural-language "Zero-to-Production" replication blueprints, skills, and multi-agent workflows for **Jetski**, **Antigravity**, **Claude Code**, and **OpenAI Codex CLI**.

Any AI coding agent can ingest these files to autonomously provision **Cloud Spanner Hybrid GraphRAG**, compile the **8 synthetic M&A / Credit / NDA PDFs**, deploy the **MCP App (SEP-1865) Dual-Surface Grid & Citation Highlighter** to Cloud Run, and link it to **Gemini Enterprise's Default Assistant**.

---

## Directory Structure

```text
agent-replication-packs/
├── README.md                                  # Quickstart guide for all 4 agent runtimes
├── SKILL.md                                   # Universal Agent Skill (Jetski / Antigravity / Claude Code)
├── jetski-workflow/
│   ├── replicate_lexgraph_mcp_app_workflow.py     # Dynamic Python run_workflow (parallel + pipeline subagents)
│   └── JETSKI_PROMPT.md                       # Copy-paste natural-language prompt for Jetski
├── antigravity/
│   └── replicate-lexgraph-mcp-app.md              # Antigravity slash-command workflow (// turbo-all)
├── claude-code/
│   ├── CLAUDE.md                              # Drop-in CLAUDE.md project context & autonomous runbook
│   └── replicate-mcp-app.md                   # .claude/commands/replicate-mcp-app.md slash command
└── codex/
    ├── AGENTS.md                              # OpenAI Codex CLI autonomous execution spec
    └── CODEX_ONE_SHOT_PROMPT.txt              # Universal 1-shot natural-language prompt script
```

---

## How to Run in Each Agent Runtime

### 1. Jetski (Dynamic Parallel/Pipeline Multi-Agent Workflow)
In Jetski, either paste the natural-language prompt from [`jetski-workflow/JETSKI_PROMPT.md`](jetski-workflow/JETSKI_PROMPT.md) or instruct Jetski:
> *"Run the dynamic workflow `agent-replication-packs/jetski-workflow/replicate_lexgraph_mcp_app_workflow.py` using `run_workflow`."*

### 2. Antigravity (`.agent/skills` + `.agent/workflows`)
This repository already registers the skill and workflow at the root:
- Skill: [`.agent/skills/replicating-lexgraph-spanner-mcp-app/SKILL.md`](../../../.agent/skills/replicating-lexgraph-spanner-mcp-app/SKILL.md)
- Deploy Workflow: [`.agent/workflows/deploy-lexgraph-spanner-mcp-app.md`](../../../.agent/workflows/deploy-lexgraph-spanner-mcp-app.md)
- Teardown Workflow: [`.agent/workflows/destroy-lexgraph-spanner-mcp-app.md`](../../../.agent/workflows/destroy-lexgraph-spanner-mcp-app.md)

Trigger in Antigravity with `/deploy-lexgraph-spanner-mcp-app` or ask in natural language: *"Replicate the LexGraph Spanner GraphRAG MCP App."*

### 3. Claude Code (`CLAUDE.md` + `/replicate-mcp-app`)
Copy `claude-code/CLAUDE.md` to your workspace root and `claude-code/replicate-mcp-app.md` into `.claude/commands/`:
```bash
cp agent-replication-packs/claude-code/CLAUDE.md .
mkdir -p .claude/commands
cp agent-replication-packs/claude-code/replicate-mcp-app.md .claude/commands/
claude "/replicate-mcp-app"
```

### 4. OpenAI Codex CLI (`AGENTS.md` + One-Shot Natural Language Script)
Run Codex with `codex/AGENTS.md` and the one-shot natural language script:
```bash
cp agent-replication-packs/codex/AGENTS.md .
codex "$(cat agent-replication-packs/codex/CODEX_ONE_SHOT_PROMPT.txt)"
```
