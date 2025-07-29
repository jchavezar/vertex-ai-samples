
import flet as ft
import re  # Import regex for advanced text parsing
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

    # Helper function to parse and format the AI\'s response
    def format_answer_content(answer: str) -> list[ft.Control]:
        controls = []
        lines = answer.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 1. Handle bullet points for "Explore Deeper" / "Other Perspectives": * **Title**: Description
            # This regex captures the title inside ** ** and the description after the colon.
            match_complex_bullet = re.match(r'^\*\s*\*\*(.*?)\*\*:\s*(.*)$', line)
            if match_complex_bullet:
                title_text = match_complex_bullet.group(1).strip()
                description_text = match_complex_bullet.group(2).strip()
                controls.append(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.CIRCLE, size=10, color=ft.Colors.BLACK), # Slightly larger icon
                            ft.Text(
                                spans=[
                                    ft.TextSpan(
                                        title_text,
                                        ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, size=16), # Increased size
                                    ),
                                    ft.TextSpan(
                                        f": {description_text}",
                                        ft.TextStyle(color=ft.Colors.BLACK, size=15), # Increased size
                                    )
                                ],
                                selectable=True,
                                overflow=ft.TextOverflow.CLIP,
                                max_lines=None, # Allow text to wrap
                                expand=True # Allow text to expand within the row
                            )
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        spacing=5
                    )
                )
                continue

            # 2. Handle simple bullet points for "Get Trending": * Point
            match_simple_bullet = re.match(r'^\*\s*(.*)$', line)
            if match_simple_bullet:
                bullet_text = match_simple_bullet.group(1).strip()
                controls.append(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.STAR, size=18, color=ft.Colors.AMBER_500), # Slightly larger icon
                            ft.Text(
                                bullet_text,
                                color=ft.Colors.BLACK,
                                selectable=True,
                                overflow=ft.TextOverflow.CLIP,
                                max_lines=None, # Allow text to wrap
                                expand=True,
                                size=15 # Increased size
                            )
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        spacing=5
                    )
                )
                continue

            # 3. Handle general bold text within paragraphs (e.g., in summaries or direct answers)
            # This splits the line by occurrences of '**...**' and creates TextSpans for each part.
            if '**' in line:
                parts = re.split(r'(\*\*.*?\*\*)', line)
                text_spans = []
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        text_spans.append(ft.TextSpan(part[2:-2], ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, size=16))) # Increased size
                    else:
                        text_spans.append(ft.TextSpan(part, ft.TextStyle(color=ft.Colors.BLACK, size=15))) # Increased size
                controls.append(
                    ft.Text(
                        spans=text_spans,
                        selectable=True,
                        overflow=ft.TextOverflow.CLIP, # Allow text to clip if needed, but primarily wrap
                        max_lines=None, # No fixed max lines for general paragraph text
                    )
                )
                continue

            # 4. Default: regular text (for summaries or direct answers)
            controls.append(ft.Text(line, color=ft.Colors.BLACK, selectable=True, size=15, overflow=ft.TextOverflow.CLIP, max_lines=None)) # Increased size

        # If after parsing, no controls were added (e.g., empty or unparseable string),
        # display the original raw text as a fallback.
        if not controls:
            controls.append(ft.Text(answer, color=ft.Colors.BLACK, selectable=True, size=15)) # Increased size

        return controls


    # Helper function to update the answer container's content and visibility
    def update_answer_container(answer_container, content, is_loading=False):
        if is_loading:
            answer_container.content = ft.Column(
                [ft.ProgressRing(width=20, height=20)],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                height=100
            )
        else:
            # Use the new formatting function here
            formatted_controls = format_answer_content(content)
            answer_container.content = ft.Column(
                formatted_controls,
                spacing=8, # Slightly reduced spacing between formatted items
                horizontal_alignment=ft.CrossAxisAlignment.START
            )
        answer_container.visible = True
        page.update()

    def on_get_trending_click(e, title, answer_container):
        update_answer_container(answer_container, None, is_loading=True)
        # Prompt for what people are saying (grounding=True for search)
        answer = send_message(f"Give me 4 concise (no more than 7 words each) key bullet point of what people is saying about: {title}", grounding=True)
        update_answer_container(answer_container, answer)

    def on_get_summary_click(e, title, snippet, answer_container):
        update_answer_container(answer_container, None, is_loading=True)
        # Prompt for summary using title and snippet (grounding=True for enhanced info)
        prompt = f"Provide a concise and precise summary (around 2-3 sentences) of the following news content, using external search if necessary:\nTitle: {title}\nSnippet: {snippet}"
        answer = send_message(prompt, grounding=True) # Changed to grounding=True
        update_answer_container(answer_container, answer)

    def on_explore_deeper_click(e, title, answer_container):
        update_answer_container(answer_container, None, is_loading=True)
        # Prompt for related articles (grounding=True for search)
        prompt = f"Suggest 3 related news articles to the topic of '{title}'. For each, provide a detailed summary of the article, formatted as a bulleted list, starting with '* **Title**: Description'."
        answer = send_message(prompt, grounding=True)
        update_answer_container(answer_container, answer)

    def on_see_other_perspectives_click(e, title, answer_container):
        update_answer_container(answer_container, None, is_loading=True)
        # Prompt for alternative viewpoints (grounding=True for search)
        prompt = f"Find 3 alternative viewpoints or counter-arguments on the topic of '{title}'. For each, provide only its title and a very brief (1-sentence) description, formatted as a bulleted list, starting with '* **Title**: Description'."
        answer = send_message(prompt, grounding=True)
        update_answer_container(answer_container, answer)

    def on_question_submit(e, answer_container, context):
        question = e.control.value
        if question:
            e.control.value = ""
            e.control.disabled = True
            update_answer_container(answer_container, None, is_loading=True)

            # Keep grounding=False for direct Q&A about the content itself
            answer = send_message(question+"\n\nContext:\n"+context, grounding=False)

            update_answer_container(answer_container, answer)
            e.control.disabled = False
            page.update()

    def go_to_main_website(e):
        main_content_container.visible = True
        search_results_container.visible = False
        _search_results_column.controls.clear()
        search_bar.value = ""
        page.update()

    def on_submit(e):
        if e.control.value:
            main_content_container.visible = False
            search_results_container.visible = True

            # Clear previous results and show a loading indicator
            _search_results_column.controls.clear()
            _search_results_column.controls.append(
                ft.Column(
                    [ft.ProgressRing(width=20, height=20)],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    height=100
                )
            )
            page.update()

            response_data = custom_search(e.control.value)

            _search_results_column.controls.clear()  # Clear loading indicator

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

                    current_title = response_data["titles"][i]
                    current_snippet = response_data["snippets"][i] if i < len(response_data["snippets"]) else ""

                    block_content.append(
                        ft.Text(
                            current_title,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        )
                    )

                    if current_snippet:
                        block_content.append(
                            ft.Text(
                                current_snippet,
                                size=15,  # Increased size for snippet
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

                        get_trending_button = ft.Container(
                            content=ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.AUTO_AWESOME),
                                        ft.Text("Get Trending"),
                                    ],
                                    spacing=5,
                                ),
                                on_click=lambda e, title=current_title, ac=answer_container: on_get_trending_click(e, title, ac),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.TRANSPARENT,
                                    padding=ft.padding.all(12),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                            width=150,
                            height=40,
                            border_radius=ft.border_radius.all(8),
                            padding=ft.padding.all(2),
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.center_left,
                                end=ft.alignment.center_right,
                                colors=[ft.Colors.CYAN_400, ft.Colors.BLUE_700],
                            ),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        )

                        # New "Get Summary" button
                        get_summary_button = ft.Container(
                            content=ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.AUTO_AWESOME),
                                        ft.Text("Get Summary"),
                                    ],
                                    spacing=5,
                                ),
                                on_click=lambda e, title=current_title, snippet=current_snippet, ac=answer_container: on_get_summary_click(e, title, snippet, ac),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.TRANSPARENT,
                                    padding=ft.padding.all(12),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                            width=150,
                            height=40,
                            border_radius=ft.border_radius.all(8),
                            padding=ft.padding.all(2),
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.center_left,
                                end=ft.alignment.center_right,
                                colors=[ft.Colors.LIGHT_GREEN_400, ft.Colors.GREEN_700],  # Distinct color
                            ),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        )

                        block_content.append(
                            ft.Container(
                                content=image_with_container,
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(top=10),
                            )
                        )

                        icon = ft.Icon(
                            name=ft.Icons.QUESTION_ANSWER,
                            color=ft.Colors.GREY_700,
                        )

                        question_textfield = ft.TextField(
                            hint_text="Ask a question about this content...",
                            hint_style=ft.TextStyle(color=ft.Colors.GREY_700, size=14),
                            text_style=ft.TextStyle(color=ft.Colors.BLACK, size=14),
                            border=ft.InputBorder.NONE,
                            bgcolor=ft.Colors.TRANSPARENT,
                            content_padding=ft.padding.only(bottom=6, right=10),
                            on_submit=lambda e, ac=answer_container, context=f"title:\n{current_title}\n\nsnippet:\n{current_snippet}": on_question_submit(e, ac, context),
                            expand=True,
                        )

                        textfield_with_icon_row = ft.Row(
                            controls=[
                                ft.Container(icon, padding=ft.padding.only(left=12, right=8)),
                                question_textfield,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        )

                        white_background_container = ft.Container(
                            content=textfield_with_icon_row,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=ft.border_radius.all(6),
                        )

                        gradient_border_container = ft.Container(
                            width=400,
                            height=40,
                            border_radius=ft.border_radius.all(8),
                            padding=ft.padding.all(2),
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.center_left,
                                end=ft.alignment.center_right,
                                colors=[ft.Colors.CYAN_400, ft.Colors.BLUE_700],
                            ),
                            content=white_background_container,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        )

                        centered_textfield_wrapper = ft.Container(
                            content=gradient_border_container,
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=10),
                        )

                        block_content.append(centered_textfield_wrapper)

                        # New row for "Explore Deeper" and "Other Perspectives" buttons
                        additional_ai_buttons_row = ft.Row(
                            [
                                ft.Container(
                                    content=ft.ElevatedButton(
                                        content=ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, size=16), ft.Text("Explore Deeper", size=12)], spacing=5),
                                        on_click=lambda e, title=current_title, ac=answer_container: on_explore_deeper_click(e, title, ac),
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.WHITE,
                                            bgcolor=ft.Colors.TRANSPARENT,
                                            padding=ft.padding.symmetric(horizontal=10, vertical=8),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                    ),
                                    border_radius=ft.border_radius.all(8),
                                    padding=ft.padding.all(1),
                                    gradient=ft.LinearGradient(
                                        begin=ft.alignment.center_left,
                                        end=ft.alignment.center_right,
                                        colors=[ft.Colors.PURPLE_400, ft.Colors.DEEP_PURPLE_700], # Distinct color
                                    ),
                                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                ),
                                ft.Container(
                                    content=ft.ElevatedButton(
                                        content=ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, size=16), ft.Text("Other Perspectives", size=12)], spacing=5),
                                        on_click=lambda e, title=current_title, ac=answer_container: on_see_other_perspectives_click(e, title, ac),
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.WHITE,
                                            bgcolor=ft.Colors.TRANSPARENT,
                                            padding=ft.padding.symmetric(horizontal=10, vertical=8),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                    ),
                                    border_radius=ft.border_radius.all(8),
                                    padding=ft.padding.all(1),
                                    gradient=ft.LinearGradient(
                                        begin=ft.alignment.center_left,
                                        end=ft.alignment.center_right,
                                        colors=[ft.Colors.ORANGE_400, ft.Colors.DEEP_ORANGE_700], # Distinct color
                                    ),
                                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                )
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.CENTER,
                            wrap=True,
                        )
                        block_content.append(ft.Container(content=additional_ai_buttons_row, margin=ft.margin.only(top=10)))


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

                    content_stack = ft.Stack(
                        controls=[
                            content_container,
                            # Original "Get Trending" button
                            ft.Container(
                                content=get_trending_button,
                                top=130,
                                right=0,
                            ),
                            # New "Get Summary" button, positioned below "Get Trending"
                            ft.Container(
                                content=get_summary_button,
                                top=180, # Adjusted position to avoid overlap
                                right=0,
                            )
                        ],
                        width=700,
                    )

                    result_row = ft.Row(
                        controls=[
                            answer_container,
                            content_stack,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        spacing=20,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )

                    centered_result_block = ft.Container(
                        content=result_row,
                        width=1120,
                    )
                    result_blocks.append(centered_result_block)

            _search_results_column.controls.extend(result_blocks)
        else:
            main_content_container.visible = True
            search_results_container.visible = False
            _search_results_column.controls.clear()
        page.update()

    search_bar = ft.TextField(
        hint_text="Keyword Search...",
        hint_style=ft.TextStyle(color=ft.Colors.GREY_700),
        text_style=ft.TextStyle(color=ft.Colors.BLACK),
        width=800,
        on_submit=on_submit,
        content_padding=ft.padding.only(left=10, right=10),
        border_radius=5,
        border_color=ft.Colors.GREY_300,
        focused_border_color=ft.Colors.BLUE_ACCENT_700,
        height=40,
        text_size=16,
        prefix_icon=ft.Icons.SEARCH
    )

    go_to_main_button = ft.ElevatedButton(
        "Home",
        on_click=go_to_main_website,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_GREY_100,
            color=ft.Colors.BLACK,
            shape=ft.RoundedRectangleBorder(radius=5)
        )
    )

    search_bar_container = ft.Container(
        content=ft.Row(
            [
                search_bar,
                go_to_main_button
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.only(bottom=20),
        width=1100,
    )

    _search_results_column = ft.Column(expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
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
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
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
