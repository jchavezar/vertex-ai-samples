import flet as ft
import first_page
import second_page

def main(page: ft.Page):
  page.title = "Multi-Page Flet App"
  page.window.height = 700

  def route_change(route):
    page.update()
    page.views.clear()
    page.views.append(first_page.view(page))
    if page.route == "/second":
      page.views.append(second_page.view(page))
    page.update()

  def view_pop(view):
    page.views.pop()
    top_view = page.views[-1]
    page.go(top_view.route)

  page.on_route_change = route_change
  page.on_view_pop = view_pop
  page.go(page.route)

ft.app(target=main)