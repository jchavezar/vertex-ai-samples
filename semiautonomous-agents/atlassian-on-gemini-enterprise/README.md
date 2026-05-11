# Atlassian on Gemini Enterprise — Two Patterns + Comparative Eval

Side-by-side reference for putting Atlassian Jira behind a chat agent, with a 500-question benchmark that scores both head-to-head.

| | Option A — Custom MCP Portal | Option B — Direct Remote MCP |
|---|---|---|
| Folder | [`option-a-custom-mcp-portal/`](./option-a-custom-mcp-portal/) | [`option-b-direct-remote-mcp/`](./option-b-direct-remote-mcp/) |
| Who runs the MCP server | **You** (Cloud Run, FastAPI) | **Atlassian** (`mcp.atlassian.com/v1/mcp`) |
| Who runs the agent | **You** (Vertex AI Agent Engine + Google ADK + Gemini 3) | Gemini Enterprise (or Claude Code, OpenAI Codex, etc. — anything that speaks MCP) |
| Tools available | Whatever you ship (current: 7 — search, report, summarize, list-projects, comments, worklogs, links) | The ~37 tools Atlassian publishes |
| Custom logic (pagination, formatting, business rules) | **Yes — full control** | No — what Atlassian ships is what you get |
| Setup time | Higher (build, deploy, register agent + auth) | Lower (DCR + console flow, ≤ 30 min) |
| Ongoing maintenance | You patch the MCP server, manage Cloud Run, ADK upgrades | Zero — Atlassian operates |
| Observability | Full Vertex AI logs + Cloud Run logs + ADK traces | Whatever the consumer logs |
| Where the LLM runs | Gemini in your Agent Engine | Whatever consumer you wire it to |

## When to pick which

- **A** when you need pagination over thousands of issues, custom tools, embedded business rules, and full observability — and you accept the ops burden.
- **B** when you want fastest time-to-value, the Atlassian-published tool catalog covers your use case, and you don't want to operate Cloud Run + Agent Engine.
- **Both** — A for analytics/dashboards, B for interactive lookups, registered side-by-side in the same engine.

Setup guides:
- [Option A — step-by-step](./option-a-custom-mcp-portal/README.md) + [PAGINATION.md](./option-a-custom-mcp-portal/PAGINATION.md)
- [Option B — step-by-step](./option-b-direct-remote-mcp/README.md)

---

## Comparative evaluation

500 grounded questions × 20 categories × 5 Jira projects (~1,310 issues). Same questions through both pipelines, scored by Claude Opus on 10 dimensions.

**Latest run (2026-05-11) — Gemini + Custom MCP vs Claude Code + Atlassian Rovo MCP:**

| | Gemini + Custom MCP | Claude Code + Rovo MCP |
|---|---|---|
| **Composite** | **91.3%** | **87.1%** |
| Citation accuracy | **99.9%** | 69.5% |
| Hallucination rate ↓ | **1.1%** | **68.9%** ⚠️ |

📊 **[View the report (with side-by-side wrong answers)](https://htmlpreview.github.io/?https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/atlassian-on-gemini-enterprise/eval/sample-run/report.html)**

The composite difference is small (4.2pp) but the failure shapes are very different. Claude+Rovo wins on **reasoning and single-issue precision** (lookup, epic-tree, comments, narrative trends — all ≥ 92%). Gemini+CustomMCP wins on **structured correctness** (counts, JQL, pagination, multi-project filters — all ≥ 84%) and has 60× lower hallucination of issue keys. The hallucination disparity is the biggest finding: a Jira agent that confidently cites fake issue keys creates broken URLs.

Full methodology + per-category breakdown: [`eval/README.md`](./eval/README.md). Question taxonomy: [`eval/question_categories.md`](./eval/question_categories.md). Reproducible run artifacts: [`eval/sample-run/`](./eval/sample-run/).

---

## Repo layout

```
atlassian-on-gemini-enterprise/
├── README.md                       (this file)
├── option-a-custom-mcp-portal/     (Vertex AI Agent + Cloud Run MCP)
├── option-b-direct-remote-mcp/     (Atlassian Rovo as a GE MCP datastore)
└── eval/                           (500-question harness)
    ├── README.md                   reproduction recipe
    ├── question_categories.md      the 20 categories + what each tests
    ├── jira_oracle.py              Jira REST helpers (Basic auth)
    ├── build_corpus.py             create 4 test projects + ~400 issues
    ├── generate_questions.py       grounded LLM question generation
    ├── runners/                    streamAssist callers + orchestrator
    ├── judge.py                    multi-dim Claude Opus judge
    ├── report.py                   pure-CSS HTML side-by-side
    └── sample-run/                 the latest committed run
```
