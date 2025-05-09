#%%
import asyncio
from google.cloud import dialogflowcx_v3
from google.api_core.client_options import ClientOptions
from flet import (
    Page,
    ListView,
    Container,
    Text,
    TextField,
    Column,
    Row,
    MainAxisAlignment,
    border,
    Colors,
    margin,
    padding,
    alignment,
    app,
    Theme,
    ThemeMode,
    CrossAxisAlignment
)
import asyncio
import os
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

client_options = ClientOptions(api_endpoint="us-central1-dialogflow.googleapis.com")

async def chatbot_send_message(prompt: str):
    print("text")
    print(prompt)
    session_client = dialogflowcx_v3.SessionsAsyncClient(client_options=client_options)

    query_input = dialogflowcx_v3.QueryInput()
    query_input.text.text = prompt
    query_input.language_code = "en"

    project_id = "jesusarguelles-sandbox"
    location_id = "us-central1"
    agent_id = "4d49e7a6-c054-4544-b36e-9e650791f4d8"
    session_id = "my-unique-session-id-123"

    session_path = session_client.session_path(project_id, location_id, agent_id, session_id)

    request = dialogflowcx_v3.DetectIntentRequest(
        session=session_path,
        query_input=query_input,
    )

    response = await session_client.detect_intent(request=request)
    return response


def main(page: Page):
    page.title = "Chat App"
    page.window_height = 700
    page.window_width = 500
    page.theme = Theme(color_scheme_seed=Colors.GREEN)
    page.theme_mode = ThemeMode.LIGHT

    list_view: ListView = ListView(
        auto_scroll=True,
        expand=True
    )

    chat_history_container: Container = Container(
        expand=True,
        border_radius=12.0,
        border=border.all(1, Colors.GREY_300),
        padding=padding.all(5), # Reduced padding for chat history overall
        content=list_view
    )

    message_input_field = TextField(
        hint_text="Type your message...",
        border_color=Colors.TRANSPARENT,
        filled=False,
        expand=True,
        shift_enter=True,
    )

    async def send_message(e):
        user_text = message_input_field.value.strip()
        if not user_text:
            return

        message_input_field.value = ""
        message_input_field.focus()

        # User message bubble - wrapped in a Row
        list_view.controls.append(
            Row(
                controls=[
                    Container(
                        content=Text(user_text, selectable=True),
                        padding=padding.all(10), # Padding inside the bubble
                        margin=margin.symmetric(vertical=4, horizontal=8), # Margin around the bubble
                        border_radius=12.0,
                        bgcolor=Colors.PINK_50,
                    )
                ],
                alignment=MainAxisAlignment.START # Aligns bubble to the left
            )
        )
        message_input_field.update()
        list_view.update()
        response_text = await chatbot_send_message(user_text)
        if response_text is None:
            response_text = "Sorry, an error occurred."

        # Bot message bubble - wrapped in a Row
        list_view.controls.append(
            Row(
                controls=[
                    Container(
                        content=Text(str(response_text), selectable=True),
                        padding=padding.all(10),
                        margin=margin.symmetric(vertical=4, horizontal=8),
                        border_radius=12.0,
                        bgcolor=Colors.BLUE_50,
                    )
                ],
                alignment=MainAxisAlignment.START # Aligns bubble to the left
            )
        )
        list_view.update()

    message_input_field.on_submit = send_message

    text_entry_area = Container(
        padding=padding.symmetric(horizontal=10, vertical=5),
        border=border.only(top=border.BorderSide(1, Colors.GREY_300)),
        content=Row(
            controls=[message_input_field],
            vertical_alignment=CrossAxisAlignment.CENTER
        )
    )

    page.add(
        Column(
            expand=True,
            controls=[
                chat_history_container,
                text_entry_area
            ],
            alignment=MainAxisAlignment.START,
            horizontal_alignment="stretch"
        )
    )

if __name__ == "__main__":
    app(target=main)