import asyncio
import os
import sys
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

# 1. LOAD ENV & SETUP CREDENTIALS
load_dotenv(override=True)
TOKEN = os.getenv("ATLASSIAN_OAUTH_TOKEN")

if not TOKEN:
    print("❌ Error: ATLASSIAN_OAUTH_TOKEN not found in .env or environment variables.")
    sys.exit(1)

async def run_test():
    clean_token = TOKEN.strip()
    print(f"--- Starting Test Client ---")
    print(f"Token present (Length: {len(clean_token)})")

    # 2. DEFINE HEADERS
    headers = {
        "Authorization": f"Bearer {clean_token}",
    }

    server_url = "http://0.0.0.0:8080/sse"
    print(f"Connecting to {server_url}...")

    try:
        # 3. CONNECT VIA SSE
        async with sse_client(server_url, headers=headers) as (read, write):
            async with ClientSession(read, write) as session:
                # Handshake
                await session.initialize()
                print("✅ Handshake Successful!")

                # 4. LIST TOOLS
                print("\n--- Available Tools ---")
                tools_result = await session.list_tools()
                for tool in tools_result.tools:
                    print(f"- {tool.name}: {tool.description}")

                # 5. CALL TOOLS
                print("\n--- Testing 'getAccessibleAtlassianResources' ---")
                resources = await session.call_tool("getAccessibleAtlassianResources", arguments={})
                print(f"Resources: {resources.content[0].text[:200]}...") # Truncate

                print("\n--- Testing 'atlassianUserInfo' ---")
                user_info = await session.call_tool("atlassianUserInfo", arguments={})
                print(f"User Info: {user_info.content[0].text[:100]}...") # Truncate for brevity

                print("\n--- Testing 'getVisibleJiraProjects' ---")
                projects = await session.call_tool("getVisibleJiraProjects", arguments={})
                print(f"Projects:\n{projects.content[0].text}")
                
                print("\n--- Testing 'getJiraProjectIssueTypesMetadata' for SMP ---")
                # Assuming SMP exists from previous output
                meta = await session.call_tool("getJiraProjectIssueTypesMetadata", arguments={"projectIdOrKey": "SMP"})
                print(f"Metadata:\n{meta.content[0].text}")

                # Parse an issue type ID from the metadata output to test the next tool
                # Expected format: "- Bug (ID: 10004) - ..."
                import re
                type_match = re.search(r"\(ID: (\d+)\)", meta.content[0].text)
                if type_match:
                    type_id = type_match.group(1)
                    print(f"\n--- Testing 'getJiraIssueTypeMetaWithFields' for SMP, Type {type_id} ---")
                    fields_meta = await session.call_tool(
                        "getJiraIssueTypeMetaWithFields",
                        arguments={"projectIdOrKey": "SMP", "issueTypeId": type_id}
                    )
                    print(f"Fields (truncated):\n{fields_meta.content[0].text[:500]}...")
                
                print("\n--- Testing 'searchJiraIssuesUsingJql' ---")
                jql_query = "created >= -30d order by created DESC"
                search_result = await session.call_tool(
                    "searchJiraIssuesUsingJql",
                    arguments={"jql": jql_query, "maxResults": 1}
                )
                print(f"Search Result:\n{search_result.content[0].text}")

                # Extract an issue key if found
                match = re.search(r"\[([A-Z]+-\d+)\]", search_result.content[0].text)
                if match:
                    issue_key = match.group(1)
                    print(f"\n--- Testing 'getJiraIssue' for {issue_key} ---")
                    issue_details = await session.call_tool(
                        "getJiraIssue",
                        arguments={"issueIdOrKey": issue_key}
                    )
                    print(f"Issue Details Length: {len(issue_details.content[0].text)}")
                    
                    print(f"\n--- Testing 'getTransitionsForJiraIssue' for {issue_key} ---")
                    transitions = await session.call_tool(
                        "getTransitionsForJiraIssue",
                        arguments={"issueIdOrKey": issue_key}
                    )
                    print(f"Transitions:\n{transitions.content[0].text}")

                    print(f"\n--- Testing 'getJiraIssueRemoteIssueLinks' for {issue_key} ---")
                    links = await session.call_tool(
                        "getJiraIssueRemoteIssueLinks",
                        arguments={"issueIdOrKey": issue_key}
                    )
                    print(f"Remote Links: {links.content[0].text}")
                else:
                    print("\n⚠️ No issue found to test 'getJiraIssue'")

                print("\n--- Testing 'lookupJiraAccountId' ---")
                lookup = await session.call_tool(
                    "lookupJiraAccountId", 
                    arguments={"searchString": "jira"}
                )
                print(f"Lookup Result (query='jira'):\n{lookup.content[0].text}")


    except Exception as e:
        print(f"\n❌ Test Failed: {type(e).__name__}: {e}")
        if hasattr(e, "exceptions"):
            for i, exc in enumerate(e.exceptions):
                print(f"  Sub-exception {i+1}: {type(exc).__name__}: {exc}")
                import httpx
                if isinstance(exc, httpx.HTTPStatusError):
                    print(f"    Server Response: {exc.response.text}")

        import httpx
        if isinstance(e, httpx.HTTPStatusError):
            print(f"Server Response: {e.response.text}")
        elif "Connection refused" in str(e):
            print("Hint: Ensure 'server.py' is running.")

if __name__ == "__main__":
    asyncio.run(run_test())
