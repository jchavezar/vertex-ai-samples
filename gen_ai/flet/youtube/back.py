import flet as ft
from local_gemini import run

def main(page: ft.Page):
  page.title = "Black Chat Window"
  page.theme_mode = ft.ThemeMode.DARK  # Set dark theme

  txt_ref = ft.Ref[ft.Text]()

  # Chat messages container
  chat_history = ft.ListView(
      auto_scroll=True,  # Enable scrolling for long chats
      expand=True,
      spacing=10,
  )

  # Message input field and send button
  message_input = ft.TextField(
      hint_text="Type a message...",
      expand=True,
      on_submit=lambda e: send_message(e),  # Call send_message on Enter
  )
  send_button = ft.ElevatedButton("Send", on_click=lambda _: send_message(None))

  # Function to add messages to the chat
  def send_message(e):
    text = message_input.value
    print(text)
    text, time = run(text)
    print(text)
    if text:
      chat_history.controls.append(
          ft.Text(
              text,
              color=ft.colors.WHITE,  # Set message text to white
          )
      )
      message_input.value = ""
      txt_ref.current.value = time
      page.update()

  page.add(
      ft.Container(
          height=300,
          expand=True,
          content=chat_history,
          bgcolor=ft.colors.BLACK,  # Set container background to black
          padding=10,
          border_radius=10,  # Optional rounded corners
      ),
      ft.Text("", ref=txt_ref),
      ft.Row(
          controls=[
              message_input,
              send_button,
          ],
      ),
  )

ft.app(target=main)
