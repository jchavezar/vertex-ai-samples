#%%
import os
import base64
from google import genai
from google.genai import types

project = "vtxdemos"
region = "us-central1"
file_url = "google_product_taxonomy.txt"

client = genai.Client(
    vertexai=True,
    project=project,
    location=region
)

system_instruction = """
You have a local file with product categories. Classify the input (text or image) using the MOST specific category from the local file.

1.  **Local File Priority:**
    * Find an EXACT match in the local file.
    * ALWAYS choose the MOST detailed (lowest level) category available.
    * If a subcategory exists, use it instead of the parent category.
    * Include the category number, full path, and hierarchy level.
    * Example: `Taxonomy: 2580 - Clothing & Accessories > Clothing > Nightwear & Loungewear > Pyjamas Source: local_file`

2.  **Search Backup:**
    * If NO exact local match, use Google Search to find a category.
    * Create a logical taxonomy path.
    * Source: `google_search`

3.  **Knowledge Fallback:**
    * If NEITHER local file nor search works, use general knowledge.
    * Create a reasonable taxonomy.
    * Source: `base_knowledge`

**Response Format:**

`Taxonomy: [Category Number] - [Full Category Path]`
`Source: [local_file, google_search, or base_knowledge]`

**Example:**

Input: Image of a jewelry set.

Output (if in local file):

`Taxonomy: 6463 - Clothing & Accessories > Jewellery & Watches > Jewellery Sets`
`Source: local_file`
"""



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

tool_history = []

def chat_bot_master(text: str, image: bytes):
    start_prompt = types.Part.from_text(text="Google Product Taxonomy (local_file):\n")
    image = types.Part.from_bytes(data=image, mime_type="image/png")
    additional_text = types.Part.from_text(text=f"The following will add additional information to the task: {text}")
    re = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[
            types.Content(
                role="user",
                parts=[
                    start_prompt,
                    document,
                    # msg,
                    image,
                    # additional_text
                ]
            )
        ],
        config=config
    )
    print(re)
    return re.text


chat_history = []


def conversation_bot(text: str, image: bytes = None, chat_bot_response: str = None):
    parts = [
        types.Part.from_text(text=text)
    ]

    print(image)
    print(chat_bot_response)
    if image and chat_bot_response:
        parts.append(types.Part.from_text(text="""Previous Tool History: \n the following are the system_instructions, images and response from a tool used
        used them in case something is asked about that previous result.
        """))
        parts.append(types.Part.from_bytes(data=image, mime_type="image/png"))
        parts.append(types.Part.from_text(text=f"Precious response from the Tool: {chat_bot_response}"))
        parts.append(types.Part.from_text(text=f"Previous tool System Instructions: \n {system_instruction} \n end_ of Previous Tool History"))

    chat_history.append(types.Content(role="user", parts=parts))

    re = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=chat_history,
    )
    chat_history.append(re.text)
    return re.text
