import os
import io
from google import genai
from google.genai import types
from google.adk import Agent
from pydantic import BaseModel
from PIL import Image, ImageColor, ImageDraw, ImageFont
from google.adk.tools.tool_context import ToolContext

model_id = "gemini-2.5-flash"

client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

class BoundingBox(BaseModel):
    box_2d: list[int]
    label: str

config = types.GenerateContentConfig(
    system_instruction="""Return bounding boxes as an array with labels. Never return masks. Limit to 25 objects.
    If an object is present multiple times, give each object a unique label according to its distinct characteristics (colors, size, position, etc..).""",
    temperature=0.5,
    response_mime_type="application/json",
    response_schema=list[BoundingBox],
)

async def image_analyze(tool_context: ToolContext):
    llm_request = tool_context.user_content
    for part in llm_request.parts:
        if part.inline_data is not None:

            prompt = "Detect the 2d bounding boxes of the image about cats only at most 25 objects (with `label` as cat description)"
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=[
                        prompt,
                        part
                    ],
                    config=config,
                )

                im = Image.open(fp=io.BytesIO(part.inline_data.data))
                width, height = im.size
                draw = ImageDraw.Draw(im)
                colors = list(ImageColor.colormap.keys())
                # Load a font
                font = ImageFont.load_default(size=int(min(width, height) / 100))
                for i, bbox in enumerate(response.parsed):
                    # Scale normalized coordinates to image dimensions
                    abs_y_min = int(bbox.box_2d[0] / 1000 * height)
                    abs_x_min = int(bbox.box_2d[1] / 1000 * width)
                    abs_y_max = int(bbox.box_2d[2] / 1000 * height)
                    abs_x_max = int(bbox.box_2d[3] / 1000 * width)

                    color = colors[i % len(colors)]

                    # Draw the rectangle using the correct (x, y) pairs
                    draw.rectangle(
                        ((abs_x_min, abs_y_min), (abs_x_max, abs_y_max)),
                        outline=color,
                        width=4,
                    )
                    if bbox.label:
                        # Position the text at the top-left corner of the box
                        draw.text(
                            (abs_x_min + 8, abs_y_min + 6),
                            bbox.label,
                            fill=color,
                            font=font,
                        )
                # Save the modified image to an in-memory byte stream as JPEG
                output_image_stream = io.BytesIO()
                im.save(output_image_stream, format="JPEG")
                output_image_bytes = output_image_stream.getvalue()

                # Save the modified image as a new artifact
                await tool_context.save_artifact(
                    filename="image_with_bounding_boxes.jpeg",
                    artifact=types.Part.from_bytes(
                        data=output_image_bytes,
                        mime_type="image/jpeg"
                    )
                )
                print("Image with bounding boxes saved as 'image_with_bounding_boxes.jpeg'")
                return f"Image analyzed. Bounding box data saved to 'bounding_boxes_data.json' and processed image saved to 'image_with_bounding_boxes.jpeg'. Found {len(response.parsed)} objects."
            except Exception as e:
                print(f"An error occurred during image processing: {e}")
                return f"Error: {e}"

    else:
        pass

root_agent = Agent(
    name="root_agent",
    model=model_id,
    description="You are AGI",
    instruction="""
     Always use your tool `image_analyze` when you receive an image to get bounding boxes.
    """,
    tools=[image_analyze]
)