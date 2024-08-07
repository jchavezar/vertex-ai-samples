import requests
from back_end import document_extraction, document_intelligent_refactor, \
  conversation
import flet as ft


def main(page: ft.Page):
  page.title = "Gemini Chatbot"
  page.vertical_alignment = ft.MainAxisAlignment.CENTER
  status_bar: ft.Text = ft.Text("Ready", size=14, color="black")
  page.session.context = ""
  messages = ft.ListView(
      expand=True,
      spacing=10,
      padding=20)

  def send_message(e):
    user_message = user_input.value
    messages.controls.append(
        ft.Row(
            [
                ft.Container(
                    content=ft.Text(f"You: {user_message}", size=14,
                                    color="black"),
                    padding=10,
                    border_radius=ft.border_radius.all(20),
                    expand=True,
                    width=400
                ),
                ft.Icon(name=ft.icons.ACCOUNT_CIRCLE, color="grey"),
            ],
            alignment=ft.MainAxisAlignment.END,
        )
    )
    user_input.value = ""
    user_input.focus()
    messages.update()

    # Send user message to the Flask server
    data = conversation(user_message, page.session.context)

    # Display chatbot response in the chat window
    messages.controls.append(
        ft.Row(
            [
                ft.Icon(name=ft.icons.ACCOUNT_CIRCLE, color="grey"),
                ft.Container(
                    content=ft.Text(f"Chatbot: {data}", size=14, color="black"),
                    padding=10,
                    border_radius=ft.border_radius.all(20),
                    bgcolor=ft.colors.GREY_50,
                    # Lighter indigo for chatbot bubble
                    expand=True,
                    width=400
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        )
    )

    # Scroll to the latest message
    messages.page.scroll = "auto"

    messages.update()

  def upload_file(e):
    file_picker.pick_files(allow_multiple=False)

  def on_file_picker_result(e):
    # global context
    if file_picker.result:
      file = file_picker.result.files[0]
      status_bar.value = "Reading your file with Document AI, please wait..."
      docai.border = ft.border.all(1, "green")
      docai.update()
      status_bar.update()
      document_ocr = document_extraction(file.path)
      document.controls[0].border = ft.border.all(1, "green")
      document.update()
      ocr.controls[0].border = ft.border.all(1, "green")
      ocr.update()
      status_bar.value = "Reading your file with Document AI, Done!"
      status_bar.update()
      status_bar.value = "Using Gemini Please wait..."
      status_bar.update()
      re = document_intelligent_refactor(document_ocr)
      page.session.context = re
      gemini.border = ft.border.all(1, "green")
      gemini.update()
      messages.controls.append(
          ft.Row(
              [
                  ft.Icon(name=ft.icons.ACCOUNT_CIRCLE, color="grey"),
                  ft.Text(f"Extraction: {re}", size=14, color="black"),
              ],
              alignment=ft.MainAxisAlignment.END,
          )
      )
      status_bar.value = "Done!"
      messages.update()
      status_bar.update()

      # Scroll to the latest message
      messages.page.scroll = "auto"

  user_input = ft.TextField(
      hint_text="Type your message here...",
      on_submit=send_message,
      expand=True,
  )

  file_picker = ft.FilePicker(on_result=on_file_picker_result)

  document: ft.Row = ft. Row(
      alignment=ft.MainAxisAlignment.CENTER,
      controls=[
          ft.Container(
              height=60,
              width=60,
              alignment=ft.alignment.center,
              border_radius=ft.border_radius.all(12.0),
              border=ft.border.all(1, ft.colors.GREY),
              content=ft.Text("pdf", size=14, color="black")
          ),
      ]
  )

  ocr: ft.Row = ft. Row(
      alignment=ft.MainAxisAlignment.CENTER,
      controls=[
          ft.Container(
              height=60,
              width=60,
              alignment=ft.alignment.center,
              border_radius=ft.border_radius.all(12.0),
              border=ft.border.all(1, ft.colors.GREY),
              content=ft.Text("ocrt", size=14, color="black")
          ),
      ]
  )

  docai: ft.Container = ft.Container(
      height=120,
      width=120,
      alignment=ft.alignment.center,
      border_radius=ft.border_radius.all(12.0),
      border=ft.border.all(1, ft.colors.GREY),
      content=ft.Text("DocumentAI", size=14, color="black")
  )

  gemini: ft.Container = ft.Container(
      height=120,
      width=120,
      alignment=ft.alignment.center,
      border_radius=ft.border_radius.all(12.0),
      border=ft.border.all(1, ft.colors.GREY),
      content=ft.Text("Gemini", size=14, color="black")
  )

  tracking_bar: ft.Container = ft.Container(
      alignment=ft.alignment.center,
      width=200,
      border_radius=ft.border_radius.all(12.0),
      border=ft.border.all(1, ft.colors.GREY),
      content=ft.Column(
          expand=True,
          alignment=ft.MainAxisAlignment.SPACE_EVENLY,
          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
          controls=[
              document,
              docai,
              ocr,
              gemini,
          ],
      )
  )

  page.add(
      ft.AppBar(
          title=ft.Text("Gemini Chatbot"),
          center_title=True),
      ft.Column(
          controls=
          [
              ft.Container(
                  expand=True,
                  padding=10,
                  border_radius=12.0,
                  border=ft.border.all(1, ft.colors.GREY),
                  content=ft.Row(
                      controls=[
                          messages,
                          tracking_bar
                      ]
                  ),
              ),
              ft.Row(
                  [
                      status_bar,
                  ],
                  alignment=ft.MainAxisAlignment.CENTER,
              ),
              ft.Container(
                  border=ft.border.all(1, ft.colors.GREY),
                  border_radius=12,
                  content=ft.Row(
                      [
                          user_input,
                          ft.IconButton(icon=ft.icons.SEND,
                                        on_click=send_message),
                          ft.ElevatedButton(on_click=upload_file,
                                            content=ft.Icon(
                                                ft.icons.ATTACH_FILE)),
                      ]
                  ),
                  padding=10,
              ),
          ],
          expand=True,
      ),
      file_picker,
  )


ft.app(target=main)
