#%%
from flet import *
from google.cloud import translate

project_id = "vtxdemos"
client = translate.TranslationServiceClient()
target_language = {"Spanish": "es"}


class ChatWidget(Container):
    def __init__(self, page):
        super().__init__()
        self.height = page.height * .70
        self.width = page.width * .50
        self.border_radius = 14
        self.padding = 20
        self.border = border.all(1, colors.GREY)
        self.title = Text("Translation Tool", size=24)
        self.textfield_input = TextField(
            on_submit=self.send_message
        )
        self.text_input = Text(
            spans=[
                TextSpan(
                    "Input Language: ",
                    visible=False,
                    style=TextStyle(weight=FontWeight.BOLD, color=colors.GREEN, size=19)
                ),
                TextSpan(style=TextStyle(size=19))
            ]
        )
        self.text_translate = Text(
            visible=False,
            spans=[
                TextSpan(
                    f"Translation ({list(target_language.keys())[0]}): ",
                    style=TextStyle(weight=FontWeight.BOLD, color=colors.RED, size=19)
                ),
                TextSpan(style=TextStyle(size=19))
            ]
        )
        self.romanize = Text(
            visible=False,
            spans=[
                TextSpan(
                    f"Romanize (Japanese): ",
                    style=TextStyle(weight=FontWeight.BOLD, color=colors.BLUE, size=19)
                ),
                TextSpan(style=TextStyle(size=19))
            ]
        )
        self.content = Column(
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                self.title,
                self.text_input,
                self.romanize,
                self.text_translate,
                self.textfield_input
            ]
        )

    def send_message(self, e):
        #self.content.scroll = ScrollMode.ALWAYS
        romanize_translation = client.romanize_text(
            parent=f"projects/{project_id}",
            contents=[e.control.value]
        )

        romanize_translation_re = romanize_translation.romanizations[0].romanized_text
        print(romanize_translation_re)

        text_translation = client.translate_text(
            parent=f"projects/{project_id}",
            contents=[e.control.value],
            source_language_code="ja",
            target_language_code=target_language["Spanish"],
        )
        print("jap")
        print(text_translation)
        print("jap")

        translation_re = text_translation.translations[0].translated_text
        self.text_input.spans[0].visible = True
        self.text_input.spans[1].text = e.control.value
        self.text_translate.spans[1].text = translation_re
        self.romanize.spans[1].text = romanize_translation_re
        self.text_translate.visible = True
        self.romanize.visible = True
        self.update()


def main(page: Page):
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.add(ChatWidget(page))


app(target=main)
