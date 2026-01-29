import base64
import mimetypes
import os
import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")

async def generate_texture(prompt, file_name):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-3-pro-image-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
        ],
        image_config=types.ImageConfig(
            image_size="1K",
            aspect_ratio="16:9",
        ),
    )

    print(f"Generating image for: {file_name}...")
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    data = part.inline_data.data
                    mime_type = part.inline_data.mime_type
                    ext = mimetypes.guess_extension(mime_type) or ".png"
                    save_binary_file(f"{file_name}{ext}", data)
                    return True
        print(f"No image data in response for {file_name}")
    except Exception as e:
        print(f"Error generating image for {file_name}: {e}")
    return False

async def main():
    assets_dir = "frontend/public/assets/comps"
    os.makedirs(assets_dir, exist_ok=True)
    
    # Bullish Texture
    await generate_texture(
        "Generate a 'Quantum-Finance' background texture. Vibrant emerald-glass textures, glowing green data lines, premium frosted glass look, dark abstract background.",
        os.path.join(assets_dir, "bullish_texture")
    )
    
    # Bearish Texture
    await generate_texture(
        "Generate a 'Quantum-Finance' background texture. Deep obsidian-chrome textures, crimson-red glowing data lines, premium frosted glass look, dark abstract background.",
        os.path.join(assets_dir, "bearish_texture")
    )
    
    # Neutral Texture
    await generate_texture(
        "Generate a 'Quantum-Finance' background texture. Sleek sapphire-glass textures, blue and white glowing data lines, premium frosted glass look, dark abstract background.",
        os.path.join(assets_dir, "neutral_texture")
    )

if __name__ == "__main__":
    asyncio.run(main())
