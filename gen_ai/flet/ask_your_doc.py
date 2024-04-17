import os
import time
import vertexai
import asyncio
from utils import preprocess
from utils.temp import *
import utils.database as vector_database
from flet import *
from vertexai.language_models import TextEmbeddingModel
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.generative_models import HarmCategory, HarmBlockThreshold

project_id = "vtxdemos"
location = "us-central1"
files_dir = "myuploads"
BC = "#45474a"
TEAL = colors.TEAL
BLACK = colors.BLACK
HEIGHT = 280
rag_schema = ""
system_prompt = f"""
            You like to be natural and act like a human, keep a conversational experience with the following 
            elements:
            - Use <User Query> as user questions/asks, etc. 
            - Use <Context> as your source of truth.
            - If you get the answer from the <Context> explain which part did you find it.
            - If someone say by and close the conversation just return an empty string.
            """
conversational_generation_config = {
    "max_output_tokens": 2048,
    "temperature": 0.4,
    "top_p": 0.4,
    "top_k": 32,
}
conversational_safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
}

variables = {
    "project_id": "vtxdemos",
    "project": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_name": "ask_your_doc_tax_lang",
    "database_password": DB,
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us",
}

vertexai.init(project=project_id, location=location)
conversational_model = GenerativeModel("gemini-1.0-pro-002", system_instruction=[system_prompt])
bot_chat = conversational_model.start_chat(response_validation=False)
model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
vector_database_client = vector_database.Client(variables)

class UploadButton(Container):
    def __init__(self, text, icon, page):
        super(UploadButton, self).__init__()
        self.page = page
        self.mypick = FilePicker(on_result=self.upload_file)
        #self.page.overlay.append(self.mypick)
        self.bgcolor = "transparent"
        self.content = ElevatedButton(
            bgcolor=colors.TEAL,
            style=ButtonStyle(
                shape=RoundedRectangleBorder(radius=10)
            ),
            icon=icon,
            text=text,
            color="white",
            on_hover=self.on_hover,
            on_click=lambda x: self.mypick.pick_files()
        )

    def build(self):
        self.page.overlay.append(self.mypick)


    def upload_file(self, e):
        upload_list = []
        if e.files is not None:
            for f in self.mypick.result.files:
                upload_list.append(
                    FilePickerUploadFile(
                        f.name,
                        upload_url=self.page.get_upload_url(f.name, 600)
                    )
                )
            self.pick.upload(upload_list)
            for f in self.mypick.result.files:
                rag, docs = preprocess.run(f.path, self.page)
                global rag_schema
                rag_schema = rag
                for i in docs:
                    self.page.controls[0].content.controls[4].content.content.controls.append(
                        Column(
                            controls=[
                                Text("Text:", color=BLACK),
                                Markdown(
                                    i,
                                    extension_set="gitHubWeb",
                                )
                            ]
                        )
                    )
                self.page.controls[0].content.controls[4].update()
            else:
                pass

    def on_hover(self, e):
        e.control.border = border.all(1, "blue") if e.data == "true" else border.all(1, "black")
        e.control.update()

