import flet as ft

class DropdownContent(ft.UserControl):
    def __init__(self) -> None:
        super().__init__()
        #self.component = ft.ListView(
        #    height=200,
        #    spacing=15
        #)
        #self.col = ft.Column()
        #self.col.controls.append(ft.Text("test"))
        #self.t = ft.Text("test")
        #self.content = self.component
    
        #self.cont = ft.Container(**components_style)
    
    def build(self):
        return ft.Container(
            content = ft.Text("Testing"),
            width = 200,
            height = 500,
            bgcolor = "#141518",
            border_radius = 10,
            padding = 15   
        )
        
def main(page: ft.Page):
    page.add(DropdownContent())

ft.app(target=main)