import flet as ft
from back import custom_search, send_message

def main(page: ft.Page):
    page.title = "AP News Replica"
    page.window_width = 1200
    page.window_height = 800
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.bgcolor = ft.Colors.WHITE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    header_content_row = ft.Row(
        controls=[
            ft.Image(src="https://www.ap.org/assets/images/ap-logo.svg", width=50, height=30),
            ft.Row(
                [
                    ft.TextButton("WORLD", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                    ft.TextButton("U.S.", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                    ft.TextButton("POLITICS", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                    ft.TextButton("SPORTS", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                    ft.TextButton("ENTERTAINMENT", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                    ft.TextButton("BUSINESS", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                    ft.TextButton("SCIENCE", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                    ft.TextButton("FACT CHECK", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                    ft.TextButton("ODDITIES", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                    ft.TextButton("MORE", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                ],
                spacing=15
            ),
            ft.Row(
                [
                    ft.TextButton("Sign In", style=ft.ButtonStyle(color=ft.Colors.BLACK)),
                    ft.ElevatedButton("DONATE", style=ft.ButtonStyle(bgcolor=ft.Colors.RED_500, color=ft.Colors.WHITE)),
                ],
                spacing=10
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        width=1100,
    )

    header = ft.Container(
        content=header_content_row,
        padding=ft.padding.all(10),
        width=1100,
        bgcolor=ft.Colors.WHITE,
    )

    def on_question_submit(e, answer_container):
        question = e.control.value
        if question:
            e.control.value = ""
            e.control.disabled = True
            answer_container.content = ft.Column(
                [ft.ProgressRing(width=20, height=20)],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                height=100
            )
            answer_container.visible = True
            page.update()

            answer = send_message(question)

            answer_container.content = ft.Column(
                [ft.Text(answer, color=ft.Colors.BLACK, selectable=True)],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.START
            )
            e.control.disabled = False
            page.update()

    def on_search_change(e):
        if e.control.value:
            main_content_container.visible = False
            search_results_container.visible = True
            _search_results_column.controls = [
                ft.Text(f"Showing results for: '{e.control.value}'", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Text("Search functionality is not fully implemented yet.", size=14, color=ft.Colors.GREY_600)
            ]
        else:
            main_content_container.visible = True
            search_results_container.visible = False
            _search_results_column.controls = []
        page.update()

    def on_submit(e):
        if e.control.value:
            main_content_container.visible = False
            search_results_container.visible = True
            response_data = custom_search(e.control.value)

            result_blocks = []
            if "titles" in response_data and response_data["titles"]:
                for i in range(len(response_data["titles"])):
                    answer_container = ft.Container(
                        content=ft.Column([]),
                        width=400,
                        padding=20,
                        margin=ft.margin.only(bottom=20, right=20),
                        border_radius=ft.border_radius.all(10),
                        bgcolor="#f5f5f5",
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=5,
                            color=ft.Colors.BLACK12,
                            offset=ft.Offset(0, 3),
                        ),
                        visible=False
                    )

                    block_content = []

                    block_content.append(
                        ft.Text(
                            response_data["titles"][i],
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        )
                    )

                    if i < len(response_data["snippets"]):
                        block_content.append(
                            ft.Text(
                                response_data["snippets"][i],
                                size=13,
                                color=ft.Colors.GREY_700,
                                max_lines=3,
                                overflow=ft.TextOverflow.ELLIPSIS
                            )
                        )

                    if i < len(response_data["thumbnails"]):
                        image_with_container = ft.Container(
                            content=ft.Image(
                                src=response_data["thumbnails"][i],
                                width=400,
                                height=250,
                                fit=ft.ImageFit.COVER,
                                border_radius=ft.border_radius.all(5),
                            ),
                            width=400,
                            height=250,
                            border_radius=ft.border_radius.all(5),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                        )

                        block_content.append(
                            ft.Container(
                                content=image_with_container,
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(top=10),
                            )
                        )

                        block_content.append(
                            ft.Container(
                                content=ft.TextField(
                                    hint_text="Ask a question about this content...",
                                    hint_style=ft.TextStyle(color=ft.Colors.GREY_700),
                                    text_style=ft.TextStyle(color=ft.Colors.BLACK),
                                    width=400,
                                    content_padding=ft.padding.only(left=10, right=10),
                                    border_radius=5,
                                    border_color=ft.Colors.GREY_300,
                                    focused_border_color=ft.Colors.BLUE_ACCENT_700,
                                    height=40,
                                    text_size=14,
                                    prefix_icon=ft.Icons.QUESTION_ANSWER,
                                    on_submit=lambda e, ac=answer_container: on_question_submit(e, ac),
                                ),
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(top=10)
                            )
                        )

                    content_container = ft.Container(
                        content=ft.Column(
                            block_content,
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.START
                        ),
                        padding=20,
                        margin=ft.margin.only(bottom=20),
                        width=600,
                        border_radius=ft.border_radius.all(10),
                        bgcolor=ft.Colors.WHITE,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=5,
                            color=ft.Colors.BLACK12,
                            offset=ft.Offset(0, 3),
                        ),
                    )

                    result_row = ft.Row(
                        controls=[
                            answer_container,
                            content_container,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        spacing=20,
                    )

                    centered_result_block = ft.Container(
                        content=result_row,
                        width=400 + 600 + 20,
                    )
                    result_blocks.append(centered_result_block)

            _search_results_column.controls = result_blocks
        else:
            main_content_container.visible = True
            search_results_container.visible = False
            _search_results_column.controls = []
        page.update()

    search_bar = ft.TextField(
        hint_text="Keyword Search...",
        hint_style=ft.TextStyle(color=ft.Colors.GREY_700),
        text_style=ft.TextStyle(color=ft.Colors.BLACK),
        width=800,
        on_change=on_search_change,
        on_submit=on_submit,
        content_padding=ft.padding.only(left=10, right=10),
        border_radius=5,
        border_color=ft.Colors.GREY_300,
        focused_border_color=ft.Colors.BLUE_ACCENT_700,
        height=40,
        text_size=16,
        prefix_icon=ft.Icons.SEARCH
    )

    search_bar_container = ft.Container(
        content=search_bar,
        alignment=ft.alignment.center,
        padding=ft.padding.only(bottom=20),
        width=1100,
    )

    _search_results_column = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
    search_results_container = ft.Container(
        content=_search_results_column, visible=False, expand=True, alignment=ft.alignment.top_center
    )

    left_column_content = ft.Column(
        [
            ft.Text(
                "US-EU deal sets a 15% tariff on most goods and averts the threat of a trade war with a global shock",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK
            ),
            ft.Text("MORE COVERAGE", size=12, color=ft.Colors.GREY_600),
            ft.Column(
                [
                    ft.Text("• Rapid change except Trump’s approval numbers remain steady", size=14, color=ft.Colors.BLACK),
                    ft.Text("• Trump’s Scotland trip is built around golf", size=14, color=ft.Colors.BLACK),
                ]
            ),
            ft.Container(
                content=ft.Text("[IMAGE PLACEHOLDER]", size=14, color=ft.Colors.GREY_500),
                width=600,
                height=300,
                bgcolor=ft.Colors.GREY_200,
                alignment=ft.alignment.center,
                border_radius=5,
                padding=ft.padding.all(10)
            ),
            ft.Text(
                "President Donald Trump shakes hands with Ursula von der Leyen at Turnberry, Scotland.",
                size=12,
                color=ft.Colors.GREY_700
            ),
            ft.Container(
                content=ft.Text(
                    "Israel begins daily pause in fighting in 3 Gaza areas to allow ‘minimal’ aid as hunger grows",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK
                ),
                padding=ft.padding.only(top=30)
            ),
            ft.Text("MORE COVERAGE", size=12, color=ft.Colors.GREY_600),
            ft.Column(
                [
                    ft.Text("• The latest child to starve to death in Gaza weighed less than when she was born", size=14, color=ft.Colors.BLACK),
                    ft.Text("• Israel intercepts Gaza-bound ship carrying activists", size=14, color=ft.Colors.BLACK),
                    ft.Text("• France’s recognition of Palestine could affect EU and US policy", size=14, color=ft.Colors.BLACK),
                ]
            ),
            ft.Container(
                content=ft.Text("[IMAGE PLACEHOLDER]", size=14, color=ft.Colors.GREY_500),
                width=600,
                height=300,
                bgcolor=ft.Colors.GREY_200,
                alignment=ft.alignment.center,
                border_radius=5,
                padding=ft.padding.all(10)
            ),
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        width=700,
    )

    right_column_content = ft.Column(
        [
            ft.Text(
                "Tom Lehrer, song satirist and mathematician, dies at 97",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK
            ),
            ft.Text("8 MINS AGO", size=12, color=ft.Colors.RED_500),
            ft.Divider(),
            ft.Text("Alec Baldwin talks his love for ‘Peanuts’ and the ‘immeasurable’ effects of his trial", size=16, color=ft.Colors.BLACK),
            ft.Divider(),
            ft.Text("Ryan Gosling and faceless alien wow crowd at Comic-Con", size=16, color=ft.Colors.BLACK),
            ft.Divider(),
            ft.Text("Tour de France finale brings excitement to Montmartre", size=16, color=ft.Colors.BLACK),
            ft.Divider(),
            ft.Text("‘Fantastic Four’ scores Marvel’s first $100M opening of 2025", size=16, color=ft.Colors.BLACK),
            ft.Divider(),
            ft.Text("Company hires Gwyneth Paltrow as spokesperson", size=16, color=ft.Colors.BLACK),
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        width=400,
    )

    main_content_row = ft.Row(
        [left_column_content, ft.VerticalDivider(width=1), right_column_content],
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20
    )

    centered_content = ft.Container(
        content=main_content_row,
        alignment=ft.alignment.center,
        width=1100,
        bgcolor=ft.Colors.WHITE
    )

    _main_content_column = ft.Column([centered_content], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    main_content_container = ft.Container(
        content=_main_content_column, visible=True, expand=True, alignment=ft.alignment.top_center
    )

    dynamic_content_area = ft.Container(
        content=ft.Column(
            [main_content_container, search_results_container],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER # Added this line
        ),
        expand=True,
        bgcolor=ft.Colors.WHITE,
        alignment=ft.alignment.top_center
    )

    page.add(
        header,
        ft.Container(height=20),
        search_bar_container,
        dynamic_content_area
    )

    page.update()

ft.app(target=main)