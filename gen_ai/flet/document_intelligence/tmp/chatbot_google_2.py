import flet as ft

class MainContent(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.test = ""
    
    def build(self):
        self.view = ft.Container(
            width = 420,
            height = 500,
            bgcolor = "#141518",
            content = ft.ListView(
                expand = True,
                height = 200,
                spacing = 15,
                auto_scroll = True
        ))
        return self.view

class Parameters(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.value = ""

    def on_change(self, e):
        print(e.control.value)
        self.value = e.control.value
    
    def build(self):
        
        self.dd =  ft.Dropdown(
                    on_change = self.on_change,
                    width = 180,
                    options = [
                        ft.dropdown.Option("Gemini Pro"),
                        ft.dropdown.Option("Text Bison")
                        ]
                )
    
        return ft.Container(
            alignment = ft.alignment.top_center, 
            margin = 2,
            width = 200,
            height = 500,
            bgcolor = "#141518",
            content = ft.Column([
                ft.Text("Model:", size=20),
                self.dd
            ])
        )
    
class Prompt(ft.UserControl):
    def __init__(self, model: str):
        super().__init__()
        self.model = model
        print(model)
        
    def run_prompt(self, e):
        print(self.model)
    
    def build(self):
        self.prompt = ft.TextField(
            on_submit=self.run_prompt,
            width = 420,
            border_color = "white"
        )
        return self.prompt
    
def main(page: ft.Page):
    parameters = Parameters()
    page.update()
    print(parameters.controls)

    page.add(
        ft.Text("Google Generative AI", size=28, weight="w800"),
        ft.Row([MainContent(), parameters]), 
        ft.Divider(height=6, color="transparent"),
        Prompt(model = parameters.value),
        )
    
    print(parameters.value)

ft.app(target=main)