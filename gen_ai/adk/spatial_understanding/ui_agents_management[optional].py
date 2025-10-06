import flet as ft
import subprocess
import json
import shlex

class TronButton(ft.FilledButton):
    def __init__(self, text, on_click=None, color=ft.Colors.CYAN_400):
        super().__init__(
            text=text,            on_click=on_click,            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),                bgcolor={"": ft.Colors.BLUE_GREY_800},                color={"": color},                overlay_color={"hovered": ft.Colors.BLUE_GREY_700},                animation_duration=200            ),        )

class InputField(ft.TextField):
    def __init__(self, label, value="", password=False, multiline=False, expand=False):
        super().__init__(
            label=label,            value=value,            password=password,            can_reveal_password=password,            multiline=multiline,            min_lines=1 if not multiline else 3,            max_lines=1 if not multiline else 5,            border_color=ft.Colors.BLUE_GREY_700,            focused_border_color=ft.Colors.CYAN_400,            label_style=ft.TextStyle(color=ft.Colors.BLUE_GREY_200),            text_style=ft.TextStyle(color=ft.Colors.WHITE),            cursor_color=ft.Colors.CYAN_400,            bgcolor=ft.Colors.BLUE_GREY_900,            border_radius=ft.border_radius.all(5),            content_padding=ft.padding.symmetric(horizontal=10, vertical=8),            expand=expand
        )

class OutputDisplay(ft.TextField):
    def __init__(self, label="Command Output", multiline=True):
        super().__init__(
            label=label,            read_only=True,            multiline=multiline,            min_lines=8,            border_color=ft.Colors.BLUE_GREY_700,            label_style=ft.TextStyle(color=ft.Colors.BLUE_GREY_200),            text_style=ft.TextStyle(color=ft.Colors.LIME_400, font_family="monospace"),            bgcolor=ft.Colors.BLUE_GREY_900,            border_radius=ft.border_radius.all(5),            content_padding=ft.padding.symmetric(horizontal=10, vertical=8),            expand=True
        )