def main(page: Page):
    background_color = colors.WHITE
    prog_bars: Dict[str, ProgressRing] = {}
    files = Ref[Column]()
    upload_button = Ref[ElevatedButton]()

    def file_picker_result(e: FilePickerResultEvent):
        upload_button.current.disabled = True if e.files is None else False
        prog_bars.clear()
        files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
                prog_bars[f.name] = prog
                files.current.controls.append(Row([prog, Text(f.name, color=BLACK)]))
        page.update()

    def on_upload_progress(e: FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress
        prog_bars[e.file_name].update()

    file_picker = FilePicker(on_result=file_picker_result, on_upload=on_upload_progress)

    def upload_files(e):
        uf = []
        if file_picker.result is not None and file_picker.result.files is not None:
            for f in file_picker.result.files:
                uf.append(
                    FilePickerUploadFile(
                        f.name,
                        upload_url=page.get_upload_url(f.name, 600),
                    )
                )
            file_picker.upload(uf)
            for f in file_picker.result.files:
                rag, docs = preprocess.run(files_dir+"/"+f.name, page)
                global rag_schema
                rag_schema = rag
                for i in docs:
                    page.controls[0].content.controls[4].content.content.controls.append(
                        Column(
                            controls=[
                                Text("Text:", color=BLACK),
                                Markdown(
                                    i,
                                    extension_set="gitHubWeb",
                                )
                            ]
                        )
                    )
                page.controls[0].content.controls[4].update()

    # hide dialog in a overlay
    page.overlay.append(file_picker)

    # chat = ChatClass()
    # page.fonts = {
    #     "Roboto Mono": "RobotoMono-VariableFont_wght.ttf",
    # }
    # page.update()
    page.bgcolor = background_color
    #page.window_frameless = True
    LogBar = Container(
        width=0,
        content=Container(
            margin=50,
            width=200,
            bgcolor=colors.TEAL_50,
            content=ListView(
                auto_scroll=True
            )
        )
    )

    def folding(e):
        if LogBar.width != 2048:
            # HeaderRow
            page.controls[0].content.controls[1].border = border.only(
                left=border.BorderSide(1, BLACK),
                right=border.BorderSide(1, BLACK),
                top=border.BorderSide(1, BLACK)
            )
            LogBar.bgcolor = colors.TEAL_50
            # LogBar.opacity = 0.2
            LogBar.width = 2048
            LogBar.margin = 10
            # LogBar.border = border.only(
            #     right=border.BorderSide(1, TEAL),
            #     top=border.BorderSide(1, TEAL),
            #     bottom=border.BorderSide(1, TEAL)
            # )
            # LogBar.content.margin = 10
            LogBar.content.width = 1024
            LogBar.content.bgcolor = "transparent"
            LogBar.update()
        else:
            page.controls[0].content.controls[1].border = border.only(
                left=border.BorderSide(1, BC),
                right=border.BorderSide(1, BC),
                top=border.BorderSide(1, BC)
            )
            LogBar.bgcolor = ""
            LogBar.width = 0

            # LogBar.border = border.only(
            #     right=border.BorderSide(1, "black"),
            #     top=border.BorderSide(1, "black"),
            #     bottom=border.BorderSide(1, "black")
            # )
            LogBar.update()

    HeaderRowContents = Container(
        height=70,
        width=2048,
        bgcolor="black",
        border=border.only(
            left=border.BorderSide(1, BC),
            right=border.BorderSide(1, BC),
            top=border.BorderSide(1, BC)
        ),
        alignment=alignment.center,
        content=Text("Demos!"),
    )

    TimerFunction = Row(
        alignment=alignment.center,
        controls=[
            Text("Response Time:", color=BC),
            Text("", color=colors.GREEN)

        ]
    )

    FirstRowContents = Container(
        height=250,
        bgcolor=background_color,
        border=border.only(
            left=border.BorderSide(1, BC),
            right=border.BorderSide(1, BC),
            top=border.BorderSide(1, BC)
        ),
        # Icons / Inserts
        content=Row(
            controls=[
                Container(
                    padding=padding.only(left=30),
                    expand=True,
                    content=Column(
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            ElevatedButton(
                                "Select files...",
                                color=colors.WHITE,
                                bgcolor=colors.TEAL,
                                icon=icons.FOLDER_OPEN,
                                on_click=lambda _: file_picker.pick_files(allow_multiple=True),
                            ),
                            Column(ref=files),
                            ElevatedButton(
                                "Upload",
                                color=colors.WHITE,
                                bgcolor=colors.TEAL,
                                ref=upload_button,
                                icon=icons.UPLOAD,
                                on_click=upload_files,
                                disabled=True,
                            ),
                        ]
                    )
                ),
                Container(
                    expand=True
                ),
                # Right side of the second row.
                Container(
                    expand=True,
                    content=Row(
                        controls=[
                            TimerFunction,
                            ElevatedButton(
                                text="Clear Session",
                                color=colors.WHITE,
                                bgcolor=colors.RED_400,
                                icon=icons.REFRESH,
                                on_click=lambda e: page.session.clear()
                            )
                        ]
                    )
                )
            ]
        )
    )

    def send_message(e):
        q = e.control.value
        start_time = time.time()
        query = model_emb.get_embeddings([q])[0].values
        if rag_schema == "":
            context = ""
        else:
            context = asyncio.run(vector_database_client.query(query, rag_schema))
            page.controls[0].content.controls[4].content.content.controls.append(
                Column(
                    width=600,
                    controls=[

                        Text("vdb response:", color=colors.BLUE, bgcolor=BLACK),
                        Container(content=Text(context, color=BLACK))
                    ]
                )
            )
            page.controls[0].content.controls[4].content.content.update()
        response_time = time.time() - start_time
        TimerFunction.controls[1].value = "{:.2f} sec".format(response_time)
        FirstRowContents.content.controls[2].update()



        def animate_text_output(name: str, prompt: str) -> None:
            if name == "User":
                #bg_color = "#282a2d"
                bg_color = colors.BLUE_GREY
                al_color = colors.BLACK
            else:
                # bg_color = "#1a3059"
                bg_color = colors.TEAL
                al_color = colors.PINK
            word_list: list = []
            msg = Column(
                controls=[
                    Container(
                        margin=20,
                        bgcolor=colors.TRANSPARENT,
                        content=Text(name, color=al_color, size=15)
                    ),
                    Container(
                        padding=padding.only(
                            left=12,
                            right=12,
                            top=8,
                            bottom=8,
                        ),
                        border_radius=12,
                        content=Text("", color=colors.WHITE, selectable=True),
                        bgcolor=bg_color
                    ),
                    Text("", color="white")
                ]
            )
            ChatSpace.controls[0].content.controls.append(msg)

            for word in list(prompt):
                word_list.append(word)
                msg.controls[1].content.value = "".join(word_list)
                ChatSpace.controls[0].content.update()
                time.sleep(0.008)
            ChatSpace.controls[1].content.value = ""
            ChatSpace.controls[1].content.update()
        animate_text_output("User", q)

        start_time = time.time()
        if context:
            llm_response = bot_chat.send_message(
                [f"<Context>:\n{context}\n\nUser Question:\n{q}\n\nResponse:"],
                generation_config=conversational_generation_config,
                safety_settings=conversational_safety_settings,
            ).text

        else:
            llm_response = bot_chat.send_message(
                [f"User Question:\n{q}\n\nResponse:"],
                generation_config=conversational_generation_config,
                safety_settings=conversational_safety_settings,
            ).text
        response_time = time.time() - start_time
        TimerFunction.controls[1].value = "{:.2f} sec".format(response_time)
        FirstRowContents.content.controls[2].update()
        animate_text_output("Gemini", llm_response)

    ChatSpace = Column(
        expand=True,
        controls=[
            # ListView is where all the message will be displayed.
            Container(
                #bgcolor="#1a1c1e",
                # bgcolor=colors.TEAL_50,
                # opacity=0.4,
                expand=True,
                border=border.all(1,BC),
                border_radius=5,
                content=ListView(
                    auto_scroll=True
                ),
            ),
            # Right Side Panel is for additional chatbot options
            Container(
                margin=15,
                height=50,
                border=border.all(1, BC),
                border_radius=15,
                content=TextField(
                    hint_style=TextStyle(color=TEAL),
                    hint_text="Type Something",
                    border_color="transparent",
                    selection_color="black",
                    color="black",
                    on_submit=send_message
                )
            )
        ]
    )

    SecondRowContents = Container(
        bgcolor=background_color,
        expand=True,
        width=3000,
        content=Row(
            spacing=0,
            controls=[
                # LeftSide
                Container(
                    alignment=alignment.center,
                    padding=padding.only(left=20, right=20, top=30, bottom=10),
                    expand=True,
                    bgcolor=background_color,
                    border=border.only(
                        left=border.BorderSide(1, BC),
                        right=border.BorderSide(1, BC),
                        top=border.BorderSide(1, BC)
                    ),
                    content=ChatSpace,
                ),
                # RightSide
                Container(
                    width=300,
                    bgcolor=background_color,
                    border=border.only(
                        right=border.BorderSide(1, BC),
                        top=border.BorderSide(1, BC),
                    ),
                    content=Container(
                        margin=20,
                        content=Column()
                    )
                )
            ]
        )
    )

    EndRow = Container(
        height=60,
        bgcolor=background_color,
        border=border.all(1, BC)
    )

    # MainLayout (All Frames)
    MainLayout = Container(
        bgcolor=background_color,
        border=border.all(1, BLACK),
        expand=True,
        content=Row(
            spacing=0,
            expand=True,
            controls=[
                # SideBar
                Container(
                    #width=256,
                    height=1024,
                    bgcolor="yellow",
                    # bgcolor="blue"
                ),
                # ChatBar
                Container(
                    expand=True,
                    content=Column(
                        spacing=0,
                        controls=[
                            FirstRowContents,
                            SecondRowContents,
                            EndRow
                        ]
                    )
                ),
                # EmptySpace,
                VerticalDivider(width=20, color=colors.TRANSPARENT),
                # LogBarWidget Dynamic.
                Row(
                    controls=[
                        # Container(
                        #     bgcolor=colors.YELLOW
                        # ),
                        Container(
                            height=HEIGHT*0.35,
                            width=6,
                            bgcolor=colors.TEAL,
                            border_radius=30,
                            border=border.all(1, colors.TEAL),
                            animate=800,
                            content=None,
                            on_click=folding
                        ),
                    ]
                ),
                LogBar
            ]

        )
    )

    page.title = "SignIn"
    page.vertical_alignment = MainAxisAlignment.CENTER
    #page.them = ThemeMode.DARK
    page.window_width = 400
    page.window_height = 400
    page.window_resizable = True

    text_user: TextField = TextField(label="Username", text_align=TextAlign.CENTER, color="black", width=200)
    password: TextField = TextField(label="Password", text_align=TextAlign.CENTER, color="black", width=200, password=True)
    button_submit: ElevatedButton = ElevatedButton(text="Sing In", width=200, disabled=True, bgcolor=colors.BLUE_100)

    def validate(e: ControlEvent) -> None:
        if text_user.value and password.value == "Chavez":
            button_submit.disabled = False
        else:
            button_submit.disabled = True
        page.update()

    def submit(e: ControlEvent) -> None:
        page.clean()
        page.add(MainLayout)

    text_user.on_change = validate
    password.on_change = validate
    button_signin: ElevatedButton = ElevatedButton(
        text="Sign In",
        width=200,
#        color=colors.WHITE,
        bgcolor=colors.BLUE,
        on_click=submit

    )
    button_submit.on_click = submit

    page.add(
        Row(
            controls=[
                Column(
                    controls=[
                        text_user,
                        password,
                        button_signin
                    ]
                )
            ],
            spacing=20,
            alignment=MainAxisAlignment.CENTER
        )
    )

app(target=main, view=AppView.WEB_BROWSER, port=8080, upload_dir=files_dir)

