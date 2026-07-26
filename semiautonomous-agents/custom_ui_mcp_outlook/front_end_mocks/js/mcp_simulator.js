/**
 * MCP CONNECTORS SIMULATOR & TELEMETRY ENGINE
 * Simulates real-time tool calls for Outlook, Jira, Google Workspace, and GitHub MCP servers.
 */

window.MCPSimulator = {
  connectors: {
    outlook: { name: 'M365 Outlook MCP', status: 'connected', latency: '14ms', tools: ['search_emails', 'send_draft', 'get_calendar'] },
    jira: { name: 'Atlassian Jira MCP', status: 'connected', latency: '28ms', tools: ['search_issues', 'create_ticket', 'get_board'] },
    workspace: { name: 'Google Workspace MCP', status: 'connected', latency: '19ms', tools: ['search_drive', 'read_doc', 'query_sheets'] },
    github: { name: 'GitHub Copilot MCP', status: 'connected', latency: '35ms', tools: ['list_repos', 'view_pr', 'grep_code'] }
  },

  samplePrompts: [
    {
      label: "📧 Outlook Mail & Calendar Query",
      prompt: "Find all unread high-priority emails from VP of Engineering regarding the Q3 MCP Architecture and check my schedule for tomorrow morning.",
      toolCall: {
        server: "outlook",
        tool: "search_emails",
        params: { query: "is:unread importance:high Q3 MCP Architecture", limit: 3 },
        result: `Found 2 matching threads:
1. [URGENT] Q3 MCP Architecture & Outlook Connector Specs (From: alex.dev@enterprise.com)
2. Follow-up: Security Review for Delegated Graph Tokens (From: sarah.sec@enterprise.com)`
      }
    },
    {
      label: "🎯 Jira Sprint & Blocker Triaging",
      prompt: "Query active sprint blockers in project VERTEX-AI and generate a executive summary with assignees.",
      toolCall: {
        server: "jira",
        tool: "search_issues",
        params: { jql: "project = 'VERTEX' AND status = 'In Progress' AND priority = 'High'", maxResults: 5 },
        result: `[VERTEX-894] ADK Agent OAuth2 callback redirect timeout (Assignee: Jesus)
[VERTEX-902] FactSet API backend .env variable override mismatch (Assignee: DevTeam)`
      }
    },
    {
      label: "⚡ Universal Multi-Agent Search",
      prompt: "Cross-reference Outlook email specs with our Google Workspace Architecture Doc and summarize integration readiness.",
      toolCall: {
        server: "workspace",
        tool: "search_drive",
        params: { query: "Universal Chat Architecture 2026", mimeType: "application/vnd.google-apps.document" },
        result: `Matched Document: "Universal Chat & MCP Connector Spec v3.4.gdoc"
- Status: Approved
- Target UI Models: gemini-3-pro-preview, gemini-3-flash-preview, gemini-2.5-pro`
      }
    }
  ],

  executeToolCall: async function(promptText, onProgress, onComplete) {
    // 1. Initial reasoning step
    onProgress({
      step: 'reasoning',
      message: 'Analyzing prompt intent & identifying required MCP connectors...'
    });

    await new Promise(r => setTimeout(r, 600));

    // 2. Select matching tool call
    const match = this.samplePrompts.find(p => promptText.toLowerCase().includes(p.label.toLowerCase().slice(3, 10))) || this.samplePrompts[0];

    onProgress({
      step: 'mcp_invoking',
      server: match.toolCall.server,
      tool: match.toolCall.tool,
      params: match.toolCall.params
    });

    await new Promise(r => setTimeout(r, 900));

    // 3. Return tool output & generate answer
    onProgress({
      step: 'mcp_completed',
      result: match.toolCall.result
    });

    await new Promise(r => setTimeout(r, 700));

    onComplete({
      answer: `I have retrieved and cross-analyzed the relevant context using **${this.connectors[match.toolCall.server].name}**:\n\n` +
              `### 🔍 Context Summary & Action Plan\n` +
              `\`\`\`json\n${JSON.stringify(match.toolCall.params, null, 2)}\n\`\`\`\n\n` +
              `${match.toolCall.result}\n\n` +
              `> **Next Action**: Would you like me to draft an automated reply or create a follow-up Jira ticket?`,
      artifact: `// Generated Artifact - Next-Gen Response Payload\n{\n  "status": "success",\n  "mcp_server": "${match.toolCall.server}",\n  "latency_ms": 18,\n  "grounding_confidence": 0.985\n}`
    });
  }
};
