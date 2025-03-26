import json
from flet import *
# Ensure you have your 'generate_content' function available, e.g.:
# from back import generate_content

def build_invoice_view(invoice_data_list):
    if not invoice_data_list or not isinstance(invoice_data_list, list):
        return Text("No valid invoice data found after parsing.", color=Colors.ORANGE)

    invoice_data = invoice_data_list[0]
    controls_list = []

    def add_field(label, value):
        if value is not None:
            controls_list.append(
                Row([
                    Text(f"{label}:", weight=FontWeight.BOLD, width=120, text_align=TextAlign.END),
                    Text(str(value), selectable=True, expand=True)
                ])
            )

    add_field("Invoice ID", invoice_data.get("invoice_id"))
    add_field("Payer Name", invoice_data.get("payer_name"))
    add_field("Payer Address", invoice_data.get("payer_address"))
    add_field("Date", invoice_data.get("date"))
    add_field("Due Date", invoice_data.get("due_date"))
    add_field("Balance Due", invoice_data.get("balance_due"))

    controls_list.append(Divider(height=10, color=Colors.TRANSPARENT))

    table_items = invoice_data.get("table", [])
    if table_items:
        data_table = DataTable(
            columns=[
                DataColumn(Text("Item")),
                DataColumn(Text("Qty"), numeric=True),
                DataColumn(Text("Rate"), numeric=True),
                DataColumn(Text("Amount"), numeric=True),
            ],
            rows=[
                DataRow(cells=[
                    DataCell(Text(str(item.get("item", "")), selectable=True)),
                    DataCell(Text(str(item.get("quantity", "")), selectable=True)),
                    DataCell(Text(str(item.get("rate", "")), selectable=True)),
                    DataCell(Text(str(item.get("amount", "")), selectable=True)),
                ]) for item in table_items
            ],
            expand=True,
            border=border.all(1, Colors.GREY_300),
            horizontal_lines=border.BorderSide(1, Colors.GREY_300),
            border_radius=border_radius.all(5),
            column_spacing=20,
        )
        controls_list.append(data_table)
        controls_list.append(Divider(height=10, color=Colors.TRANSPARENT))

    add_field("Subtotal", invoice_data.get("subtotal"))
    add_field("Discounts", invoice_data.get("discounts"))
    add_field("Tax", invoice_data.get("tax"))
    add_field("Total", invoice_data.get("total"))
    add_field("Amount Paid", invoice_data.get("amount_paid"))
    add_field("Notes", invoice_data.get("notes"))
    add_field("Terms", invoice_data.get("terms"))

    return ListView(controls=controls_list, expand=True, spacing=8, auto_scroll=True)

def main(page: Page):
    page.title = "Invoice Extractor"
    page.window_width = 800
    page.window_height = 700
    page.window_resizable = True

    page.vertical_alignment = MainAxisAlignment.SPACE_BETWEEN
    page.horizontal_alignment = CrossAxisAlignment.STRETCH

    def pick_files_result(e: FilePickerResultEvent):
        print("Selected files:", e.files)
        gemini.content = Column([ProgressRing()], alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, expand=True)
        gemini.visible = True
        page.update()

        if e.files:
            f = e.files[0]
            try:
                # Assuming generate_content is imported and returns a JSON string
                response_string = generate_content(f.path)
                print("API Response String received") # Minimal print
                parsed_data = json.loads(response_string)
                print("Parsed Data successfully") # Minimal print
                gemini.content = build_invoice_view(parsed_data)

            except json.JSONDecodeError as json_err:
                print(f"Error parsing JSON response: {json_err}")
                gemini.content = Text(f"Error: Could not parse the response data.\n{json_err}", color=Colors.RED)
            except Exception as ex:
                # Make sure generate_content is defined/imported correctly
                print(f"Error processing file or building view: {ex}")
                gemini.content = Text(f"Error: {ex}", color=Colors.RED)
        else:
            print("No files selected.")
            gemini.visible = False

        page.update()


    pick_files_dialog = FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)

    def pick_files(e):
        pick_files_dialog.pick_files(
            allow_multiple=False,
            allowed_extensions=["pdf"]
        )

    header = Container(
        alignment=alignment.center,
        height=100,
        margin=10,
        border=border.all(0.3, Colors.GREY_50),
        border_radius=12.0,
        content=Text("Invoice Extractor", color=Colors.CYAN, size=20, weight=FontWeight.BOLD)
    )

    gemini = Container(
        expand=True,
        margin=10,
        padding=10,
        border=border.all(0.3, Colors.GREY_50),
        border_radius=12.0,
        content=None,
        visible=False,
        clip_behavior=ClipBehavior.ANTI_ALIAS,
        alignment=alignment.top_left
    )

    body = Container(
        expand=True,
        content=Row(
            controls=[
                gemini,
            ],
            vertical_alignment=CrossAxisAlignment.START,
            expand=True,
        )
    )

    bottom = Container(
        height=80,
        margin=10,
        padding=10,
        content=Row(
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=CrossAxisAlignment.CENTER,
            controls=[
                Container(
                    expand=True,
                    padding=padding.only(right=10),
                    content=TextField(
                        label="Ask something about the invoice...",
                        border_color=Colors.GREY,
                        border_radius=12,
                        border_width=0.3
                    )
                ),
                send_button := ElevatedButton(
                    "Send",
                    style=ButtonStyle(bgcolor=Colors.CYAN, color=Colors.WHITE)
                ),
                upload_button := IconButton(
                    icon=Icons.UPLOAD_FILE,
                    tooltip="Upload PDF Invoice",
                    on_click=pick_files
                )
            ]
        )
    )

    page.add(
        header,
        body,
        bottom,
    )

if __name__ == "__main__":
    # Make sure to define or import generate_content function before running
    try:
        from back import generate_content # Attempt to import
    except ImportError:
        print("Warning: 'generate_content' function not found. Please ensure it's defined or imported from 'back.py'.")
        # Define a dummy function so the app can at least start
        def generate_content(path):
            print(f"Dummy generate_content called for {path}")
            return '[]' # Return empty JSON array string

    app(target=main)