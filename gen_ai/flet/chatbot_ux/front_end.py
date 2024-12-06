import flet as ft
from back_end import vertexai_conversation, preloaded_questions_recommendations

# Load the preloaded questions
preloaded_questions = preloaded_questions_recommendations()

class ChatBubble(ft.Row):
  def __init__(self, text, page, is_user):
    super().__init__()
    self.is_user = is_user
    self.text = text
    self.alignment = (
        ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
    )
    self.vertical_alignment = ft.CrossAxisAlignment.START

    text_color = ft.Colors.WHITE if self.is_user else ft.Colors.BLACK
    bg_color = "#087FFE" if self.is_user else ft.Colors.GREY_200

    if self.is_user:
      content = ft.Text(
          self.text,
          color=text_color,
          no_wrap=False,  # allow wrapping
      )
    else:
      content = ft.Markdown(  # Markdown directly in Container
          self.text,
          selectable=True,
          extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
          md_style_sheet=ft.MarkdownStyleSheet(
              p_text_style=ft.TextStyle(color=text_color),
              h1_text_style=ft.TextStyle(color=text_color),
              h2_text_style=ft.TextStyle(color=text_color),
              h3_text_style=ft.TextStyle(color=text_color),
              h4_text_style=ft.TextStyle(color=text_color),
              h5_text_style=ft.TextStyle(color=text_color),
              h6_text_style=ft.TextStyle(color=text_color),
          ),
          width=min(500, page.width * 0.6 - 20), # width constraint on Markdown
      )


    self.controls = [
        ft.Container(
            content=content,
            padding=ft.padding.only(left=9, right=10, top=5, bottom=5),
            border_radius=ft.border_radius.only(
                top_left=10 if not self.is_user else 0,
                top_right=10 if self.is_user else 0,
                bottom_left=10,
                bottom_right=10,
            ),
            bgcolor=bg_color,
        )
    ]

def main(page: ft.Page):
  page.title = "AI Chatbot"
  page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
  page.vertical_alignment = ft.MainAxisAlignment.START
  page.theme_mode = ft.ThemeMode.LIGHT
  log_window_width = 350

  # Chat history container
  chat_history = ft.ListView(
      expand=True,
      height=400,
      spacing=20,
  )

  # Logs container
  logs_inner_container = ft.Column(
      scroll=ft.ScrollMode.ALWAYS,
      spacing=10,
  )

  # Dialog to display table results
  dlg = ft.AlertDialog(
      title=ft.Text("Table Data"),
      actions=[ft.TextButton("Close", on_click=lambda e: page.close_dialog())],
  )
  page.add(dlg)

  def open_dlg(e):
    page.show_dialog(dlg)

  # Button to show table results
  table_button = ft.ElevatedButton(
      "Table Results",
      on_click=open_dlg,
      disabled=True,
  )

  # Logs window container
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
                  content=logs_inner_container
              ),
              ft.Container(
                  padding=30,
                  height=page.height*.80*.20,
                  width=log_window_width,
                  content=table_button
              )
          ]
      ),
      # bgcolor=ft.Colors.BLUE_GREY_600,
      bgcolor="#293241",
      border_radius=10,
      padding=10,
  )

  # Text field for user input
  txt_field = ft.TextField(
      border_color="#087FFE",
      hint_text="Ask me anything...",
      expand=True,
      on_submit=lambda e: send_message(e),
  )

  # Send button
  send_button = ft.IconButton(
      icon=ft.Icons("send"),
      icon_color="#087FFE",
      tooltip="Send",
      on_click=lambda e: send_message(e),
  )

  # Helper text
  helper_text = ft.Text(
      "Enter your message and press Enter or click the send icon.",
      size=12,
      color=ft.Colors.GREY_500,
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
                              ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                              helper_text,
                          ],
                      ),
                  ),
                  ft.VerticalDivider(width=1, color=ft.Colors.GREY_600),
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
    chat_history.controls.append(ChatBubble(user_message, page, True))
    txt_field.value = ""
    page.update()

    # Get response, details and big query result
    response, details, bq_response = vertexai_conversation(user_message)
    response = response.replace("\\n", "\n")
    page.update()
    # If there is a table result, format it for a flet data table and show it in the dialog
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

    # If there are any errors, show a error text to the user.
    if details is None:
      details = ["Error", "Error"]
    # Chatbot response is rendered in a gray bubble with proper markdown formatting

    chat_history.controls.append(ChatBubble(response, page, False))

    # Logic to display the logs of what was performed in the back end
    logs = []
    logs_inner_container.controls.clear()
    table_button.disabled = False
    for num, item in enumerate(details):
      if num == 0:
        logs.append(ft.Text("Logs", size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD))
      logs.append(ft.Text(f"Iteration Number {num+1}", size=12, color=ft.Colors.WHITE))
      logs.append(ft.Text(item, size=12, color=ft.Colors.GREEN_300, selectable=True))

    logs_inner_container.controls = logs

    page.update()

ft.app(target=main, port=8000, host="0.0.0.0", view=ft.WEB_BROWSER)