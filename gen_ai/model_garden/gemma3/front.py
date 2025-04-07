import json
from flet import *
from back import generate_content, conversational_bot

def build_invoice_view(extraction):
    return ListView(controls=[Text(extraction)], expand=True, spacing=8, auto_scroll=True)

def main(page: Page):
    page.title = "Invoice Extractor"
    page.window_width = 800
    page.window_height = 700
    page.window_resizable = True

    page.vertical_alignment = MainAxisAlignment.SPACE_BETWEEN
    page.horizontal_alignment = CrossAxisAlignment.STRETCH

    chat_display_area = ListView(expand=True, spacing=10, auto_scroll=True)

    def pick_files_result(e: FilePickerResultEvent):
        print("Selected files:", e.files)
        gemini.content = Column([ProgressRing()], alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, expand=True)
        gemini.visible = True
        chat_display_area.controls.clear()
        chat_display_area.controls.append(Text("Processing invoice...", italic=True, color=Colors.GREY))
        page.update()

        if e.files:
            f = e.files[0]
            new_invoice_content = None
            try:
                response_string = generate_content(f.path)
                print(response_string)
                page.session.set("document", response_string)
                print("API Response String received")
                print("Parsed Data successfully")
                new_invoice_content = build_invoice_view(response_string)
                chat_display_area.controls.clear()
                chat_display_area.controls.append(Text("Document loaded. Ask me anything!", weight=FontWeight.BOLD))

            except json.JSONDecodeError as json_err:
                print(f"Error parsing JSON response: {json_err}")
                error_message = f"Error: Could not parse the response data.\n{json_err}"
                new_invoice_content = Text(error_message, color=Colors.RED, selectable=True)
                chat_display_area.controls.clear()
                chat_display_area.controls.append(Text(error_message, color=Colors.RED))
                if page.session.contains_key("document"):
                    page.session.remove("document")

            except Exception as ex:
                print(f"Error processing file or building view: {ex}")
                error_message = f"Error: {ex}"
                new_invoice_content = Text(error_message, color=Colors.RED, selectable=True)
                chat_display_area.controls.clear()
                chat_display_area.controls.append(Text(error_message, color=Colors.RED))
                if page.session.contains_key("document"):
                    page.session.remove("document")

            gemini.content = new_invoice_content

        else:
            print("No files selected.")
            gemini.visible = False
            gemini.content = None
            chat_display_area.controls.clear()
            chat_display_area.controls.append(Text("Upload an invoice PDF to begin.", italic=True, color=Colors.GREY))
            if page.session.contains_key("document"):
                page.session.remove("document")

        page.update()

    pick_files_dialog = FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)

    def pick_files(e):
        pick_files_dialog.pick_files(
            allow_multiple=False,
            allowed_extensions=["pdf"]
        )

    def send_message_click(e):
        user_input = txt_input_field.value
        if not user_input:
            return

        txt_input_field.value = ""
        chat_display_area.controls.append(Text(f"You: {user_input}"))
        page.update()

        response_text = "Thinking..."
        thinking_message = Text(f"Bot: {response_text}", italic=True, color=Colors.GREY)
        chat_display_area.update()
        # re=conversational_bot(prompt=user_input)
        chat_display_area.controls.append(thinking_message)
        page.update()

        try:
            if page.session.contains_key('document'):
                document_data = page.session.get('document')
                print(document_data)
                response_text = conversational_bot(prompt=user_input, history=document_data)
            else:
                response_text = conversational_bot(prompt=user_input)

            thinking_message.value = f"Bot: {response_text}"
            thinking_message.italic = False
            thinking_message.color = None
        except Exception as bot_ex:
            print(f"Error calling conversational_bot: {bot_ex}")
            thinking_message.value = f"Bot: Error getting response - {bot_ex}"
            thinking_message.italic = False
            thinking_message.color = Colors.RED

        page.update()

    header = Container(
        alignment=alignment.center,
        height=60,
        margin=margin.only(left=10, right=10, top=10),
        border=border.all(0.4, Colors.GREY_50),
        border_radius=12.0,
        content=Text("Invoice Extractor & Chat", color=Colors.CYAN, size=20, weight=FontWeight.BOLD)
    )

    gemini = Container(
        expand=2,
        margin=10,
        padding=10,
        border=border.all(0.4, Colors.GREY_50),
        border_radius=12.0,
        visible=False,
        clip_behavior=ClipBehavior.ANTI_ALIAS,
        alignment=alignment.top_left,
        content=Column(
            [Text("Upload an invoice PDF using the button below.")],
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.START
        )
    )

    chat_container = Container(
        expand=1,
        margin=10,
        padding=10,
        border=border.all(0.4, Colors.GREY_50),
        border_radius=12.0,
        content=chat_display_area,
        alignment=alignment.top_left
    )

    body = Container(
        expand=True,
        content=Row(
            controls=[
                gemini,
                chat_container,
            ],
            vertical_alignment=CrossAxisAlignment.START,
            expand=True,
        )
    )

    txt_input_field = TextField(
        label="Ask something about the invoice...",
        border_color=Colors.GREY,
        border_radius=12,
        border_width=0.3,
        expand=True,
        on_submit=send_message_click
    )

    send_button = ElevatedButton(
        "Send",
        style=ButtonStyle(bgcolor=Colors.CYAN, color=Colors.WHITE),
        on_click=send_message_click
    )

    upload_button = IconButton(
        icon=Icons.UPLOAD_FILE,
        tooltip="Upload PDF Invoice",
        on_click=pick_files
    )

    bottom = Container(
        height=60,
        margin=margin.only(left=10, right=10, bottom=10),
        padding=padding.symmetric(horizontal=10, vertical=5),
        content=Row(
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=CrossAxisAlignment.CENTER,
            controls=[
                txt_input_field,
                send_button,
                upload_button
            ]
        )
    )

    page.add(
        header,
        body,
        bottom,
    )

if __name__ == "__main__":
    app(target=main)