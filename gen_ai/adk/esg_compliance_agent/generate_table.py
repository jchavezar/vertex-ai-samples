#%%
import os
import json
from google import genai
from prompts import GENERATE_ESG_TABLE

model_id = "gemini-2.5-flash"

table_schema_required = {
    "name": "get_esg_policy_master_list",
    "description": "Retrieves the master table of corporate ESG policies defines required green actions based on tech items.",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "policies": {
                "type": "array",
                "description": "List of rows representing the ESG policy table.",
                "items": {
                    "type": "object",
                    "properties": {
                        "Policy_ID": {
                            "type": "string",
                            "description": "Unique ID for the policy rule (e.g., 'POL-01')."
                        },
                        "Trigger_Item_Keywords": {
                            "type": "string",
                            "description": "Keywords of usual technology items that trigger this policy (e.g., 'Laptops, Desktops, Monitors')."
                        },
                        "Emission_Intensity": {
                            "type": "string",
                            "description": "Description of the impact category (e.g., 'Low - Scope 3 Manufacturing' or 'High - Continuous Power Draw')."
                        },
                        "Required_Green_Action": {
                            "type": "string",
                            "description": "The specific ESG measure the company must take (e.g., 'Reforestation/Tree Planting', 'Purchase Carbon Credits')."
                        },
                        "Agent_Calculation_Rule": {
                            "type": "string",
                            "description": "Natural language instructions for the AI on how to calculate the required units based on CO2 data found online."
                        }
                    },
                    "required": [
                        "Policy_ID",
                        "Trigger_Item_Keywords",
                        "Emission_Intensity",
                        "Required_Green_Action",
                        "Agent_Calculation_Rule"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": [
            "policies"
        ],
        "additionalProperties": False
    }
}

config = genai.types.GenerateContentConfig(
    # response_schema=table_schema_required,
    response_json_schema=table_schema_required,
    response_mime_type="application/json",
)

client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)

re = client.models.generate_content(
    model=model_id,
    contents=GENERATE_ESG_TABLE,
    config=config,
)

output = json.loads(re.text)

