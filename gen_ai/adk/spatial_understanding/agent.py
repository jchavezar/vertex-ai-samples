import os
import io
import sys

from google import genai
from google.genai import types
from google.adk import Agent
from pydantic import BaseModel
from PIL import Image, ImageColor, ImageDraw, ImageFont
from google.adk.tools.tool_context import ToolContext

model_id = "gemini-1.5-flash"

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

async def prepare_image_for_analysis(tool_context: ToolContext):
    """
    Prepares an image for analysis. It first checks the user's current message for an image and saves it.
    If no image is in the current message, it checks for a pre-existing image artifact.
    This tool standardizes the image artifact name to "user_uploaded_image.jpeg" for subsequent analysis.
    """
    print("IMAGE PREPARE", file=sys.stdout)
    for p in tool_context.user_content.parts:
        if p.inline_data and "image" in p.inline_data.mime_type:
            try:
                await tool_context.save_artifact(
                    filename="user_uploaded_image.jpeg",
                    artifact=types.Part.from_bytes(data=p.inline_data.data, mime_type=p.inline_data.mime_type)
                )
                return "Image prepared successfully and is ready for analysis."
            except Exception as e:
                return f"Error saving image: {e}. Please try again."

    try:
        artifacts = await tool_context.list_artifacts()
        image_artifacts = [
            a for a in artifacts
            if "image" in a.metadata.mime_type and a.filename not in ["image_with_bounding_boxes.jpeg", "user_uploaded_image.jpeg"]
        ]
        print(image_artifacts, file=sys.stdout)

        if any(a.filename == "user_uploaded_image.jpeg" for a in artifacts):
            return "Image is ready for analysis."

        if image_artifacts:
            latest_artifact_name = image_artifacts[-1].filename
            loaded_artifact = await tool_context.load_artifact(filename=latest_artifact_name)
            await tool_context.save_artifact(
                filename="user_uploaded_image.jpeg",
                artifact=loaded_artifact
            )
            return f"Found a previously uploaded image ('{latest_artifact_name}'). It is now ready for analysis."
    except Exception as e:
        return f"An error occurred while checking for existing images: {e}."

    return "Error: No image found to prepare. Please upload an image."

async def image_analyze(item_type_analysis: str, tool_context: ToolContext):
    """
    Analyzes the prepared image ("user_uploaded_image.jpeg") to detect 2D bounding boxes of a specified object type.
    Requires that the 'prepare_image_for_analysis' tool has been successfully run first.
    """
    image_artifact_name = "user_uploaded_image.jpeg"
    part = None

    try:
        part = await tool_context.load_artifact(filename=image_artifact_name)
        if not (part.inline_data and "image" in part.inline_data.mime_type):
            return f"Error: Artifact '{image_artifact_name}' is not a valid image."
        data = part.inline_data.data
    except Exception:
        return f"Error: Failed to load '{image_artifact_name}'. Please ensure an image was uploaded and prepared first."

    if data is None or part is None:
        return "Error: No image data found for analysis. Please ensure an image was prepared correctly."

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[item_type_analysis, part],
            config=config,
        )
        im = Image.open(fp=io.BytesIO(data))
        width, height = im.size
        draw = ImageDraw.Draw(im)
        colors = list(ImageColor.colormap.keys())
        font = ImageFont.load_default(size=int(min(width, height) / 100))
        for i, bbox in enumerate(response.parsed):
            abs_y_min = int(bbox.box_2d[0] / 1000 * height)
            abs_x_min = int(bbox.box_2d[1] / 1000 * width)
            abs_y_max = int(bbox.box_2d[2] / 1000 * height)
            abs_x_max = int(bbox.box_2d[3] / 1000 * width)
            color = colors[i % len(colors)]
            draw.rectangle(
                ((abs_x_min, abs_y_min), (abs_x_max, abs_y_max)),
                outline=color,
                width=4,
            )
            if bbox.label:
                draw.text(
                    (abs_x_min + 8, abs_y_min + 6),
                    bbox.label,
                    fill=color,
                    font=font,
                )
        output_image_stream = io.BytesIO()
        im.save(output_image_stream, format="JPEG")
        output_image_bytes = output_image_stream.getvalue()

        await tool_context.save_artifact(
            filename="image_with_bounding_boxes.jpeg",
            artifact=types.Part.from_bytes(
                data=output_image_bytes,
                mime_type="image/jpeg"
            )
        )
        return f"Image analyzed. Processed image saved to 'image_with_bounding_boxes.jpeg'. Found {len(response.parsed)} objects."
    except Exception as e:
        return f"Error during image analysis: {e}"


root_agent = Agent(
    name="root_agent",
    model=model_id,
    description="You are an object detection specialist. You identify objects in images and draw bounding boxes around them.",
    instruction="""You are an intelligent object detector. Your primary function is to identify objects in images and draw bounding boxes around them.

    **Core Workflow**

    1.  **Image Preparation**: When a user provides an image, you MUST ALWAYS call the `prepare_image_for_analysis` tool first. This is a mandatory first step to process and standardize the image.

    2.  **Decision Point**: After `prepare_image_for_analysis` runs successfully, you must decide the next action based on the user's original request:

        *   **Scenario A (One-Shot Request):** If the user's message that included the image *also* contained instructions on what to detect (e.g., "find the cats in this picture," "can you spot the scratch on this car"), you MUST IMMEDIATELY proceed to call the `image_analyze` tool. Use the object description from the user's prompt as the `item_type_analysis` parameter. Do not ask the user for information they have already provided.

        *   **Scenario B (Image-Only Upload):** If the user's message only contained an image without specifying what to detect, THEN you MUST ask the user what specific object(s) they want you to find in the image. Once they respond, you can then call the `image_analyze` tool with their description.

    **Initial Interaction**

    When the conversation starts, ask the user to choose from these options:
    1. Detect objects in an image.
    2. Ask a general question.

    If they choose option 2, simply answer their question directly.
    """,
    tools=[prepare_image_for_analysis, image_analyze]
)