def main(page: ft.Page):
    page.title = "Agentspace ADK Manager"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLUE_GREY_900
    page.window_width = 850
    page.window_height = 950
    page.appbar = ft.AppBar(
        title=ft.Text("Agentspace ADK Manager", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),        bgcolor=ft.Colors.BLUE_GREY_900,        center_title=True,    )

    project_id_field = InputField("PROJECT_ID", value="vtxdemos", expand=True)
    app_id_field = InputField("APP_ID", value="agentspace-testing_1748446185255", expand=True)
    reasoning_engine_location_dropdown = ft.Dropdown(
        label="REASONING_ENGINE_LOCATION",        options=[
            ft.dropdown.Option("australia-southeast2"), ft.dropdown.Option("asia-northeast1"),
            ft.dropdown.Option("northamerica-northeast2"), ft.dropdown.Option("asia-south2"),
            ft.dropdown.Option("europe-west3"), ft.dropdown.Option("us-central1"),
            ft.dropdown.Option("europe-west1"), ft.dropdown.Option("europe-west2"),
        ],        value="us-central1", border_color=ft.Colors.BLUE_GREY_700,
        focused_border_color=ft.Colors.CYAN_400, label_style=ft.TextStyle(color=ft.Colors.BLUE_GREY_200),
        text_style=ft.TextStyle(color=ft.Colors.WHITE), bgcolor=ft.Colors.BLUE_GREY_900,
        border_radius=ft.border_radius.all(5), content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        expand=True
    )

    output_area = OutputDisplay()

    def run_command(command, description=""):
        output_area.value = f"Executing: {description}\n\nCommand:\n```bash\n{command}\n```\n\n"
        page.update()
        try:
            process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True, encoding='utf-8')
            output_area.value += f"STATUS: SUCCESS\n\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        except subprocess.CalledProcessError as e:
            output_area.value += f"STATUS: ERROR (Exit Code: {e.returncode})\n\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        except Exception as e:
            output_area.value += f"STATUS: UNEXPECTED ERROR\n\nError details: {str(e)}"
        page.update()

    def get_gcloud_access_token():
        try:
            process = subprocess.run("gcloud auth print-access-token", shell=True, capture_output=True, text=True, check=True, encoding='utf-8')
            return process.stdout.strip()
        except subprocess.CalledProcessError as e:
            output_area.value = f"Error getting gcloud access token: Please ensure gcloud CLI is installed and authenticated.\n{e.stderr}"
            page.update()
            return None
        except Exception as e:
            output_area.value = f"An unexpected error occurred while getting gcloud access token: {str(e)}"
            page.update()
            return None

    auth_id_field = InputField("AUTH_ID (unique identifier)", value="my-auth-resource", expand=True)
    oauth_client_id_field = InputField("OAUTH_CLIENT_ID", value="your-oauth-client-id", expand=True)
    oauth_client_secret_field = InputField("OAUTH_CLIENT_SECRET", password=True, expand=True)
    oauth_auth_uri_field = InputField("OAUTH_AUTH_URI", value="https://accounts.google.com/o/oauth2/v2/auth", expand=True)
    oauth_token_uri_field = InputField("OAUTH_TOKEN_URI", value="https://oauth2.googleapis.com/token", expand=True)

    def register_auth_resource(e):
        gcloud_access_token = get_gcloud_access_token()
        if not gcloud_access_token: return
        project_id = project_id_field.value
        auth_id = auth_id_field.value
        payload_dict = {
            "name": f"projects/{project_id}/locations/global/authorizations/{auth_id}",
            "serverSideOauth2": {
                "clientId": oauth_client_id_field.value, "clientSecret": oauth_client_secret_field.value,
                "authorizationUri": oauth_auth_uri_field.value, "tokenUri": oauth_token_uri_field.value
            }
        }
        payload_json = json.dumps(payload_dict, indent=2)
        command = (
            f"curl -X POST "
            f"-H \"Authorization: Bearer {gcloud_access_token}\" "
            f"-H \"Content-Type: application/json\" "
            f"-H \"X-Goog-User-Project: {shlex.quote(project_id)}\" "
            f"\"https://discoveryengine.googleapis.com/v1alpha/projects/{shlex.quote(project_id)}/locations/global/authorizations?authorizationId={shlex.quote(auth_id)}\" "
            f"-d {shlex.quote(payload_json)}"
        )
        run_command(command, "Register Authorization Resource")

    def delete_auth_resource(e):
        gcloud_access_token = get_gcloud_access_token()
        if not gcloud_access_token: return
        project_id = project_id_field.value
        auth_id = auth_id_field.value
        command = (
            f"curl -X DELETE "
            f"-H \"Authorization: Bearer {gcloud_access_token}\" "
            f"-H \"Content-Type: application/json\" "
            f"-H \"X-Goog-User-Project: {shlex.quote(project_id)}\" "
            f"\"https://discoveryengine.googleapis.com/v1alpha/projects/{shlex.quote(project_id)}/locations/global/authorizations/{shlex.quote(auth_id)}\""
        )
        run_command(command, "Delete Authorization Resource")

    agent_display_name_field = InputField("DISPLAY_NAME", value="MyPreciousAgent", expand=True)
    agent_description_field = InputField("DESCRIPTION", value="A helpful and friendly assistant.", multiline=True, expand=True)
    agent_icon_uri_field = InputField("ICON_URI", value="https://example.com/icon.png", expand=True)
    agent_tool_description_field = InputField("TOOL_DESCRIPTION (for LLM routing)", value="An expert at processing user requests.", multiline=True, expand=True)
    adk_deployment_id_field = InputField("ADK_DEPLOYMENT_ID", value="your-adk-deployment-id", expand=True)
    agent_resource_name_field = InputField("AGENT_RESOURCE_NAME (e.g., projects/...)", value="", multiline=True, expand=True)
    auth_ids_for_agent_field = InputField("AUTH_ID(s) (comma-separated)", value="", expand=True)

    def build_agent_payload_dict():
        project_id = project_id_field.value
        payload = {
            "displayName": agent_display_name_field.value,
            "description": agent_description_field.value,
            "icon": {"uri": agent_icon_uri_field.value} if agent_icon_uri_field.value else {},
            "adk_agent_definition": {
                "tool_settings": { "tool_description": agent_tool_description_field.value },
                "provisioned_reasoning_engine": {
                    "reasoning_engine": f"projects/{project_id}/locations/{reasoning_engine_location_dropdown.value}/reasoningEngines/{adk_deployment_id_field.value}"
                }
            }
        }
        auth_ids_str = auth_ids_for_agent_field.value.strip()
        if auth_ids_str:
            auth_resources = [ f"projects/{project_id}/locations/global/authorizations/{aid.strip()}" for aid in auth_ids_str.split(',') if aid.strip() ]
            if auth_resources:
                payload["authorization_config"] = {"tool_authorizations": auth_resources}
        return payload

    def register_agent(e):
        gcloud_access_token = get_gcloud_access_token()
        if not gcloud_access_token: return
        project_id = project_id_field.value
        app_id = app_id_field.value
        payload_json = json.dumps(build_agent_payload_dict(), indent=2)
        command = (
            f"curl -X POST "
            f"-H \"Authorization: Bearer {gcloud_access_token}\" "
            f"-H \"Content-Type: application/json\" "
            f"-H \"X-Goog-User-Project: {shlex.quote(project_id)}\" "
            f"\"https://discoveryengine.googleapis.com/v1alpha/projects/{shlex.quote(project_id)}/locations/global/collections/default_collection/engines/{shlex.quote(app_id)}/assistants/default_assistant/agents\" "
            f"-d {shlex.quote(payload_json)}"
        )
        run_command(command, "Register Agent")

    def update_agent(e):
        gcloud_access_token = get_gcloud_access_token()
        if not gcloud_access_token: return
        project_id = project_id_field.value
        agent_resource_name = agent_resource_name_field.value
        if not agent_resource_name:
            output_area.value = "Error: AGENT_RESOURCE_NAME is required for an update operation."
            page.update()
            return
        payload_json = json.dumps(build_agent_payload_dict(), indent=2)
        command = (
            f"curl -X PATCH "
            f"-H \"Authorization: Bearer {gcloud_access_token}\" "
            f"-H \"Content-Type: application/json\" "
            f"-H \"X-Goog-User-Project: {shlex.quote(project_id)}\" "
            f"\"https://discoveryengine.googleapis.com/v1alpha/{shlex.quote(agent_resource_name)}\" "
            f"-d {shlex.quote(payload_json)}"
        )
        run_command(command, "Update Agent")

    def view_agent(e):
        gcloud_access_token = get_gcloud_access_token()
        if not gcloud_access_token: return
        project_id = project_id_field.value
        agent_resource_name = agent_resource_name_field.value
        if not agent_resource_name:
            output_area.value = "Error: AGENT_RESOURCE_NAME is required for a view operation."
            page.update()
            return
        command = (
            f"curl -X GET "
            f"-H \"Authorization: Bearer {gcloud_access_token}\" "
            f"-H \"Content-Type: application/json\" "
            f"-H \"X-Goog-User-Project: {shlex.quote(project_id)}\" "
            f"\"https://discoveryengine.googleapis.com/v1alpha/{shlex.quote(agent_resource_name)}\""
        )
        run_command(command, "View Agent")

    def list_agents(e):
        gcloud_access_token = get_gcloud_access_token()
        if not gcloud_access_token: return
        project_id = project_id_field.value
        app_id = app_id_field.value
        command = (
            f"curl -X GET "
            f"-H \"Authorization: Bearer {gcloud_access_token}\" "
            f"-H \"Content-Type: application/json\" "
            f"-H \"X-Goog-User-Project: {shlex.quote(project_id)}\" "
            f"\"https://discoveryengine.googleapis.com/v1alpha/projects/{shlex.quote(project_id)}/locations/global/collections/default_collection/engines/{shlex.quote(app_id)}/assistants/default_assistant/agents\""
        )
        run_command(command, "List Agents")

    def delete_agent(e):
        gcloud_access_token = get_gcloud_access_token()
        if not gcloud_access_token: return
        project_id = project_id_field.value
        agent_resource_name = agent_resource_name_field.value
        if not agent_resource_name:
            output_area.value = "Error: AGENT_RESOURCE_NAME is required for a delete operation."
            page.update()
            return
        command = (
            f"curl -X DELETE "
            f"-H \"Authorization: Bearer {gcloud_access_token}\" "
            f"-H \"Content-Type: application/json\" "
            f"-H \"X-Goog-User-Project: {shlex.quote(project_id)}\" "
            f"\"https://discoveryengine.googleapis.com/v1alpha/{shlex.quote(agent_resource_name)}\""
        )
        run_command(command, "Delete Agent")

    # --- Tab Content ---
    auth_tab_content = ft.Column(
        [
            ft.Text("Register/Delete Authorization Resource", style=ft.TextStyle(size=18, color=ft.Colors.CYAN_400, weight=ft.FontWeight.BOLD)),
            ft.Text("Define OAuth 2.0 credentials for your agent's authorization.", style=ft.TextStyle(size=12, color=ft.Colors.BLUE_GREY_200)),
            ft.Divider(height=10, color=ft.Colors.BLUE_GREY_700),
            ft.Row([auth_id_field]), ft.Row([oauth_client_id_field, oauth_client_secret_field]),
            ft.Row([oauth_auth_uri_field]), ft.Row([oauth_token_uri_field]),
            ft.Container(height=10),
            ft.Row(
                [ TronButton("Register Auth Resource", on_click=register_auth_resource, color=ft.Colors.LIME_400), TronButton("Delete Auth Resource", on_click=delete_auth_resource, color=ft.Colors.RED_400), ],
                alignment=ft.MainAxisAlignment.START, spacing=20
            ),
        ],
        spacing=10, scroll=ft.ScrollMode.ADAPTIVE
    )

    agent_tab_content = ft.Column(
        [
            ft.Text("Manage ADK Agents", style=ft.TextStyle(size=18, color=ft.Colors.CYAN_400, weight=ft.FontWeight.BOLD)),
            ft.Text("Define and manage your ADK agents within Agentspace.", style=ft.TextStyle(size=12, color=ft.Colors.BLUE_GREY_200)),
            ft.Divider(height=10, color=ft.Colors.BLUE_GREY_700),
            ft.Text("Common Agent Parameters:", style=ft.TextStyle(size=14, color=ft.Colors.BLUE_GREY_100)),
            ft.Row([app_id_field]), ft.Row([reasoning_engine_location_dropdown, adk_deployment_id_field]),
            ft.Divider(height=10, color=ft.Colors.BLUE_GREY_700),
            ft.Text("Agent Details (for Register/Update):", style=ft.TextStyle(size=14, color=ft.Colors.BLUE_GREY_100)),
            ft.Row([agent_display_name_field]), ft.Row([agent_icon_uri_field]),
            ft.Row([agent_description_field]), ft.Row([agent_tool_description_field]),
            ft.Row([auth_ids_for_agent_field]), ft.Container(height=10),
            ft.Row(
                [ TronButton("Register Agent", on_click=register_agent, color=ft.Colors.LIME_400), TronButton("Update Agent", on_click=update_agent, color=ft.Colors.ORANGE_400), TronButton("List Agents", on_click=list_agents, color=ft.Colors.GREEN_400), ],
                alignment=ft.MainAxisAlignment.START, spacing=20
            ),
            ft.Divider(height=20, color=ft.Colors.BLUE_GREY_700),
            ft.Text("For View/Delete operations, provide the full Agent Resource Name:", style=ft.TextStyle(size=14, color=ft.Colors.BLUE_GREY_100)),
            ft.Row([agent_resource_name_field]), ft.Container(height=10),
            ft.Row(
                [ TronButton("View Agent", on_click=view_agent, color=ft.Colors.BLUE_400), TronButton("Delete Agent", on_click=delete_agent, color=ft.Colors.RED_400), ],
                alignment=ft.MainAxisAlignment.START, spacing=20
            ),
        ],
        spacing=10, scroll=ft.ScrollMode.ADAPTIVE
    )

    # --- Main Layout ---
    tabs_control = ft.Tabs(
        selected_index=0,        animation_duration=300,        tabs=[
            ft.Tab(
                text="Authorization Resources",
                content=ft.Container(
                    content=auth_tab_content, padding=20, bgcolor=ft.Colors.BLUE_GREY_800, border_radius=ft.border_radius.all(10),
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.CYAN_700, offset=ft.Offset(0, 0), blur_style=ft.ShadowBlurStyle.OUTER),
                )
            ),
            ft.Tab(
                text="Agent Management",
                content=ft.Container(
                    content=agent_tab_content, padding=20, bgcolor=ft.Colors.BLUE_GREY_800, border_radius=ft.border_radius.all(10),
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.LIME_700, offset=ft.Offset(0, 0), blur_style=ft.ShadowBlurStyle.OUTER),
                )
            ),
        ],
        label_color=ft.Colors.CYAN_400, unselected_label_color=ft.Colors.BLUE_GREY_200,
        divider_color=ft.Colors.BLUE_GREY_800, indicator_color=ft.Colors.CYAN_400,
        expand=True
    )

    collapsible_tabs = ft.ExpansionPanelList(
        expand_icon_color=ft.Colors.CYAN_400,        elevation=4,        divider_color=ft.Colors.BLUE_GREY_700,        controls=[
            ft.ExpansionPanel(
                header=ft.ListTile(title=ft.Text("Configuration", style=ft.TextStyle(size=16, color=ft.Colors.CYAN_200))),
                content=ft.Container(content=tabs_control, height=500),
                bgcolor=ft.Colors.BLUE_GREY_800,
            )
        ]
    )

    main_layout = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Automate your Google Agentspace ADK agent workflows.", style=ft.TextStyle(size=16, color=ft.Colors.CYAN_200)),
                    ft.Text("⚠️ Important: Ensure gcloud CLI is installed and authenticated.", style=ft.TextStyle(size=14, color=ft.Colors.AMBER_400), text_align=ft.TextAlign.RIGHT),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(height=20, color=ft.Colors.BLUE_GREY_700),
            ft.Row([project_id_field]),
            collapsible_tabs,
            ft.Divider(height=20, color=ft.Colors.BLUE_GREY_700),
            # --- THE FIX IS HERE ---
            ft.Text("Output Log:", style=ft.TextStyle(size=16, color=ft.Colors.CYAN_400, weight=ft.FontWeight.BOLD)),
            ft.Container(
                content=output_area,
                expand=1,
            ),
        ],
        spacing=15,
        expand=True,
    )

    page.add(
        ft.Container(
            content=main_layout,
            padding=20,
            expand=True,
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)