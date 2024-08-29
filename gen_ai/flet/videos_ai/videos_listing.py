from flet import *
from back_end import listing_results

results = []

videos_list: Column = Column(
    alignment=alignment.center,
    horizontal_alignment=CrossAxisAlignment.CENTER,
)

def open_link(e, url):
  e.page.launch_url(url)

for i in listing_results:
  if i["uri"] not in results:
    videos_list.controls.append(
        Column(
            alignment=MainAxisAlignment.SPACE_EVENLY,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            controls=[
                Text(i["title"].strip()),
                Text(
                    spans=[
                        TextSpan(
                            i["uri"],
                            TextStyle(decoration=TextDecoration.UNDERLINE),
                            on_click=lambda e: open_link(e, i["public_uri"].strip())
                        )
                    ]
                ),
                Divider(height=25, color=colors.TRANSPARENT)
            ]
        )
    )
    results.append(i["uri"])

listing: Column = Column(
    alignment=alignment.center,
    horizontal_alignment=CrossAxisAlignment.CENTER,
    expand=True,
    scroll="auto",
    controls=[
        Container(
            height=100,
            alignment=alignment.center,
            content=Text("Available Videos", size=26)
        ),
        Container(
            height=500,
            content=videos_list
        )
    ]
)

