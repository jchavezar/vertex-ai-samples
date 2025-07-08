
import flet as ft
import flet_video as fv
from backend import find_most_similar, generate_chat_response
import time
from urllib.parse import urlparse, parse_qs, quote_plus
from google import genai
from google.genai import types


def main(page: ft.Page):
    page.title = "Semantic Video Search"
    page.theme_mode = ft.ThemeMode.DARK

    def perform_search(query, results_view, progress_bar):
        if not query:
            return

        progress_bar.visible = True
        results_view.controls.clear()
        page.update()

        search_results = find_most_similar(query, top_n=6)
        time.sleep(1)

        progress_bar.visible = False

        if not search_results:
            results_view.controls.append(
                ft.Text("No matching video moments found.", size=16, color="white54")
            )
        else:
            for result in search_results:
                video_uri = result['video_gcs_uri']
                summary = result['summary_text']
                encoded_summary = quote_plus(summary)

                thumbnail_card = ft.Card(
                    elevation=4,
                    content=ft.Container(
                        width=280,
                        height=280,
                        on_click=lambda _, v=video_uri, s=encoded_summary, offset=result['start_offset_sec']: page.go(f"/watch?video_uri={v}&summary_text={s}&start_offset={offset}"),
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
                                        result['video_title'],
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

    def route_change(route):
        page.views.clear()

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
                                icon=ft.Icons.SEARCH,
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

        if page.route.startswith("/watch"):
            query_params = parse_qs(urlparse(page.route).query)
            video_uri = query_params.get("video_uri", [None])[0]
            summary_text = query_params.get("summary_text", [""])[0]
            start_offset = float(query_params.get("start_offset", [0.0])[0])

            if not video_uri:
                page.go("/")
                return

            def play_from_offset_click(e):
                if start_offset > 0:
                    player.seek(int(start_offset * 1000))
                player.play()

            player = fv.Video(
                playlist=[fv.VideoMedia(resource=video_uri)],
                autoplay=False,
            )

            chat_history_view = ft.ListView(expand=True, spacing=10, auto_scroll=True)
            new_message_field = ft.TextField(hint_text="Ask a question...", expand=True)

            def send_message_click(e):
                user_question = new_message_field.value
                if not user_question:
                    return
                new_message_field.value = ""
                chat_history_view.controls.append(ft.Text(f"You: {user_question}", weight=ft.FontWeight.BOLD))
                chat_history_view.controls.append(ft.Text("Assistant: Thinking...", selectable=True))
                page.update()
                response = generate_chat_response(video_uri, user_question, chat_history_view, page)
                if "Error" in response:
                    if chat_history_view.controls:
                        chat_history_view.controls[-1].value = response
                        chat_history_view.controls[-1].color = "red"
                    else:
                        chat_history_view.controls.append(ft.Text(response, color="red"))
                else:
                    assistant_response = chat_history_view.controls[-1]
                    assistant_response.value = "Assistant: "
                    page.update()

                    assistant_response.value = f"Assistant: {response}"
                page.update()

            new_message_field.on_submit = send_message_click

            play_from_offset_button = ft.ElevatedButton(
                "Play from relevant moment",
                icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                on_click=play_from_offset_click,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color="white",
                    bgcolor="purple700"
                )
            )

            content_column = ft.Column(
                [
                    ft.Container(
                        content=player,
                        aspect_ratio=16 / 9,
                        bgcolor="black",
                        alignment=ft.alignment.center
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=30),
                        content=ft.Text(
                            f'"{summary_text}"',
                            italic=True,
                            size=16,
                            color="white70",
                            text_align=ft.TextAlign.CENTER
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        padding=20,
                        content=ft.Column(
                            [
                                ft.Row([
                                    ft.Text("Chat about this video", size=20, weight=ft.FontWeight.BOLD),
                                    play_from_offset_button
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Container(content=chat_history_view, expand=True,
                                             border=ft.border.all(1, "#444444"), border_radius=8, padding=10),
                                ft.Row(
                                    [
                                        new_message_field,
                                        ft.IconButton(icon=ft.Icons.SEND, on_click=send_message_click,
                                                      tooltip="Send message"),
                                    ]
                                )
                            ],
                            expand=True,
                        )
                    )
                ],
                expand=True,
                spacing=20,
            )

            back_button = ft.ElevatedButton(
                "Go Back",
                icon="arrow_back",
                on_click=lambda _: page.go("/"),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color="white",
                    bgcolor="black45"
                ),
                top=20,
                left=20,
            )

            page.views.append(
                ft.View(
                    route=page.route,
                    padding=0,
                    bgcolor="#141218",
                    controls=[
                        ft.Stack(
                            [
                                content_column,
                                back_button,
                            ],
                            expand=True,
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
