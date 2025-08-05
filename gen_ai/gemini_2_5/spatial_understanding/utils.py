import requests
from PIL import Image, ImageColor, ImageDraw, ImageFont


def plot_bounding_boxes(image_uri: str, bounding_boxes: list) -> Image.Image:
    """
    Plots bounding boxes on an image with labels, using PIL and normalized coordinates.

    Args:
        image_uri: The URI of the image file.
        bounding_boxes: A list of BoundingBox objects. Each box's coordinates are in
                        normalized [y_min, x_min, y_max, x_max] format.
    Returns:
        A PIL Image object with the bounding boxes drawn on it.
    """
    im = Image.open(requests.get(image_uri, stream=True, timeout=10).raw)

    width, height = im.size
    draw = ImageDraw.Draw(im)
    colors = list(ImageColor.colormap.keys())

    # Load a font
    font = ImageFont.load_default(size=int(min(width, height) / 100))

    for i, bbox in enumerate(bounding_boxes):
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

    return im