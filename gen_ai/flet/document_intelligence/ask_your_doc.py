import base64
import time
from flet import *
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.generative_models import HarmCategory, HarmBlockThreshold

project_id = "vtxdemos"
model = GenerativeModel("gemini-1.5-pro-preview-0409")

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0,
    "top_p": 0.95,
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
}

def main(page: Page):
    page.bgcolor = colors.WHITE
    page.window_center = True
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.title = "Gemini"
    page.update()

    global_width = 600
    file_path: Text = Text("", color=colors.BLUE_200, text_align=TextAlign.CENTER, style=TextStyle(weight="bold"))
    time_lat: Text = Text("", color=colors.WHITE, bgcolor="#1a3059")

    def select_file(e: FilePickerResultEvent):
        page.add(filepicker)
        filepicker.pick_files("Select file...")

    def return_file(e: FilePickerResultEvent):
        global file_path_int
        if e.files:
            headerBox.content.controls[1].value = e.files[0].name
            file_path_int = e.files[0].path
            file_path.update()
        else:
            headerBox.content.controls[1].value = "Canceled!"
            file_path.update()

    def animate_text_output(name: str, prompt: str) -> None:
        if name == "User":
            bg_color = "#282a2d"
            al_color = "#212121"
            txt_color = "#e2e2e5"
        else:
            bg_color = "#1a3059"
            al_color = "#212121"
            txt_color = "#e2e2e5"
        word_list: list = []
        msg = Column(
            spacing=0,
            controls=[
                Container(
                    padding=padding.only(left=10, right=5, top=5, bottom=0),
                    margin=margin.only(left=10, right=10, top=5, bottom=0),
                    bgcolor=colors.TRANSPARENT,
                    content=Text(name, color=al_color, size=15, weight=FontWeight.BOLD)
                ),
                Container(
                    padding=padding.only(left=15, right=15, top=4, bottom=1),
                    margin=margin.only(left=20, right=10, top=2, bottom=0),
                    border_radius=12,
                    content=Text("", color=txt_color, selectable=True),
                    bgcolor=bg_color
                ),
                Divider(color=colors.TRANSPARENT)
            ]
        )
        listView.controls.append(msg)

        for word in list(prompt):
            word_list.append(word)
            msg.controls[1].content.value = "".join(word_list)
            listView.update()
            time.sleep(0.008)

    def send_message(e):

        prompt = f"""
            You are a tax expert, so your response needs to be acurate, consistent and brief 
            when possible.
            
            User Query:
            {e.control.value}
            
            Response:
            """

        animate_text_output("User", e.control.value)
        try:
            with open(file_path_int, 'rb') as f:
                text = base64.b64encode(f.read())

            document1 = Part.from_data(
                    mime_type="application/pdf",
                    data=base64.b64decode(text))
            prompt_list = [prompt, document1]
        except:
            prompt_list = [prompt]

        start = time.time()
        response = model.generate_content(
            prompt_list,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

        try:
            animate_text_output("Gemini", response.text)
            time_lat.value = "Response time: {:.2f} seconds".format(time.time() - start)
            time_lat.update()
        except:
            listView.controls.append(Text("Error, try again", color=colors.RED))
            listView.update()

    filepicker = FilePicker(on_result=return_file)

    headerBox: Container = Container(
        height=100,
        border_radius=4,
        border=border.all(1, colors.GREY),
        bgcolor=colors.GREY_100,
        width=global_width,
        content=Row(
            alignment=MainAxisAlignment.CENTER,
            controls=[
                ElevatedButton("Upload", on_click=select_file),
                file_path,
                time_lat
            ]
        )
    )

    listView: ListView = ListView(
        auto_scroll=True
    )

    displayMessage: Container = Container(
        height=600,
        width=global_width,
        border_radius=4,
        border=border.all(1, colors.GREY),
        bgcolor=colors.WHITE,
        content=listView,
    )

    textInput: Container = Container(
        width=global_width,
        border_radius=4,
        border=border.all(1, colors.GREY),
        content=TextField(
            hint_text="Write something here",
            hint_style=TextStyle(color=colors.GREY_700),
            color=colors.BLACK,
            border_color=colors.GREY,
            border_radius=4,
            on_submit=send_message,
        )
    )

    logosBar: Container = Container(
        height=100,
        width=global_width,
        border_radius=4,
        border=border.all(1, colors.GREY),
        content=Row(
            alignment = MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Image("https://storage.googleapis.com/vtxdemos_images/deloitte_logo.png", scale=0.5),
                Image("https://storage.googleapis.com/vtxdemos_images/gcp.png", scale=0.5)
            ]
        )
    )

    mainLayout: Column = Column(
        controls=[
            logosBar,
            headerBox,
            displayMessage,
            textInput
        ]
    )

    page.add(mainLayout)

app(target=main)