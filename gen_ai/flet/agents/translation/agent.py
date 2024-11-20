#%%
import os
from typing import Dict

import vertexai
from traits.trait_types import false
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig

class Agent:
  def __init__(self, instruction: str, file: str="", description:str="", model: str="gemini-1.5-flash-002", output_json: bool = False, schema: Dict = ""):
    self.file = file
    self.system_instruction = description
    self.user_instruction = instruction
    self.model = model
    self.output_json = output_json
    self.schema = schema
    vertexai.init(
        project=os.getenv("PROJECT_ID", "vtxdemos"),
        location=os.getenv("REGION", "us-central1")
    )
    print(self.file)
    print(self.model)
    print(self.system_instruction)
    self.response = self.run()

  def run(self):
    if self.file != "":
      with open(self.file, "rb") as f:
        _pdf_data = f.read()
      _file = Part.from_data(
          mime_type="application/pdf",
          data=_pdf_data
      )
    else: _file = "No file available"
    _model = GenerativeModel(
        self.model,
        system_instruction=self.system_instruction
    )
    print(self.user_instruction)
    try:
      if self.output_json and self.schema != "":
        _re=_model.generate_content(
            [self.user_instruction, "\nFile:\n", _file],
            generation_config=GenerationConfig(
                response_mime_type="application/json", response_schema=self.schema
            ),
        )
        return _re.text
      elif self.output_json and self.schema == "":
        return "schema is needed"
      else:
        _re=_model.generate_content(
            [self.user_instruction, "\nFile:\n", _file],
        )
        return _re.text
    except Exception as e:
      print(e)
