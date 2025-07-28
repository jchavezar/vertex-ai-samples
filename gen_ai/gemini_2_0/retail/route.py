from flet import *
import first_page
import second_page
import search_results_page

def main(page: Page):
  page.title = "Multi-Page Flet App"
  page.window.height = 700
  page.bgcolor=colors.TRANSPARENT
  page.theme = Theme(color_scheme_seed=colors.GREY)
  page.theme_mode = ThemeMode.LIGHT
  page.update()

  def route_change(route):
    page.update()
    page.views.clear()
    page.views.append(first_page.view(page))
    if page.route == "/second":
      page.views.append(second_page.view(page))
    elif page.route == "/search_results":
      page.views.append(search_results_page.view(page))
    page.update()

  def view_pop(view):
    page.views.pop()
    top_view = page.views[-1]
    page.go(top_view.route)

  page.on_route_change = route_change
  page.on_view_pop = view_pop
  page.go(page.route)

app(target=main)