"""Spatial Understanding agent for Gemini Enterprise.

Pipeline:
  1. User attaches an image in GE chat. GE delivers it as an ADK ARTIFACT and
     injects `<start_of_user_uploaded_file: NAME>` text markers into the user
     message. (Confirmed by the-paperclip-detective forensic agent.)
  2. `detect_objects` lists artifacts, loads the user's image, asks Gemini for
     2-D bounding boxes (normalised 0..1000), draws them with PIL, and saves
     the annotated JPEG as a NEW artifact ("annotated_<source>.jpeg").
  3. The agent is registered with the built-in `load_artifacts` tool. ADK auto-
     injects an "artifacts available" notice on the next turn and, when the
     model calls `load_artifacts`, appends the JPEG bytes as an `inline_data`
     Part. The model then echoes that Part in its response, and the GE chat UI
     renders it inline because its mime type starts with `image/`.

References:
  - ADK artifacts: https://adk.dev/artifacts/
  - load_artifacts source: https://github.com/google/adk-python/blob/main/src/google/adk/tools/load_artifacts_tool.py
  - GE streamAssist part shape (inlineData): discoveryengine v1alpha
"""
from __future__ import annotations

import io
import logging
import os

from google import genai
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext, load_artifacts
from google.genai import types
from PIL import Image, ImageColor, ImageDraw, ImageFont
from pydantic import BaseModel

logger = logging.getLogger("spatial-on-ge")
logger.setLevel(logging.INFO)

DETECTION_MODEL = os.environ.get("SPATIAL_DETECTION_MODEL", "gemini-2.5-flash")
AGENT_MODEL = os.environ.get("SPATIAL_AGENT_MODEL", "gemini-2.5-flash")

_client = genai.Client(
    vertexai=True,
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
)


class BoundingBox(BaseModel):
    box_2d: list[int]  # [y_min, x_min, y_max, x_max] normalised 0..1000
    label: str


_DETECT_CONFIG = types.GenerateContentConfig(
    system_instruction=(
        "Return bounding boxes as a JSON array of objects with `box_2d` "
        "([y_min, x_min, y_max, x_max] normalised 0..1000) and `label`. "
        "Never return masks. Limit to 25 objects. Give each instance a "
        "unique label using its distinguishing colour, size, or position."
    ),
    temperature=0.3,
    response_mime_type="application/json",
    response_schema=list[BoundingBox],
)


async def _pick_source_image(tool_context: ToolContext) -> tuple[str, types.Part] | None:
    """Find the most recent user-uploaded image artifact (skip our own outputs)."""
    try:
        names = await tool_context.list_artifacts()
    except Exception as exc:  # noqa: BLE001
        logger.warning("list_artifacts failed: %s", exc)
        return None

    candidates = []
    for name in names or []:
        if name.startswith("annotated_"):
            continue
        try:
            part = await tool_context.load_artifact(name)
        except Exception as exc:  # noqa: BLE001
            logger.warning("load_artifact(%s) failed: %s", name, exc)
            continue
        inline = getattr(part, "inline_data", None)
        if inline and (inline.mime_type or "").startswith("image/"):
            candidates.append((name, part))

    if not candidates:
        return None
    return candidates[-1]


