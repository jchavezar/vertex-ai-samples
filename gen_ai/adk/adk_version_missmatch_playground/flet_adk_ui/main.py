import asyncio
import mimetypes
import os
import secrets

from flet import *
from vertexai import agent_engines

display_name = "adk_version_missmatch_playground"
user_id = "jesus_c"
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
location = os.getenv("GOOGLE_CLOUD_LOCATION", None)
agent_engine_display_name = "image_object_detector"
USER_ID = "user-1"
UPLOAD_DIRECTORY = "uploaded_files"

# Safely initialize the deployed agent
try:
    deployed_agent_list = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{display_name}"')]
    if deployed_agent_list:
        deployed_agent = agent_engines.get(deployed_agent_list[0])
    else:
        deployed_agent = None
        print(f"Agent with display name '{display_name}' not found.")
except Exception as e:
    deployed_agent = None
    print(f"Error initializing agent: {e}")

session_holder = {"session": None}

async def init_session():
    """Creates a new session with the deployed agent."""
    if not deployed_agent:
        print("Agent not found or deployed.")
        return None
    try:
        print("Creating a new session...")
        session = await deployed_agent.async_create_session(
            user_id=USER_ID,
        )
        print(f"New session created with ID: {session['id']}")
        return session
    except Exception as e:
        print(f"Error creating a new session: {e}")
        return None

async def close_session(session_obj, deployed_agent_obj):
    if session_obj and deployed_agent_obj:
        try:
            await deployed_agent_obj.async_delete_session(
                user_id=session_obj['user_id'],
                session_id=session_obj['id']
            )
            print(f"Successfully deleted session: {session_obj['id']}")
        except Exception as e:
            print(f"Error deleting session {session_obj['id']}: {e}")

