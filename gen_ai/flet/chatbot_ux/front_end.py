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
    log_window_height = 550
    log_window_width = 350

    chat_history = ft.ListView(
        expand=True,
        height=400,
        spacing=20,
    )

    logs_inner_container = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        spacing=10,
    )

    dlg = ft.AlertDialog(
        title=ft.Text("Table Data"),
        actions=[ft.TextButton("Close", on_click=lambda e: page.close_dialog())],
    )
    page.add(dlg)

    def open_dlg(e):
      page.show_dialog(dlg)

    table_button = ft.ElevatedButton(
        "Table Results",
        on_click=open_dlg,
        disabled=True,
    )

    # Logs window (wrapped in a Container)
    logs_window = ft.Container(
        height=page.height*.80,
        width=log_window_width,
        content=ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            spacing=10,
            controls=[
                ft.Container(
                    height=page.height*.80*.75,
                    width=log_window_width,
                    bgcolor=ft.Colors.AMBER_50,
                    content=logs_inner_container
                ),
                ft.Container(
                    padding=30,
                    height=page.height*.80*.20,
                    width=log_window_width,
                    bgcolor=ft.Colors.GREY_600,
                    content=table_button
                )
            ]
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

        response, details, bq_response = vertexai_conversation(user_message)
        if bq_response:
          dlg.content=""
          print(bq_response)
          column_names = [ft.DataColumn(ft.Text(key)) for key in bq_response[0]]
          data = [
              ft.DataRow(
                  cells=[ft.DataCell(ft.Text(v)) for k,v in row.items()]
              )
              for row in bq_response
          ]
          table = ft.DataTable(
              columns=column_names,
              rows=data
          )
          dlg.content = table
          dlg.update()
        if details is None:
            details = ["Error", "Error"]
        chat_history.controls.append(ChatBubble(response.replace("\n","").strip(), False))
        logs = []
        logs_inner_container.controls.clear()
        table_button.disabled = False
        for num, item in enumerate(details):
            if num == 0:
              logs.append(ft.Text("Logs", size=16, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD))
            logs.append(ft.Text(f"Iteration Number {num+1}", size=12, color=ft.colors.WHITE))
            logs.append(ft.Text(item, size=12, color=ft.colors.GREEN_300, selectable=True))

        logs_inner_container.controls = logs

        page.update()


ft.app(target=main, port=8000, host="0.0.0.0", view=ft.WEB_BROWSER)
