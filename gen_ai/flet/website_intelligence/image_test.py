from flet import *

def main(page: Page):
 page.add(
     Text("test"),
     Container(
         height=500,
         width=500,
         content=Image("./website_intelligence.png", fit=ImageFit.CONTAIN)
     ),
     #Image("./assets/website_intelligence.png", width=200, height=200),
     # Image(src="./website_intelligence.png", fit=ImageFit.SCALE_DOWN),
     # Image(src="website_intelligence.png")
 )

app(target=main, assets_dir="assets")