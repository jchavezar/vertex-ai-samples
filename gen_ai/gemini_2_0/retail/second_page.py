from flet import *

def view(page):
  return View(
      "/second",
      [
          Text("Welcome to the Second Page!"),
          Row(
              alignment=MainAxisAlignment.CENTER,
              controls=[
                  Container(
                      height=550,
                      content=Image(src="https://gcpetsy.sonrobots.net/artifacts/et_diagram.png", fit=ImageFit.CONTAIN)
                  ),
              ]
          ),
          ElevatedButton("Back to First Page", on_click=lambda _: page.go("/"))
      ]
  )