def main(page: Page):
    page.title = "Futuristic Agentspace"
    page.theme_mode = ThemeMode.DARK
    page.bgcolor = "#0D1117"
    page.window.height = 900
    page.window.width = 920
    page.padding = 20
    page.vertical_alignment = MainAxisAlignment.START
    page.horizontal_alignment = CrossAxisAlignment.CENTER

    def on_disconnect(e):
        s = session_holder["session"]
        print(f"Flet page disconnected. Attempting to close session {s['id'] if s else 'N/A'}.")
        if s and deployed_agent:
            asyncio.run(close_session(s, deployed_agent))

    page.on_disconnect = on_disconnect

    image_status_text = Text(value="", size=10, italic=True, color=Colors.GREY_500)

    status_indicator = ProgressRing(width=16, height=16, stroke_width=2, visible=False, color=Colors.CYAN_ACCENT_400)
    status_text = Text("Initializing...", size=10, visible=True, color=Colors.ORANGE_400)
    current_session_id_text = Text("ID: Loading...", size=10, color=Colors.ORANGE_400, selectable=True)

    sessions_list_column = Column(
        controls=[Text("Sessions", weight=FontWeight.BOLD, color=Colors.WHITE)],
        scroll=ScrollMode.ADAPTIVE,
        expand=True
    )

    output_column: Column = Column(
        scroll=ScrollMode.ADAPTIVE,
        auto_scroll=True,
        spacing=12,
        controls=[],
        expand=True
    )

    text_input: TextField = TextField(
        border_color=Colors.BLUE_GREY_800,
        focused_border_color=Colors.CYAN_400,
        hint_text="Message agent...",
        expand=True,
        border_radius=20,
        filled=True,
        bgcolor="#161B22",
        color=Colors.WHITE,
        content_padding=padding.symmetric(horizontal=15, vertical=10),
        disabled=True
    )

    async def list_and_display_sessions():
        sessions_list_column.controls = [Text("Sessions", weight=FontWeight.BOLD, color=Colors.WHITE)]
        sessions_list_column.controls.append(
            Row([ProgressRing(width=16, height=16, stroke_width=2, color=Colors.CYAN_400), Text("Loading...")], spacing=10)
        )
        page.update()

        s = session_holder["session"]

        if not deployed_agent:
            sessions_list_column.controls = [Text("Sessions", weight=FontWeight.BOLD), Text("Agent not deployed.", color=Colors.RED_400)]
            page.update()
            return

        try:
            sessions_page = await deployed_agent.async_list_sessions(
                user_id=USER_ID
            )
            sessions_list_column.controls.pop()

            session_list = sessions_page.get('sessions', [])

            if not session_list:
                sessions_list_column.controls.append(Text("No active sessions.", color=Colors.GREY_600))
            else:
                for session_entry in session_list:
                    is_current = s and (session_entry['id'] == s['id'])
                    item_color = Colors.CYAN_400 if is_current else Colors.WHITE
                    bg_color = Colors.BLUE_GREY_800 if is_current else Colors.TRANSPARENT

                    session_row = Container(
                        content=Row(
                            controls=[
                                Icon(Icons.CIRCLE, color=item_color, size=8),
                                Text(session_entry['id'], size=10, color=item_color, selectable=True, expand=True, overflow=TextOverflow.ELLIPSIS),
                                IconButton(
                                    icon=Icons.DELETE_OUTLINE,
                                    icon_size=14,
                                    tooltip=f"Delete session {session_entry['id']}",
                                    on_click=lambda e, sid=session_entry['id']: page.run_task(delete_session_and_refresh, sid),
                                    disabled=is_current,
                                    icon_color=Colors.GREY_500,
                                    style=ButtonStyle(shape=CircleBorder(), padding=5)
                                )
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=CrossAxisAlignment.CENTER
                        ),
                        padding=padding.symmetric(horizontal=10, vertical=5),
                        border_radius=8,
                        bgcolor=bg_color
                    )
                    sessions_list_column.controls.append(session_row)

        except Exception as e:
            sessions_list_column.controls = [Text("Sessions", weight=FontWeight.BOLD), Text(f"Error: {e}", color=Colors.RED_400)]

        page.update()

    async def delete_session_and_refresh(session_id_to_delete: str):
        if not deployed_agent: return
        try:
            await deployed_agent.async_delete_session(
                user_id=USER_ID,
                session_id=session_id_to_delete
            )
            print(f"Deleted session: {session_id_to_delete}")
        except Exception as e:
            print(f"Failed to delete session {session_id_to_delete}: {e}")
        await list_and_display_sessions()

    async def stream_gemini_response(message_text: str):
        s = session_holder["session"]

        try:
            if not deployed_agent or not s:
                output_column.controls.append(
                    Row([Container(
                        padding=10,
                        content=Text("Agent not initialized.", weight=FontWeight.BOLD, color=Colors.WHITE),
                        border_radius=10,
                        bgcolor=Colors.RED_900
                    )], alignment=MainAxisAlignment.CENTER)
                )
                output_column.update()
                return

            response_text_control = Text("", color=Colors.WHITE, selectable=True)
            gemini_container = Container(
                content=Column(
                    controls=[
                        Row([Icon(Icons.AUTO_MODE_SHARP, size=16, color=Colors.CYAN_300), Text("Agent", color=Colors.CYAN_300, weight=FontWeight.BOLD)]),
                        response_text_control,
                    ],
                    spacing=5,
                    horizontal_alignment=CrossAxisAlignment.START
                ),
                padding=padding.all(15),
                border_radius=border_radius.only(top_left=15, top_right=15, bottom_right=15, bottom_left=5),
                bgcolor="#161B22",
                width=450,
                border=border.all(1, Colors.BLUE_GREY_800)
            )
            output_column.controls.append(Row(controls=[gemini_container], alignment=MainAxisAlignment.START))
            output_column.update()

            full_response = ""
            async for event in deployed_agent.async_stream_query(
                    user_id=USER_ID,
                    session_id=s['id'],
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
        if not message_text.strip() or text_input.disabled:
            text_input.value = ""
            page.update()
            return

        output_column.controls.append(
            Row(
                controls=[
                    Container(
                        content=Column(
                            controls=[
                                Row([Icon(Icons.PERSON, size=16), Text("You", weight=FontWeight.BOLD)]),
                                Text(value=message_text, selectable=True),
                            ],
                            spacing=5,
                            horizontal_alignment=CrossAxisAlignment.START
                        ),
                        padding=padding.all(15),
                        border_radius=border_radius.only(top_left=15, top_right=15, bottom_left=15, bottom_right=5),
                        bgcolor=Colors.BLUE_700,
                        width=450
                    )
                ],
                alignment=MainAxisAlignment.END
            )
        )
        status_indicator.visible = True
        status_text.value = "Agent is thinking..."
        status_text.color = Colors.CYAN_ACCENT_400
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
        file_picker.upload(upload_list)
        print(f"Starting background upload for: {file_names}")
        page.update()

    file_picker = FilePicker(on_result=handle_file_selection, on_upload=handle_upload_complete)
    page.overlay.append(file_picker)

    text_input.on_submit = lambda e: on_message_submitted(e.data)

    image_upload_button = IconButton(
        icon=Icons.ATTACH_FILE,
        tooltip="Upload Files",
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),
        icon_color=Colors.GREY_400
    )


    send_button = IconButton(
        icon=Icons.SEND_ROUNDED,
        tooltip="Send Message",
        on_click=lambda e: on_message_submitted(text_input.value),
        icon_color=Colors.CYAN_ACCENT_400,
        disabled=True
    )

    input_controls_row = Row(
        controls=[image_upload_button, text_input, send_button],
        alignment=MainAxisAlignment.START,
        spacing=5,
        vertical_alignment=CrossAxisAlignment.CENTER
    )

    status_row = Row(
        controls=[status_indicator, status_text],
        alignment=MainAxisAlignment.START,
        spacing=5,
        vertical_alignment=CrossAxisAlignment.CENTER
    )

    chat_area_column = Column(
        controls=[
            output_column,
            status_row,
            image_status_text,
            Container(
                content=input_controls_row,
                border_radius=25,
                border=border.all(1, Colors.BLUE_GREY_800),
                padding=padding.only(left=5, right=5)
            ),
        ],
        expand=True,
        horizontal_alignment=CrossAxisAlignment.STRETCH
    )

    session_panel_content = Column(
        controls=[
            Row([Icon(Icons.HUB_OUTLINED), Text("Session Control", size=16, weight=FontWeight.BOLD, color=Colors.WHITE)]),
            Divider(height=20, color=Colors.BLUE_GREY_800),
            Text("Active Session:", size=12, color=Colors.GREY_400),
            current_session_id_text,
            Divider(height=20, color=Colors.BLUE_GREY_800),
            ElevatedButton(
                "Refresh List",
                on_click=lambda e: page.run_task(list_and_display_sessions),
                icon=Icons.REFRESH,
                style=ButtonStyle(
                    color=Colors.WHITE,
                    bgcolor=Colors.BLUE_GREY_700,
                    shape=RoundedRectangleBorder(radius=8)
                )
            ),
            Container(
                content=sessions_list_column,
                expand=True,
                margin=margin.only(top=15)
            )
        ],
        expand=True,
        horizontal_alignment=CrossAxisAlignment.STRETCH,
        spacing=10
    )


    main_content_row = Row(
        controls=[
            Container(
                content=chat_area_column,
                expand=True,
                padding=padding.only(right=20)
            ),
            VerticalDivider(width=1, thickness=1, color=Colors.BLUE_GREY_800),
            Container(
                content=session_panel_content,
                width=280,
                bgcolor="#161B22",
                padding=15,
                border_radius=15,
                margin=margin.only(left=10),
                border=border.all(1, Colors.BLUE_GREY_800)
            )
        ],
        expand=True,
        vertical_alignment=CrossAxisAlignment.START
    )

    page.add(
        Container(
            content=Column(
                controls=[
                    Row([Icon(Icons.DEVICE_HUB), Text("Agentspace", size=20, weight=FontWeight.BOLD, color=Colors.WHITE)]),
                    main_content_row
                ],
                expand=True,
                spacing=20,
            ),
            expand=True,
            padding=15
        )
    )
    page.update()

    async def init_session_and_update_ui():
        s = await init_session()
        session_holder["session"] = s

        current_session_id_text.value = f"ID: {s['id'] if s else 'N/A'}"
        current_session_id_text.color = Colors.CYAN_400

        if s:
            status_text.value = "Ready."
            status_text.color = Colors.GREEN_ACCENT_400
            text_input.disabled = False
            send_button.disabled = False
        else:
            status_text.value = "Session Failed. Cannot chat."
            status_text.color = Colors.RED_400
            text_input.disabled = True
            send_button.disabled = True

        page.update()

        await list_and_display_sessions()

    page.run_task(init_session_and_update_ui)

if __name__ == "__main__":
    if "FLET_SECRET_KEY" not in os.environ:
        os.environ["FLET_SECRET_KEY"] = secrets.token_hex(16)
    app(target=main, upload_dir=UPLOAD_DIRECTORY)