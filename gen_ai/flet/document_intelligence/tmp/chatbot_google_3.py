import flet as ft

    
def main(page: ft.Page):
    
    def MainContent():
        return ft.Container(
            width = 420,
            height = 500,
            bgcolor = "#141518",
            content = ft.ListView(
                expand = True,
                height = 200,
                spacing = 15,
                auto_scroll = True
        ))
        
    def Prompt():
        return ft.TextField(
            width = 420,
            border_color = "white"
        )
        
    def dropdown_changed(e):
        t.value = e.control.value
        print(t.value)
        page.update()
        
    def DropDown():
        
        dd = ft.Dropdown(
            on_change = dropdown_changed,
            options = [
                ft.dropdown.Option("red"),
                ft.dropdown.Option("blue")
                ]
            )
        
        print(dd.value)
        
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
        
    
    t = ft.Text()
    
    page.add(
        ft.Text("Google Generative AI", size=28, weight="w800"),
        ft.Row([MainContent(), DropDown()[0]]), 
        ft.Divider(height=6, color="transparent"),
        Prompt(),
        #Prompt(model = parameters.value),
        t
        )
    
    print(DropDown()[1].value)
    
    page.update()

ft.app(target=main)