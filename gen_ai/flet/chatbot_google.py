import time
import vertexai
import flet as ft
from vertexai.language_models import TextGenerationModel
from vertexai.preview.generative_models import GenerativeModel, Part

vertexai.init(project="vtxdemos", location="us-central1")
bison_parameters = {
    "candidate_count": 1,
    "max_output_tokens": 1024,
    "temperature": 0.9,
    "top_p": 1
}

models_d = {
    "Gemini Pro": "gemini-pro",
    "Text Bison 2": "text-bison@002",
    "Text Bison 2 (32k)": "text-bison-32k@002"
}

models_l = [k for k,v in models_d.items()]

def main_style() -> dict:
    return {
      "width": 420,
      "height": 500,
      "bgcolor": "#141518",
      "border_radius": 10,
      "padding": 15   
    }

class MainContentArea(ft.Container):
    def __init__(self) -> None:
        super().__init__(**main_style())
        self.chat = ft.ListView(
            expand=True,
            height=200,
            spacing=15,
            auto_scroll=True,
        )
        
        self.content = self.chat

class CreateMessage(ft.Column):
    def __init__(self, name: str, message: str) -> None:
        self.name: str = name
        self.message: str = message
        self.text = ft.Text(self.message)
        super().__init__(spacing=4)
        self.controls = [ft.Text(self.name, opacity=0.6), self.text]

def main(page: ft.Page):

    # Set your API keys and model names (adjust as needed)
    main_chat = MainContentArea()
    chat = main_chat.chat

    # Create dropdown for LLM selection
    llm_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option(models_l[0]),
            ft.dropdown.Option(models_l[1]),
            ft.dropdown.Option(models_l[2])
            ],
        width=200,
        hint_text="LLM Options",
    )
    
    parameters = ft.Column(
        [
            ft.Text("Select a Model:"),
            llm_dropdown
        ]
    )

    # Function to send user input to LLM and update response
    def send_message(message):
        
        def animate_text_output(name: str, prompt: str) -> None:
            word_list: list = []
            msg = CreateMessage(name, "")
            chat.controls.append(msg)
        
            for word in list(prompt):
                word_list.append(word)
                msg.text.value = "".join(word_list)
                chat.update()
                time.sleep(0.008)
        
        animate_text_output("Me", message.control.value)
        
        if models_d[llm_dropdown.value] == "gemini-pro":
            model = GenerativeModel(models_d[llm_dropdown.value])
            responses = model.generate_content(
                    message.control.value,
                    generation_config={
                        "max_output_tokens": 2048,
                        "temperature": 0.9,
                        "top_p": 1
                        },
                        #stream=True,
                )
            r = responses.candidates[0].content.parts[0].text
        
        elif models_d[llm_dropdown.value] == "text-bison@002":
            model = TextGenerationModel.from_pretrained("text-bison@002")
            response = model.predict(
                message.control.value,
                **bison_parameters)
            r = response.text
        
        animate_text_output(llm_dropdown.value, r)

    # Create text input for user messages
    user_input = ft.TextField(
        width = 420,
        border_color = "white",
        cursor_color = "white",
        label = "Type your message here...",
        on_submit = send_message)

    # Add controls to the page
    page.add(
        ft.Row(controls=[main_chat,parameters]),
        user_input,
        )
    
    # Run the app

ft.app(target=main)


