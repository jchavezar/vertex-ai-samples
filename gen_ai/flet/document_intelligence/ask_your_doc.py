import os
import time
import vertexai
import asyncio
import pandas as pd
from utils import preprocess
from utils.temp import *
# import utils.database as vector_database
import scann
from flet import *
import numpy as np
from vertexai.language_models import TextEmbeddingModel
from vertexai.generative_models import GenerativeModel
from vertexai.preview.generative_models import HarmCategory, HarmBlockThreshold

# Workaround to upload key required

os.environ["FLET_SECRET_KEY"] = "dummy"

# Conversational Bot Defintion.
files_dir = "myuploads"
conversational_bot_model = "gemini-1.0-pro-002"
embeddings_model = "textembedding-gecko@001"

project_id = "vtxdemos"
region = "us-central1"

# variables = {
#     "project_id": "vtxdemos",
#     "project": "vtxdemos",
#     "region": "us-central1",
#     "instance_name": "pg15-pgvector-demo",
#     "database_user": "emb-admin",
#     "database_name": "ask_your_doc_tax_lang",
#     "database_password": DB,
#     "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
#     "location": "us",
# }

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
    "temperature": 0,
    "top_p": 0.4,
    "top_k": 32,
}
conversational_safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
}

# Large Language Models Initialization
vertexai.init(project=project_id, location=region)
conversational_model = GenerativeModel(conversational_bot_model, system_instruction=[system_prompt])
bot_chat = conversational_model.start_chat(response_validation=False)
model_emb = TextEmbeddingModel.from_pretrained(embeddings_model)

# Cloud SQL (pggvector) Database Initialization
# vector_database_client = vector_database.Client(variables)

# Document Preprocessing to fetch documents offline / Refer to manual_doc_preprocess.py
df = pd.read_pickle("tax_vdb_latest.pkl")

