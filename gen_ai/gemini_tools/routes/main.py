from flet import *
from views.routes import router
#from user_controls.app_bar import NavBar

def main(page: Page):

  #page.theme_mode = "dark"
  #page.appbar = NavBar(page)
  page.on_route_change = router.route_change
  router.page = page
  page.add(
      router.body
  )
  page.go('/logo_widget')

app(target=main, assets_dir="assets")