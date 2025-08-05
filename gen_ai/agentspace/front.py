import flet as ft
import requests
import json
import subprocess
import asyncio
import sys

# --- Function to get ADC token ---
def get_adc_token():
    """
    Attempts to get a Google Cloud ADC (Application Default Credentials) access token.
    Requires gcloud CLI to be installed and authenticated.
    """
    try:
        print("Attempting to get ADC token using 'gcloud auth print-access-token'...")
        # Ensure gcloud is in PATH and authenticated
        result = subprocess.run(
            ['gcloud', 'auth', 'print-access-token'],
            capture_output=True,
            text=True,
            check=True,
            # For Windows, shell=True might be needed if gcloud isn't directly in PATH
            shell=(sys.platform == "win32")
        )
        token = result.stdout.strip()
        if token:
            print("Successfully retrieved ADC token.")
        else:
            print("ADC token command ran, but returned empty string.")
        return token
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error getting ADC token: {e}")
        print("Please ensure 'gcloud CLI' is installed, configured, and authenticated (e.g., run 'gcloud auth application-default login').")
        return None

# --- API Configuration (placeholders to be filled by the user in the UI) ---
PROJECT_ID = ""
APP_ID = ""
AUTH_TOKEN = ""

BASE_URL = "https://discoveryengine.googleapis.com/v1alpha"

# --- API Functions ---

def get_common_headers():
    """
    Constructs common HTTP headers for API requests, including Authorization and Project ID.
    Returns None if required global variables are not set.
    """
    if not AUTH_TOKEN:
        print("Error: AUTH_TOKEN is missing for headers.")
        return None
    if not PROJECT_ID:
        print("Error: PROJECT_ID is missing for headers.")
        return None
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID,
    }
    print(f"Constructed headers: {headers}")
    return headers

