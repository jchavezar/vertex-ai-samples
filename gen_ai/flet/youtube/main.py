import flet as ft
from local_gemini import run


def main(page: ft.Page):
  page.title = "Chat Bot"
  page.padding = 10

  def send_message(e):  # Add the 'e' argument
    """
    :param e:
    """
    user_message = message_input.value
    print(e.control.value)
    print(user_message)
    if user_message:
      chat_messages.controls.append(
          ft.Row(
              [
                  ft.Container(
                      content=ft.Text(user_message, text_align="right", no_wrap=False,
                              style=ft.TextStyle(color=ft.colors.WHITE)),
                      bgcolor=ft.colors.BLUE,
                      padding=10,
                      border_radius=10,
                  ),

              ],
              alignment=ft.MainAxisAlignment.END,
          )
      )
      page.update()
      re, time = run(user_message)
      response_time.value = time
      message_input.value = ""
      get_bot_response(re.strip())

  chat_messages = ft.ListView(auto_scroll=True, expand=True, spacing=10, item_extent=20)
  message_input = ft.TextField(hint_text="Type a message...", expand=True,
                               on_submit=send_message)
  send_button = ft.IconButton(icon=ft.icons.SEND, on_click=send_message)

  response_time: ft.Text = ft.Text("")
  header: ft.Container = ft.Container(
      height=100,
      padding=10,
      border=ft.border.all(1, ft.colors.GREY),
      border_radius=10,
      content=ft.Row(
          controls=[
              ft.Text("Response Time: ",
                      style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=16)),
              response_time
          ]
      )
  )

  page.add(
      header,
      chat_messages,
      ft.Row([message_input, send_button]),
  )

  def get_bot_response(user_message):
    """
    :param user_message:
    """
    # Bot response (replace with your actual logic)
    bot_response = f"Gemini: {user_message}"

    # Bot message styling
    chat_messages.controls.append(
        ft.Row(
            [
                ft.Container(
                    width=400,
                    content=ft.Container(
                        ft.Text(bot_response,),
                        bgcolor=ft.colors.BLUE_GREY_100,
                        padding=10,
                        border_radius=10,
                    )
                ),

            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        )
    )
    page.update()

  page.update()


ft.app(target=main)
