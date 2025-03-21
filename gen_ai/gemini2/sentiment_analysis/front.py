import json
import flet as ft
from google import genai
from google.genai import types
from back import conversation_bot
import base64


def main(page: ft.Page):
    page.title = "Tron Chatbot"
    page.theme_mode = ft.ThemeMode.DARK  # For that Tron feel
    page.session.set("uploaded_image", None)
    page.session.set("image_response", None)

    chat_history = ft.Column(scroll=ft.ScrollMode.AUTO)

    def send_message(e):
        user_message = message_text.value
        # Retrieve image and response from session
        image = page.session.get("uploaded_image")
        chatbot_response = page.session.get("image_response")

        try:
            response = conversation_bot(user_message)
            response_json = json.loads(response)
        except Exception as e:
            response = f"Error check the logs!\n{e}"
            pass

        if user_message:
            chat_history.controls.append(
                ft.Container(
                    content=ft.Text(
                        spans=[
                            ft.TextSpan(
                                "You: ",
                                ft.TextStyle(
                                    color=ft.Colors.CYAN,
                                    weight=ft.FontWeight.BOLD,
                                    size=20,
                                ),
                            ),
                            ft.TextSpan(
                                user_message,
                                ft.TextStyle(
                                    color=ft.Colors.WHITE,
                                    size=20,
                                ),
                            ),
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
                            ft.TextSpan(
                                "Tech Imm Bot: ",
                                ft.TextStyle(
                                    color=ft.Colors.CYAN,
                                    weight=ft.FontWeight.BOLD,
                                    size=20,
                                ),
                            ),
                            ft.TextSpan(
                                response,
                                ft.TextStyle(
                                    color=ft.Colors.WHITE,
                                    size=20,
                                ),
                            ),
                            ft.TextSpan("\n"),
                        ],
                    ),
                    padding=ft.padding.all(10.0),
                    border_radius=ft.border_radius.all(10.0),
                )
            )
            aggregated_sentiment_counts = {}
            # Aggregate sentiment from sentiment_analysis_by_aspect
            aspect_positive = 0
            aspect_negative = 0
            if 'sentiment_analysis_by_aspect' in response_json:
                square1.controls[0].content = ft.Text("Aspect Sentiment Analysis", weight=ft.FontWeight.BOLD, size=20)
                for item in response_json['sentiment_analysis_by_aspect']:
                    square1.controls[1].content.controls.append(ft.Row(controls=[
                        ft.Text(
                            item["aspect"] + ":", size=16),
                        ft.Text(
                            item["sentiment"],
                            style=ft.TextStyle(
                                color=ft.Colors.GREEN if item["sentiment"] == "Positive" else ft.Colors.RED,
                                weight=ft.FontWeight.BOLD,
                                size=16,
                            )
                        )
                    ]))

            if 'key_adjectives_w_sentiment' in response_json:
                square2.controls[0].content = ft.Text("Key Adjectives", weight=ft.FontWeight.BOLD, size=20)
                for item in response_json['key_adjectives_w_sentiment']:
                    square2.controls[1].content.controls.append(ft.Row(controls=[
                        ft.Text(item["adjective"] + ":", size=16),
                        ft.Text(
                            item["sentiment"],
                            style=ft.TextStyle(
                                color=ft.Colors.GREEN if item["sentiment"] == "Positive" else ft.Colors.RED,
                                weight=ft.FontWeight.BOLD,
                                size=16,
                            )
                        )
                    ]))

            if 'negation_and_sarcasm' in response_json:
                square3.controls[0].content = ft.Text("Sarcasm and Negation", weight=ft.FontWeight.BOLD, size=20)
                for item in response_json['negation_and_sarcasm']:
                    square3.controls[1].content.controls.append(ft.Row(controls=[
                        ft.Text(item["phrase"] + ":", size=16),
                        ft.Text(
                            item["sentiment"],
                            style=ft.TextStyle(
                                color=ft.Colors.GREEN if item["sentiment"] == "Positive" else ft.Colors.RED,
                                weight=ft.FontWeight.BOLD,
                                size=16,
                            )
                        )
                    ]))

            if 'summary' in response_json:
                square4.controls[0].content = ft.Text("Summary", weight=ft.FontWeight.BOLD, size=20)
                square4.controls[1].content = ft.Text(response_json['summary'], size=18)

            if 'sentiment_analysis_by_aspect' or 'key_adjectives_w_sentiment' or 'negation_and_sarcasm' or 'summary':
                dashboard.visible = True
                message_text.value = ""
                page.update()

        # Clear session data after use.
        # page.session.set("uploaded_image", None)
        # page.session.set("image_response", None)
        else:
            print("Empty Message")

    def pick_files_result(e: ft.FilePickerResultEvent):
        chat_history.controls.append(
            ft.Container(
                content=ft.Text(
                    spans=[
                        ft.TextSpan(
                            "Tech Bot: ",
                            ft.TextStyle(
                                color=ft.Colors.CYAN,
                                weight=ft.FontWeight.BOLD,
                                size=20,
                            ),
                        ),
                        ft.TextSpan(
                            "Please Wait, your image is processing...",
                            ft.TextStyle(
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
                    print("hahaha")
                    page.update()
        else:
            pass

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
            [
                ft.Text(
                    "Sentiment Analysis Classification",
                    color=ft.Colors.CYAN,
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.VerticalDivider(width=20)
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # Center the header elements
        ),
        dashboard := ft.Container(
            visible=False,
            padding=ft.padding.all(20),
            border=ft.border.all(2, ft.Colors.CYAN),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                controls=[
                    square1 := ft.Column(
                        controls=[
                            ft.Container(alignment=ft.alignment.center_left),
                            ft.Container(
                                margin=ft.margin.only(left=20),
                                alignment=ft.alignment.center_right,
                                content=ft.Column(
                                    spacing=0
                                )
                            )
                        ]
                    ),
                    square2 := ft.Column(
                        controls=[
                            ft.Container(alignment=ft.alignment.center_left),
                            ft.Container(
                                margin=ft.margin.only(left=20),
                                alignment=ft.alignment.center_right,
                                content=ft.Column(
                                    spacing=0
                                )
                            )
                        ]
                    ),
                    square3 := ft.Column(
                        controls=[
                            ft.Container(alignment=ft.alignment.center_left),
                            ft.Container(
                                margin=ft.margin.only(left=20),
                                alignment=ft.alignment.center_right,
                                content=ft.Column(
                                    spacing=0
                                )
                            )
                        ]
                    ),
                    square4 := ft.Column(
                        controls=[
                            ft.Container(alignment=ft.alignment.center_left),
                            ft.Container(
                                margin=ft.margin.only(left=20),
                                alignment=ft.alignment.center_right,
                                content=ft.Column(
                                    spacing=0
                                )
                            )
                        ]
                    ),
                ]
            )
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