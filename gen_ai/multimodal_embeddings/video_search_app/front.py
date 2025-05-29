import flet as ft
import flet_video as fv
from backend import find_most_similar
import time
from urllib.parse import urlparse, parse_qs

def main(page: ft.Page):
    page.title = "Semantic Video Search"
    page.theme_mode = ft.ThemeMode.DARK

    # --- Main Application Logic ---
    def perform_search(query, results_view, progress_bar):
        if not query:
            return

        progress_bar.visible = True
        results_view.controls.clear()
        page.update()

        search_results = find_most_similar(query, top_n=3)
        time.sleep(1)

        progress_bar.visible = False

        if not search_results:
            results_view.controls.append(
                ft.Text("No matching video moments found.", size=16, color="white54")
            )
        else:
            for result in search_results:
                thumbnail_card = ft.Card(
                    elevation=4,
                    content=ft.Container(
                        width=280,
                        height=280,
                        on_click=lambda e: page.go(f"/watch?video_uri={e.control.data}"),
                        data=result['video_gcs_uri'],
                        content=ft.Stack([
                            ft.Image(src=result['thumbnail_gcs_uri'], fit=ft.ImageFit.COVER),
                            ft.Container(
                                padding=10,
                                gradient=ft.LinearGradient(
                                    begin=ft.alignment.top_center,
                                    end=ft.alignment.bottom_center,
                                    colors=["transparent", "black"],
                                ),
                                content=ft.Column([
                                    ft.Container(expand=True),
                                    ft.Text(
                                        result['summary_text'],
                                        weight=ft.FontWeight.BOLD,
                                        size=14,
                                        max_lines=3,
                                        overflow=ft.TextOverflow.ELLIPSIS
                                    ),
                                ])
                            )
                        ]),
                        border_radius=ft.border_radius.all(8),
                    )
                )
                results_view.controls.append(thumbnail_card)
        page.update()


    # --- Router: Builds the UI based on the current URL ---
    def route_change(route):
        page.views.clear()

        # Search View (/)
        if page.route == "/":
            search_field = ft.TextField(
                hint_text="Search for a video moment...",
                expand=True,
                height=50,
                border_color="#444444",
                focused_border_color="purple400",
                border_radius=8,
                on_submit=lambda e: perform_search(e.control.value, results_view, progress_bar)
            )
            progress_bar = ft.ProgressBar(visible=False, color="purple400", bgcolor="#222222")
            results_view = ft.GridView(
                expand=True,
                runs_count=5,
                max_extent=300,
                child_aspect_ratio=1.0,
                spacing=20,
                run_spacing=20,
            )

            page.views.append(
                ft.View(
                    route="/",
                    padding=25,
                    bgcolor="#141218",
                    controls=[
                        ft.Row([
                            search_field,
                            ft.IconButton(
                                icon=ft.icons.SEARCH,
                                on_click=lambda e: perform_search(search_field.value, results_view, progress_bar),
                                icon_size=30,
                                tooltip="Search"
                            )
                        ]),
                        progress_bar,
                        results_view
                    ]
                )
            )

        # Watch View (/watch?video_uri=...)
        if page.route.startswith("/watch"):
            query_params = parse_qs(urlparse(page.route).query)
            video_uri = query_params.get("video_uri", [None])[0]

            if not video_uri:
                # Fallback if URL is malformed
                page.go("/")
                return

            player = fv.Video(
                expand=True,
                playlist=[fv.VideoMedia(resource=video_uri)],
                autoplay=True,
            )

            page.views.append(
                ft.View(
                    route=page.route,
                    padding=0,
                    bgcolor="black",
                    controls=[
                        player,
                        ft.ElevatedButton(
                            "Go Back",
                            icon="arrow_back",
                            on_click=lambda _: page.go("/"),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=5),
                                color="white",
                                bgcolor="black"
                            ),
                            top=15,
                            left=15,
                        )
                    ]
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)