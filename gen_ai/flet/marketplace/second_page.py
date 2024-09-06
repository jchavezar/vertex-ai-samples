from flet import *

def view(page):
  return View(
      "/second",
      [
          Text("Welcome to the Second Page!"),
          ElevatedButton("Back to First Page", on_click=lambda _: page.go("/"))
      ]
  )