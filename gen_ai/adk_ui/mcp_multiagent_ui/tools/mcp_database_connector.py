# tools/mcp_database_connector.py
from typing import Any, Dict, Optional
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
mcp_tool = toolbox.load_toolset('bq-toolset')