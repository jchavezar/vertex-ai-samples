import flet as ft

class Flet:
    def DropDown(self):
        self.t = ft.Text()
        
        def dropdown_changed(e):
            self.t.value = e.control.value
        
        dd = ft.Dropdown(
            on_change = dropdown_changed,
            options = [
                ft.dropdown.Option("red"),
                ft.dropdown.Option("blue")
                ]            
        )
        
        return [ft.Container(
            alignment = ft.alignment.top_center, 
            margin = 2,
            width = 200,
            height = 500,
            bgcolor = "#141518",
            content = ft.Column([
                ft.Text("Model:", size=20),
                dd
            ])
        ),  dd]
    
def main(page: ft.Page):
    
    f = Flet()
    
    page.add(
        f.DropDown()[0],
        ft.Text()
    )

ft.app(target=main)