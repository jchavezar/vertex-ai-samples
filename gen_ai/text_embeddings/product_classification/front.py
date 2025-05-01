#%%
import json
import pandas as pd
import numpy as np
from flet import *
from google import genai
from google.genai import types

project = "vtxdemos"
location = "us-central1"
gen_model = "gemini-2.5-flash-preview-04-17"

df = pd.read_csv("florida_connecticut_product_name_examples.csv")

client = genai.Client(
    vertexai=True,
    project=project,
    location=location
)

mapped_names = list(df["mapped_name"].unique())  # Unique Names for Mapped Name

config = types.GenerateContentConfig(
    system_instruction=
    f"""
        Your mission is to classify the products based on the following table {mapped_names},
        
        The product can come in packets like 5x2g, so take into account the total weight of the box.
        Pay special attention to the weight (1 means 1g, 0.100 means 100mg and the product_name where sometimes
        it comes with the quantity so the weight can vary, it has to be the total weight when expressed like this (quantityXweight in mg or g)).
    """,
    thinking_config=types.ThinkingConfig(
        thinking_budget=0
    )
)

iteration_counter = 0


def gen_ai_process_row(row):
    print(row)
    global iteration_counter
    try:
        iteration_counter += 1
        re = client.models.generate_content(
            model=gen_model,
            config=config,
            contents=f"""Classify the following product:
            Product Name: {row["product_name"]},
            Brand: {row["brand"]},
            SubCategory: {row["sub_category"]},
            Product Weight: {row["product_weight"]}
            """
        )
        if iteration_counter % 20 == 0:
            print(f"Iteration {iteration_counter}: {re.text}")
        return re.text
    except Exception as e:
        print(f"Error: {e}")
        return None


#%%


def main(page: Page):
    page.window.width = 1200
    page.window.height = 800

    page.title = "Verano Product Labeling"

    def action(e):
        raw_text = input_text.value or ""
        product_list = [item.strip() for item in raw_text.strip().split("\n") if item.strip()]

        results_list_view.controls.clear()

        if not product_list:
            results_list_view.controls.append(Text("Please enter product names."))
            page.update()
            return

        if df.empty:
            results_list_view.controls.append(Text("Error: Product data not loaded."))
            page.update()
            return

        filtered_df = df[df["product_name"].isin(product_list)].copy()

        if filtered_df.empty:
            results_list_view.controls.append(Text("No matching products found for the given input."))
            page.update()
            return

        # This line calls the GenAI model for each row found, which can be slow.
        filtered_df["detected_label"] = filtered_df.apply(lambda x: gen_ai_process_row(x), axis=1)
        print("Processing complete. Detected Labels:")
        print(filtered_df[["product_name", "mapped_name", "detected_label"]])

        header_row = Row(
            controls=[
                Container(Text("Input Product", weight=FontWeight.BOLD), width=250, padding=5),
                Container(Text("Mapped Name (CSV)", weight=FontWeight.BOLD), width=250, padding=5),
                Container(Text("Detected Label", weight=FontWeight.BOLD), width=250, padding=5),
            ]
        )
        results_list_view.controls.append(header_row)
        results_list_view.controls.append(Divider(height=1, color=Colors.BLACK26))

        for index, row_data in filtered_df.iterrows():
            input_name = row_data["product_name"]
            mapped_name = row_data["mapped_name"]
            detected_label = row_data["detected_label"] or "Error/None"

            cleaned_detected_label = detected_label.strip().strip('"').strip("'")

            match_color = Colors.GREEN if mapped_name == cleaned_detected_label else Colors.RED

            data_row = Row(
                controls=[
                    Container(Text(input_name, selectable=True), width=250, padding=5),
                    Container(Text(mapped_name, color=match_color, selectable=True), width=250, padding=5),
                    Container(Text(cleaned_detected_label, color=match_color, selectable=True), width=250, padding=5),
                ]
            )
            results_list_view.controls.append(data_row)
            results_list_view.controls.append(Divider(height=1, color=Colors.BLACK12))

        page.update()
    header: Container = Container(
        margin=margin.only(left=40, right=40),
        height=80,
        border=border.all(1, Colors.BLACK87),
        border_radius=12.0,
        content=Row(
            alignment=MainAxisAlignment.SPACE_EVENLY,
            controls=[
                Container(
                    margin=10,
                    content=Image(src="https://verano.com/wp-content/uploads/2021/11/Verano_Blk_RGB.svg")
                ),
                Container(
                    alignment=alignment.center,
                    margin=10,
                    content=Text("Products Labeling / Classification")
                )
            ]
        )
    )
    input_text: TextField = TextField(
        label="Enter the Product Items",
        multiline=True,
        min_lines=20,
        border_color=Colors.TRANSPARENT,
        on_submit=action,
        shift_enter=True,
    )

    results_list_view: ListView = ListView(
        padding=10,
        expand=True,
        controls=[
        ]
    )

    body: Container = Container(
        margin=30,
        expand=True,
        content=Row(
            vertical_alignment=CrossAxisAlignment.STRETCH,
            expand=True,
            controls=[
                Container(
                    expand=3,
                    padding=20,
                    border=border.all(color=Colors.BLACK87),
                    border_radius=12.0,
                    content=input_text
                ),
                VerticalDivider(width=15, color=Colors.TRANSPARENT),
                Container(
                    expand=5,
                    padding=20,
                    border=border.all(color=Colors.BLACK87),
                    border_radius=12.0,
                    content=results_list_view
                ),
            ]
        )
    )

    page.add(
        Column(
            expand=True,
            # alignment=MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                header,
                Divider(height=20),
                body
            ]
        )
    )

app(main)