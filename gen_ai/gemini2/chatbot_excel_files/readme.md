# Excel to Gemini Chatbot

This project demonstrates how to create a simple chatbot that uses Gemini to answer questions based on data from an Excel (XLSX) file.  The Excel data is first converted to JSON format, which is then used as context for the Gemini model.

## Project Overview

The Python script `excel_to_gemini.py` (or similar name) performs the following steps:

1.  **Reads Excel Data:** Reads data from an XLSX file using the `pandas` library.  It handles multiple sheets and converts the data into a structured dictionary.

2.  **Converts to JSON:** Converts the dictionary to a JSON string using the `json` library. This JSON string represents the context for Gemini.

3.  **Initializes Gemini:** Initializes the Gemini client using the `google-generativeai` library.  You'll need to configure your project and API key.

4.  **Defines `chat_message` Function:** Creates a function `chat_message` to interact with Gemini. This function takes a user prompt, adds it to the conversation history, sends it to Gemini with the JSON context as `system_instruction`, and prints the response.

## Code Breakdown

```python
import json
from google import genai
from google.genai import types
import pandas as pd

## Reading Spreadsheet
excel_file_path = "dataset.xlsx"  # Path to your Excel file

try:
    all_sheets = pd.read_excel(excel_file_path, sheet_name=None)
    data = {}
    for sheet_name, df in all_sheets.items():
        sheet_data = []
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            sheet_data.append(row_dict)
        data[sheet_name] = sheet_data

    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)  # Print JSON to console (optional)

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)  # Save JSON to file

except FileNotFoundError:
    print(f"Error: File not found at {excel_file_path}")
except Exception as e:
    print(f"An error occurred: {e}")

## AI Interaction
model = "gemini-1.5-pro-001"  # Or your preferred Gemini model
contents = []  # Conversation history
system_instruction = f"Use the following context to answer questions: {str(json_data)}\n\n End of Context.\n\n"

client = genai.Client(
    vertexai=True,
    project="your-project-id",  # Replace with your Google Cloud project ID
    location="your-project-location" # Replace with your Google Cloud location
)

def chat_message(prompt: str):
    contents.append(types.Content(role="user", parts=[types.Part.from_text(prompt)]))

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )
        print(response.text)
        contents.append(types.Content(role="model", parts=[types.Part.from_text(response.text)]))
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error"

# Example usage:
chat_message("What is the price of Product X from the Products sheet?") # Example query