async def detect_objects(
    object_description: str,
    tool_context: ToolContext,
) -> dict:
    """Detect objects matching `object_description` in the most recent uploaded image.

    Loads the latest user-uploaded image artifact, asks Gemini for normalised
    2-D bounding boxes for the requested object class(es), draws coloured
    rectangles + labels with PIL, and saves the annotated image as a new
    artifact named `annotated_<source>.jpeg`.

    Args:
      object_description: What to detect, e.g. "all cats", "scratches on the
        car", "every bottle on the shelf". Free-form natural language.

    Returns:
      A dict with `status`, `count`, `annotated_artifact`, and `objects`
      (list of {label, box_2d}). On failure returns `status="error"` with
      a human-readable `message`.
    """
    picked = await _pick_source_image(tool_context)
    if picked is None:
        return {
            "status": "error",
            "message": (
                "No image found. Please attach an image to the chat (paperclip "
                "icon) and re-send your request."
            ),
        }
    source_name, part = picked
    image_bytes = part.inline_data.data
    mime_type = part.inline_data.mime_type or "image/jpeg"

    try:
        response = _client.models.generate_content(
            model=DETECTION_MODEL,
            contents=[
                f"Detect the following in this image: {object_description}",
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
            config=_DETECT_CONFIG,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Detection model call failed")
        return {"status": "error", "message": f"Detection model error: {exc}"}

    boxes: list[BoundingBox] = response.parsed or []
    if not boxes:
        return {
            "status": "ok",
            "count": 0,
            "annotated_artifact": None,
            "objects": [],
            "message": (
                f"No '{object_description}' detected in the attached image."
            ),
        }

    try:
        im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Could not open image: {exc}"}

    width, height = im.size
    draw = ImageDraw.Draw(im)
    palette = [
        "#FF3B30", "#FF9500", "#FFCC00", "#34C759", "#00C7BE",
        "#30B0C7", "#007AFF", "#5856D6", "#AF52DE", "#FF2D55",
    ]
    font_size = max(14, int(min(width, height) / 60))
    try:
        font = ImageFont.load_default(size=font_size)
    except TypeError:
        font = ImageFont.load_default()

    serialised = []
    for i, bbox in enumerate(boxes):
        if not bbox.box_2d or len(bbox.box_2d) != 4:
            continue
        y_min = int(bbox.box_2d[0] / 1000 * height)
        x_min = int(bbox.box_2d[1] / 1000 * width)
        y_max = int(bbox.box_2d[2] / 1000 * height)
        x_max = int(bbox.box_2d[3] / 1000 * width)
        colour = palette[i % len(palette)]
        draw.rectangle([(x_min, y_min), (x_max, y_max)], outline=colour, width=4)
        label = bbox.label or "object"
        text_xy = (x_min + 6, max(0, y_min - font_size - 4))
        try:
            text_bbox = draw.textbbox(text_xy, label, font=font)
            draw.rectangle(text_bbox, fill=colour)
            draw.text(text_xy, label, fill="white", font=font)
        except Exception:  # noqa: BLE001
            draw.text(text_xy, label, fill=colour, font=font)
        serialised.append({"label": label, "box_2d": bbox.box_2d})

    out_buf = io.BytesIO()
    im.save(out_buf, format="JPEG", quality=88)
    annotated_bytes = out_buf.getvalue()

    annotated_name = f"annotated_{source_name.rsplit('.', 1)[0]}.jpeg"
    await tool_context.save_artifact(
        filename=annotated_name,
        artifact=types.Part.from_bytes(data=annotated_bytes, mime_type="image/jpeg"),
    )
    logger.info(
        "Detected %d object(s) in %s -> %s", len(serialised), source_name, annotated_name
    )

    return {
        "status": "ok",
        "count": len(serialised),
        "source_artifact": source_name,
        "annotated_artifact": annotated_name,
        "objects": serialised,
    }


INSTRUCTION = """\
You are a spatial-understanding specialist. You detect objects in user-attached
images and return an annotated image with coloured bounding boxes plus a list
of what you found.

## How files reach you
When a user attaches an image via the chat paperclip, two things happen:
  - The image lands in the ADK artifact store.
  - A text marker `<start_of_user_uploaded_file: NAME>` is injected into the
    user's message so you know an image is present.

The bytes are NOT inline in your context. To act on the image you call the
`detect_objects` tool — it loads the artifact for you.

## Required workflow on every detection request

1. **Confirm an image is present.** If the user message contains a
   `<start_of_user_uploaded_file:` marker, an image is attached. If it does
   not, ask the user to attach one and stop.

2. **Decide what to detect.**
   - If the user's message says what to look for (e.g. "find the cats", "spot
     the scratch", "count the bottles"), use that as the
     `object_description`.
   - If the user only attached an image with no instruction, ask what they
     want detected. Do NOT call the tool yet.

3. **Call `detect_objects`** with the `object_description`. Wait for the
   result.

4. **Render the annotated image.** After `detect_objects` returns successfully
   (status="ok", count > 0), you MUST call `load_artifacts` and pass it the
   `annotated_artifact` filename from the tool result. This pulls the
   annotated JPEG into your response so the chat UI displays it inline.

5. **Reply with a short summary.** One or two sentences naming what you
   detected and how many. The image is rendered automatically — do not try
   to describe pixels you cannot see.

## Edge cases
- `count == 0`: tell the user nothing matched and suggest a different query.
  Do NOT call `load_artifacts` — there is nothing to render.
- `status == "error"`: relay the error message verbatim and ask them to try
  again.
- General questions unrelated to images: answer directly, no tool calls.
"""


root_agent = LlmAgent(
    name="spatial_on_ge",
    model=AGENT_MODEL,
    description=(
        "Detects and annotates objects in user-attached images using Gemini "
        "spatial understanding, then renders the boxed image inline in chat."
    ),
    instruction=INSTRUCTION,
    tools=[detect_objects, load_artifacts],
)
