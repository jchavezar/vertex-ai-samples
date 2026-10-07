"""
Jetski Dynamic Workflow (`run_workflow` tool):
End-to-End Autonomous Replication of the LexGraph Spanner Hybrid GraphRAG & MCP App (SEP-1865).

Usage in Jetski:
  Call `run_workflow` with:
  ScriptPath="/usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/lexgraph-spanner-mcp-app/agent-replication-packs/jetski-workflow/replicate_lexgraph_mcp_app_workflow.py"
"""

REPO_DIR = "/usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/lexgraph-spanner-mcp-app"

STEP_SCHEMA = {
    "type": "object",
    "properties": {
        "component": {"type": "string"},
        "status": {"type": "string", "enum": ["SUCCESS", "SKIPPED", "ERROR"]},
        "endpoint_or_resource": {"type": "string"},
        "latency_ms": {"type": "number"},
        "verification_notes": {"type": "string"},
    },
    "required": ["component", "status", "endpoint_or_resource", "verification_notes"],
}

# ============================================================================
# PHASE 1: PARALLEL INFRASTRUCTURE, CORPUS & CODE VERIFICATION
# ============================================================================
phase("Phase 1: Parallel Spanner GraphRAG, PDF Corpus & MCP App Verification")

tasks_phase_1 = [
    {
        "role": "Legal Corpus Compiler",
        "prompt": (
            f"Working in `{REPO_DIR}/demo-documents`, run `python3 generate_demo_pdfs.py` "
            "and verify that all 8 PDF agreements in `pdf/` and all 9 text files in `text/` exist and are non-empty. "
            "Return the verification summary matching the schema."
        ),
    },
    {
        "role": "Spanner GraphRAG Architect",
        "prompt": (
            f"Working in `{REPO_DIR}/spanner-graphrag`, verify the Cloud Spanner instance `lexgraph-legal-spanner` "
            "and database `lexgraph-legal-context` in project `vtxdemos`. If not provisioned or seeded, run "
            "`provision_spanner_graph.py` and `seed_spanner_graph.py`. Verify that `LexGraphLegalGraph` returns "
            "the 6 Intapp-cleared documents and blocks `DOC-M999-WALL`."
        ),
    },
    {
        "role": "MCP App & UI Engineer",
        "prompt": (
            f"Working in `{REPO_DIR}/mcp-app-grid-server`, audit `app.py` and `ui_template.py`. "
            "Verify that: (1) `html, body` use `position: fixed; inset: 0; overflow: hidden;` with `lockRootViewport()`, "
            "(2) `scrollIntoView` is never called in JS code, (3) `resources/read` uses `LATEST_WORKSPACE_STATE` "
            "for <100ms response, and (4) `python3 -m py_compile app.py ui_template.py` succeeds."
        ),
    },
]

phase1_results = await parallel(
    tasks_phase_1,
    lambda item: agent(
        prompt=item["prompt"],
        role=item["role"],
        schema=STEP_SCHEMA,
        workspace="inherit",
    ),
)
log("Phase 1 results:", phase1_results)

# ============================================================================
# PHASE 2: SEQUENTIAL CLOUD RUN DEPLOYMENT -> GE CONNECTOR -> E2E QA
# ============================================================================
phase("Phase 2: Sequential Cloud Run Deploy, GE Connector Link & Live QA")

tasks_phase_2 = [
    {
        "role": "Cloud Run & GE Connector Deployer",
        "prompt": (
            f"Deploy `{REPO_DIR}/mcp-app-grid-server` to Cloud Run service `lexgraph-legal-grid-mcp-agent` "
            "in project `vtxdemos` (`us-central1`) with `--allow-unauthenticated --no-cpu-throttling --quiet`. "
            "Then verify or run `register_custom_mcp_connector.py` so the Gemini Enterprise connector is ACTIVE."
        ),
    },
    {
        "role": "End-to-End MCP App QA Verifier",
        "prompt": (
            "Test `POST https://lexgraph-legal-grid-mcp-agent-254356041555.us-central1.run.app/mcp` with: "
            "1) `initialize`, 2) `tools/list`, 3) `tools/call` (`open_legal_analysis_grid`), and "
            "4) `resources/read` (`ui://lexgraph/legal-grid-workspace.html`). "
            "Verify HTTP 200 on all 4 calls and confirm `resources/read` latency is under 150ms."
        ),
    },
]

phase2_results = await pipeline(
    tasks_phase_2,
    lambda item: agent(
        prompt=item["prompt"],
        role=item["role"],
        schema=STEP_SCHEMA,
        workspace="inherit",
    ),
)
log("Phase 2 results:", phase2_results)
