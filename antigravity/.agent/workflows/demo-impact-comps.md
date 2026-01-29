---
description: A workflow that creates the layer of Comp Analysis in the left side panel.
---

Builds a high-impact, agent-driven "Comps Analysis" tab. Uses the logic in @backend/src/adk_comps_workflow.py (search for this file in the workspace under the folder stock-terminal-next) which uses google-adk to gather intelligence and Nano Banana 3 to generate dynamic, high-fidelity visual assets for a "Wow Factor" demo experience.

The first window should be input text target ticker and another input text strategic focus ticker.

Step 1: Spawn the Isolated "Intelligence Agent"
Agent Instruction: Use the google-adk skill to instantiate a standalone backend agent process.

Step 2: Clone the adk_comps_workflow.py and its components in a new comp_analysis folder with all the logic and add components to the google adk pipe inside to gather the following information:

you should run a dry run first to check if the pipe works from end to end before creating the UI content.

- Don't just look for stock prices. Find:
-- Latest product launch news using google-search tool in adk.
-- Sentiment from using the chatbot endpoint already built. Or if can't find it use google-search tool in adk to get it 
-- Visual brand identity assets for competitors (e.g., NVDA, AAPL, TSLA).

Logic: The agent must synthesize this into a "Battlecard" format for each competitor, ready for UI population.

Step 3: Visual Generation with Nano Banana 3

Agent Instruction: Use Nano Banana 3 as the "Creative Engine" to generate high-impact visual assets for the tab:

- The Creative Prompt: "Generate a 'Quantum-Finance' background texture for each competitor card (as a template). If the company is Bullish, use vibrant emerald-glass textures; if Bearish, use deep obsidian-chrome.


Action: Save these generated images to an isolated assets folder.

Step 4: UI/UX "Wow Factor" Design (Code-Builder)
The Tab Experience:
The "Arena" View: Instead of a list, design an "Arena" layout. Competitors are displayed in a 3D arc using Framer Motion.
Holographic Comparison: When two companies are selected, the isolated agent must generate a "Holographic Diff"—a glowing overlay showing the performance gap, using the Nano Banana 3 glass textures.
Glassmorphism: Apply a heavy "Banana-Frost" (frosted glass) effect to all data panels to ensure a premium, modern feel.

Step 5: Filling the fields:
- Once your assets for the UI has been designed store them in a special folder for the visuals.
- Design all the UI so when the input texts has been fulfill start the syncying process using the backend google adk python code described before.
- The backend script will start to gather all the information.
- Once the information has been gathered either use the templates stored and dynamically change the comp analysis page with the content generated or build another pipeline to create the the battlecards again with the information gathered.


Here are some instructions of how to use nano banana in python:
# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import mimetypes
import os
from google import genai
from google.genai import types


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-3-pro-image-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""generate"""),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
        image_config=types.ImageConfig(
            image_size="1K",
        ),
        tools=tools,
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            file_name = f"ENTER_FILE_NAME_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            save_binary_file(f"{file_name}{file_extension}", data_buffer)
        else:
            print(chunk.text)

if __name__ == "__main__":
    generate()


Visuals are important but the information gathering need to be real using the backend and scripts.