async def list_agents_api(project_id, app_id, auth_token):
    """
    Lists existing agents via the Discovery Engine API.
    """
    global PROJECT_ID, APP_ID, AUTH_TOKEN
    PROJECT_ID = project_id
    APP_ID = app_id
    AUTH_TOKEN = auth_token

    print(f"List Agents API Call: Project ID: {PROJECT_ID}, App ID: {APP_ID}")

    headers = get_common_headers()
    if not headers:
        return {"error": "Project ID, App ID, or Auth Token is missing. Please fill in the configuration."}

    url = f"{BASE_URL}/projects/{PROJECT_ID}/locations/global/collections/default_collection/engines/{APP_ID}/assistants/default_assistant/agents"
    print(f"List Agents URL: {url}")
    try:
        response = await asyncio.to_thread(requests.get, url, headers=headers)
        response.raise_for_status() # Raise an exception for HTTP errors
        print(f"List Agents API Response Status: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        error_detail = f"API Error: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_detail += f" - Response Status: {e.response.status_code}"
            error_detail += f" - Response Body: {e.response.text}"
        print(f"Error in list_agents_api: {error_detail}")
        return {"error": error_detail}

async def register_agent_api(agent_data, project_id, app_id, auth_token):
    """
    Registers a new agent via the Discovery Engine API.
    """
    global PROJECT_ID, APP_ID, AUTH_TOKEN
    PROJECT_ID = project_id
    APP_ID = app_id
    AUTH_TOKEN = auth_token

    print(f"Register Agent API Call: Project ID: {PROJECT_ID}, App ID: {APP_ID}, Agent Data: {json.dumps(agent_data, indent=2)}")

    headers = get_common_headers()
    if not headers:
        return {"error": "Project ID, App ID, or Auth Token is missing. Please fill in the configuration."}

    url = f"{BASE_URL}/projects/{PROJECT_ID}/locations/global/collections/default_collection/engines/{APP_ID}/assistants/default_assistant/agents"
    print(f"Register Agent URL: {url}")
    try:
        response = await asyncio.to_thread(requests.post, url, headers=headers, json=agent_data)
        response.raise_for_status()
        print(f"Register Agent API Response Status: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        error_detail = f"API Error: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_detail += f" - Response Status: {e.response.status_code}"
            error_detail += f" - Response Body: {e.response.text}"
        print(f"Error in register_agent_api: {error_detail}")
        return {"error": error_detail}

async def delete_agent_api(agent_name, project_id, app_id, auth_token):
    """
    Deletes an agent via the Discovery Engine API.
    `agent_name` is expected to be the full resource path (e.g., projects/P_ID/.../agents/AGENT_ID).
    """
    global PROJECT_ID, APP_ID, AUTH_TOKEN
    PROJECT_ID = project_id
    APP_ID = app_id
    AUTH_TOKEN = auth_token

    print(f"Delete Agent API Call: Agent Name: {agent_name}, Project ID: {PROJECT_ID}, App ID: {APP_ID}")

    headers = get_common_headers()
    if not headers:
        return {"error": "Project ID, App ID, or Auth Token is missing. Please fill in the configuration."}

    url = f"{BASE_URL}/{agent_name}" # agent_name is already the full resource path
    print(f"Delete Agent URL: {url}")
    try:
        response = await asyncio.to_thread(requests.delete, url, headers=headers)
        response.raise_for_status() # This will raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Delete Agent API Response Status: {response.status_code}")
        # A successful delete usually returns an empty body or a status 204 No Content
        return {"success": f"Agent {agent_name} deleted successfully."}
    except requests.exceptions.RequestException as e:
        error_detail = f"API Error: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_detail += f" - Response Status: {e.response.status_code}"
            error_detail += f" - Response Body: {e.response.text}"
        print(f"Error in delete_agent_api: {error_detail}")
        return {"error": error_detail}

# --- Flet Application ---

def main(page: ft.Page):
    page.title = "ADK Agent Manager"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 900
    page.window_height = 800
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- UI Elements ---
    project_id_input = ft.TextField(label="Project ID (e.g., your-gcp-project)", value="vtxdemos", width=400)
    app_id_input = ft.TextField(label="App ID (e.g., agentspace-testing_123456789)", value="agentspace-testing_1748446185255", width=400)

    initial_auth_token = get_adc_token()
    if initial_auth_token is None:
        print("ADC token not retrieved, please enter manually or check gcloud setup.")
        auth_token_value = ""
        auth_token_hint = "Enter your Google Cloud access token manually or ensure gcloud CLI is configured."
    else:
        auth_token_value = initial_auth_token
        auth_token_hint = ""

    auth_token_input = ft.TextField(
        label="Auth Token",
        password=True,
        can_reveal_password=True,
        width=400,
        value=auth_token_value,
        hint_text=auth_token_hint
    )
    status_text = ft.Text("")

    # --- Register Agent Form ---
    reg_display_name = ft.TextField(label="Display Name*", expand=True)
    reg_description = ft.TextField(label="Description*", multiline=True, expand=True)
    reg_icon_uri = ft.TextField(label="Icon URI (Optional)", expand=True)
    reg_tool_description = ft.TextField(label="Tool Description*", multiline=True, expand=True)
    reg_reasoning_engine_path = ft.TextField(
        label="Reasoning Engine Path* (e.g., projects/P_ID/locations/L_LOC/reasoningEngines/ADK_DEP_ID)",
        expand=True
    )
    reg_auth_id = ft.TextField(label="Authorization ID (Optional, e.g., myauthconfig)",
                               hint_text="Will be projects/P_ID/locations/global/authorizations/AUTH_ID",
                               expand=True)

    # --- Agent List Table ---
    agents_data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Display Name")),
            ft.DataColumn(ft.Text("Description")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Actions")),
        ],
        rows=[],
        expand=True,
        column_spacing=20,
    )

    # --- Event Handlers ---

    def show_status(message, color=ft.Colors.BLACK):
        """Helper function to update the status text in the UI."""
        status_text.value = message
        status_text.color = color
        page.update()

    async def delete_agent_immediately(e):
        """
        Handles the immediate deletion of an agent upon trash icon click.
        """
        agent_to_delete, display_name_to_delete = e.control.data # Get agent name and display name from data
        print(f"Attempting to delete agent immediately: '{display_name_to_delete}' ({agent_to_delete})")

        show_status(f"Deleting agent '{display_name_to_delete}'...", ft.Colors.BLUE_700)
        result = await delete_agent_api(
            agent_to_delete,
            project_id_input.value,
            app_id_input.value,
            auth_token_input.value
        )
        if "error" in result:
            show_status(f"Error deleting agent: {result['error']}", ft.Colors.RED_700)
            print(f"Deletion failed: {result['error']}")
        else:
            show_status(f"Agent '{display_name_to_delete}' deleted successfully. Refreshing list...", ft.Colors.GREEN_700)
            print(f"Deletion successful for '{display_name_to_delete}'.")
            await list_agents() # Refresh the agent list after deletion
        page.update() # Ensure UI updates after status change


    async def list_agents(e=None):
        """
        Fetches and displays the list of agents in the DataTable.
        """
        show_status("Fetching agents...", ft.Colors.BLUE_700)
        print("list_agents called.")
        result = await list_agents_api(
            project_id_input.value,
            app_id_input.value,
            auth_token_input.value
        )

        agents_data_table.rows.clear() # Clear existing rows before populating
        if "error" in result:
            show_status(f"Error listing agents: {result['error']}", ft.Colors.RED_700)
            print(f"Error listing agents: {result['error']}")
        elif "agents" in result:
            if not result.get("agents"):
                show_status("No agents found.", ft.Colors.BLACK)
                print("No agents found by API.")
            else:
                for agent in result["agents"]:
                    agent_name = agent.get("name", "N/A") # Full resource path of the agent
                    display_name = agent.get("displayName", "N/A")
                    description = agent.get("description", "N/A")
                    state = agent.get("state", "N/A")

                    agents_data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(display_name)),
                                ft.DataCell(ft.Text(description)),
                                ft.DataCell(ft.Text(state)),
                                ft.DataCell(
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        tooltip=f"Delete {display_name}",
                                        # Pass both agent_name and display_name as a tuple
                                        data=(agent_name, display_name),
                                        on_click=delete_agent_immediately # Directly call the async deletion function
                                    )
                                ),
                            ]
                        )
                    )
                show_status(f"Successfully listed {len(result['agents'])} agents.", ft.Colors.GREEN_700)
                print(f"Successfully listed {len(result['agents'])} agents.")
        else:
            show_status("Unexpected API response when listing agents.", ft.Colors.RED_700)
            print("Unexpected API response structure.")
        page.update()
        print("list_agents finished updating page.")


    async def register_agent(e):
        """
        Handles the registration of a new agent based on form inputs.
        """
        show_status("Registering agent...", ft.Colors.BLUE_700)
        print("register_agent called.")

        if not all([reg_display_name.value, reg_description.value, reg_tool_description.value, reg_reasoning_engine_path.value]):
            show_status("Please fill in all required fields (marked with *).", ft.Colors.ORANGE_700)
            print("Missing required registration fields.")
            return

        agent_data = {
            "displayName": reg_display_name.value,
            "description": reg_description.value,
            "adkAgentDefinition": {
                "toolSettings": {
                    "toolDescription": reg_tool_description.value
                },
                "provisionedReasoningEngine": {
                    "reasoningEngine": reg_reasoning_engine_path.value
                }
            }
        }

        if reg_icon_uri.value:
            agent_data["icon"] = {"uri": reg_icon_uri.value}

        if reg_auth_id.value and project_id_input.value:
            auth_resource_name = f"projects/{project_id_input.value}/locations/global/authorizations/{reg_auth_id.value}"
            agent_data["adkAgentDefinition"]["authorizations"] = [auth_resource_name]
        print(f"Agent data prepared for registration: {json.dumps(agent_data, indent=2)}")

        result = await register_agent_api(
            agent_data,
            project_id_input.value,
            app_id_input.value,
            auth_token_input.value
        )

        if "error" in result:
            show_status(f"Error registering agent: {result['error']}", ft.Colors.RED_700)
            print(f"Error registering agent: {result['error']}")
        else:
            show_status(f"Agent '{result.get('displayName', 'N/A')}' registered successfully!", ft.Colors.GREEN_700)
            print(f"Agent '{result.get('displayName', 'N/A')}' registered successfully.")
            # Clear the registration form fields upon success
            reg_display_name.value = ""
            reg_description.value = ""
            reg_icon_uri.value = ""
            reg_tool_description.value = ""
            reg_reasoning_engine_path.value = ""
            reg_auth_id.value = ""
            await list_agents() # Refresh the agent list after registration
        page.update()
        print("register_agent finished.")

    # --- Layout ---
    page.add(
        ft.Column(
            [
                ft.Text("ADK Agent Manager", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Divider(),
                ft.Text("Global Configuration", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Row([project_id_input, app_id_input]),
                auth_token_input,
                status_text, # Display area for messages
                ft.Divider(),
                ft.Text("Register New Agent", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Row([reg_display_name, reg_icon_uri]),
                reg_description,
                reg_tool_description,
                reg_reasoning_engine_path,
                reg_auth_id,
                ft.ElevatedButton("Register Agent", on_click=register_agent),
                ft.Divider(),
                ft.Text("Registered Agents", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.ElevatedButton("List Agents", on_click=list_agents),
                ft.Container(
                    content=agents_data_table,
                    margin=ft.margin.only(top=10),
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=ft.border_radius.all(5),
                    padding=10,
                ),
            ]
        )
    )

# Run the Flet application
ft.app(target=main)