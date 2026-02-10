# 🛠️ ADK Tooling & Integrations

## 1. Custom Function Tools
The most common way to extend agents. ADK inspects docstrings and type hints.

```python
from google.adk.tools import tool

@tool
def calculate_roi(investment: float, return_val: float) -> str:
    """
    Calculates the Return on Investment.

    Args:
        investment (float): The initial cost.
        return_val (float): The final value.
    """
    roi = (return_val - investment) / investment
    return f"ROI is {roi:.2%}"
```
- **Docstrings**: Essential! They are the "Manual" for the LLM.
- **Type Hints**: Mandatory for generating the JSON schema.

## 2. Built-in Tools
ADK comes with verified Google tools.
```python
from google.adk.tools.google_search import GoogleSearchTool

agent = LlmAgent(
    tools=[GoogleSearchTool()]
)
```
*Note: Requires `GOOGLE_CSE_ID` for custom search.*

## 3. MCP (Model Context Protocol)
Connect to existing tool servers.
```python
from google.adk.tools.mcp import McpTool

# Connect to a local or remote MCP server
filesystem_tools = McpTool(server_url="http://localhost:8001")
```

## 4. Agents-as-a-Tool
You can turn an entire agent into a tool.
```python
specialist = LlmAgent(...)
parent = LlmAgent(
    tools=[specialist.to_tool()]
)
```

---
*Reference: adk-docs/docs/tools-custom/function-tools.md*
