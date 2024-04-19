#%%
import flet as ft


# %%
def main(page: ft.Page):
    main_container = ft.Container(
        width=500,
        height=500,
        bgcolor='red',
        content=ft.Column(
            controls=[ft.Text("testing")]
        )
    )
    
    page.add(main_container)

ft.app(target=main, view=ft.WEB_BROWSER)
    
    