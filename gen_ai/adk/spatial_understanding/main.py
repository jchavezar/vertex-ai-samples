import asyncio
import mimetypes
import os
import secrets

from flet import *
from vertexai import agent_engines
from google.adk.sessions import VertexAiSessionService

user_id = "jesus_c"
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
location = os.getenv("GOOGLE_CLOUD_LOCATION", None)
agent_engine_display_name = "image_object_detector"
HARDCODED_SESSION_ID = None
UPLOAD_DIRECTORY = "uploaded_files"

try:
    agent_resource_name = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{agent_engine_display_name}"')][0]
    deployed_agent = agent_engines.get(agent_resource_name)
except IndexError:
    print(f"ERROR: Could not find agent engine with display name: {agent_engine_display_name}")
    deployed_agent = None

session_service = VertexAiSessionService(
    project=project_id, location=location
)

async def init_session():
    if not deployed_agent:
        return None

    app_resource_name = deployed_agent.resource_name

    if HARDCODED_SESSION_ID:
        try:
            print(f"Attempting to reuse session: {HARDCODED_SESSION_ID}")
            session = await session_service.get_session(
                app_name=app_resource_name,
                user_id=user_id,
                session_id=HARDCODED_SESSION_ID
            )
            print("Session reused successfully.")
            return session
        except Exception as e:
            print(f"Error retrieving session {HARDCODED_SESSION_ID} (may be NotFound): {e}. Creating a new one.")

    session = await session_service.create_session(
        app_name=app_resource_name,
        user_id=user_id,
    )
    print(f"New session created with ID: {session.id}")
    return session

async def close_session(session_obj, deployed_agent_obj):
    if session_obj and deployed_agent_obj:
        try:
            await session_service.delete_session(
                app_name=deployed_agent_obj.resource_name,
                user_id=session_obj.user_id,
                session_id=session_obj.id
            )
            print(f"Successfully deleted session: {session_obj.id}")
        except Exception as e:
            print(f"Error deleting session {session_obj.id}: {e}")

session = asyncio.run(init_session())