# Main function for the front end, Flet (flutter) is being used. -> https://flet.dev/
def main(page: Page):
    buttons_color = "#F5EFF7"
    buttons_text_color = "#6750A4"
    border_color = "#45474a"
    light_primary = colors.BLUE_300
    background_color = colors.WHITE
    prog_bars: Dict[str, ProgressRing] = {}
    files = Ref[Row]()
    upload_button = Ref[ElevatedButton]()

    # Function to upload a file.
    def file_picker_result(e: FilePickerResultEvent):
        upload_button.current.disabled = True if e.files is None else False
        prog_bars.clear()
        files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
                prog_bars[f.name] = prog
                files.current.controls.append(Row([prog, Text(f.name, color=colors.BLACK)]))
        page.update()

    def on_upload_progress(e: FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress
        prog_bars[e.file_name].update()

    file_picker = FilePicker(on_result=file_picker_result, on_upload=on_upload_progress)

    def upload_files(e):
        global cashed_documents
        global stream_df
        global searcher
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
                searcher, docs = preprocess.run(files_dir + "/" + f.name, page)

                for i in docs:
                    page.controls[0].content.controls[4].content.content.controls.append(
                        Column(
                            controls=[
                                Text("Text:", color=colors.BLACK),
                                Markdown(
                                    i,
                                    extension_set="gitHubWeb",
                                )
                            ]
                        )
                    )
                stream_df = pd.read_pickle("realtime_table.pkl")
                cashed_documents = False
                page.controls[0].content.controls[4].update()

    # hide dialog in a overlay
    page.overlay.append(file_picker)

    # LogBar is the container with the Document Extraction and Vector Query Result childs.
    page.bgcolor = background_color
    LogBar = Container(
        width=0,
        content=Container(
            margin=50,
            width=200,
            bgcolor=colors.GREY_500,
            content=ListView(
                auto_scroll=True
            )
        )
    )

    # Function "folding" to show document extraction and vector database response during a query.
    def folding(e):
        if LogBar.width != 2048:
            # HeaderRow
            page.controls[0].content.controls[1].border = border.only(
                left=border.BorderSide(1, colors.BLACK),
                right=border.BorderSide(1, colors.BLACK),
                top=border.BorderSide(1, colors.BLACK)
            )
            LogBar.bgcolor = colors.GREY_500
            # LogBar.opacity = 0.2
            LogBar.width = 2048
            LogBar.margin = 10
            LogBar.content.width = 1024
            LogBar.content.bgcolor = "transparent"
            LogBar.update()
        else:
            page.controls[0].content.controls[1].border = border.only(
                left=border.BorderSide(1, border_color),
                right=border.BorderSide(1, border_color),
                top=border.BorderSide(1, border_color)
            )
            LogBar.bgcolor = ""
            LogBar.width = 0
            LogBar.update()

    # Time widget to calculate the response time.
    TimerFunction = Column(
        alignment=alignment.center,
        controls=[
            Text("Response Time:", color=colors.GREY_900, weight=FontWeight.BOLD, size=16),
            Text("", color=colors.WHITE, bgcolor="#B388FF", weight=FontWeight.BOLD, size=30)
        ]
    )

    # Dropdown to select the preprocessed document.
    drop_down: Dropdown = Dropdown(
        value="1040.pdf",
        bgcolor=colors.WHITE,
        color=colors.BLACK,
        width=150,
        options=[
            dropdown.Option("1040.pdf"),
            dropdown.Option("1065.pdf"),
            dropdown.Option("1120.pdf"),
            dropdown.Option("5471.pdf"),
            dropdown.Option("k1_565.pdf"),
            dropdown.Option("All")
        ]
    )

    # Submit button for RAG in Memory using ScaNN -> https://github.com/google-research/google-research/tree/master/scann
    def doc_internal_rag(e):
        global cashed_documents
        global filtered_df
        global searcher
        if drop_down.value != "All":
            filtered_df = df.copy()
            filtered_df = filtered_df[filtered_df["filename"] == drop_down.value]
            filtered_df = filtered_df.reset_index(drop=True)
            print("3"*80)
            img = np.array([r["embeddings"] for i, r in filtered_df.iterrows()])
            k = int(np.sqrt(df.shape[0]))
            searcher = scann.scann_ops_pybind.builder(img, num_neighbors=3, distance_measure="squared_l2").tree(
                num_leaves=k, num_leaves_to_search=1, training_sample_size=filtered_df.shape[0]).score_ah(
                2, anisotropic_quantization_threshold=0.2).reorder(7).build()
        else:
            filded_df = df.copy()
            img = np.array([r["embeddings"] for i, r in filtered_df.iterrows()])
            k = int(np.sqrt(df.shape[0]))
            searcher = scann.scann_ops_pybind.builder(img, num_neighbors=3, distance_measure="squared_l2").tree(
                num_leaves=k, num_leaves_to_search=int(int(k/20)), training_sample_size=filtered_df.shape[0]).score_ah(
                2, anisotropic_quantization_threshold=0.2).reorder(7).build()
            cashed_documents = True

    submit_button: ElevatedButton = ElevatedButton(
        # color="#FFFFFF",
        # bgcolor="#6200EE",
        color=buttons_text_color,
        bgcolor=buttons_color,
        text="submit",
        on_click=doc_internal_rag
    )

    # Header of the website
    FirstRowContents = Container(
        height=150,
        bgcolor=background_color,
        border=border.only(
            left=border.BorderSide(1, border_color),
            right=border.BorderSide(1, border_color),
            top=border.BorderSide(1, border_color)
        ),
        # Icons / Inserts
        content=Row(
            controls=[
                Container(
                    alignment=alignment.center,
                    padding=padding.only(left=30),
                    expand=True,
                    content=Row(
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            ElevatedButton(
                                "Select files...",
                                # color="#FFFFFF",
                                # bgcolor="#6200EE",
                                color=buttons_text_color,
                                bgcolor=buttons_color,
                                icon=icons.FOLDER_OPEN,
                                on_click=lambda _: file_picker.pick_files(allow_multiple=True),
                            ),
                            ElevatedButton(
                                "Upload",
                                # color="#FFFFFF",
                                # bgcolor="#6200EE",
                                color=buttons_text_color,
                                bgcolor=buttons_color,
                                ref=upload_button,
                                icon=icons.UPLOAD,
                                on_click=upload_files,
                                disabled=True,
                            ),
                            Row(ref=files),
                        ]
                    )
                ),
                Container(
                    padding=padding.only(top=30),
                    alignment=alignment.center,
                    expand=True,
                    content=TimerFunction
                ),
                # Right side of the second row.
                Container(
                    alignment=alignment.center,
                    expand=True,
                    content=Container(
                        padding=padding.only(left=15),
                        alignment=alignment.center,
                        content=Row(
                            spacing=30,
                            controls=[
                                Text("Select a file:", color=colors.GREY_900),
                                drop_down,
                                submit_button,
                            ]
                        )
                    )
                ),
            ]
        )
    )

    # Chatbot Display Container
    def send_message(e):
        q = e.control.value
        start_time = time.time()
        query = model_emb.get_embeddings([q])[0].values
        print(cashed_documents)
        if cashed_documents:
            context = ""
            if "filtered_df" in globals():
                neighbors, distances = searcher.search(query, final_num_neighbors=10)
                vdb_df = filtered_df.loc[neighbors, :]
                context = ""
                for index, row in vdb_df.iterrows():
                    head = "\n\n" + "###"*80 + "\n\n"
                    sch = f"Page Number: {row['page_number']}, " \
                          f"Chunk Number: {row['chunk_number']} "  \
                          f"Extraction Duration Time: {row['extraction_time_in_seconds']} " \
                          f"Filename: {row['filename']}\n\n"
                    text = row["page_text"]
                    context += head + sch + text + "###"*80 + "\n\n"
                LogBar.content.content.controls.append(
                    Column(
                        width=600,
                        controls=[

                            Text("vdb response:", color=colors.BLUE, bgcolor=colors.BLACK),
                            Container(
                                content=Markdown(
                                    context,
                                    code_style=TextStyle(color=colors.BLACK)
                                )
                            )
                        ]
                    )
                )
                LogBar.content.content.update()
            else:
                context = ""
        else:
            neighbors, distances = searcher.search(query)
            stream_df["distance"] = 100.0
            stream_df.loc[neighbors, "distance"] = distances.astype(float)

            context = ""
            for index, row in stream_df.loc[neighbors, :].iterrows():
                context += "##Page Number: {page}\n##Content:\n{content}".format(page=row["page"], content=row["page_text"])
                context += "\n\n" + "#"*80 + "\n\n"
            # Keep stored in a CloudSQL pgvector [optional]
            #context = asyncio.run(vector_database_client.query(query, rag_schema))
            LogBar.content.content.controls.append(
                Column(
                    width=600,
                    controls=[

                        Text("vdb response:", color=colors.BLUE, bgcolor=colors.BLACK),
                        Container(content=Text(context, color=colors.BLACK))
                    ]
                )
            )
            LogBar.content.content.update()
        response_time = time.time() - start_time
        TimerFunction.controls[1].value = "{:.2f} sec".format(response_time)
        TimerFunction.update()

        def animate_text_output(name: str, prompt: str) -> None:
            if name == "User":
                bg_color = "#E0E0E0"
                al_color = "#212121"
                txt_color = "#212121"
            else:
                bg_color = "#757575"
                al_color = "#FFFFFF"
                txt_color = "FFFFFF"
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
                        padding=padding.only(left=15, right=15, top=4, bottom=4),
                        margin=margin.only(left=20, right=10, top=2, bottom=2),
                        border_radius=12,
                        content=Text("", color=txt_color, selectable=True),
                        bgcolor=bg_color
                    ),
                    Divider(color=colors.TRANSPARENT)
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
                    [f"Context:\n{context}\n\nUser Question:\n{q}\n\nResponse:"],
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
                margin=15,
                expand=True,
                border=border.all(1, "#1D1B20"),
                border_radius=5,
                content=ListView(
                    auto_scroll=True
                ),
            ),
            # Right Side Panel is for additional chatbot options
            Container(
                bgcolor="#F5EFF7",
                margin=15,
                height=50,
                border=border.all(1, "#1D1B20"),
                border_radius=15,
                content=TextField(
                    hint_style=TextStyle(color="#6750A4"),
                    hint_text="Type Something",
                    border_color="transparent",
                    selection_color="#ECE6F0",
                    color="#49454F",
                    on_submit=send_message
                )
            )
        ]
    )

    # Main Container for the Chat Space
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
                        left=border.BorderSide(1, border_color),
                        right=border.BorderSide(1, border_color),
                        top=border.BorderSide(1, border_color)
                    ),
                    content=ChatSpace,
                ),
                # RightSide
                Container(
                    width=300,
                    bgcolor=background_color,
                    border=border.only(
                        right=border.BorderSide(1, border_color),
                        top=border.BorderSide(1, border_color),
                    ),
                    content=Container(
                        margin=20,
                        content=Column(
                            controls=[
                                Text("Processing Logs", bgcolor=colors.GREY_50, color=colors.BLACK)
                            ]
                        )
                    )
                )
            ]
        )
    )

    EndRow = Container(
        height=60,
        bgcolor=background_color,
        border=border.all(1, border_color)
    )

    # MainLayout (All Frames)
    MainLayout = Container(
        bgcolor=background_color,
        expand=True,
        content=Row(
            spacing=0,
            expand=True,
            controls=[
                # SideBar
                Container(
                    height=1024,
                    bgcolor="yellow",
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
                        Container(
                            margin=0,
                            alignment=alignment.center,
                            height=60,
                            width=60,
                            bgcolor=buttons_text_color,
                            border_radius=30,
                            #border=border.all(1, colors.PURPLE),
                            animate=800,
                            content=Text("logs"),
                            shadow=BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color=colors.BLUE_GREY_300,
                                offset=Offset(0, 0),
                                blur_style=ShadowBlurStyle.OUTER,
                            ),
                            on_click=folding
                        ),
                    ]
                ),
                LogBar
            ]

        )
    )

    # Login Format
    page.title = "SignIn"
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 400
    page.window_resizable = True

    # Login Input
    text_user: TextField = TextField(label="Username", text_align=TextAlign.CENTER, color=colors.BLACK, width=200)
    password: TextField = TextField(label="Password", text_align=TextAlign.CENTER, color=colors.BLACK, width=200, password=True)
    button_submit: ElevatedButton = ElevatedButton(text="Sing In", width=200, disabled=True, bgcolor=colors.BLUE_100)

    def validate(e: ControlEvent) -> None:
        if text_user.value and password.value == "C":
            button_submit.disabled = False
        else:
            button_submit.disabled = True
        page.update()

    def submit(e: ControlEvent) -> None:
        page.clean()
        page.title = "Ask Your Doc"
        page.window_width = 2048
        page.window_height = 1024
        page.window_resizable = True
        page.add(MainLayout)

    text_user.on_change = validate
    password.on_change = validate
    button_signin: ElevatedButton = ElevatedButton(
        text="Sign In",
        width=200,
        # color="#FFFFFF",
        # bgcolor="#625B71",
        on_click=submit

    )

    # Adding all the childs to the session.
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

app(target=main, view=AppView.WEB_BROWSER, port=8000, upload_dir=files_dir)

