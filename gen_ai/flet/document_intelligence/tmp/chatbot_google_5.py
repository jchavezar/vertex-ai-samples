import flet as ft

def prompt_style() -> dict:
    return {
        "width": 420,
        "height": 40,
        "border_color": "white",
        "content_padding": 10,
        "cursor_color": "white"
    }

class DropDown(ft.Container):
    model = ft.Text()
    
    def __init__(self):
        super().__init__()
        self.alignment = ft.alignment.top_center
        self.margin = 2
        self.width = 200
        self.height = 500
        self.bgcolor = "#141518"
        
        pass
        
        def dropdown_changed(e):
            self.model.value = str(e.control.value)
            print(self.model)
            self.model.update()
        
        dd = ft.Dropdown(
            on_change = dropdown_changed,
            options = [
                ft.dropdown.Option("red"),
                ft.dropdown.Option("blue")
            ]
        )
        
        self.content = ft.Column(
            [dd, self.model]
        )
        
        if self.model != "":
            print("alright")
        
class Prompt(ft.TextField):
    def __init__(self, model):
        super().__init__(**prompt_style(), on_submit=self.run_prompt)
        self.model = model
        print("")
        print(self.model)
    def run_prompt(self, e):
        print("--")
        print(self.model)
        print(e.control.value)
        
        
def main(page: ft.Page):
    
    drop = DropDown()
    page.add(
        drop,
        Prompt(model=drop.model.value)
        )

if __name__ == "__main__":
    ft.app(target=main)