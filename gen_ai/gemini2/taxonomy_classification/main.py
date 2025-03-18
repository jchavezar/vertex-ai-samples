#%%
import os
import base64
from google import genai
from google.genai import types

project = "vtxdemos"
region = "us-central1"
file_url = "./gen_ai/gemini2/taxonomy_classification/google_product_taxonomy.txt"

client = genai.Client(
    vertexai=True,
    project=project,
    location=region
)

system_instruction = """You have access to a strictly limited local file containing a partial Google Product Taxonomy. Your task is to classify either text or images into the EXACT matching category within this local file, if and only if a precise match exists.

Process:

1. Strict Local File Matching:
    * First and Foremost: Absolutely verify if the provided text or image exactly matches a category within the attached local file (Google Product Taxonomy).
    * If and ONLY if a precise, identical match is found: Use that category. Include the complete category path, the numerical hierarchy level AND the category number from the local file in your response.
    * For example: `Taxonomy: 2580 - Clothing & Accessories > Clothing > Nightwear & Loungewear > Pyjamas (Level 5) Source: local_file`
    * If there is ANY deviation or ambiguity, DO NOT use the local file.

2. Google Search Grounding (If No Exact Match):
    * ONLY if a precise match is NOT found in the local file, use Google Search to find relevant product categories.
    * Create a new taxonomy path based on the search results.
    * Ensure the taxonomy is logical and aligns with standard product classifications.

3. Knowledge Base Fallback (If Google Search Fails):
    * ONLY if NEITHER the local file NOR Google Search provides a clear or accurate classification, use your general knowledge to create a reasonable product taxonomy.

Response Format:

Provide your response in the following format:

`Taxonomy: [Category Number] - [Full Category Path] (Level [Hierarchy Level])`
`Source: [local_file, google_search, or base_knowledge]`

Example:

Input: Image of a men's red pajamas.

Possible Output (if found in local file):

`Taxonomy: 2580 - Clothing & Accessories > Clothing > Nightwear & Loungewear > Pyjamas (Level 5)`
`Source: local_file`

Possible Output (if not found in local file, but found via google search):

`Taxonomy: Clothing > Men's Clothing > Nightwear > Loungewear`
`Source: google_search`

Possible Output (if neither local file nor google search provide an answer):

`Taxonomy: Clothing > Pajamas`
`Source: base_knowledge`"""

message_to_classify = """
PRODUCT_NAME: National Tree Co. 10' Kinswood Fir Pencil Tree
PRODUCT DESCRIPTION: A festive fit for small plces and tight spaces, this lifelike kingswood fir 
is pre-strung with 600 clear lights that remain lit even if a bulb burns out.
"""

msg = types.Part.from_text(text=message_to_classify)


with open(file_url, "rb") as f:
    doc = f.read()
    document = types.Part.from_bytes(
        data=doc,
        mime_type="text/plain"
    )

tools = [
    types.Tool(google_search=types.GoogleSearch())
]

config = types.GenerateContentConfig(
    temperature=0,
    system_instruction=system_instruction,
    tools=tools
)

re = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=[
        types.Content(
            role="user",
            parts=[
                msg,
                document
            ]
        )
    ],
    config=config
)

re.text