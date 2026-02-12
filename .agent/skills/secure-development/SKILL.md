---
name: secure-development
description: Enforces strict 'Zero-Leak' security practices, including secret management, gitignore rules, and environment variable protocols. Use when starting new projects or rigorously auditing existing ones.
---

# Secure Development & Zero-Leak Protocol

## When to use this skill
- Starting ANY new project (backend, frontend, or tools).
- When the user mentions "Security", "Secrets", "API Keys", or "Leaks".
- Before deploying or committing code.

## Instructions

### 1. The Zero-Leak Policy
**NEVER** commit secrets, API keys, credentials, or `.env` files to git.
If a secret is committed, it is considered compromised and must be revoked immediately.

### 2. Global Exclusion Rules (.gitignore)
You MUST ensure the `.gitignore` file includes the following "Ironclad" section:
```gitignore
# Data & Secrets (MANDATORY)
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
client_secret*.json
credentials.json
*_token.json
```
**Exception**: `.env.example` must be tracked, but meaningful values must be empty.

### 3. Variable Management: The "Accumulate" Rule
- **Single Source of Truth**: The `.env` file is the source of truth for secrets.
- **Template Sync**: Every time you add a variable to `.env`, you **MUST** immediately add it to `.env.example` with an empty value.
- **Verification**: Run `diff <(grep -o '^[^=]*' .env | sort) <(grep -o '^[^=]*' .env.example | sort)` to ensure parity.

### 4. Code Scanning
- Generally avoid hardcoding keys (e.g., `AIza...`) in source code.
- Use `os.environ.get("KEY")` or `process.env.KEY` strictly.

### 5. Remediation (If a leak occurs)
1. **Revoke** the key at the provider immediately.
2. **Rotate** the key (generate new).
3. **Scrub** historical commits if necessary (git filter-repo).