def main(page: Page):
    page.title = "Agentspace Testing"
    page.theme_mode = ThemeMode.DARK
    page.window.height = 900
    page.window.width = 920
    page.padding = 10
    page.vertical_alignment = MainAxisAlignment.START # Changed from END to START
    page.horizontal_alignment = CrossAxisAlignment.CENTER

    def on_disconnect(e):
        print(f"Flet page disconnected. Attempting to close session {session.id}.")
        if session and deployed_agent:
            asyncio.run(close_session(session, deployed_agent))

    page.on_disconnect = on_disconnect

    image_status_text = Text(value="", size=10, italic=True)

    status_indicator = ProgressRing(width=16, height=16, stroke_width=2, visible=False)
    status_text = Text("Ready.", size=10, visible=True, color=Colors.GREEN_ACCENT_400)
    current_session_id_text = Text(f"Current ID: {session.id if session else 'N/A'}", size=12, color=Colors.AMBER_400, selectable=True)

    sessions_list_column = Column(
        controls=[Text("Sessions List:", weight=FontWeight.BOLD)],
        scroll=ScrollMode.ADAPTIVE,
        expand=True
    )

    output_column : Column = Column(
        scroll=ScrollMode.ADAPTIVE,
        auto_scroll=True,
        spacing=8,
        controls=[],
        expand=True
    )

    text_input : TextField = TextField(
        border_color=Colors.TRANSPARENT,
        hint_text="Message image_object_detector...",
        expand=True,
        border_radius=30,
        filled=True,
        bgcolor=Colors.BLACK26
    )

    async def list_and_display_sessions():
        sessions_list_column.controls = [Text("Sessions List:", weight=FontWeight.BOLD, color=Colors.WHITE)]
        sessions_list_column.controls.append(ProgressRing(width=20, height=20, stroke_width=2))
        page.update()

        if not deployed_agent:
            sessions_list_column.controls = [Text("Sessions List:", weight=FontWeight.BOLD), Text("Agent not deployed.", color=Colors.RED_400)]
            page.update()
            return

        try:
            sessions_page = await session_service.list_sessions(
                app_name=deployed_agent.resource_name,
                user_id=user_id
            )

            sessions_list_column.controls.pop()

            if not sessions_page.sessions:
                sessions_list_column.controls.append(Text("No active sessions found.", color=Colors.GREY_600))
            else:
                for s in sessions_page.sessions:
                    is_current = s.id == session.id
                    item_color = Colors.AMBER_400 if is_current else Colors.WHITE

                    session_row = Row(
                        controls=[
                            Text(s.id, size=10, color=item_color, selectable=True, expand=True),
                            IconButton(
                                icon=Icons.CLOSE,
                                icon_size=12,
                                tooltip=f"Delete session {s.id}",
                                on_click=lambda e, sid=s.id: page.run_task(delete_session_and_refresh, sid),
                                disabled=is_current
                            )
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN
                    )
                    sessions_list_column.controls.append(session_row)

        except Exception as e:
            sessions_list_column.controls = [Text("Sessions List:", weight=FontWeight.BOLD), Text(f"Error listing sessions: {e}", color=Colors.RED_400)]

        page.update()

    async def delete_session_and_refresh(session_id_to_delete: str):
        if not deployed_agent: return

        try:
            await session_service.delete_session(
                app_name=deployed_agent.resource_name,
                user_id=user_id,
                session_id=session_id_to_delete
            )
            print(f"Deleted session: {session_id_to_delete}")
        except Exception as e:
            print(f"Failed to delete session {session_id_to_delete}: {e}")

        await list_and_display_sessions()

    page.run_task(list_and_display_sessions)


    async def stream_gemini_response(message_text: str):
        try:
            if not deployed_agent or not session:
                output_column.controls.append(
                    Container(
                        padding=10,
                        content=Text("Gemini: Agent not initialized.", weight=FontWeight.BOLD),
                        border_radius=10,
                        bgcolor=Colors.RED_50
                    )
                )
                output_column.update()
                return

            response_text_control = Text("", color=Colors.WHITE)
            gemini_container = Container(
                content=Column(
                    controls=[
                        Text("Gemini", color=Colors.WHITE, weight=FontWeight.BOLD),
                        response_text_control,
                    ],
                    spacing=0,
                    horizontal_alignment=CrossAxisAlignment.START
                ),
                padding=padding.only(left=10, right=10, top=5, bottom=8),
                border_radius=border_radius.only(top_left=20, top_right=20, bottom_right=20, bottom_left=5),
                bgcolor=Colors.BLUE_GREY_900,
                width=350
            )
            output_column.controls.append(Row(controls=[gemini_container], alignment=MainAxisAlignment.START))
            output_column.update()

            full_response = ""
            async for event in deployed_agent.async_stream_query(
                    user_id=user_id,
                    session_id=session.id,
                    message=message_text,
            ):
                if event["content"]["parts"][0].get("text"):
                    full_response += event["content"]["parts"][0]["text"]
                    response_text_control.value = full_response
                    output_column.update()

        finally:
            status_indicator.visible = False
            status_text.value = "Ready."
            status_text.color = Colors.GREEN_ACCENT_400
            page.update()

    def on_message_submitted(message_text: str):
        if not message_text.strip():
            text_input.value = ""
            page.update()
            return

        output_column.controls.append(
            Row(
                controls=[
                    Container(
                        content=Column(
                            controls=[
                                Text("User", color=Colors.BLACK, weight=FontWeight.BOLD),
                                Text(color=Colors.BLACK, value=message_text),
                            ],
                            spacing=0,
                            horizontal_alignment=CrossAxisAlignment.START
                        ),
                        padding=padding.only(left=10, right=10, top=5, bottom=8),
                        border_radius=border_radius.only(top_left=20, top_right=20, bottom_left=20, bottom_right=5),
                        bgcolor=Colors.LIME_ACCENT_100,
                        width=350
                    )
                ],
                alignment=MainAxisAlignment.END
            )
        )
        status_indicator.visible = True
        status_text.value = "Waiting for Gemini..."
        status_text.color = Colors.YELLOW_ACCENT_400
        output_column.update()
        page.update()

        text_input.value = ""
        text_input.focus()

        page.run_task(stream_gemini_response, message_text)

    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    def handle_upload_complete(e):
        print(f"Server-side check: Upload complete! Files saved to {UPLOAD_DIRECTORY}")

    def handle_file_selection(e):
        if not e.files:
            page.update()
            return

        upload_list = []
        file_names = ", ".join([file.name for file in e.files])
        print(f"Files selected: {file_names}")

        for file in e.files:
            upload_url = page.get_upload_url(file.name, 3600)
            upload_list.append(FilePickerUploadFile(file.name, upload_url))
            print(f"Generated URL for {file.name}: {upload_url}")

        file_picker.upload(upload_list)

        print(f"Starting background upload for: {file_names}")
        page.update()

    file_picker = FilePicker(
        on_result=handle_file_selection,
        on_upload=handle_upload_complete
    )
    page.overlay.append(file_picker)
    page.update()

    text_input.on_submit = lambda e: on_message_submitted(e.data)

    image_upload_button = IconButton(
        icon=Icons.IMAGE,
        tooltip="Upload Image",
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),
        icon_color=Colors.GREY_400
    )

    send_button = IconButton(
        icon=Icons.SEND,
        tooltip="Send Message",
        on_click=lambda e: on_message_submitted(text_input.value),
        icon_color=Colors.WHITE
    )

    input_controls_row = Row(
        controls=[
            image_upload_button,
            text_input,
            send_button,
        ],
        alignment=MainAxisAlignment.START,
        spacing=5
    )

    status_row = Row(
        controls=[
            status_indicator,
            status_text
        ],
        alignment=MainAxisAlignment.START,
        spacing=5
    )

    chat_area_column = Column(
        controls=[
            output_column,
            status_row,
            image_status_text,
            Container(
                content=input_controls_row,
                border_radius=30,
                border=border.all(2, color=Colors.BLUE_GREY_600),
                padding=padding.only(left=5, right=5, top=2, bottom=2)
            ),
        ],
        expand=True,
        horizontal_alignment=CrossAxisAlignment.STRETCH
    )

    session_panel_content = Column(
        controls=[
            Text("Session Tools", size=16, weight=FontWeight.BOLD, color=Colors.WHITE),
            Divider(height=10, color=Colors.GREY_700),
            Text("Active Session:", size=12, color=Colors.GREY_400),
            current_session_id_text,
            Divider(height=10, color=Colors.GREY_700),
            ElevatedButton(
                "Refresh Sessions",
                on_click=lambda e: page.run_task(list_and_display_sessions),
                icon=Icons.REFRESH,
                color=Colors.LIGHT_BLUE_ACCENT_400
            ),
            Container(
                content=sessions_list_column,
                expand=True,
                margin=margin.only(top=10)
            )
        ],
        expand=True,
        horizontal_alignment=CrossAxisAlignment.STRETCH
    )

    main_content_row = Row(
        controls=[
            Container(
                content=chat_area_column,
                width=550,
                expand=True,
                padding=padding.only(right=10)
            ),
            VerticalDivider(width=1, thickness=1, color=Colors.GREY_700),
            Container(
                content=session_panel_content,
                width=280,
                expand=True, # Added expand=True
                # Removed height=780
                bgcolor=Colors.BLACK54,
                padding=15,
                border_radius=10,
                margin=margin.only(left=10)
            )
        ],
        expand=True,
        vertical_alignment=CrossAxisAlignment.START
    )

    page.add(
        Container(
            content=Column(
                controls=[
                    Text("Agentspace Chat", size=18, weight=FontWeight.BOLD, color=Colors.WHITE),
                    main_content_row
                ],
                expand=True,
                spacing=15,
                horizontal_alignment=CrossAxisAlignment.CENTER
            ),
            width=850,
            # Removed height=830
            expand=True, # Added expand=True to the outermost container
            bgcolor=Colors.BLACK87,
            padding=15
        )
    )

if __name__ == "__main__":
    if "FLET_SECRET_KEY" not in os.environ:
        os.environ["FLET_SECRET_KEY"] = secrets.token_hex(16)

    app(target=main, upload_dir=UPLOAD_DIRECTORY)