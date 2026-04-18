import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client
# Using vertexai=True as per workspace norms, region 'global' or 'us-central1'
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1" # Or 'global' if using preview models

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)

MODEL_NAME = "gemini-2.5-flash" # Use allowed model

class ChatMessage(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    history: List[ChatMessage]
    message: str

@app.get("/api/spots")
async def get_spots(query: str = Query(..., description="The vibe or location to search for")):
    """
    Search for real places using Gemini with Google Search Grounding.
    """
    # Step 1: Search (Text info)
    search_prompt = f"Find 3 real restaurants, attractions, or cafes in {query}. Provide details about rating, description, and vibe."
    
    try:
        search_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=search_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
        )
        search_text = search_response.text
    except Exception as e:
        return {"error": f"Search failed: {str(e)}", "fallback": True}

    # Step 2: Format (JSON)
    format_prompt = f"""
    Format the information into a JSON array of objects matching the schema below.
    Text:
    {search_text}

    Schema:
    [
      {{
        "title": "Place Name",
        "type": "Restaurant, Attraction, or Cafe",
        "rating": 4.5,
        "desc": "Short 1-2 sentence description.",
        "summary": "Detailed summary citing why it's recommended.",
        "category": "food, nature, cafe, or other",
        "tags": ["insta", "blog", "tube"]
      }}
    ]
    """

    try:
        format_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=format_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json" # Supported here because NO search tool is used!
            )
        )
        parsed_data = format_response.text
        print(f"DEBUG Initial type: {type(parsed_data)}, value preview: {str(parsed_data)[:100]}")
        while isinstance(parsed_data, str):
            try:
                temp = json.loads(parsed_data)
                print(f"DEBUG Parsed type: {type(temp)}, value preview: {str(temp)[:100]}")
                parsed_data = temp
            except Exception as e:
                print(f"DEBUG Parse failed: {e}")
                break
        print(f"DEBUG Final type: {type(parsed_data)}")
        return parsed_data
    except Exception as e:
        return {"error": f"Format failed: {str(e)}", "raw_text": search_text}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat with the Vibe Concierge, grounded in search if needed.
    """
    # Convert history to Gemini format
    contents = []
    for msg in request.history:
        role = "user" if msg.role == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.text)]))
    
    # Append the new message
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=request.message)]))

    system_instruction = "You are the Local Pulse Concierge. You use Google Search to find real, current information about local spots. Be helpful, enthusiastic, and provide real links or names if possible. Keep it concise."

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
        )
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Sorry, I had an error: {str(e)}"}

@app.get("/api/spots/similar")
async def get_similar_spots(title: str = Query(..., description="The name of the place to find similar spots for")):
    """
    Search for similar real places using Gemini with Google Search Grounding.
    """
    # Step 1: Search (Find similar)
    search_prompt = f"Find 3 real restaurants, attractions, or cafes that are SIMILAR to '{title}' in vibe, category, or experience. Provide details about rating and how they are similar."
    
    try:
        search_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=search_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
        )
        search_text = search_response.text
    except Exception as e:
        return {"error": f"Search failed: {str(e)}", "fallback": True}

    # Step 2: Format (JSON)
    format_prompt = f"""
    Format the information into a JSON array of objects matching the schema below.
    Text:
    {search_text}

    Schema:
    [
      {{
        "title": "Place Name",
        "type": "Restaurant, Attraction, or Cafe",
        "rating": 4.5,
        "desc": "Short 1-2 sentence description of similarities.",
        "summary": "Detailed summary citing why it's recommended.",
        "category": "food, nature, cafe, or other",
        "tags": ["insta", "blog"]
      }}
    ]
    """

    try:
        format_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=format_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        parsed_data = format_response.text
        # double parse checking
        while isinstance(parsed_data, str):
            try:
                parsed_data = json.loads(parsed_data)
            except:
                break
        return parsed_data
    except Exception as e:
        return {"error": f"Format failed: {str(e)}", "raw_text": search_text}

@app.get("/health")
async def health():
    return {"status": "ok", "version": 2}
