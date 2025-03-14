import json
import flet as ft
from google import genai
from google.genai import types
from middleware import chatbot

client = genai.Client(
    vertexai=True,
    project="vtxdemos",
    location="us-central1",
)

system_instruction = """
You are the funniest thing in the world. Be original, funny and concise.

Your goal is to:
-Answer user questions.
-After each answer, generate three unique, related questions to continue 
the conversation, 
ensuring you don't repeat any previously asked questions.

Rules:
New questions needs to be short.
Do not repeat questions

Output in JSON format with 2 keys: answer, questions (a list)
"""

def main(page: ft.Page):
  page.title = "Tron Chatbot"
  page.theme_mode = ft.ThemeMode.DARK  # For that Tron feel

  chat_history = ft.Column(scroll=ft.ScrollMode.AUTO)

  def send_message(e):
    user_message = message_text.value
    response = chatbot(user_message)
    # st_response = json.loads(response)
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

      # Placeholder for bot response - replace with your actual logic
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
                  # [ft.TextSpan(q+"\n", ft.TextStyle(color=ft.Colors.GREEN, size=18)) for q in st_response["questions"]]
              ),
              padding=ft.padding.all(10.0),
              border_radius=ft.border_radius.all(10.0),
          )
      )

      message_text.value = ""  # Clear input field
      page.update()
    else:
      print("Empty Message")

  message_text = ft.TextField(
      hint_text="Enter your message...",
      border_radius=ft.border_radius.all(10),
      expand=True,  # Makes text field take available width
      text_style=ft.TextStyle(color=ft.Colors.WHITE),
      border_color=ft.Colors.CYAN,
      focused_border_color=ft.Colors.LIGHT_BLUE,
      on_submit=send_message
  )

  send_button = ft.ElevatedButton(
      "Send", on_click=send_message,  style=ft.ButtonStyle(bgcolor=ft.Colors.CYAN)
  )

  page.add(
      ft.Row(
          alignment=ft.MainAxisAlignment.END,
          controls=[
              ft.Text(
                  "Churn Predictor",
                  color=ft.Colors.CYAN,
                  size=30,
                  weight=ft.FontWeight.BOLD
              ),
              ft.VerticalDivider(width=20)
          ]
      ),
      message_container:=ft.Container(
          content=chat_history,
          expand=True,
          padding=30,
          border=ft.border.all(2, ft.Colors.TRANSPARENT),  # Tron-like border
          border_radius=10,
      ),
      ft.Row(
          [
              message_text,
              send_button,
          ],
      ),
  )


ft.app(target=main)