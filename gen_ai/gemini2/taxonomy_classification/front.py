import json
import flet as ft
from google import genai
from google.genai import types
from back import chat_bot_master
import base64

def main(page: ft.Page):
    page.title = "Tron Chatbot"
    page.theme_mode = ft.ThemeMode.DARK  # For that Tron feel

    chat_history = ft.Column(scroll=ft.ScrollMode.AUTO)

    def send_message(e):
        user_message = message_text.value
        # response = chatbot(user_message)
        response = "hi"
        if user_message:
            chat_history.controls.append(
                ft.Container(
                    content=ft.Text(
                        spans=[
                            ft.TextSpan("You: ", ft.TextStyle(
                                color=ft.Colors.CYAN,
                                weight=ft.FontWeight.BOLD,
                                size=20,
                            )),
                            ft.TextSpan(user_message, ft.TextStyle(
                                color=ft.Colors.WHITE,
                                size=20,
                            )),
                        ],
                    ),
                    padding=ft.padding.all(10.0),
                    border_radius=ft.border_radius.all(10.0),
                )
            )

            chat_history.controls.append(
                ft.Container(
                    content=ft.Text(
                        spans=[
                            ft.TextSpan("Tech Imm Bot: ", ft.TextStyle(
                                color=ft.Colors.CYAN,
                                weight=ft.FontWeight.BOLD,
                                size=20
                            )),
                            ft.TextSpan(response, ft.TextStyle(
                                color=ft.Colors.WHITE,
                                size=20,
                            )),
                            ft.TextSpan("\n"),
                        ]
                    ),
                    padding=ft.padding.all(10.0),
                    border_radius=ft.border_radius.all(10.0),
                )
            )

            message_text.value = ""
            page.update()
        else:
            print("Empty Message")

    def pick_files_result(e: ft.FilePickerResultEvent):
        chat_history.controls.append(
            ft.Container(
                content=ft.Text(
                    spans=[
                        ft.TextSpan("Tech Bot: ", ft.TextStyle(
                            color=ft.Colors.CYAN,
                            weight=ft.FontWeight.BOLD,
                            size=20,
                            ),
                        ),
                        ft.TextSpan("Please Wait, your image is processing...", ft.TextStyle(
                            color=ft.Colors.WHITE,
                            size=20,
                            )
                        )
                    ]
                )
            )
        )
        page.update()
        if e.files:
            for f in e.files:
                with open(f.path, "rb") as image_file:
                    image = image_file.read()
                    encoded_string = base64.b64encode(image).decode('utf-8')
                response = chat_bot_master(message_text.value, image)
                chat_history.controls.append(
                    ft.Container(
                        content=ft.Image(src_base64=encoded_string, fit=ft.ImageFit.CONTAIN, width=200, height=200),
                        padding=ft.padding.all(10.0),
                        border_radius=ft.border_radius.all(10.0),
                    )
                )

                # response = chatbot("Image uploaded") # add image context to chatbot here if needed.
                chat_history.controls.append(
                    ft.Container(
                        content=ft.Text(
                            spans=[
                                ft.TextSpan("Tech Imm Bot: ", ft.TextStyle(
                                    color=ft.Colors.CYAN,
                                    weight=ft.FontWeight.BOLD,
                                    size=20
                                )),
                                ft.TextSpan(response, ft.TextStyle(
                                    color=ft.Colors.WHITE,
                                    size=20,
                                )),
                                ft.TextSpan("\n"),
                            ]
                        ),
                        padding=ft.padding.all(10.0),
                        border_radius=ft.border_radius.all(10.0),
                    )
                )
                page.update()

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)

    def pick_files(e):
        pick_files_dialog.pick_files(allowed_extensions=["png", "jpg", "jpeg"])

    message_text = ft.TextField(
        hint_text="Enter your message...",
        border_radius=ft.border_radius.all(10),
        expand=True,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        border_color=ft.Colors.CYAN,
        focused_border_color=ft.Colors.LIGHT_BLUE,
        on_submit=send_message
    )

    send_button = ft.ElevatedButton(
        "Send", on_click=send_message, style=ft.ButtonStyle(bgcolor=ft.Colors.CYAN, color=ft.Colors.WHITE)
    )

    upload_button = ft.IconButton(
        icon=ft.Icons.IMAGE_OUTLINED,
        on_click=pick_files
    )

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.Text(
                    "Image Taxonomy Classificator",
                    color=ft.Colors.CYAN,
                    size=30,
                    weight=ft.FontWeight.BOLD
                ),
                ft.VerticalDivider(width=20)
            ]
        ),
        message_container := ft.Container(
            content=chat_history,
            expand=True,
            padding=30,
            border=ft.border.all(2, ft.Colors.TRANSPARENT),
            border_radius=10,
        ),
        ft.Row(
            [
                message_text,
                send_button,
                upload_button,
            ],
        ),
    )

ft.app(target=main)