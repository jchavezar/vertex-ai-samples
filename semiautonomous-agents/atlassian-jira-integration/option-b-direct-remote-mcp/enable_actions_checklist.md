# Enable Actions — manual UI steps

The Discovery Engine REST API will create the custom MCP datastore and wire
its `actionConfig`, but the **per-tool enablement** and the **OAuth
re-authentication** are console-only — there is no public API equivalent.
This file is the hand-off checklist for the human running through it.

Prerequisites
- `python dcr_register.py` has succeeded and `~/.secrets/atlassian-rovo-dcr-ge.json` exists.
- `python register_datastore.py` has succeeded and the datastore name was printed (e.g. `jiramcp-rovo-1778188383_mcp_data`).
- You have the engine's URL handy: `https://console.cloud.google.com/gen-app-builder/engines/jira-testing_1778158449701/data?project=vtxdemos`.

Steps

1. Open Cloud Console → AI Applications → **Engine `jira-testing`** (project `vtxdemos`).
2. Click the **Data stores** tab.
3. If the new datastore (`mcp_data`, displayed under collection name `jiramcp-rovo-<timestamp>`) is not listed under this engine, click **Edit data stores** → search for the new id → check it → save. (See note at bottom on single-datastore engines.)
4. Click the new datastore name to open it.
5. Open the **Actions** tab.
6. Click **Reload custom actions**. Wait ~30 seconds — the panel calls the MCP server's `tools/list` and populates ~37 tools.
7. Tick the boxes next to the tools you want to expose. Recommended baseline:
   - `searchJiraIssuesUsingJql`
   - `getJiraIssue`
   - `createJiraIssue`
   - `editJiraIssue`
   - `getVisibleJiraProjects`
   - `addCommentToJiraIssue`
   - `addWorklogToJiraIssue`
   - `getTransitionsForJiraIssue`
   - `transitionJiraIssue`
   - `getJiraIssueTypeMetaWithFields`
   - `getJiraProjectIssueTypesMetadata`
   - `atlassianUserInfo`
   - `getConfluencePage`
   - `searchConfluenceUsingCql`
8. Click **Enable actions**.
9. The console opens a **Re-authenticate** dialog. Run `python reauth_helper.py` in another terminal to print the values, then paste:
   - **Client ID** → from `~/.secrets/atlassian-rovo-dcr-ge.json`.
   - **Client Secret** → same file.
10. Click **Connect**. A popup opens at `mcp.atlassian.com/v1/authorize`.
11. Approve the Atlassian consent screen.
12. On the standard 3LO consent that follows (`api.atlassian.com/oauth2/authorize/server/consent`), choose **`sockcop.atlassian.net`** and approve.
13. The popup closes. The connector flips to **ACTIVE** and tools are now callable from GE chat.

Verification
- Open the engine's chat surface (no agent picked) and ask: `How many open SOCKCOP issues?`.
- Expect the assistant to call `searchJiraIssuesUsingJql` with a JQL like `project = SOCKCOP AND statusCategory != Done` and return a numbered list.

Single-datastore engine note
- `jira-testing_1778158449701` was originally provisioned in single-datastore mode. The DE public API will refuse to add or swap a second datastore on it (`FAILED_PRECONDITION: Engines linked to a single data store cannot change their linked data store`). The console UI has an internal admin path that **can** swap, hence step 3.
- If the console also refuses, two options: (a) use the previously-attached MCP datastore (`mcp-jira_1778158685439_mcp_data`) — it's the same connector kind on the same MCP server and was already working; (b) create a fresh engine in multi-datastore mode and attach the new datastore there.

Common failure modes
- `invalid_client` in the popup: credentials came from `auth.atlassian.com` instead of `cf.mcp.atlassian.com`. Re-run `python dcr_register.py --force`.
- Tools list empty after **Reload**: connector hasn't propagated yet. Wait 60 seconds, click again.
- `Jira connector tool is currently unavailable`: tools were enabled but **Re-authenticate** was skipped or the popup was blocked. Re-open the dialog from the Actions tab.
- 403 on Confluence tools: scopes missing. Verify the scopes in the connector's `actionParams` include `read:confluence-content.all` and `read:confluence-space.summary`; re-mint DCR if not.
