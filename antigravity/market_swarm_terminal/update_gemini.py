
import os

file_path = "/Users/jesusarguelles/.gemini/GEMINI.md"
new_content = """
### Google Search MCP Server

The project includes a Model Context Protocol (MCP) server for Google Search, located in `google_search_mcp_server`.

It provides two tools:
*   `google_web_search`: Performs a web search using the Google Custom Search API. Use this to gather information, find solutions to errors, or look up documentation.
*   `google_image_search`: Searches for images.

**Instruction:**
Use the `google_web_search` tool when you need to gather external information, research solutions to problems, or find documentation that is not available in the current context.

"""

try:
    with open(file_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    inserted = False
    for line in lines:
        if line.strip() == "## State Management" and not inserted:
            new_lines.append(new_content)
            inserted = True
        new_lines.append(line)

    if not inserted:
        new_lines.append(new_content)

    with open(file_path, "w") as f:
        f.writelines(new_lines)

    print("Successfully updated GEMINI.md")
except Exception as e:
    print(f"Error: {e}")
