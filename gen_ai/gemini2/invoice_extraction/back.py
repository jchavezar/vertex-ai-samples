#%%
import json
from google import genai
from google.genai import types

project = "vtxdemos"
location = "us-central1"
model = "gemini-2.0-flash-001"

gem_client = genai.Client(
    vertexai=True,
    project=project,
    location=location
)

system_instruction = """
You are an ocr expert, your mission is to extract every single value from the document.
"""

response_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "invoice_id": {
                "type": "string"
            },
            "payer_name": {
                "type": "string"
            },
            "payer_address": {
                "type": "string"
            },
            "date": {
                "type": "string"
            },
            "due_date": {
                "type": "string"
            },
            "balance_due": {
                "type": "string"
            },
            "table": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item": {
                            "type": "string"
                        },
                        "quantity": {
                            "type": "integer"
                        },
                        "rate": {
                            "type": "string"
                        },
                        "amount": {
                            "type": "string"
                        }
                    }
                }
            },
            "subtotal": {
                "type": "number"
            },
            "discounts": {
                "type": "number"
            },
            "tax": {
                "type": "number"
            },
            "total": {
                "type": "number"
            },
            "amount_paid": {
                "type": "number"
            },
            "notes": {
                "type": "string"
            },
            "terms": {
                "type": "string"
            }
        }
    }
}

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    response_mime_type="application/json",
    response_schema=response_schema
)



def generate_content(file_location: str) -> json:
    with open(file_location, "rb") as f:
        doc = f.read()
    file_to_gem = types.Part.from_bytes(data=doc, mime_type="application/pdf")

    try:
        response = gem_client.models.generate_content(
            model=model,
            contents=[file_to_gem, types.Part.from_text(text="extract")],
            config=config
        )
        return response.text
    except Exception as e:
        print(f"Error {e}")
        return "Error"