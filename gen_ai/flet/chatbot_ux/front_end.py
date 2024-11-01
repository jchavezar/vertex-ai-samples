import time
import flet as ft
from back_end import vertexai_conversation


def main(page: ft.Page):
    page.title = "AI Chatbot"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.LIGHT

    # Chat window
    chat_history = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        expand=True,
        height=400,
        spacing=10,
    )

    # Logs window (wrapped in a Container)
    logs_window = ft.Container(
        height=550,
        width=350,
        content=ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            spacing=10,
        ),
        bgcolor=ft.colors.BLUE_GREY_600,
        border_radius=10,
        padding=10,
    )

    # Text field
    txt_field = ft.TextField(
        hint_text="Ask me anything...",
        expand=True,
        on_submit=lambda e: send_message(e),
    )

    # Send button
    send_button = ft.IconButton(
        icon=ft.icons.SEND,
        icon_color="#087FFE",
        tooltip="Send",
        on_click=lambda e: send_message(e),
    )

    # Helper text (for styling)
    helper_text = ft.Text(
        "Enter your message and press Enter or click the send icon.",
        size=12,
        color=ft.colors.GREY_500,
        italic=True,
    )

    # Layout
    page.add(
        ft.Container(
            padding=ft.padding.only(left=14.0, right=14.0, top=5.0, bottom=5.0),
            alignment=ft.alignment.center,
            expand=True,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        padding=ft.padding.all(8.0),
                        expand=2,
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            expand=True,
                            width=700,
                            controls=[
                                chat_history,
                                ft.Row(
                                    controls=[
                                        txt_field,
                                        send_button,
                                    ],
                                ),
                                helper_text,
                            ],
                        ),
                    ),
                    ft.VerticalDivider(width=1, color=ft.colors.GREY_600),
                    ft.Container(
                        alignment=ft.alignment.center,
                        expand=1,
                        content=logs_window
                    )
                ],
            )
        )
    )

    def send_message(e):
        # Add user message to chat history
        user_message = txt_field.value
        chat_history.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    ft.Container(
                        content=ft.Text(
                            user_message, style=ft.TextThemeStyle.BODY_MEDIUM
                        ),
                        padding=ft.padding.all(10),
                        border_radius=ft.border_radius.all(10),
                        bgcolor=ft.colors.BLUE_GREY_100,
                        alignment=ft.alignment.center_left,
                    )
                ],
            )
        )
        # Clear text field
        txt_field.value = ""
        page.update()

        chat_history.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                # wrap=True,
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "Typing...",  # Set initial "Typing..." here
                            style=ft.TextThemeStyle.BODY_MEDIUM,
                            color=ft.colors.WHITE
                        ),
                        padding=ft.padding.all(10),
                        border_radius=ft.border_radius.all(10),
                        bgcolor="#087FFE",
                        alignment=ft.alignment.center_right,
                    )
                ],
            )
        )
        page.update()

        bot_message = "Typing..."
        page.update()
        response, details = vertexai_conversation(user_message)
        if details is None:
            details = ["Error", "Error"]

        # Chatbot response
        # Initialize bot_message here
        bot_message = ""
        for char in response:
            time.sleep(0.004)  # Adjust typing speed
            bot_message = bot_message + char  # Add the character to bot_message
            chat_history.controls[-1].controls[0].content.value = bot_message
            page.update()

        logs = []
        logs_window.content.controls.clear()
        for num, item in enumerate(details):
            logs.append(ft.Text(f"Iteration Number {num+1}", size=12, color=ft.colors.WHITE))
            logs.append(ft.Text(item, size=12, color=ft.colors.GREEN_300))

        logs_window.content.controls = logs

        # Add log entry
        # logs_window.content.controls.append(
        #     ft.Text(f"User: {user_message}",
        #             size=12, color=ft.colors.WHITE)
        # )
        # logs_window.content.controls.append(
        #     ft.Text(f"Bot: {response}", size=12, color=ft.colors.GREEN_300)
        # )
        page.update()


ft.app(target=main)
