from flet import *
import main_page
import second_page
import third_page
import search_results_page

def main(page: Page):
  page.title = "Welcome to Esty"
  page.window.height = 700
  page.bgcolor = colors.TRANSPARENT
  page.theme = theme.Theme(color_scheme_seed=colors.GREY)
  page.theme_mode = ThemeMode.LIGHT
  page.update()

  def route_change(route):
    page.views.clear()
    page.views.append(main_page.view(page))
    if page.route == "/second":
      page.views.append(second_page.view(page))
    elif page.route == "/third":
      page.views.append(third_page.view(page))
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

app(target=main, port=8000, host="0.0.0.0")