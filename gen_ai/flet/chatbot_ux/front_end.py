import time
import flet as ft
from back_end import vertexai_conversation, preloaded_questions_recommendations

preloaded_questions = preloaded_questions_recommendations()

class ChatBubble(ft.Row):
  def __init__(self, text, is_user):
    super().__init__()
    self.is_user = is_user
    self.text = text
    self.current_text = ""
    self.expand = True
    self.alignment = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START

    self.controls = [
        ft.AnimatedSwitcher(
            duration=400,
            transition=ft.AnimatedSwitcherTransition.SCALE,
            switch_in_curve=ft.AnimationCurve.EASE_IN_CUBIC,
            switch_out_curve=ft.AnimationCurve.EASE_OUT_CUBIC,
            content=ft.Container(
                content=ft.Text(self.text,
                                size=16,
                                selectable=True,
                                color=ft.colors.WHITE if self.is_user else ft.colors.BLACK,
                                no_wrap=True if len(self.text)*9 < 700 else False),
                padding=ft.padding.only(left=9, right=10, top=5, bottom=5),
                border_radius=ft.border_radius.only(
                    top_left=10 if not self.is_user else 0,
                    top_right =10 if self.is_user else 0,
                    bottom_left =10,
                    bottom_right=10,
                ),
                bgcolor="#087FFE" if self.is_user else ft.colors.GREY_200,
                width=min(len(self.text) * 9 if len(self.text) > 9 else 100, 700),
            )
        )
    ]

  def did_mount(self):
    self.type_message()

  def type_message(self):
    if len(self.current_text) < len(self.text):
      self.current_text += self.text[len(self.current_text)]
      self.update()
      time.sleep(0.05)  # Adjust typing speed here
      self.type_message()

def main(page: ft.Page):
    page.title = "AI Chatbot"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.LIGHT

    chat_history = ft.ListView(
        expand=True,
        height=400,
        spacing=20,
    )

    # Logs window (wrapped in a Container)
    logs_window = ft.Container(
        height=550,
        width=350,
        content=ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            spacing=10,
        ),
        # bgcolor=ft.colors.BLUE_GREY_600,
        bgcolor="#293241",
        border_radius=10,
        padding=10,
    )

    # Text field
    txt_field = ft.TextField(
        border_color="#087FFE",
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

    def button_message(e):
      txt_field.value = e.control.text
      page.update()

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
                            controls=[
                                chat_history,
                                ft.Container(
                                    height=100,
                                    content=ft.Row(
                                        scroll=ft.ScrollMode.ALWAYS,
                                        controls=[
                                           ft.TextButton(item, on_click=button_message) for item in preloaded_questions["recommended_questions"]
                                        ]
                                    )
                                ),
                                ft.Row(
                                    controls=[
                                        txt_field,
                                        send_button,
                                    ],
                                ),
                                ft.Divider(height=5, color=ft.colors.TRANSPARENT),
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
        chat_history.controls.append(ChatBubble(user_message, True))
        txt_field.value = ""
        page.update()

        response, details = vertexai_conversation(user_message)
        if details is None:
            details = ["Error", "Error"]
        chat_history.controls.append(ChatBubble(response.replace("\n","").strip(), False))
        logs = []
        logs_window.content.controls.clear()
        for num, item in enumerate(details):
            if num == 0:
              logs.append(ft.Text("Logs", size=16, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD))
            logs.append(ft.Text(f"Iteration Number {num+1}", size=12, color=ft.colors.WHITE))
            logs.append(ft.Text(item, size=12, color=ft.colors.GREEN_300, selectable=True))

        logs_window.content.controls = logs

        page.update()


ft.app(target=main, port=8000, host="0.0.0.0")
