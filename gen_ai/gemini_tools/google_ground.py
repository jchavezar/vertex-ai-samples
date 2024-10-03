#%%
import vertexai
from flet import *
import pandas as pd
from vertexai.generative_models import GenerativeModel, Tool, grounding, GenerationConfig

project_id = "vtxdemos"
model_name = "gemini-1.5-flash-002"
dataset = "gs://vtxdemos-datasets-private/sp_dataset.csv"
df = pd.read_csv(dataset)

# Init
vertexai.init(project=project_id, location="us-central1")

# Tools Definition
tools = [
    Tool.from_google_search_retrieval(
        google_search_retrieval=grounding.GoogleSearchRetrieval()
    ),
]

# Output Schema
response_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "physical_location": {
                "type": "string",
            },
        },
        "required": ["physical_location"],
    },
}

# Model
model = GenerativeModel(
    model_name,
    tools=tools
)


#%%
def gemini(prompt: str):
    try:
        response = model.generate_content(
            [f'''
            Give me the physical location (address) from the following query:
            
            Rules:
            * **Format**: JSON Values Output format <String>(Number, Street, City, etc)
            * **Do Nots**: 
            -- If you dont know the answer just say not found.
            -- Do not Add ANY annotation format like ``` or json```
            
            Output Format:
            {{"physical_location": <address>}}
            
            {prompt}
            
            Output:
            '''],
        )
        print(response)
        return response.text.replace("`", "").replace("json", "")
    except:
        return "Error"


response2 = model.generate_content(
    [f"""
    Give me the physical location (address) from the following query:
    
    Rules:
    * **Format**: JSON Values Output format <String>(Number, Street, City, etc)
    * **Do Nots**: If you dont know the answer just say not found.
    
    {df["Search Query"].iloc[0]}
    """],
    generation_config=GenerationConfig(
        response_mime_type="application/json", response_schema=response_schema
    ),
)


class OutputWidget(Container):
    def __init__(self, page):
        super().__init__()
        self.border = border.all(1, color=colors.GREY)
        self.border_radius = 14
        self.width = page.width * .50
        self.height = page.height * .70
        self.padding = 14
        self.response = Text(value="")
        self.content = Column(
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.START,
            controls=[
                Text("Response: ", style=TextStyle(size=18, weight=FontWeight.BOLD, color=colors.GREEN)),
                self.response
            ]
        )

    def update_text(self, new_text: str):
        self.response.value = new_text
        self.update()


class InputWidget(Container):
    def __init__(self, page, output_widget: OutputWidget):
        super().__init__()
        self.border = border.all(1, color=colors.GREY)
        self.border_radius = 14
        self.width = page.width * .50
        self.height = 100
        self.padding = 10
        self.output_widget = output_widget
        self.content = TextField(on_submit=self.send_output)

    def send_output(self, e):
        re = gemini(e.control.value)
        print(re)
        self.output_widget.update_text(re)


def main(page: Page):
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    output_widget = OutputWidget(page)  # Create OutputWidget first
    input_widget = InputWidget(page, output_widget)

    page.add(output_widget, input_widget)


app(target=main)
