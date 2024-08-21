import json
import vertexai
from flet import *
from google.cloud import bigquery
from vertexai.generative_models import GenerativeModel

project_id = "vtxdemos"  # Replace with your Google Cloud project ID
bq_dataset_id = "vtxdemos.demos_us.ecommerce_balanced"  # Replace with your BigQuery dataset ID

# BigQuery
bq_client = bigquery.Client(project=project_id)
table = bq_client.get_table(bq_dataset_id)
schema = table.schema

dataset = []
query = "SELECT DISTINCT {field_name} FROM `{bq_dataset_id}`"

for i in schema:
  query_job = bq_client.query(query.format(field_name=i.name, bq_dataset_id=bq_dataset_id))
  results = query_job.result()

  unique_values = [row[0] for row in results]
  dataset.append({"name": i.name, "type": i.field_type, "uniques": unique_values})


mapping = {
    "INTEGER" : ["greater than or equal to", "below than"],
    "STRING" : ["=", "!="]
}
# End BigQuery

# Gemini
vertexai.init(project=project_id, location="us-central1")

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json",
}

system_instructions = f"""
You are a friendly and helpful conversational chatbot. You can answer a wide range of questions.
Your main mission is to create a dictionary with the schema column names selected and the sql query to run.

<bigquery_schema_values_type>
{str(dataset)}
</bigquery_schema_values_type>

<bigquery_schema_descripton>
latest_ecommerce_progress: What is the customer's progress in the checkout process? (For example: 1 = added to cart, 2 = entered shipping info, 3 = completed payment)
bounces: How many times has the customer visited the website but left after viewing only one page?
time_on_site: How many seconds did the customer spend on the website during their last visit?
pageviews: How many pages did the customer view during their last visit?
source: Where did the customer come from? (For example: Google, Facebook, newsletter)
medium: What marketing medium brought the customer to the website? (For example: organic, cpc, email)
channelGrouping: What is the overall channel grouping of the customer's visit? (For example: Organic Search, Paid Search, Direct)
deviceCategory: What type of device did the customer use? (For example: desktop, mobile, tablet)
country: What country is the customer located in?
</bigquery_schema_description>

<expected_output_in_json_format>
  {{
    "response": <any response from you>,
    "sql_query": <the sql query>,
    "<bigquery_sechema_column_name_selected_1>": <detect the value from the prompt (can be string or integer)>, 
    "<bigquery_sechema_column_name_selected_2>": <detect the value from the prompt (can be string or integer)>,
    etc
  }}
</expect_output_in_json_format>

"""

model = GenerativeModel(
    "gemini-1.5-flash-001",
    system_instruction=system_instructions
)
chat = model.start_chat()
# End Gemini

def gen_value_by_key(key_to_match):
  for item in dataset:
    for k, v in item.items():
      if v == key_to_match:
        return item["uniques"]

def main(page: Page):
  rows = []

  def add_rule(e):
    def sub_dropdown(e):
      print(dd.value)
      print(dd.value)
      for i in dataset:
        print(i["name"], i["type"])
      # new_row.controls.pop(1)
      del new_row.controls[1:]
      print(new_row.controls)

      selected_type = next((item["type"] for item in dataset if item["name"] == dd.value), None)

      if selected_type:
        options_for_dd2 = mapping.get(selected_type, [])  # Get options based on type, default to empty list if not found
      else:
        options_for_dd2 = []

      new_row.controls.append(
          dd2 := Dropdown(
              width=210,
              value=options_for_dd2[0],
              options=[dropdown.Option(opt) for opt in options_for_dd2]
          )
      )
      new_row.controls.append(
          ElevatedButton(
              "delete",
              icon=icons.DELETE,
              on_click=lambda e: delete_row(new_row)
          )
      )
      inner_body.update()

    def delete_row(row_to_delete):
      print(row_to_delete)
      # Remove the row from the list
      rows.remove(row_to_delete)
      # Update the UI
      inner_body.update()

    new_row = Row(
        controls=[
            dd := Dropdown(
                options=[dropdown.Option(i["name"]) for i in dataset],
                on_change=sub_dropdown
            ),
            ElevatedButton(
                "delete",
                icon=icons.DELETE,
                on_click=lambda e: delete_row(new_row)
            )
        ]
    )
    rows.append(new_row)
    inner_body.content.controls = rows
    inner_body.update()

  button_body: Row = Row(
      controls=[
          ElevatedButton(
              "Add Rule",
              on_click=add_rule
          )
      ]
  )

  inner_body: Container = Container(
      bgcolor=colors.TEAL_50,
      # height=350,
      content=Column(
          controls=rows
      )
  )

  inner_layout: Column = Column(
      controls=[
          Container(
              border=border.all(1, colors.GREY),
              margin=12,
              padding=12,
              border_radius=12,
              content=Column(
                  controls=[
                      inner_header:=Container(
                          height=100,
                          content=Row(
                              alignment=MainAxisAlignment.SPACE_EVENLY,
                              controls=[
                                  inner_text:=TextField(
                                      expand=True,
                                      label="Audience Name"
                                  ),
                                  VerticalDivider(width=10, color=colors.TRANSPARENT),
                                  Icon(icons.EDIT)
                              ]
                          ),
                      ),
                      button_body,
                      inner_body
                  ]
              )
          )
      ]
  )

  def chat_message(e):
    text = e.control.value,
    chat_res = chat.send_message([f"Query:{text}\nOutput:\n"], generation_config=generation_config).text
    _res = json.loads(chat_res)
    for k,v in _res.items():
      if k != "sql_query" and k != "response" and k != "will_buy_on_return_visit":
        values = gen_value_by_key(k)
        print(values)
        inner_body.content.controls.append(
            Row(
                controls=[
                    Dropdown(
                        value=k,
                        options=[dropdown.Option(i["name"]) for i in dataset]
                    ),
                    Dropdown(
                        value=v,
                        options=[dropdown.Option(i) for i in values]
                    )
                ]
            )
        )
    inner_body.update()

    chat_bot.content.controls[0].value = chat_res
    chat_bot.update()

  chat_bot: Container = Container(
      height=200,
      content=Column(
          controls=[
              Text(),
              TextField(
                  label="Write something...",
                  on_submit=chat_message
              )
          ]
      )
  )

  page.add(
      AppBar(
          title=Text("Gemini SQL"),
          center_title=True),
      main_layout := Column(
          controls=[
              inner_layout,
              chat_bot
          ]
      )
  )


app(target=main)