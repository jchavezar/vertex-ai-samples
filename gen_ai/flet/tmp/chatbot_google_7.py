import time
import flet as ft
from vertexai.preview.generative_models import GenerativeModel, Part

def main_style() -> dict:
    return {
      "width": 420,
      "height": 500,
      "bgcolor": "#141518",
      "border_radius": 10,
      "padding": 15   
    }

def components_style() -> dict:
    return {
        "margin": 10,
        "width": 200,
        "height": 100,
        "bgcolor": "#141518",
        "border_radius": 10,
        "padding": 15   
    }

def dropdown_style() -> dict:
    return {
        
    }

def prompt_style() -> dict:
    return {
        "width": 420,
        "height": 40,
        "border_color": "white",
        "content_padding": 10,
        "cursor_color": "white"
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
                        

class Prompt(ft.TextField):
    def __init__(self, chat: ft.ListView):
        super().__init__(**prompt_style(), on_submit=self.run_prompt)
        self.chat = chat
        
    def animate_text_output(self, name: str, prompt: str) -> None:
        word_list: list = []
        msg = CreateMessage(name, "")
        self.chat.controls.append(msg)
        
        for word in list(prompt):
            word_list.append(word)
            msg.text.value = "".join(word_list)
            self.chat.update()
            time.sleep(0.008)
            
    def llm(self, prompt):
        
        _ = {
            "Gemini Pro" : "gemini-pro",
            "Text Bison": "text-bison@002"
        }
        

        model = GenerativeModel(_["Gemini Pro"])
        responses = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 2048,
                "temperature": 0.9,
                "top_p": 1
                },
                #stream=True,
        )

        return responses.candidates[0].content.parts[0].text

    def user_output(self, prompt):
        self.animate_text_output("Me", prompt)
        #msg = CreateMessage("Me", prompt)
        #self.chat.controls.append(msg)
        self.chat.update()
        ...
        
    def bot_output(self, prompt):
        prompt = self.llm(prompt)
        self.animate_text_output("Gemini Pro", prompt)

    def run_prompt(self, event):
        print(event.control.value)
        text = event.control.value
        
        self.user_output(prompt=text)
        ...
        
        self.bot_output(prompt=text)
        
        
def main(page: ft.Page) -> None:
    page.horizontal_aligment = "center"
    page.vertical_aligment = "center"
    page.theme_mode = "dark"
    page.update()
    
    main = MainContentArea()
    prompt = Prompt(chat=main.chat)

    page.add(
        ft.Text("Python Gemini Pro - Flet App", size=28, weight="w800"),
        ft.Row([main]),
        ft.Divider(height=6, color="transparent"),
        prompt,
        )
    
if __name__ == "__main__":
    ft.app(target=main)