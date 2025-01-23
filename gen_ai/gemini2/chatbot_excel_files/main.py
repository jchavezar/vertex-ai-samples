#%%
import json
from google import genai
from google.genai import types
import pandas as pd

## Reading Spreadsheet
excel_file_path = "~/Downloads/test.xlsx"

try:
  all_sheets = pd.read_excel(excel_file_path, sheet_name=None)

  data = {}  # Dictionary to store all sheet data

  for sheet_name, df in all_sheets.items():
    sheet_data = []  # List to hold data for each row in the sheet
    for _, row in df.iterrows():
      row_dict = row.to_dict()  # Convert row to dictionary
      sheet_data.append(row_dict)  # Add row data to the list

    data[sheet_name] = sheet_data  # Add sheet data to the main dictionary

  # Convert to JSON:
  json_data = json.dumps(data, indent=4, ensure_ascii=False)  # indent for pretty printing, ensure_ascii for non-ASCII characters

  # Option 1: Print JSON to console:
  print(json_data)

  # Option 2: Save JSON to a file:
  with open("output.json", "w", encoding="utf-8") as f: # Use utf-8 encoding
    json.dump(data, f, indent=4, ensure_ascii=False) # Directly dump the dictionary to the file

except FileNotFoundError:
  print(f"Error: File not found at {excel_file_path}")
except Exception as e:
  print(f"An error occurred: {e}")

#%%

## AI
model = "gemini-1.5-pro-001"
contents = []
system_instruction = f"Use the following context to answer questions: {str(json_data)}\n\n End of Context.\n\n"

client = genai.Client(
    vertexai=True,
    project="jesusarguelles-sandbox",
    location="us-central1"
)

def chat_message(prompt: str):
  contents.append(
      types.Content(
          role="user",
          parts=[
              types.Part.from_text(prompt)
          ]
      )
  )

  try:
    re = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        )
    )
    print(re.text)
    contents.append(
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(re.text),
            ]
        )
    )
    return re.text
  except Exception as e:
    print(f"An error occurred: {e}")
    return "Error"

