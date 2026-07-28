import logging
import os
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

from google.adk.agents import Agent
from google.adk.tools import AgentTool, google_search
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams
from google.adk.models.anthropic_llm import Claude
from google.adk.models.registry import LLMRegistry

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claude_sonnet_a2a_agent")

# Register Claude model class in ADK registry before initialization
LLMRegistry.register(Claude)

# ==================== Gemini Search Sub-Agent ====================
search_agent = Agent(
    name="google_search_agent",
    model="gemini-3.1-flash-lite",
    instruction="Use Google Search to answer any questions about current events, news, or general knowledge.",
    tools=[google_search]
)
search_agent_tool = AgentTool(agent=search_agent)

# ==================== Lazy MCP Toolset ====================
class LazyMcpToolset(BaseToolset):
    """Lazy wrapper for McpToolset to resolve pickle serialization issues

    on Agent Runtime. Defers the initialization of MCP connections to runtime.
    Reads the target server URL dynamically from session state ('MCP_URL').
    """
    def __init__(self, default_url: str):
        super().__init__()
        self._default_url = default_url
        self._toolset = None

    def _get_toolset(self, readonly_context):
        if self._toolset is None:
            mcp_url = self._default_url
            
            # Retrieve dynamic MCP URL from session state if present
            if readonly_context and hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
                session_state = dict(readonly_context.session.state)
                mcp_url = session_state.get("MCP_URL", self._default_url)
            
            logger.info(f"[LazyMCP] Initializing McpToolset for SSE URL: {mcp_url}")
            self._toolset = McpToolset(
                connection_params=SseConnectionParams(url=mcp_url, timeout=120),
                errlog=lambda msg: logger.info(f"[MCP-Logs] {msg}"),
            )
        return self._toolset

    async def get_tools(self, readonly_context=None):
        toolset = self._get_toolset(readonly_context)
        try:
            return await toolset.get_tools(readonly_context)
        except Exception as e:
            logger.exception("Error calling get_tools on McpToolset:")
            raise

    def __getstate__(self):
        # Only pickle the parameters, not the active toolset connection objects
        return {
            "_default_url": self._default_url,
            "_toolset": None
        }

    def __setstate__(self, state):
        self.__init__(state["_default_url"])


# ==================== Agent Configuration ====================
# Default local URL fallback if no dynamic MCP_URL is supplied
LOCAL_MCP_FALLBACK = "http://localhost:8000/sse"
mcp_toolset = LazyMcpToolset(default_url=LOCAL_MCP_FALLBACK)

root_agent = Agent(
    name="claude_sonnet_a2a_agent",
    model="claude-sonnet-4-6@default",  # Claude 4.6 in Model Garden
    instruction=(
        "You are an expert software developer assistant running inside Google Cloud Agent Runtime. "
        "You have access to: \n"
        "1. The user's local filesystem and shell commands via your repository MCP tools.\n"
        "2. The internet via your google_search_agent tool.\n\n"
        "Help the user solve programming tasks, write clean code, and execute commands as requested. "
        "Use the repository tools to inspect and modify files directly.\n\n"
        "Note: When the user refers to 'my fileserver' or 'fileserver', they mean the local directory 'semiautonomous-agents/docparse/out'. Use your repository tools to inspect it."
    ),
    tools=[search_agent_tool, mcp_toolset]
)
