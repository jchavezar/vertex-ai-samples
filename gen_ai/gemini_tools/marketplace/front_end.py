import vertexai
from flet import *
from google.cloud import bigquery
from vertexai.language_models import TextEmbeddingModel
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

project_id = "vtxdemos"
model_name = "gemini-1.5-flash-002"
emb_model_name = "text-embedding-004"


class Gemini:
    def __init__(self):
        self.project = project_id
        self.model_name = model_name
        self.model = GenerativeModel(
            model_name=self.model_name,
        )

        vertexai.init(project=self.project, location="us-central1")
        self.chat = self.model.start_chat()


class GoogleCloud(Gemini):
    def __init__(self):
        super().__init__()
        bq_client = bigquery.Client(project=self.project)
        model = TextEmbeddingModel.from_pretrained(emb_model_name)


gemini = Gemini()


class InfoWidget(ResponsiveRow):
    def __init__(self, page: Page):
        super().__init__()
        self.image_container = Container(
            content=Image(
                page.session.data["link"],
                fit=ImageFit.CONTAIN
            )
        )
        # Main Left Content
        self.left = Container(
            height=page.height * .80,
            width=page.width * .50,
            col={"sm": 6, "md": 6, "xl": 6},
            content=Column(
                scroll=ScrollMode.ALWAYS,
                controls=[
                    self.image_container
                ]
            )
        )
        self.title = Text(value="Fairy Dance Bag")
        self.price = Text(value="$8.00")
        self.materials = Text(value="Polyester")
        self.description = Text(
            value="This personalized pink fairies drawstring bag is the perfect choice for kids who love dance, ballet, or simply need a stylish and practical bag for their games. It's made from high-quality polyester and features a vibrant design with 100s of options available to choose from. You can personalize it with a name or initials, making it a unique and special gift. The bag measures 44cm x 36.4cm and is equipped with a drawstring closure for easy access. It's ideal for carrying essentials like shoes, clothes, and toys.")
        self.text_input = Container(
            expand=True,
            content=TextField(
                hint_text="Looking for specific info? Ask Chatsy!",
                hint_style=TextStyle(size=14),
                multiline=True,
                min_lines=1,
                max_lines=10,
                shift_enter=True,
                on_submit=self.execute
            )
        )
        self.chatbot_window = Container(
            padding=padding.only(left=15, right=15),
            width=page.width * .50,
            content=Row(
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    Container(
                        height=30,
                        width=30,
                        content=Image(src="https://gcpetsy.sonrobots.net/artifacts/etsymate.png", fit=ImageFit.CONTAIN),
                    ),
                    self.text_input,
                    IconButton(
                        icon=icons.SEND,
                        icon_color=colors.DEEP_ORANGE_400,
                        on_click=self.execute
                    )
                ]
            )
        )

        self.response = Text()

        self.chatbot_response = Container(
            padding=15,
            border=border.all(1, color=colors.DEEP_ORANGE_400),
            border_radius=14,
            width=page.width * .50,
            content=Column(
                alignment=MainAxisAlignment.START,
                spacing=5,
                controls=[
                    Text("Chatsy: ", style=TextStyle(color=colors.DEEP_ORANGE_400, weight=FontWeight.BOLD)),
                    self.response
                ]
            )
        )
        # Main Right Content
        self.right = Container(
            height=page.height * .80,
            width=page.width * .50,
            col={"sm": 6, "md": 6, "xl": 6},
            padding=14.0,
            content=Column(
                scroll=ScrollMode.ALWAYS,
                alignment=MainAxisAlignment.START,
                spacing=20,
                controls=[
                    self.title,
                    self.price,
                    self.description,
                    self.chatbot_window,
                    self.chatbot_response
                ]
            )
        )
        self.controls = [
            self.left,
            self.right,
        ]

    def execute(self, e):
        re = gemini.chat.send_message(e.control.value).text
        self.response.value = re
        self.left.content.controls.append(
            Text(
                spans=[
                    TextSpan("User: ", style=TextStyle(color=colors.BLUE, weight=FontWeight.BOLD)),
                    TextSpan(e.control.value)
                ]
            )
        )
        self.left.content.controls.append(
            Text(
                spans=[
                    TextSpan("Chatsy: ", style=TextStyle(color=colors.DEEP_ORANGE_400, weight=FontWeight.BOLD)),
                    TextSpan(re)
                ]
            )
        )
        self.update()


class SearchPageWidget(Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.alignment = alignment.center
        self.margin = margin.only(top=30)
        self.text_input = Container(
            width=page.width * 0.50,
            padding=10,
            border=border.all(0.5, color=colors.GREY_400),
            border_radius=30,
            content=TextField(
                prefix_icon=icons.SEARCH,
                height=28,
                text_size=12,
                text_vertical_align=VerticalAlignment.START,
                content_padding=10,
                border_color=colors.TRANSPARENT,
                data=1,
                on_submit=self.search,
                #on_change=textbox_changed
            ),
            #on_hover=shadow
        )
        self.content = Column(
            horizontal_alignment=CrossAxisAlignment.CENTER,
            controls=[
                self.text_input
            ]
        )

    def search(self, e):
        self.page.session.data = {"link": "https://gcpetsy.sonrobots.net/etsy-10k/il_570xN.3685682282_c6cy.jpg"}
        self.page.go("/info_widget")


def main(page: Page):
    """

    :type page: flet control
    """
    page.window.bgcolor = colors.WHITE
    page.bgcolor = colors.WHITE

    def route_change(route):
        page.views.clear()
        page.views.append(
            View(
                "/",
                [SearchPageWidget(page)]
            )
        )
        if page.route == "/info_widget":
            page.views.append(
                View(
                    "/info_widget",
                    bgcolor=colors.WHITE,
                    controls=[
                        InfoWidget(page),
                        BottomAppBar(
                            bgcolor=colors.TRANSPARENT,
                            content=Row(
                                alignment=MainAxisAlignment.START,
                                controls=[
                                    IconButton(
                                        icon=icons.ARROW_BACK_IOS_NEW,
                                        icon_color=colors.DEEP_ORANGE_400,
                                        on_click=lambda _: page.go("/")
                                    )
                                ]
                            )
                        )
                    ],
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


app(target=main)
