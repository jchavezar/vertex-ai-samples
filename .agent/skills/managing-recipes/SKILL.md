---
name: managing-recipes
description: Enforces strict guidelines for creating, modifying, and refactoring reproducible recipes under the `agy-recipes/` folder. Use when developing setup/teardown scripts, IAM configurations, API enablement, or workflows for replicating deployments.
---

# Managing Recipes (agy-recipes)

This skill provides a set of strict guidelines and workflows to ensure that all recipes in `agy-recipes/` are highly reproducible, self-contained, and clean up after themselves, while integrating seamlessly with the Antigravity agent's workspace structure.

## When to use this skill
- When creating a new recipe folder under `agy-recipes/`.
- When developing, editing, or refactoring `setup.py` / `teardown.py` scripts.
- When creating or editing skills/workflows associated with any recipe.

## Unified Recipe Structure

Every recipe developed in `agy-recipes/` must have a corresponding presence in the `.agent/` folder:

```
├── .agent/
│   ├── skills/
│   │   └── replicating-<recipe_name>/
│   │       └── SKILL.md                 # Guides the agent through manual or diagnostic tasks for this recipe
│   └── workflows/
│       ├── deploy-<recipe_name>.md      # Workflow with // turbo blocks to automate recipe setup
│       └── destroy-<recipe_name>.md     # Workflow with // turbo blocks to automate recipe teardown
├── agy-recipes/
│   └── <recipe_name>/
│       ├── README.md                    # Local documentation of the recipe, APIs, and IAM requirements
│       └── scripts/
│           ├── setup.py                 # Idempotent setup/provisioning script
│           ├── teardown.py              # Cleanup/destruction script
│           └── test_recipe.py           # Verification/testing script (optional but recommended)
```

## Core Principles

1. **Replicability & Automation**:
   - Every recipe must be fully automatable. A user (or agent) should be able to set up and tear down the entire recipe using scripts without manual intervention in the GCP Console.
   - Setup must include:
     - Enabling necessary Google Cloud APIs.
     - Checking/verifying IAM permissions or environment variables.
     - Provisioning all required GCP resources.
     - Storing created resource names/IDs in a local tracker file (`last_setup_resources.json`) so the teardown script can identify them.

2. **Clean Teardown**:
   - The teardown process must be 100% reliable. It must delete *all* resources created by the setup process.
   - The teardown script must read the resource tracker file and cleanly delete everything, even if the setup process failed halfway.
   - The tracker file itself must be removed upon successful teardown.

3. **No Leftovers (Git and GCP Cleanliness)**:
   - Do not commit resource tracker files (e.g., `last_setup_resources.json`) or any temporary assets to git. They must be ignored.
   - No GCP resources should be left running or orphaned after teardown.

4. **Code Quality & Best Practices**:
   - **Python execution**: Use `uv` for python project execution. Scripts must contain the `// script` inline metadata at the top listing all dependencies, allowing them to be run with `uv run <script_path>`.
   - **No Hardcoded Project/Env Configs**: Do NOT hardcode project specific configuration (such as GCP Project ID, Project Number, or Engine IDs) without allowing environment variable overrides. For example, use `PROJECT_ID = os.environ.get("GCP_PROJECT", "vtxdemos")` to allow flexibility.
   - **No Secrets in Code**: Follow the Zero-Leak Policy. Do not hardcode API keys, credentials, or private files. Use standard authentication mechanisms (`google.auth.default()`).
   - **Robustness**: Implement proper error handling, logging, and retries for transient API issues (e.g., waiting for Long-Running Operations).
   - **API & IAM Checkers**: Setup scripts should check if the required Google Cloud APIs are enabled and warn or attempt to enable them using the Service Usage API, and check/verify IAM permissions beforehand if possible.

---

## Step-by-Step Recipe Creation Workflow

Use this checklist when developing a recipe:

### [ ] Step 1: Scaffold Code
- Copy the template directory `agy-recipes/_template/` to your new recipe location: `agy-recipes/<recipe_name>/`
- Update `agy-recipes/<recipe_name>/README.md` to document the specific:
  - Purpose of the recipe.
  - Required Google Cloud APIs to enable.
  - Required IAM roles for execution.
  - Required environment variables or local configurations.

### [ ] Step 2: Implement Setup & Teardown Code
- Implement `agy-recipes/<recipe_name>/scripts/setup.py` (resource creation and tracker JSON serialization).
- Implement `agy-recipes/<recipe_name>/scripts/teardown.py` (tracker JSON deserialization and resource deletion).
- Run and verify setup: `uv run agy-recipes/<recipe_name>/scripts/setup.py`
- Run and verify teardown: `uv run agy-recipes/<recipe_name>/scripts/teardown.py`
- Verify in GCP console/CLI that all resources are deleted.

### [ ] Step 3: Register Antigravity Skill
- Create `.agent/skills/replicating-<recipe_name>/SKILL.md`. Use YAML frontmatter:
  ```yaml
  name: replicating-<recipe_name>
  description: Orchestrates setup, testing, and teardown of <recipe_name>. Use when the user requests deployment, replication, or testing of <recipe_name>.
  ```
- Detail the pre-flight checks, manual overrides, and diagnostics instructions inside this skill.

### [ ] Step 4: Register Antigravity Workflows
- Create `.agent/workflows/deploy-<recipe_name>.md`. It must contain the automated `// turbo` blocks pointing to `setup.py` and verification steps.
- Create `.agent/workflows/destroy-<recipe_name>.md`. It must contain the automated `// turbo` blocks pointing to `teardown.py`.
- Make sure tracker files (`last_setup_resources.json`) are ignored in `.gitignore`.
- Update the main index in `antigravity/README.md` if the recipe is associated with a core project.
