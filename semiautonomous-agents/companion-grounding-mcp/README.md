# Local Companion Grounding Engine & Database

A private, 100% local grounding connector and SQLite Full-Text Search (FTS5) engine running on Apple Silicon. It indexes historical communications, Google Meet calls, and multi-month strategic advisories to provide instantaneous recall for relationship dynamics, interaction calibration, and communication coaching.

## Architecture

```
~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/
├── data/
│   ├── ground_truth.db                # SQLite + FTS5 full-text search index
│   ├── gemini_advisory_archive.json   # 147 conversation turns harvested from Day 1 (June 1)
│   ├── gemini_advisory_archive.md     # Clean human-readable Markdown transcript
├── scripts/
│   ├── harvest_gemini.py              # Automated Chrome AppleScript harvester
│   ├── ingest_all.py                  # Master indexing pipeline into SQLite & FTS5
│   └── query.py                       # CLI search helper
└── server.py                          # FastMCP local server
```

## Grounded Knowledge Ingested

| Dataset | Records | Description |
| :--- | :--- | :--- |
| **Gemini Strategic Advisories** | 147 turns | 100% complete advisory history from Day 1 (June 1) to present, including all *Models* deconstructions, tone calibrations, and reply options. |
| **Raw Messages** | 1,158 messages | Complete 3-month Instagram DMs, emojis, reactions, media descriptions, and Google Chat exchanges. |
| **Google Meet Transcripts** | 2 sessions | Verbatim transcript of Aug 26, 2026 call (`oue-drmk-nox`) and April 23, 2024 onboarding call (`Notes - Jesus / Selene`). |
| **Grounding Dossier** | 8 sections | Psychological profile, relationship principles, inside jokes, and timeline. |

## Quick CLI Queries

Run searches from anywhere via the helper:

```bash
# 1. Search raw Instagram & Google Chat messages
python3 scripts/query.py raw "Constantine"
python3 scripts/query.py raw "brakes" Instagram

# 2. Search past strategic advice & psychological analyses
python3 scripts/query.py advice "Labor Day"
python3 scripts/query.py advice "neediness"
python3 scripts/query.py advice "seen"

# 3. Search Google Meet transcripts & call notes
python3 scripts/query.py meet "canvas"

# 4. Pull grounding dossier & principles
python3 scripts/query.py dossier

# 5. Evaluate a draft message against calibration rules
python3 scripts/query.py check "Hey hope you are enjoying your day sorry to bother!"
```
