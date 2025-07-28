import flet as ft

def main(page: ft.Page):
    page.title = "AP News Replica"
    page.window_width = 1200
    page.window_height = 800
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.bgcolor = ft.Colors.WHITE
    # Set the page's horizontal alignment to center all its direct children
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- Header Section ---
    # Inner Row for Header Content to control its width and spacing
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
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, # Distribute items within this row's width
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        width=1100, # Set a specific width for this inner row, matching the main content width
    )

    # Outer Container for Header, which itself will now be centered by the page.horizontal_alignment
    header = ft.Container(
        content=header_content_row, # Contains the inner row (which is 1100 wide)
        padding=ft.padding.all(10),
        width=1100, # Set the header container's width to match the main content width for consistent alignment
        bgcolor=ft.Colors.WHITE,
        # The alignment property for content centering within this container is no longer needed,
        # as header_content_row already fills this width.
    )

    # --- Search Bar ---
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

    search_bar = ft.TextField(
        hint_text="Keyword Search...",
        width=800, # Adjusted width to better fit within the 1100px content area
        on_change=on_search_change,
        content_padding=ft.padding.only(left=10, right=10),
        border_radius=5,
        border_color=ft.Colors.GREY_300,
        focused_border_color=ft.Colors.BLUE_ACCENT_700,
        height=40,
        text_size=16,
        prefix_icon=ft.Icons.SEARCH
    )

    # Container for search bar to be centered within the 1100px content band
    search_bar_container = ft.Container(
        content=search_bar,
        alignment=ft.alignment.center, # Center the search bar within this container
        padding=ft.padding.only(bottom=20),
        width=1100, # Make this container 1100px wide so it aligns with other content blocks
    )

    # --- Search Results Container ---
    _search_results_column = ft.Column(expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    search_results_container = ft.Container(content=_search_results_column, visible=False, expand=True)

    # --- Main Content ---
    # Left column (Main news)
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

    # Right column (Side news)
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

    # Center layout container for main content (already 1100 wide and its content centers)
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
    main_content_container = ft.Container(content=_main_content_column, visible=True, expand=True)

    dynamic_content_area = ft.Container(
        content=ft.Column([main_content_container, search_results_container], expand=True),
        expand=True,
        bgcolor=ft.Colors.WHITE,
        alignment=ft.alignment.top_center # This will align the column within dynamic_content_area.
    )

    # Add everything to page
    page.add(
        header,
        ft.Container(height=20),
        search_bar_container, # Use the new search_bar_container for consistent alignment
        dynamic_content_area
    )

    page.update()

ft.app(target=main)
